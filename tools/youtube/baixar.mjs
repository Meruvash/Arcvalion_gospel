#!/usr/bin/env node
// Baixa um vídeo PÚBLICO do YouTube em MP4 (vídeo + áudio), na melhor resolução disponível.
// Sem login Google, sem cookies, sem yt-dlp, sem Cobalt.
//
// Motores (dois extratores independentes entre si, ambos open source):
//   1. @distube/ytdl-core 5.x  — InnerTube próprio, assinatura resolvida localmente, PO token gerado
//      localmente (BotGuard via bgutils-js), formatos só-SABR via googlevideo.
//   2. youtubei.js (LuanRT)    — InnerTube, clientes ANDROID_VR e MWEB.
//   3. site (loader.to)        — serviço web de terceiros aberto num Chromium sem tela (Playwright): o servidor DELE
//      baixa do YouTube e entrega o MP4 pronto. Reserva para redes onde os motores 1 e 2 levam 403/429
//      (ex.: contêiner de nuvem do Claude Code). Sem login, sem cookies, sem resolver CAPTCHA.
// Vídeo e áudio chegam separados (DASH) e são juntados com ffmpeg sem recodificar.
//
// Uso:  node tools/youtube/baixar.mjs <url-ou-id> [opções]
//   --saida <pasta>          pasta de destino (padrão: .)
//   --nome <arquivo.mp4>     nome do arquivo final (padrão: título + id)
//   --max-altura <n>         limita a resolução (ex.: 1080). Padrão: a maior disponível
//   --h264                   só vídeo H.264 (avc1): máxima compatibilidade; no YouTube vai até 1080p
//   --vertical               avisa que o vídeo é 9:16 (Shorts/Reels) quando só o motor site roda (ajusta a opção pedida)
//   --motor distube|youtubei|site  força um motor (padrão: distube → youtubei → site)
//   --verificar-decodificacao decodifica o arquivo inteiro com ffmpeg para achar corrupção (mais lento)
//   --info                   só lista os formatos, sem baixar
//   --diagnostico            testa a rede (IP de extração × IP do servidor de mídia) e sai
//   --json                   imprime o resumo final em JSON no stdout
//
// Códigos de saída: 0 ok · 2 argumentos · 3 extração · 4 download · 5 integridade · 6 falta ffmpeg
import { spawnSync } from "node:child_process";
import { createWriteStream, existsSync, mkdirSync, appendFileSync, statSync, rmSync, renameSync } from "node:fs";
import { Readable } from "node:stream";
import { pipeline } from "node:stream/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

// O fetch nativo do Node só respeita HTTPS_PROXY com NODE_USE_ENV_PROXY=1 (Node 22.21+): reinicia com ele.
if ((process.env.HTTPS_PROXY || process.env.https_proxy) && !process.env.NODE_USE_ENV_PROXY && import.meta.url === `file://${process.argv[1]}`) {
  const r = spawnSync(process.execPath, process.argv.slice(1), {
    stdio: "inherit",
    env: { ...process.env, NODE_USE_ENV_PROXY: "1", NODE_NO_WARNINGS: "1" },
  });
  process.exit(r.status ?? 1);
}

export const SAIDA = { OK: 0, ARGS: 2, EXTRACAO: 3, DOWNLOAD: 4, INTEGRIDADE: 5, FFMPEG: 6 };

class Falha extends Error {
  constructor(codigo, mensagem, detalhe) { super(mensagem); this.codigo = codigo; this.detalhe = detalhe; }
}

// ---------- utilidades puras (testadas em teste.mjs) ----------

export function extrairId(entrada) {
  const s = String(entrada || "").trim();
  if (/^[A-Za-z0-9_-]{11}$/.test(s)) return s;
  let u;
  try { u = new URL(s); } catch { return null; }
  const host = u.hostname.replace(/^www\.|^m\.|^music\./, "");
  if (host === "youtu.be") return valido(u.pathname.slice(1).split("/")[0]);
  if (host === "youtube.com" || host === "youtube-nocookie.com") {
    if (u.searchParams.get("v")) return valido(u.searchParams.get("v"));
    const m = u.pathname.match(/^\/(?:shorts|embed|live|v)\/([A-Za-z0-9_-]{11})/);
    if (m) return m[1];
  }
  return null;
  function valido(id) { return /^[A-Za-z0-9_-]{11}$/.test(id || "") ? id : null; }
}

