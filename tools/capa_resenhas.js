// Gera estudos/capa.jpg (1200×630, imagem de prévia do WhatsApp) com o mosaico das capas publicadas.
// Uso: node tools/capa_resenhas.js   (rode de novo a cada resenha publicada)
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const pauta = JSON.parse(fs.readFileSync(path.join(ROOT, 'pauta.json'), 'utf8'));
const slugs = pauta.publicadas.map(p => p.url.replace(/\/$/, '').split('/').pop()).reverse();
const capas = slugs.map(s => path.join(ROOT, s, 'capa.jpg')).filter(fs.existsSync).slice(0, 8);
const n = pauta.publicadas.length;
const cols = capas.length > 4 ? Math.ceil(capas.length / 2) : capas.length;

const html = `<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;700&family=Inter:wght@500;600&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0}
body{width:1200px;height:630px;overflow:hidden;background:radial-gradient(circle at 80% 30%,#1d2540 0,#0a0c11 65%);color:#e9ecf2;font-family:Inter,sans-serif;position:relative}
.txt{position:absolute;left:64px;top:0;bottom:0;width:470px;display:flex;flex-direction:column;justify-content:center}
.brand{font-family:Oswald;font-weight:700;color:#f2c14e;letter-spacing:.12em;font-size:30px}
h1{font-family:Oswald;font-weight:700;font-size:118px;line-height:.95;text-transform:uppercase;margin:14px 0 18px;text-shadow:0 0 30px rgba(242,193,78,.25)}
p{font-size:25px;line-height:1.35;color:#cdd3de}
.n{margin-top:26px;display:inline-block;align-self:flex-start;font-family:Oswald;font-size:24px;letter-spacing:.06em;text-transform:uppercase;background:#f2c14e;color:#1b1503;border-radius:8px;padding:6px 16px}
.grid{position:absolute;right:-30px;top:50%;width:640px;display:grid;grid-template-columns:repeat(${cols},1fr);gap:16px;transform:translateY(-50%) rotate(-6deg)}
.grid img{width:100%;aspect-ratio:1;object-fit:cover;border-radius:14px;border:2px solid rgba(242,193,78,.55);box-shadow:0 12px 30px rgba(0,0,0,.6)}
.fade{position:absolute;inset:0;background:linear-gradient(90deg,#0a0c11 36%,rgba(10,12,17,.0) 52%);pointer-events:none}
</style></head><body>
<div class="grid">${capas.map(c => `<img src="data:image/jpeg;base64,${fs.readFileSync(c).toString('base64')}">`).join('')}</div>
<div class="fade"></div>
<div class="txt">
 <div class="brand">✝ O PALADINO</div>
 <h1>Resenhas</h1>
 <p>Só jogos premiados. O que funciona, pontos de atenção e para quem é.</p>
 <div class="n">${n} resenhas publicadas</div>
</div></body></html>`;

(async () => {
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: 1200, height: 630 } });
  await pg.setContent(html, { waitUntil: 'networkidle' });
  await pg.evaluate(() => document.fonts.ready);
  await pg.screenshot({ path: path.join(ROOT, 'resenhas', 'capa.jpg'), type: 'jpeg', quality: 85 });
  await b.close();
  console.log('ok estudos/capa.jpg', capas.length, 'capas');
})();
