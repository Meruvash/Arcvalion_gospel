#!/usr/bin/env node
// Baixa um vídeo público do YouTube em MP4, sem login, sem cookies e sem yt-dlp.
//   Motor 1: instância LOCAL do Cobalt (imputnet/cobalt, AGPL-3.0), via POST JSON.
//   Motor 2: YouTube.js (LuanRT/YouTube.js, MIT) + FFmpeg para juntar vídeo e áudio.
// Só declara sucesso depois de verificar o arquivo com ffprobe (vídeo + áudio + duração).
// Uso: node baixar.mjs <url> [--pasta DIR] [--qualidade 1080|1440|2160|max] [--motor auto|cobalt|youtubejs]
//                              [--cobalt http://localhost:9000/] [--json]
// Códigos de saída: 0 verificado · 2 exige login/idade · 3 fluxo bloqueado (PO Token ou IP) · 4 limite/bloqueio de IP
//                   5 vídeo indisponível/privado/região · 6 instância do Cobalt fora do ar · 1 outro erro
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

// ------------------------------------------------------------------ argumentos
const argv = process.argv.slice(2);
const opt = { pasta: process.cwd(), qualidade: '1080', motor: 'auto', cobalt: process.env.COBALT_API_URL || 'http://localhost:9000/', json: false };
const pos = [];
for (let i = 0; i < argv.length; i++) {
  const a = argv[i];
  if (a === '--json') opt.json = true;
  else if (a.startsWith('--')) opt[a.slice(2)] = argv[++i];
  else pos.push(a);
}
const URL_IN = pos[0];
if (!URL_IN) { console.error('uso: node baixar.mjs <url do YouTube> [--pasta DIR] [--qualidade 1080|1440|2160|max] [--motor auto|cobalt|youtubejs]'); process.exit(1); }
fs.mkdirSync(opt.pasta, { recursive: true });
const LOG = path.join(opt.pasta, '.youtube_baixar.log');
const log = (evento, dados = {}) => {
  const linha = { quando: new Date().toISOString(), evento, ...dados };
  fs.appendFileSync(LOG, JSON.stringify(linha) + '\n');
  if (!opt.json) console.error(`[${evento}]`, Object.entries(dados).map(([k, v]) => `${k}=${typeof v === 'string' ? v : JSON.stringify(v)}`).join(' '));
};

// O ambiente pode exigir proxy HTTPS: o fetch do Node só o usa com um dispatcher do undici.
try {
  if (process.env.HTTPS_PROXY || process.env.https_proxy) {
    const { EnvHttpProxyAgent, setGlobalDispatcher } = await import('undici');
    setGlobalDispatcher(new EnvHttpProxyAgent());
  }
} catch { /* sem undici: segue sem proxy */ }

