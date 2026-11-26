// Renderiza a cena 3D: quadros PNG em out/ a 30 fps. Uso: node shot.cjs [segundos] [fps]
const { chromium } = require('playwright'); const path = require('path'); const fs = require('fs');
(async () => {
  const dur = +(process.argv[2] || 0), fps = +(process.argv[3] || 30);
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1080 } });
  p.on('pageerror', e => console.log('ERR', e.message)); p.on('console', m => { if (m.type() === 'error') console.log('CONSOLE', m.text()); });
  await p.goto('file://' + path.resolve(__dirname, 'fazenda3d.html')); await p.waitForFunction(() => window.ready, null, { timeout: 120000 });
  fs.mkdirSync(path.join(__dirname, 'out'), { recursive: true });
  const n = dur ? Math.round(dur * fps) : 1;
  for (let i = 0; i < n; i++) { const t = dur ? i / fps : 2; await p.evaluate(t => window.renderAt(t), t);
    await p.locator('canvas').screenshot({ path: path.join(__dirname, 'out', `f_${String(i).padStart(4, '0')}.png`) });
    if (i % 30 === 0) console.log('quadro', i, '/', n); }
  await b.close();
})();