/** Normaliza um formato de qualquer motor para {itag, altura, fps, mime, codec, bitrate, tamanho, video, audio}. */
export function normalizar(f) {
  const mimeCompleto = f.mimeType ?? f.mime_type ?? "";
  const [mime, resto = ""] = mimeCompleto.split(";");
  const codec = (resto.match(/codecs="([^"]+)"/) || [])[1] || "";
  return {
    itag: f.itag,
    altura: f.height ?? 0,
    largura: f.width ?? 0,
    fps: f.fps ?? 0,
    mime: mime.trim(),
    codec,
    bitrate: f.bitrate ?? f.average_bitrate ?? 0,
    tamanho: Number(f.contentLength ?? f.content_length ?? 0) || 0,
    video: Boolean(f.hasVideo ?? f.has_video),
    audio: Boolean(f.hasAudio ?? f.has_audio),
    rotulo: f.qualityLabel ?? f.quality_label ?? "",
    canais: f.audioChannels ?? f.audio_channels ?? 0,
  };
}

const RANK_CODEC = (c) => (c.startsWith("avc1") ? 2 : c.startsWith("av01") ? 1 : 0);

/**
 * Escolhe o melhor par vídeo (MP4) + áudio (M4A).
 * Critério: maior altura <= maxAltura; empate → H.264 antes de AV1 (compatibilidade), depois fps e bitrate.
 * Sem formato adaptativo em MP4, cai para o progressivo MP4 com áudio (itag 18/22).
 */
export function escolherFormatos(formatos, { maxAltura = Infinity, h264 = false } = {}) {
  const fs = formatos.map((f) => (f.mime !== undefined && f.altura !== undefined ? f : normalizar(f)));
  const videos = fs
    .filter((f) => f.video && !f.audio && f.mime === "video/mp4" && f.altura > 0 && f.altura <= maxAltura)
    .filter((f) => !h264 || f.codec.startsWith("avc1"))
    .sort((a, b) => b.altura - a.altura || RANK_CODEC(b.codec) - RANK_CODEC(a.codec) || b.fps - a.fps || b.bitrate - a.bitrate);
  const audios = fs
    .filter((f) => f.audio && !f.video && f.mime === "audio/mp4")
    // estéreo antes de 5.1 (itag 256/258): toca em qualquer aparelho
    .sort((a, b) => Number((a.canais || 2) > 2) - Number((b.canais || 2) > 2) || b.bitrate - a.bitrate);
  if (videos.length && audios.length) return { tipo: "adaptativo", video: videos[0], audio: audios[0] };
  const progressivo = fs
    .filter((f) => f.video && f.audio && f.mime === "video/mp4" && f.altura <= maxAltura)
    .sort((a, b) => b.altura - a.altura)[0];
  if (progressivo) return { tipo: "progressivo", video: progressivo, audio: null };
  return null;
}

