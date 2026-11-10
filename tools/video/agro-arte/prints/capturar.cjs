// Captura a página oficial da Res. CMN 5.330 no BCB e mede a posição dos trechos a realçar.
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1000, height: 1400 }, deviceScaleFactor: 2 });
  await p.goto('https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Resolu%C3%A7%C3%A3o%20CMN&numero=5330', { waitUntil: 'networkidle', timeout: 90000 });
  await p.waitForTimeout(3000);
  // esconde cabeçalho/rodapé do portal para ficar só o documento
  await p.addStyleTag({ content: 'header, footer, .navbar, #barra-brasil, .cookie, [class*=cookie], [class*=lgpd] {display:none!important}' });
  const alvos = ['RESOLUÇÃO CMN Nº 5.330, DE 23 DE JULHO DE 2026', 'perdas em duas ou mais safras', 'no mínimo, 30% (trinta por cento)', 'prazo para contratação: até 12 de novembro de 2026', 'até oito anos', 'secas ou estiagens', 'inundações', 'chuvas de granizo', 'geadas', 'vendaval', 'redução dos preços', 'laudo emitido por profissional habilitado', '6% a.a. (seis por cento ao ano)', '9% a.a. (nove por cento ao ano)', '12% a.a. (doze por cento ao ano)'];
  const rects = await p.evaluate((alvos) => {
    const out = {};
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    const nodes = []; let n; while ((n = walker.nextNode())) nodes.push(n);
    for (const a of alvos) {
      for (const node of nodes) {
        const norm = node.textContent.replace(/\s+/g, ' ').replace(/​/g, '');
        const i = norm.indexOf(a); if (i < 0) continue;
        // mapeia índice normalizado -> índice real (aproximação: texto sem quebras múltiplas)
        const raw = node.textContent; let ri = raw.replace(/​/g,'').indexOf(a);
        if (ri < 0) ri = i;
        const r = document.createRange(); r.setStart(node, Math.min(ri, raw.length)); r.setEnd(node, Math.min(ri + a.length, raw.length));
        const rs = [...r.getClientRects()].map(x => ({ x: x.x + scrollX, y: x.y + scrollY, w: x.width, h: x.height }));
        out[a] = rs; break;
      }
    }
    return out;
  }, alvos);
  await p.screenshot({ path: 'prints/res5330-full.png', fullPage: true });
  require('fs').writeFileSync('prints/trechos.json', JSON.stringify({ url: p.url(), capturado: new Date().toISOString(), escala: 2, rects }, null, 1));
  console.log(JSON.stringify(rects, null, 0).slice(0, 1500));
  await b.close();
})();
