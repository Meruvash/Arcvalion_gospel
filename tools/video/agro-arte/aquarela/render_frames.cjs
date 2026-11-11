// Renderiza uma página p5.brush quadro a quadro: node render_frames.cjs pagina.html duracao_s pasta_saida [fps] [--stills a,b,c]
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
(async () => {
  const [page, dur, out, fpsArg] = process.argv.slice(2); const fps = +(fpsArg || 30);
  const si = process.argv.indexOf('--stills'); const stills = si > 0 ? process.argv[si + 1].split(',').map(Number) : null;
  fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1080 } });
  const errs = []; p.on('pageerror', e => errs.push(String(e)));
  const [pf, hs] = page.split('#'); await p.goto('file://' + path.resolve(pf) + (hs ? '#' + hs : '')); await p.evaluate(() => window.READY);
  const times = stills || Array.from({ length: Math.round(dur * fps) }, (_, i) => i / fps);
  const t0 = Date.now();
  for (let i = 0; i < times.length; i++) {
    await p.evaluate((t) => window.drawFrame(t), times[i]);
    await p.screenshot({ path: path.join(out, stills ? `t${times[i].toFixed(2)}.png` : `f${String(i).padStart(5, '0')}.png`) });
  }
  console.log(`${times.length} quadros em ${((Date.now() - t0) / 1000).toFixed(1)} s`, errs.length ? errs.slice(0, 3) : '');
  await b.close();
})();