export function nomeArquivo(titulo, id) {
  const limpo = String(titulo || "video")
    .normalize("NFKC")
    .replace(/[\\/:*?"<>|\u0000-\u001f]/g, "")
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, 120);
  return `${limpo || "video"} [${id}].mp4`;
}

/** Traduz erros conhecidos dos motores para uma mensagem acionável. */
export function explicarErro(msg) {
  const m = String(msg || "");
  if (/LOGIN_REQUIRED|Sign in to confirm|not a bot/i.test(m))
    return "O YouTube pediu verificação anti-robô para este IP (LOGIN_REQUIRED). Isto é bloqueio de rede/IP, não do vídeo. Tente outra rede; esta ferramenta não usa login nem cookies.";
  if (/\b429\b|Too Many Requests/i.test(m))
    return "O YouTube limitou este IP (HTTP 429). Espere alguns minutos ou use outra rede.";
  if (/age|idade|AGE_VERIFICATION|inappropriate/i.test(m))
    return "Vídeo com restrição de idade: exige conta Google, que esta ferramenta não usa por regra.";
  if (/private|privado|members|membros/i.test(m))
    return "Vídeo privado ou só para membros: não é público, fora do escopo.";
  if (/\b403\b|non 2xx/i.test(m))
    return "O servidor de mídia (googlevideo) recusou o download (HTTP 403). Rode --diagnostico: em redes com saída por mais de um IP (nuvem, VPN, CGNAT dividido) a URL é assinada para um IP e o download sai por outro.";
  if (/unavailable|indisponível|UNPLAYABLE/i.test(m))
    return "O vídeo está indisponível para este cliente/região, ou foi removido.";
  return null;
}

// ---------- registro ----------

let ARQ_LOG = null;
function log(...partes) {
  const linha = `[${new Date().toISOString()}] ${partes.join(" ")}`;
  process.stderr.write(linha + "\n");
  if (ARQ_LOG) try { appendFileSync(ARQ_LOG, linha + "\n"); } catch { /* log é auxiliar */ }
}

// ---------- ffmpeg ----------

function temFfmpeg() {
  return spawnSync("ffmpeg", ["-version"]).status === 0 && spawnSync("ffprobe", ["-version"]).status === 0;
}

function juntar(video, audio, destino) {
  const r = spawnSync("ffmpeg", ["-y", "-v", "error", "-i", video, "-i", audio, "-map", "0:v:0", "-map", "1:a:0",
    "-c", "copy", "-movflags", "+faststart", destino], { encoding: "utf8" });
  if (r.status !== 0) throw new Falha(SAIDA.INTEGRIDADE, "ffmpeg não conseguiu juntar vídeo e áudio", r.stderr);
}

function remuxar(entrada, destino) {
  const r = spawnSync("ffmpeg", ["-y", "-v", "error", "-i", entrada, "-c", "copy", "-movflags", "+faststart", destino], { encoding: "utf8" });
  if (r.status !== 0) throw new Falha(SAIDA.INTEGRIDADE, "ffmpeg não conseguiu remuxar o arquivo", r.stderr);
}

/** Verifica o MP4 final: contêiner legível, 1 trilha de vídeo, ≥1 de áudio, duração coerente. */
export function verificar(arquivo, duracaoEsperada, { decodificar = false } = {}) {
  const r = spawnSync("ffprobe", ["-v", "error", "-show_entries",
    "format=duration,format_name:stream=codec_type,codec_name,width,height,avg_frame_rate", "-of", "json", arquivo], { encoding: "utf8" });
  if (r.status !== 0) throw new Falha(SAIDA.INTEGRIDADE, "ffprobe não leu o arquivo (contêiner corrompido?)", r.stderr);
  const p = JSON.parse(r.stdout);
  const v = p.streams.filter((s) => s.codec_type === "video");
  const a = p.streams.filter((s) => s.codec_type === "audio");
  const dur = Number(p.format?.duration || 0);
  const problemas = [];
  if (v.length !== 1) problemas.push(`esperava 1 trilha de vídeo, achou ${v.length}`);
  if (a.length < 1) problemas.push("sem trilha de áudio");
  if (!/mp4/.test(p.format?.format_name || "")) problemas.push(`contêiner não é MP4 (${p.format?.format_name})`);
  if (duracaoEsperada > 0 && Math.abs(dur - duracaoEsperada) > Math.max(2, duracaoEsperada * 0.01))
    problemas.push(`duração ${dur.toFixed(1)}s difere da esperada ${duracaoEsperada}s (download truncado?)`);
  if (decodificar) {
    const d = spawnSync("ffmpeg", ["-v", "error", "-i", arquivo, "-f", "null", "-"], { encoding: "utf8" });
    if (d.status !== 0 || d.stderr.trim()) problemas.push(`erros de decodificação: ${d.stderr.trim().split("\n").slice(0, 3).join(" | ")}`);
  }
  const res = {
    duracao: Number(dur.toFixed(2)),
    video: v[0] ? { codec: v[0].codec_name, largura: v[0].width, altura: v[0].height, fps: v[0].avg_frame_rate } : null,
    audio: a[0] ? { codec: a[0].codec_name } : null,
    tamanho_bytes: statSync(arquivo).size,
  };
  if (problemas.length) throw new Falha(SAIDA.INTEGRIDADE, `arquivo reprovado: ${problemas.join("; ")}`, JSON.stringify(res));
  return res;
}

// ---------- download com progresso ----------

async function gravar(origem, destino, total, rotulo) {
  let n = 0, ultimo = -1;
  const contador = async function* (fonte) {
    for await (const pedaco of fonte) {
      n += pedaco.length;
      const pct = total ? Math.floor((n / total) * 100) : -1;
      if (pct >= 0 && pct >= ultimo + 10) { ultimo = pct - (pct % 10); log(`  ${rotulo}: ${pct}% (${(n / 1e6).toFixed(1)} MB)`); }
      else if (pct < 0 && Math.floor(n / 25e6) > ultimo) { ultimo = Math.floor(n / 25e6); log(`  ${rotulo}: ${(n / 1e6).toFixed(0)} MB (tamanho total não informado)`); }
      yield pedaco;
    }
  };
  await pipeline(origem, contador, createWriteStream(destino));
  if (n === 0) throw new Falha(SAIDA.DOWNLOAD, `${rotulo}: download vazio (0 bytes)`);
  if (total && n < total) throw new Falha(SAIDA.DOWNLOAD, `${rotulo}: download incompleto (${n} de ${total} bytes)`);
  log(`  ${rotulo}: concluído, ${(n / 1e6).toFixed(1)} MB`);
  return n;
}

// ---------- motores ----------

const MOTORES = {
  async distube(id) {
    const { Ytdl } = await import("@distube/ytdl-core");
    const yt = new Ytdl();
    const info = await yt.getInfo(`https://www.youtube.com/watch?v=${id}`);
    return {
      titulo: info.videoDetails.title,
      duracao: Number(info.videoDetails.lengthSeconds || 0),
      formatos: info.formats.map((f) => ({ ...normalizar(f), _url: f.url, _cliente: f.client })),
      abrir: (f) => yt.download(info, { quality: f.itag }),
    };
  },
  async youtubei(id) {
    const { Innertube, Platform } = await import("youtubei.js");
    // Avaliador do código de assinatura do player, como no exemplo oficial do YouTube.js.
    Platform.shim.eval = async (data, env) => {
      const props = [];
      if (env.n) props.push(`n: exportedVars.nFunction(${JSON.stringify(env.n)})`);
      if (env.sig) props.push(`sig: exportedVars.sigFunction(${JSON.stringify(env.sig)})`);
      return new Function(`${data.output}\nreturn { ${props.join(", ")} }`)();
    };
    const yt = await Innertube.create({ retrieve_player: true });
    let ultimoErro;
    for (const client of ["ANDROID_VR", "MWEB", "TV"]) {
      try {
        const info = await yt.getBasicInfo(id, { client });
        const sd = info.streaming_data;
        if (!sd) throw new Error(`${client}: ${info.playability_status?.status} ${info.playability_status?.reason || ""}`);
        const brutos = [...(sd.formats || []), ...(sd.adaptive_formats || [])];
        return {
          titulo: info.basic_info.title,
          duracao: Number(info.basic_info.duration || 0),
          formatos: brutos.map((f) => ({ ...normalizar(f), _cliente: client, _bruto: f })),
          abrir: async (f) => Readable.fromWeb(await info.download({
            itag: f.itag, client, format: "any",
            type: f.video && f.audio ? "video+audio" : f.video ? "video" : "audio",
          })),
          urlDe: async (f) => f._bruto.decipher(yt.session.player),
        };
      } catch (e) { ultimoErro = e; log(`  youtubei: cliente ${client} falhou: ${e.message}`); }
    }
    throw ultimoErro;
  },
};

// ---------- diagnóstico de rede ----------

/**
 * O YouTube assina cada URL de mídia para o IP que pediu os metadados (parâmetro ip=).
 * Se o servidor de mídia enxerga outro IP, ele redireciona (mip=) e devolve 403.
 */
export async function diagnosticarIp(url) {
  const assinado = new URL(url).searchParams.get("ip");
  const r = await fetch(url, { method: "GET", redirect: "manual", headers: { Range: "bytes=0-1023" } });
  let visto = null, status = r.status;
  if (r.status >= 300 && r.status < 400 && r.headers.get("location")) {
    const loc = new URL(r.headers.get("location"));
    visto = loc.searchParams.get("mip");
    const r2 = await fetch(loc, { headers: { Range: "bytes=0-1023" } });
    status = r2.status;
    await r2.body?.cancel();
  } else await r.body?.cancel();
  return { ip_assinado: assinado, ip_visto_pelo_servidor_de_midia: visto, status_final: status,
    divergente: Boolean(visto && assinado && visto !== assinado) };
}

// ---------- fluxo principal ----------

// ---------- motor 3: site de conversão (loader.to) via Playwright ----------

let META = null; // título e duração obtidos por um motor anterior (servem para nomear e conferir o arquivo do site)
export const SITE = "https://en.loader.to/4/";

/**
 * Opções do seletor do loader.to a tentar, da melhor para a pior (no máximo 3).
 * Em vídeo VERTICAL o site rotula pelo lado errado: medido em 23/11/2026, "1080" entregou 480x854 e "1440" entregou
 * 720x1280. Por isso, em vertical, a opção pedida sobe um degrau ("4k" para buscar 1080x1920), e --h264 não corta o 4k.
 */
export function opcoesSite(maxAltura = Infinity, h264 = false, vertical = false) {
  if (vertical) {
    const lado = Math.min(maxAltura, 1920); // altura do vertical (1920 = 1080x1920)
    const mapa = [[1920, "4k"], [1280, "1440"], [854, "1080"], [640, "720"], [426, "480"]];
    return mapa.filter(([a]) => a <= lado).slice(0, 3).map(([, o]) => o);
  }
  const lim = h264 ? Math.min(maxAltura, 1080) : maxAltura;
  return [2160, 1440, 1080, 720, 480, 360].filter((a) => a <= lim).slice(0, 3).map((a) => (a === 2160 ? "4k" : String(a)));
}

/** Lado curto esperado para a opção pedida (horizontal: a própria altura; vertical: a largura). */
export function ladoCurtoEsperado(opcao, vertical = false) {
  if (vertical) return { "4k": 1080, "1440": 720, "1080": 480, "720": 360, "480": 240 }[opcao] ?? 0;
  return opcao === "4k" ? 2160 : Number(opcao);
}

function carregarPlaywright() {
  const req = createRequire(import.meta.url);
  for (const nome of ["playwright", "playwright-core"]) {
    try { return req(nome); } catch { /* tenta o próximo */ }
  }
  throw new Falha(SAIDA.DOWNLOAD, "motor site precisa do Playwright com Chromium (npm i -g playwright && npx playwright install chromium)");
}

/** Abre o site, cola o link, escolhe o formato e espera o link final do arquivo. */
async function linkDoSite(navegador, url, opcao, limiteMs) {
  const ctx = await navegador.newContext({ viewport: { width: 1280, height: 900 } });
  const p = await ctx.newPage();
  ctx.on("page", (aba) => { if (aba !== p) aba.close().catch(() => {}); }); // fecha abas de anúncio
  try {
    await p.goto(SITE, { waitUntil: "domcontentloaded", timeout: 60000 });
    const valores = await p.$$eval("#format option", (os) => os.map((o) => o.value));
    if (!valores.includes(opcao)) throw new Error(`o site não oferece mais a opção ${opcao} (layout mudou?)`);
    await p.fill("#link", url);
    await p.selectOption("#format", opcao);
    await p.click("#load");
    const inicio = Date.now();
    let ultimo = "";
    while (Date.now() - inicio < limiteMs) {
      await p.waitForTimeout(4000);
      const r = await p.evaluate(() => {
        const a = document.querySelector('a[id$="_downloadLink"]');
        const b = document.querySelector('button[id$="_downloadButton"]');
        const pr = document.querySelector('[id$="_progress"]') || document.querySelector('.progress');
        const erro = [...document.querySelectorAll('[id*="error"], .error, .alert')].find((e) => e.offsetParent && e.innerText.trim());
        return { href: a?.href || "", pronto: Boolean(b && !b.disabled), progresso: pr?.innerText.trim() || "", erro: erro?.innerText.trim() || "" };
      });
      if (r.erro) throw new Error(`o site informou erro: ${r.erro.slice(0, 150)}`);
      if (r.progresso && r.progresso !== ultimo) { ultimo = r.progresso; log(`  site: convertendo ${r.progresso}`); }
      if (r.pronto && r.href && !r.href.endsWith("#")) return r.href;
    }
    throw new Error(`o site não terminou a conversão em ${Math.round(limiteMs / 60000)} min`);
  } finally { await ctx.close().catch(() => {}); }
}

async function baixarViaSite(id, o) {
  const url = `https://www.youtube.com/watch?v=${id}`;
  const vertical = Boolean(META?.vertical || o.vertical);
  const opcoes = opcoesSite(o.maxAltura, o.h264, vertical);
  if (!opcoes.length) throw new Falha(SAIDA.ARGS, "--max-altura abaixo de 360 não é oferecido pelo site");
  log(`motor site: convertendo ${id} em ${SITE} (serviço de terceiros; sem login, sem cookies)`);
  if (o.info || o.diagnostico) throw new Falha(SAIDA.ARGS, "--info e --diagnostico não se aplicam ao motor site");
  const { chromium } = carregarPlaywright();
  const proxy = process.env.HTTPS_PROXY || process.env.https_proxy;
  const navegador = await chromium.launch(proxy ? { proxy: { server: proxy } } : {});
  let href, opcao, erroUltimo;
  try {
    for (opcao of opcoes) {
      try { log(`  site: pedindo MP4 ${opcao === "4k" ? "2160p" : opcao + "p"}`); href = await linkDoSite(navegador, url, opcao, (opcao === "4k" ? 20 : 12) * 60000); break; }
      catch (e) { erroUltimo = e; log(`  site: ${opcao} falhou: ${e.message}`); }
    }
  } finally { await navegador.close().catch(() => {}); }
  if (!href) throw new Falha(SAIDA.DOWNLOAD, `site não entregou o arquivo: ${erroUltimo?.message}`);

  mkdirSync(o.saida, { recursive: true });
  const final = path.join(o.saida, o.nome || nomeArquivo(META?.titulo || `youtube`, id));
  const tmp = path.join(o.saida, `.${id}.${process.pid}`);
  const pb = `${tmp}.site.mp4`, pm = `${tmp}.final.mp4`;
  try {
    const r = await fetch(href);
    if (!r.ok || !r.body) throw new Falha(SAIDA.DOWNLOAD, `servidor do site respondeu HTTP ${r.status}`);
    const tipo = r.headers.get("content-type") || "";
    if (/text\/html|json/.test(tipo)) throw new Falha(SAIDA.DOWNLOAD, `o site devolveu ${tipo} em vez de vídeo`);
    await gravar(Readable.fromWeb(r.body), pb, Number(r.headers.get("content-length")) || 0, `arquivo do site (${opcao})`);
    remuxar(pb, pm); // MP4 com faststart; sem recodificar
    const ver = verificar(pm, META?.duracao || 0, { decodificar: o.decodificar });
    const curto = Math.min(ver.video.largura, ver.video.altura), esperado = ladoCurtoEsperado(opcao, vertical);
    if (esperado && curto < esperado * 0.95)
      log(`  AVISO: o site entregou ${ver.video.largura}x${ver.video.altura}, abaixo do pedido (${opcao}, lado curto ${esperado}). ` +
        (vertical ? "Em vertical o site rotula errado; tente --max-altura 1920." : "O vídeo pode não ter essa resolução."));
    if (ver.video.codec !== "h264" && o.h264) log(`  AVISO: --h264 pedido, mas o site entregou ${ver.video.codec}`);
    renameSync(pm, final);
    log(`  verificado: ${ver.video.largura}x${ver.video.altura} ${ver.video.codec} + ${ver.audio.codec}, ${ver.duracao}s, ${(ver.tamanho_bytes / 1e6).toFixed(1)} MB` +
      (META?.duracao ? "" : " (duração não conferida: nenhum motor anterior obteve os metadados)"));
    return { ok: true, motor: "site", servico: SITE, id, titulo: META?.titulo || null, arquivo: path.resolve(final), ...ver };
  } finally {
    for (const p of [pb, pm]) if (existsSync(p)) rmSync(p, { force: true });
  }
}

function lerArgs(argv) {
  const o = { saida: ".", maxAltura: Infinity, h264: false, motor: null, info: false, diagnostico: false, json: false, decodificar: false };
  const pos = [];
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--saida") o.saida = argv[++i];
    else if (a === "--nome") o.nome = argv[++i];
    else if (a === "--max-altura") o.maxAltura = Number(argv[++i]);
    else if (a === "--h264") o.h264 = true;
    else if (a === "--vertical") o.vertical = true;
    else if (a === "--motor") o.motor = argv[++i];
    else if (a === "--info") o.info = true;
    else if (a === "--diagnostico") o.diagnostico = true;
    else if (a === "--json") o.json = true;
    else if (a === "--verificar-decodificacao") o.decodificar = true;
    else if (a === "-h" || a === "--help") o.ajuda = true;
    else if (a.startsWith("--")) throw new Falha(SAIDA.ARGS, `opção desconhecida: ${a}`);
    else pos.push(a);
  }
  o.entrada = pos[0];
  if (o.motor && !MOTORES[o.motor] && o.motor !== "site") throw new Falha(SAIDA.ARGS, `motor inválido: ${o.motor} (use distube, youtubei ou site)`);
  if (!Number.isFinite(o.maxAltura) && o.maxAltura !== Infinity) throw new Falha(SAIDA.ARGS, "--max-altura precisa ser um número");
  return o;
}