// ------------------------------------------------------------------ utilidades
const idDoVideo = (u) => {
  try {
    const x = new URL(u);
    if (x.hostname.endsWith('youtu.be')) return x.pathname.slice(1).split('/')[0];
    if (x.searchParams.get('v')) return x.searchParams.get('v');
    const m = x.pathname.match(/\/(shorts|embed|live|v)\/([\w-]{11})/); if (m) return m[2];
  } catch {}
  return /^[\w-]{11}$/.test(u) ? u : null;
};
const ID = idDoVideo(URL_IN);
if (!ID) { log('erro', { tipo: 'url_invalida', url: URL_IN }); process.exit(1); }
const limpa = (s) => (s || ID).replace(/[\\/:*?"<>|\n\r]+/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 150);
const alvoQ = opt.qualidade === 'max' ? 4320 : parseInt(opt.qualidade, 10) || 1080;

class Falha extends Error { constructor(tipo, msg, codigo, extra = {}) { super(msg); this.tipo = tipo; this.codigo = codigo; this.extra = extra; } }

function ffprobe(arq) {
  const r = spawnSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration,size:stream=codec_type,codec_name,width,height', '-of', 'json', arq], { encoding: 'utf8' });
  if (r.status !== 0) return { ok: false, erro: (r.stderr || '').trim().slice(0, 300) };
  const j = JSON.parse(r.stdout);
  const v = j.streams.find(s => s.codec_type === 'video'), a = j.streams.find(s => s.codec_type === 'audio');
  const dur = parseFloat(j.format?.duration || '0');
  return { ok: Boolean(v && a && dur > 0), video: v ? `${v.codec_name} ${v.width}x${v.height}` : null, altura: v?.height || 0, audio: a?.codec_name || null, duracao_s: dur, bytes: Number(j.format?.size || 0) };
}

async function baixarParaArquivo(url, destino, { pedacos = false, total = 0 } = {}) {
  // googlevideo limita a velocidade de pedidos grandes: baixa em pedaços de 10 MB quando se sabe o tamanho.
  const out = fs.createWriteStream(destino);
  let n = 0;
  try {
    if (pedacos && total > 0) {
      const PASSO = 10 * 1024 * 1024;
      for (let ini = 0; ini < total; ini += PASSO) {
        const fim = Math.min(total - 1, ini + PASSO - 1);
        const r = await fetch(`${url}&range=${ini}-${fim}`);
        if (r.status !== 200 && r.status !== 206) throw new Falha(r.status === 403 ? 'fluxo_403' : r.status === 429 ? 'limite_ip' : 'http', `servidor de vídeo respondeu ${r.status}`, r.status === 403 ? 3 : r.status === 429 ? 4 : 1, { status: r.status });
        const buf = Buffer.from(await r.arrayBuffer()); n += buf.length; out.write(buf);
      }
    } else {
      const r = await fetch(url);
      if (!r.ok) throw new Falha(r.status === 403 ? 'fluxo_403' : r.status === 429 ? 'limite_ip' : 'http', `servidor respondeu ${r.status}`, r.status === 403 ? 3 : r.status === 429 ? 4 : 1, { status: r.status });
      for await (const ch of r.body) { n += ch.length; out.write(ch); }
    }
  } finally { await new Promise(res => out.end(res)); }
  return n;
}

// ------------------------------------------------------------------ motor 1: Cobalt local
const ERROS_COBALT = {
  'youtube.login': ['exige_login', 'o YouTube pediu login ("confirme que você não é um robô"): bloqueio do IP ou da instância', 2],
  'content.video.age': ['exige_login', 'vídeo com restrição de idade: só com conta logada', 2],
  'youtube.no_session_tokens': ['po_token', 'a instância exige PO Token de sessão (YOUTUBE_SESSION_SERVER) e não tem', 3],
  'youtube.token_expired': ['po_token', 'o token de sessão do YouTube expirou', 3],
  'fetch.rate': ['limite_ip', 'o YouTube limitou os pedidos deste IP (rate limit)', 4],
  'content.video.private': ['indisponivel', 'vídeo privado', 5],
  'content.video.unavailable': ['indisponivel', 'vídeo indisponível ou removido', 5],
  'content.video.region': ['indisponivel', 'vídeo bloqueado nesta região', 5],
  'content.video.live': ['indisponivel', 'transmissão ao vivo: não suportada', 5],
  'youtube.drm': ['indisponivel', 'vídeo com DRM: não é possível baixar', 5],
  'youtube.no_matching_format': ['formato', 'nenhum formato compatível com a qualidade pedida', 1],
  'fetch.fail': ['rede', 'a instância não conseguiu buscar o vídeo no YouTube', 1],
};
async function viaCobalt() {
  let r;
  try {
    r = await fetch(opt.cobalt, { method: 'POST', headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: `https://www.youtube.com/watch?v=${ID}`, videoQuality: opt.qualidade === 'max' ? 'max' : String(alvoQ), youtubeVideoCodec: 'h264', downloadMode: 'auto', filenameStyle: 'basic' }) });
  } catch (e) { throw new Falha('cobalt_fora', `instância do Cobalt fora do ar em ${opt.cobalt} (${e.cause?.code || e.message})`, 6); }
  const j = await r.json().catch(() => ({}));
  log('cobalt_resposta', { status: j.status, codigo: j.error?.code });
  if (j.status === 'error') {
    const chave = (j.error?.code || '').replace(/^error\.api\./, '');
    const [tipo, msg, cod] = ERROS_COBALT[chave] || ['cobalt', `erro do Cobalt: ${j.error?.code}`, 1];
    throw new Falha(tipo, msg, cod, { cobalt: j.error?.code });
  }
  if (!['tunnel', 'redirect'].includes(j.status)) throw new Falha('cobalt', `resposta inesperada do Cobalt: ${j.status}`, 1);
  const nome = limpa((j.filename || ID).replace(/\.\w+$/, ''));
  const destino = path.join(opt.pasta, `${nome}.mp4`);
  const n = await baixarParaArquivo(j.url, destino);
  if (n === 0) {
    fs.rmSync(destino, { force: true });
    // O túnel do Cobalt devolve 200 vazio quando o googlevideo recusa o fluxo (403): típico de PO Token ausente ou IP bloqueado.
    throw new Falha('fluxo_vazio', 'o túnel do Cobalt devolveu 0 byte: o servidor de vídeo do YouTube recusou o fluxo (provável exigência de PO Token ou bloqueio do IP)', 3);
  }
  return destino;
}

