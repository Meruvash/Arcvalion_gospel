// Print final: andamento da MPV 1.376/2026 (Congresso Nacional), com retângulos do trecho da data final.
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1000, height: 1100 }, deviceScaleFactor: 2 });
  await p.goto('https://www.congressonacional.leg.br/materias/medidas-provisorias/-/mpv/175190', { waitUntil: 'networkidle', timeout: 90000 });
  await p.waitForTimeout(2500);
  for (const t of ['Prazos', 'Tramitação']) {
    const h = p.getByText(t, { exact: true });
    for (let i = 0; i < await h.count(); i++) if (await h.nth(i).isVisible()) { await h.nth(i).click().catch(() => {}); await p.waitForTimeout(1500); }
  }
  const alvo = p.getByText('Data final após prorrogação: 11/11/2026', { exact: false }).nth(1);
  await alvo.scrollIntoViewIfNeeded(); await p.evaluate(() => window.scrollBy(0, 120)); await p.waitForTimeout(800);
  const rects = await alvo.evaluate((el) => {
    const out = {}; const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT); let n;
    while ((n = w.nextNode())) for (const a of ['Data final após prorrogação: 11/11/2026', '08/09/2026']) {
      const i = n.textContent.indexOf(a); if (i < 0) continue;
      const r = document.createRange(); r.setStart(n, i); r.setEnd(n, i + a.length);
      out[a] = [...r.getClientRects()].map(x => ({ x: x.x, y: x.y, w: x.width, h: x.height }));
    }
    return out;
  });
  await p.screenshot({ path: 'prints/cn-andamento.png' });
  require('fs').writeFileSync('prints/cn-andamento.json', JSON.stringify({ url: p.url(), capturado: new Date().toISOString(), escala: 2, rects }, null, 1));
  console.log(JSON.stringify(rects));
  await b.close();
})();