async function baixarCom(nomeMotor, id, o) {
  log(`motor ${nomeMotor}: extraindo formatos de ${id} (sem login, sem cookies)`);
  const fonte = await MOTORES[nomeMotor](id);
  const maior = fonte.formatos.filter((f) => f.video).sort((a, b) => b.altura - a.altura)[0];
  META = { titulo: fonte.titulo, duracao: fonte.duracao, vertical: Boolean(maior && maior.largura && maior.largura < maior.altura) };
  const alturas = [...new Set(fonte.formatos.filter((f) => f.video).map((f) => f.altura))].sort((a, b) => b - a);
  log(`  título: ${fonte.titulo} · duração ${fonte.duracao}s · ${fonte.formatos.length} formatos · alturas ${alturas.join("/")}`);
  const escolha = escolherFormatos(fonte.formatos, { maxAltura: o.maxAltura, h264: o.h264 });
  if (!escolha) throw new Falha(SAIDA.EXTRACAO, "nenhum formato MP4 utilizável retornado");
  log(`  escolhido: vídeo itag ${escolha.video.itag} ${escolha.video.altura}p${escolha.video.fps || ""} ${escolha.video.codec}` +
    (escolha.audio ? ` + áudio itag ${escolha.audio.itag} ${escolha.audio.codec}` : " (progressivo)"));

  if (o.info) return { motor: nomeMotor, id, titulo: fonte.titulo, duracao: fonte.duracao, escolha, formatos: fonte.formatos.map(({ _url, _bruto, ...f }) => f) };

  if (o.diagnostico) {
    const f = escolha.audio || escolha.video;
    const url = f._url || (fonte.urlDe ? await fonte.urlDe(f) : null);
    if (!url) throw new Falha(SAIDA.EXTRACAO, "formato só por SABR, sem URL direta para diagnosticar");
    const d = await diagnosticarIp(url);
    log(`  diagnóstico: IP assinado ${d.ip_assinado} · IP visto pelo servidor de mídia ${d.ip_visto_pelo_servidor_de_midia ?? "(mesmo, sem redirecionamento)"} · HTTP ${d.status_final}`);
    if (d.divergente) log("  → REDE INCOMPATÍVEL: metadados e mídia saem por IPs diferentes; nenhuma ferramenta baixa daqui. Use outra rede (ex.: a sua máquina, sem VPN).");
    else if (d.status_final >= 200 && d.status_final < 300) log("  → rede OK: o servidor de mídia aceitou a URL.");
    return { motor: nomeMotor, id, diagnostico: d };
  }

  mkdirSync(o.saida, { recursive: true });
  const final = path.join(o.saida, o.nome || nomeArquivo(fonte.titulo, id));
  const tmp = path.join(o.saida, `.${id}.${process.pid}`);
  const pv = `${tmp}.video.mp4`, pa = `${tmp}.audio.m4a`, pm = `${tmp}.final.mp4`;
  try {
    await gravar(await fonte.abrir(escolha.video), pv, escolha.video.tamanho, `vídeo ${escolha.video.altura}p`);
    if (escolha.audio) {
      await gravar(await fonte.abrir(escolha.audio), pa, escolha.audio.tamanho, "áudio");
      log("  juntando vídeo e áudio (ffmpeg, sem recodificar)");
      juntar(pv, pa, pm);
    } else remuxar(pv, pm);
    const ver = verificar(pm, fonte.duracao, { decodificar: o.decodificar });
    renameSync(pm, final);
    log(`  verificado: ${ver.video.largura}x${ver.video.altura} ${ver.video.codec} + ${ver.audio.codec}, ${ver.duracao}s, ${(ver.tamanho_bytes / 1e6).toFixed(1)} MB`);
    return { ok: true, motor: nomeMotor, id, titulo: fonte.titulo, arquivo: path.resolve(final), ...ver };
  } finally {
    for (const p of [pv, pa, pm]) if (existsSync(p)) rmSync(p, { force: true });
  }
}

