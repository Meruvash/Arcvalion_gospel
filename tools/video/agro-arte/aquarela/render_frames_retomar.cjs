// Retoma o render quadro a quadro de onde parou: node resume.cjs pagina.html duracao pasta fps
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
(async () => {
  const [page, dur, out, fpsArg] = process.argv.slice(2); const fps = +(fpsArg || 30), n = Math.round(dur * fps);
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1080 } });
  await p.goto('file://' + path.resolve(page)); await p.evaluate(() => window.READY);
  let feitos = 0;
  for (let i = 0; i < n; i++) { const f = path.join(out, `f${String(i).padStart(5, '0')}.png`); if (fs.existsSync(f) && fs.statSync(f).size > 0) continue;
    await p.evaluate((t) => window.drawFrame(t), i / fps); await p.screenshot({ path: f }); feitos++; }
  console.log('quadros novos:', feitos); await b.close();
})();
