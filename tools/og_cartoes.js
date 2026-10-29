// Fotografa os cartões de prévia (og:image, 1200×630) montados por tools/og.py.
// Uso: node tools/og_cartoes.js <tarefas.json>   — cada tarefa: {"html": "/caminho/cartao.html", "saida": "/caminho/img.jpg"}
const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  const tarefas = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1200, height: 630 } });
  for (const t of tarefas) {
    await p.goto('file://' + t.html, { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    await p.screenshot({ path: t.saida, type: 'jpeg', quality: 82 });
  }
  await b.close();
  console.log('ok', tarefas.length, 'cartões');
})();