async function principal() {
  const o = lerArgs(process.argv.slice(2));
  if (o.ajuda || !o.entrada) {
    process.stdout.write("Uso: node tools/youtube/baixar.mjs <url-ou-id> [--saida pasta] [--nome x.mp4] [--max-altura 1080] [--h264]\n" +
      "       [--motor distube|youtubei|site] [--verificar-decodificacao] [--info] [--diagnostico] [--json]\n");
    return o.ajuda ? SAIDA.OK : SAIDA.ARGS;
  }
  const id = extrairId(o.entrada);
  if (!id) throw new Falha(SAIDA.ARGS, `não reconheci um vídeo do YouTube em: ${o.entrada}`);
  if (!o.info && !o.diagnostico && !temFfmpeg()) throw new Falha(SAIDA.FFMPEG, "ffmpeg/ffprobe não encontrados no PATH (instale: apt install ffmpeg)");
  if (!o.info && !o.diagnostico) { mkdirSync(o.saida, { recursive: true }); ARQ_LOG = path.join(o.saida, "baixar-youtube.log"); }

  // --info e --diagnostico só fazem sentido nos motores que falam com o YouTube direto
  const ordem = o.motor ? [o.motor] : (o.info || o.diagnostico) ? ["distube", "youtubei"] : ["distube", "youtubei", "site"];
  const erros = [];
  for (const m of ordem) {
    try {
      const r = m === "site" ? await baixarViaSite(id, o) : await baixarCom(m, id, o);
      if (o.json || o.info) process.stdout.write(JSON.stringify(r, null, 2) + "\n");
      else if (r.arquivo) process.stdout.write(r.arquivo + "\n");
      return SAIDA.OK;
    } catch (e) {
      const dica = explicarErro(`${e.message} ${e.cause?.message || ""}`);
      log(`motor ${m} falhou: ${e.message}${e.cause?.message ? ` (${e.cause.message})` : ""}`);
      if (dica) log(`  explicação: ${dica}`);
      erros.push({ motor: m, erro: e.message, codigo: e.codigo ?? (/\b403\b|non 2xx|download/i.test(`${e.message} ${e.cause?.message}`) ? SAIDA.DOWNLOAD : SAIDA.EXTRACAO), dica });
      if (e.codigo === SAIDA.FFMPEG || e.codigo === SAIDA.ARGS) break;
    }
  }
  if (o.json) process.stdout.write(JSON.stringify({ ok: false, id, erros }, null, 2) + "\n");
  log("FALHOU: nenhum motor conseguiu. Veja as explicações acima; para checar a rede rode com --diagnostico.");
  return erros.at(-1)?.codigo ?? SAIDA.DOWNLOAD;
}

if (import.meta.url === `file://${process.argv[1]}` || fileURLToPath(import.meta.url) === path.resolve(process.argv[1] || "")) {
  principal().then((c) => process.exit(c), (e) => {
    log(`erro: ${e.message}`);
    if (e.detalhe) log(`  detalhe: ${String(e.detalhe).slice(0, 500)}`);
    process.exit(e.codigo ?? 1);
  });
}
