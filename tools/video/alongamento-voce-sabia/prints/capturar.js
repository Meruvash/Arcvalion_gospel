// Print da página INTEIRA das fontes oficiais (BCB e STJ) e posição, em pixels do print, de cada trecho a realçar.
// Uso (da pasta do vídeo): node prints/capturar.js
const { chromium } = require('playwright');
const fs = require('fs');
const ALVOS = [
  ['bcb-res-5314', 'https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Resolu%C3%A7%C3%A3o%20CMN&numero=5314',
    ['por sua conveniência e decisão', 'RESOLUÇÃO CMN Nº 5.314, DE 25 DE JUNHO DE 2026', 'Esta Resolução entra em vigor em 1º de julho de 2026']],
  ['stj-sumula-298', 'https://scon.stj.jus.br/SCON/sumstj/toc.jsp?livre=%27298%27.num.&O=JT',
    ['direito do devedor', 'O alongamento de dívida originada de crédito rural', 'DJ 22/11/2004']],
];
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 900, height: 1400 }, deviceScaleFactor: 2 });
  const saida = {};
  for (const [nome, url, trechos] of ALVOS) {
    await p.goto(url, { waitUntil: 'networkidle', timeout: 90000 });
    await p.waitForTimeout(3000);
    for (const t of ['Rejeitar cookies', 'Rejeitar']) {
      const btn = p.getByRole('button', { name: t });
      if (await btn.count()) { await btn.first().click().catch(() => {}); await p.waitForTimeout(800); break; }
    }
    await p.addStyleTag({ content: '[vw], .vw-plugin-wrapper, [vw-access-button] { display: none !important; }' });
    const rects = {};
    for (const t of trechos) {
      rects[t] = await p.evaluate((t) => {
        const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let n;
        while ((n = w.nextNode())) {
          const orig = n.textContent; const i = orig.replace(/\s+/g, ' ').indexOf(t); if (i < 0) continue;
          let a = 0, k = 0; while (k < i) { if (/\s/.test(orig[a])) { while (/\s/.test(orig[a + 1] || '')) a++; } a++; k++; }
          let e = a; k = 0; while (k < t.length) { if (/\s/.test(orig[e])) { while (/\s/.test(orig[e + 1] || '')) e++; } e++; k++; }
          const r = document.createRange(); r.setStart(n, a); r.setEnd(n, e);
          return [...r.getClientRects()].map((q) => [(q.left + scrollX) * 2, (q.top + scrollY) * 2, (q.right + scrollX) * 2, (q.bottom + scrollY) * 2]);
        }
        return null;
      }, t);
    }
    await p.screenshot({ path: `prints/${nome}.png`, fullPage: true });
    saida[nome] = { url, capturado_em: new Date().toISOString(), trechos: rects };
    console.log(nome, JSON.stringify(rects));
  }
  fs.writeFileSync('prints/trechos.json', JSON.stringify(saida, null, 1));
  await b.close();
})();
