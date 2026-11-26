const { chromium } = require('playwright'); const path = require('path');
(async () => { const b = await chromium.launch();
  for (const [f, h, o] of [['v.html', 1920, 'capa-9x16.png'], ['f.html', 1350, 'capa-4x5.png']]) { const p = await b.newPage({ viewport: { width: 1080, height: h } });
    await p.goto('file://' + path.resolve(f)); await p.evaluate(() => document.fonts.ready); await p.screenshot({ path: o }); }
  await b.close(); })();
