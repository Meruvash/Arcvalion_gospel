// Gera as imagens de prévia (og:image, 1200×630) do arquivo de notícias e do calendário de lançamentos,
// no mesmo molde de tools/capa_resenhas.js: mosaico de capas à direita, nome da seção à esquerda.
// Uso: node tools/capa_secoes.js   -> noticias/capa.jpg e lancamentos/capa.jpg
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const b64 = f => fs.readFileSync(f).toString('base64');
const fonte = b64(path.join(ROOT, 'fontes', 'public-sans.woff2'));

// notícias: imagens das notas mais recentes que têm foto
const notas = fs.readdirSync(path.join(ROOT, 'conteudo', 'noticias')).filter(f => f.endsWith('.json'))
  .map(f => JSON.parse(fs.readFileSync(path.join(ROOT, 'conteudo', 'noticias', f), 'utf8')))
  .filter(n => n.imagem).sort((a, b) => (b.publicado_em || '').localeCompare(a.publicado_em || ''));
const fotosNotas = notas.map(n => path.join(ROOT, 'noticias', n.imagem.arquivo)).filter(fs.existsSync).slice(0, 8);

// lançamentos: capas do mês corrente (ou do último mês salvo) no calendário da Ludopedia
const meses = fs.readdirSync(path.join(ROOT, 'conteudo', 'lancamentos')).filter(f => f.endsWith('.json')).sort();
const hoje = new Date().toISOString().slice(0, 7);
const mes = meses.includes(`${hoje}.json`) ? `${hoje}.json` : meses[meses.length - 1];
const cal = JSON.parse(fs.readFileSync(path.join(ROOT, 'conteudo', 'lancamentos', mes), 'utf8'));
const capasCal = [...cal.previstos, ...cal.lancados].filter(j => j.fl_tipo === 1)
  .map(j => path.join(ROOT, 'lancamentos', 'capas', `${j.id_jogo}.webp`)).filter(fs.existsSync).slice(0, 8);
const ano = mes.slice(0, 4);

const pagina = (titulo, texto, selo, imgs, tipo) => `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:PS;src:url(data:font/woff2;base64,${fonte}) format("woff2");font-weight:400 800}
*{box-sizing:border-box;margin:0}
body{width:1200px;height:630px;overflow:hidden;background:radial-gradient(circle at 80% 30%,#1d2540 0,#0a0c11 65%);color:#e9ecf2;font-family:PS,sans-serif;position:relative}
.txt{position:absolute;left:64px;top:0;bottom:0;width:500px;display:flex;flex-direction:column;justify-content:center}
.brand{font-weight:800;color:#f2c14e;letter-spacing:.12em;font-size:28px}
h1{font-weight:800;font-size:96px;line-height:.95;letter-spacing:-.02em;margin:14px 0 18px}
p{font-size:25px;line-height:1.35;color:#cdd3de}
.n{margin-top:26px;align-self:flex-start;font-weight:800;font-size:22px;letter-spacing:.04em;text-transform:uppercase;background:#f2c14e;color:#1b1503;border-radius:8px;padding:6px 16px}
.grid{position:absolute;right:-30px;top:50%;width:640px;display:grid;grid-template-columns:repeat(4,1fr);gap:16px;transform:translateY(-50%) rotate(-6deg)}
.grid img{width:100%;aspect-ratio:${tipo === 'foto' ? '4/3' : '1'};object-fit:cover;border-radius:14px;border:2px solid rgba(242,193,78,.55);box-shadow:0 12px 30px rgba(0,0,0,.6);background:#fff}
.fade{position:absolute;inset:0;background:linear-gradient(90deg,#0a0c11 38%,rgba(10,12,17,0) 56%)}
</style></head><body>
<div class="grid">${imgs.map(f => `<img src="data:image/${f.endsWith('.webp') ? 'webp' : 'jpeg'};base64,${b64(f)}">`).join('')}</div>
<div class="fade"></div>
<div class="txt"><div class="brand">✝ PORTAL CRISTÃO</div><h1 style="font-size:${titulo.length > 10 ? 72 : 96}px">${titulo}</h1><p>${texto}</p><div class="n">${selo}</div></div>
</body></html>`;

(async () => {
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: 1200, height: 630 } });
  for (const [saida, html] of [
    ['noticias/capa.jpg', pagina('Notícias', 'Jogos de tabuleiro com fonte, data e opinião separada do fato.', 'Todos os dias', fotosNotas, 'foto')],
    ['lancamentos/capa.jpg', pagina(`Lançamentos ${ano}`, 'O calendário das editoras brasileiras, mês a mês.', 'Jogos, expansões e RPGs', capasCal, 'capa')],
  ]) {
    await pg.setContent(html, { waitUntil: 'load' });
    await pg.evaluate(() => document.fonts.ready);
    await pg.screenshot({ path: path.join(ROOT, saida), type: 'jpeg', quality: 85 });
    console.log('ok', saida);
  }
  await b.close();
})();