// ------------------------------------------------------------------ motor 2: YouTube.js + FFmpeg
async function viaYoutubeJs() {
  const { Innertube, Platform, Log } = await import('youtubei.js');
  Log.setLevel(process.env.YTJS_DEBUG ? Log.Level.DEBUG : Log.Level.NONE);
  // Os scripts do player do YouTube (decifrar assinatura e "n") precisam de um avaliador de JS.
  Platform.shim.eval = async (data) => new Function(data.output)();
  const yt = await Innertube.create({ retrieve_player: true });
  const tentativas = [];
  for (const client of ['IOS', 'MWEB', 'WEB', 'TV']) {
    let info;
    try { info = await yt.getBasicInfo(ID, { client }); }
    catch (e) { tentativas.push({ client, erro: String(e.message || e).slice(0, 160) }); continue; }
    const ps = info.playability_status || {};
    if (ps.status && ps.status !== 'OK') {
      tentativas.push({ client, status: ps.status, motivo: ps.reason });
      if (/sign in|confirm you.re not a bot|robô/i.test(ps.reason || '')) continue;
      if (ps.status === 'LOGIN_REQUIRED') continue;
      continue;
    }
    const fmts = info.streaming_data?.adaptive_formats || [];
    const vids = fmts.filter(f => f.has_video && !f.has_audio && f.height <= alvoQ).sort((a, b) => (b.height - a.height) || ((/avc1/.test(b.mime_type) ? 1 : 0) - (/avc1/.test(a.mime_type) ? 1 : 0)) || (b.bitrate - a.bitrate));
    const auds = fmts.filter(f => f.has_audio && !f.has_video).sort((a, b) => ((/mp4a/.test(b.mime_type) ? 1 : 0) - (/mp4a/.test(a.mime_type) ? 1 : 0)) || (b.bitrate - a.bitrate));
    if (!vids.length || !auds.length) { tentativas.push({ client, erro: 'sem formatos adaptativos de vídeo e áudio' }); continue; }
    const v = vids[0], a = auds[0];
    const urlDe = async (f) => f.url || (await f.decipher(yt.session.player));
    let uv, ua;
    try { uv = await urlDe(v); ua = await urlDe(a); } catch (e) { tentativas.push({ client, erro: 'decifrar: ' + String(e.message || e).slice(0, 120) }); continue; }
    const teste = await fetch(`${uv}&range=0-1023`).catch(e => ({ status: 'rede ' + (e.cause?.code || e.message) }));
    if (teste.status !== 200 && teste.status !== 206) { tentativas.push({ client, formato: `${v.height}p`, fluxo: teste.status }); continue; }
    log('youtubejs_formato', { client, video: `${v.height}p ${v.mime_type.split(';')[0]}`, audio: a.mime_type.split(';')[0] });
    const nome = limpa(info.basic_info?.title);
    const tv = path.join(opt.pasta, `.${ID}.video`), ta = path.join(opt.pasta, `.${ID}.audio`);
    await baixarParaArquivo(uv, tv, { pedacos: true, total: Number(v.content_length || 0) });
    await baixarParaArquivo(ua, ta, { pedacos: true, total: Number(a.content_length || 0) });
    const destino = path.join(opt.pasta, `${nome} (${v.height}p).mp4`);
    // Junta com FFmpeg: copia o vídeo; áudio Opus vira AAC para caber em MP4 com compatibilidade ampla.
    const acodec = /mp4a/.test(a.mime_type) ? ['-c:a', 'copy'] : ['-c:a', 'aac', '-b:a', '192k'];
    const vcodec = /avc1|av01|vp09|vp9/.test(v.mime_type) ? ['-c:v', 'copy'] : ['-c:v', 'libx264', '-crf', '18'];
    const ff = spawnSync('ffmpeg', ['-v', 'error', '-y', '-i', tv, '-i', ta, '-map', '0:v:0', '-map', '1:a:0', ...vcodec, ...acodec, '-movflags', '+faststart', destino], { encoding: 'utf8' });
    fs.rmSync(tv, { force: true }); fs.rmSync(ta, { force: true });
    if (ff.status !== 0) throw new Falha('ffmpeg', 'FFmpeg falhou ao juntar vídeo e áudio: ' + (ff.stderr || '').slice(0, 300), 1);
    return destino;
  }
  // Nenhum cliente serviu: classifica o motivo.
  const txt = JSON.stringify(tentativas);
  log('youtubejs_tentativas', { tentativas });
  if (/LOGIN_REQUIRED|sign in|not a bot/i.test(txt)) throw new Falha('exige_login', 'o YouTube exige login ou verificação "não sou um robô" para este IP', 2, { tentativas });
  if (/"fluxo":403/.test(txt)) throw new Falha('po_token', 'os formatos aparecem, mas o servidor de vídeo responde 403: o YouTube exige PO Token para o fluxo, ou bloqueou o IP', 3, { tentativas });
  if (/"fluxo":429/.test(txt)) throw new Falha('limite_ip', 'o YouTube limitou os pedidos deste IP (429)', 4, { tentativas });
  if (/UNPLAYABLE|ERROR|unavailable|private/i.test(txt)) throw new Falha('indisponivel', 'vídeo indisponível para os clientes anônimos', 5, { tentativas });
  throw new Falha('youtubejs', 'nenhum cliente do YouTube.js conseguiu o vídeo', 1, { tentativas });
}

