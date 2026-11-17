#!/usr/bin/env node
// Baixa um vídeo PÚBLICO do TikTok na maior resolução que a própria página oferece (até 1080x1920), sem login e sem cookies.
// Abre a página num Chromium de verdade (Playwright), lê os endereços em __UNIVERSAL_DATA_FOR_REHYDRATION__ e baixa no mesmo
// contexto. Só diz "VERIFICADO" depois do ffprobe (vídeo + duração). Grava autor, endereço, data e números ao lado (.json)
// para o crédito na tela. Uso: node baixar_tiktok.cjs <url> [pasta]   Saída: 0 verificado · 1 falha (motivo impresso)
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path'); const { spawnSync } = require('child_process');
(async () => {
  const [url, pasta = '.'] = process.argv.slice(2);
  if (!url) { console.error('uso: node baixar_tiktok.cjs <url do TikTok> [pasta]'); process.exit(1); }
  fs.mkdirSync(pasta, { recursive: true });
  const b = await chromium.launch(); const ctx = await b.newContext(); const p = await ctx.newPage();
  try {
    const r = await p.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
    if (!r || r.status() >= 400) throw new Error(`página respondeu ${r ? r.status() : 'sem resposta'}`);
    await p.waitForTimeout(4000);
    const it = await p.evaluate(() => { const el = document.getElementById('__UNIVERSAL_DATA_FOR_REHYDRATION__'); if (!el) return null;
      const j = JSON.parse(el.textContent); return j.__DEFAULT_SCOPE__?.['webapp.video-detail']?.itemInfo?.itemStruct || { erro: j.__DEFAULT_SCOPE__?.['webapp.video-detail']?.statusMsg || 'sem dados do vídeo' }; });
    if (!it || it.erro) throw new Error('a página não trouxe os dados do vídeo (' + (it?.erro || 'bloqueio, vídeo privado ou removido') + ')');
    const cands = (it.video.bitrateInfo || []).map(x => ({ gear: x.GearName, codec: x.CodecType, w: x.PlayAddr?.Width || 0, h: x.PlayAddr?.Height || 0, u: x.PlayAddr?.UrlList?.[0] }))
      .filter(x => x.u).sort((a, c) => (c.w * c.h) - (a.w * a.h) || (a.codec === 'h264' ? -1 : 1));
    if (it.video.playAddr) cands.push({ gear: 'playAddr', codec: '?', w: it.video.width, h: it.video.height, u: it.video.playAddr });
    const nome = `${it.author.uniqueId}_${it.id}`; const destino = path.join(pasta, nome + '.mp4'); let ok = null;
    for (const c of cands) {
      const resp = await ctx.request.get(c.u, { headers: { referer: 'https://www.tiktok.com/' } });
      const buf = await resp.body();
      if (resp.status() !== 200 || buf.length < 100000) { console.error(`[tentativa] ${c.gear} ${c.w}x${c.h}: ${resp.status()} ${buf.length} bytes`); continue; }
      fs.writeFileSync(destino, buf); ok = c; break;
    }
    if (!ok) throw new Error('nenhuma versão do vídeo foi entregue (todas recusadas)');
    const pr = spawnSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration:stream=codec_type,codec_name,width,height', '-of', 'json', destino], { encoding: 'utf8' });
    const j = JSON.parse(pr.stdout || '{}'); const v = (j.streams || []).find(s => s.codec_type === 'video'); const dur = parseFloat(j.format?.duration || 0);
    if (!v || !(dur > 0)) throw new Error('arquivo baixado não passou no ffprobe');
    const meta = { url, autor: '@' + it.author.uniqueId, nome_autor: it.author.nickname, publicado: new Date(it.createTime * 1000).toISOString().slice(0, 10), descricao: it.desc,
      numeros_em: new Date().toISOString().slice(0, 10), visualizacoes: it.stats?.playCount, curtidas: it.stats?.diggCount, compartilhamentos: it.stats?.shareCount,
      arquivo: destino, versao: ok.gear, video: `${v.codec_name} ${v.width}x${v.height}`, duracao_s: dur };
    fs.writeFileSync(path.join(pasta, nome + '.json'), JSON.stringify(meta, null, 1));
    console.log(`VERIFICADO: ${destino} · ${meta.video} · ${dur.toFixed(1)} s · ${meta.autor} (${meta.publicado})`);
    await b.close(); process.exit(0);
  } catch (e) { console.log('NÃO BAIXADO: ' + e.message); await b.close(); process.exit(1); }
})();