// ------------------------------------------------------------------ execução
const motores = opt.motor === 'cobalt' ? [['cobalt', viaCobalt]] : opt.motor === 'youtubejs' ? [['youtubejs', viaYoutubeJs]] : [['cobalt', viaCobalt], ['youtubejs', viaYoutubeJs]];
const falhas = [];
log('inicio', { id: ID, pasta: opt.pasta, qualidade: opt.qualidade, motores: motores.map(m => m[0]) });
for (const [nome, fn] of motores) {
  try {
    const arq = await fn();
    const p = ffprobe(arq);
    if (!p.ok) { fs.renameSync(arq, arq + '.invalido'); throw new Falha('verificacao', `arquivo baixado não passou na verificação (${p.erro || 'falta vídeo, áudio ou duração'})`, 1, p); }
    log('verificado', { motor: nome, arquivo: arq, ...p, abaixo_do_pedido: p.altura < Math.min(alvoQ, 1080) });
    const res = { ok: true, motor: nome, arquivo: arq, ...p };
    console.log(opt.json ? JSON.stringify(res) : `VERIFICADO: ${arq} · ${p.video} + ${p.audio} · ${p.duracao_s.toFixed(1)} s · ${(p.bytes / 1e6).toFixed(1)} MB`);
    process.exit(0);
  } catch (e) {
    const f = e instanceof Falha ? e : new Falha('inesperado', String(e.message || e), 1);
    falhas.push({ motor: nome, tipo: f.tipo, mensagem: f.message, codigo: f.codigo, ...f.extra });
    log('falha', { motor: nome, tipo: f.tipo, mensagem: f.message });
  }
}
// Código de saída: o motivo mais informativo (bloqueios do YouTube têm prioridade sobre "Cobalt fora do ar").
const ordem = [2, 3, 4, 5, 1, 6];
const codigo = ordem.find(c => falhas.some(f => f.codigo === c)) ?? 1;
const res = { ok: false, codigo, falhas, log: LOG };
console.log(opt.json ? JSON.stringify(res) : `NÃO BAIXADO (código ${codigo}).\n` + falhas.map(f => `- ${f.motor}: ${f.mensagem}`).join('\n') + `\nRegistro: ${LOG}`);
process.exit(codigo);
