// Auditoria de UX (laboratório): Lighthouse mobile, axe-core e screenshots das páginas-chave.
//
// Uso (as dependências ficam numa pasta temporária, fora do repositório):
//   mkdir -p /tmp/aud && (cd /tmp/aud && npm i lighthouse@12 @axe-core/playwright@4)
//   python3 -m http.server 8080 &            # na raiz do repositório
//   NODE_PATH=/tmp/aud/node_modules node tools/ux/auditar.mjs docs/ux-baseline
//
// Saída: <pasta>/lighthouse.json, <pasta>/axe.json, <pasta>/resumo.md e <pasta>/screens/*.jpg.
// Tudo é dado de LABORATÓRIO (servidor local, CPU e rede simuladas pelo Lighthouse), não dado de campo (CrUX).
import { createRequire } from "node:module";
import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const { default: AxeBuilder } = require("@axe-core/playwright");
const lighthouse = require("lighthouse").default ?? require("lighthouse");

const BASE = process.env.BASE || "http://localhost:8080";
const SAIDA = process.argv[2] || "docs/ux-baseline";
const PAGINAS = (process.env.PAGINAS || "/,/noticias/,/estudos/,/root/,/consulta/,/lancamentos/,/noticias/vantage-chega-ao-brasil/").split(",");
const LARGURAS = (process.env.LARGURAS || "320,375,768,1440").split(",").map(Number);
const CHROME = process.env.CHROME || "/opt/pw-browsers/chromium-1243/chrome-linux64/chrome";
// o medidor da Cloudflare não roda no servidor local; bloqueado para não poluir a medição
const BLOQUEAR = ["*cloudflareinsights.com*"];

const nome = p => (p.replace(/^\/|\/$/g, "").replace(/\//g, "_") || "home");
mkdirSync(join(SAIDA, "screens"), { recursive: true });

const browser = await chromium.launch({ executablePath: CHROME, args: ["--remote-debugging-port=9333"] });
const lh = {}, axe = {};

for (const p of PAGINAS) {
  const url = BASE + p;
  // Lighthouse (perfil mobile padrão: Moto G Power, 4G lento simulado)
  const r = await lighthouse(url, { port: 9333, output: "json", logLevel: "error", blockedUrlPatterns: BLOQUEAR,
    onlyCategories: ["performance", "accessibility", "best-practices", "seo"] });
  const a = r.lhr.audits, c = r.lhr.categories;
  lh[p] = {
    performance: Math.round(c.performance.score * 100), acessibilidade: Math.round(c.accessibility.score * 100),
    boas_praticas: Math.round(c["best-practices"].score * 100), seo: Math.round(c.seo.score * 100),
    fcp_ms: Math.round(a["first-contentful-paint"].numericValue), lcp_ms: Math.round(a["largest-contentful-paint"].numericValue),
    tbt_ms: Math.round(a["total-blocking-time"].numericValue), cls: +a["cumulative-layout-shift"].numericValue.toFixed(3),
    si_ms: Math.round(a["speed-index"].numericValue), peso_kb: Math.round(a["total-byte-weight"].numericValue / 1024),
    dom: a["dom-size"]?.numericValue ?? null,
    falhas_a11y: Object.values(a).filter(x => x.score === 0 && r.lhr.categories.accessibility.auditRefs.some(ref => ref.id === x.id)).map(x => x.id),
  };
  // axe-core (WCAG 2.0/2.1/2.2 A e AA) e screenshots
  for (const w of LARGURAS) {
    const ctx = await browser.newContext({ viewport: { width: w, height: w < 768 ? 740 : 900 }, deviceScaleFactor: 1 });
    await ctx.route(/cloudflareinsights/, rt => rt.abort());
    const pg = await ctx.newPage();
    await pg.goto(url, { waitUntil: "networkidle" });
    const larg = await pg.evaluate(() => document.documentElement.scrollWidth);
    const alt = await pg.evaluate(() => document.documentElement.scrollHeight);
    await pg.screenshot({ path: join(SAIDA, "screens", `${nome(p)}-${w}.jpg`), type: "jpeg", quality: 55,
      clip: { x: 0, y: 0, width: w, height: Math.min(alt, 4000) } });
    if (w === 375) {
      const res = await new AxeBuilder({ page: pg }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]).analyze();
      axe[p] = res.violations.map(v => ({ id: v.id, impacto: v.impact, nos: v.nodes.length, ajuda: v.help,
        exemplos: v.nodes.slice(0, 3).map(n => n.target.join(" ")) }));
    }
    lh[p][`rolagem_horizontal_${w}`] = larg > w;
    await ctx.close();
  }
  console.log("ok", p);
}
await browser.close();

writeFileSync(join(SAIDA, "lighthouse.json"), JSON.stringify(lh, null, 1));
writeFileSync(join(SAIDA, "axe.json"), JSON.stringify(axe, null, 1));
const linhas = ["| Página | Perf | A11y | BP | SEO | FCP | LCP | TBT | CLS | Peso | Violações axe (nós) | Rolagem horizontal |", "|---|---|---|---|---|---|---|---|---|---|---|---|"];
for (const p of PAGINAS) {
  const x = lh[p], v = axe[p] || [];
  const rol = LARGURAS.filter(w => x[`rolagem_horizontal_${w}`]).join(", ") || "não";
  linhas.push(`| ${p} | ${x.performance} | ${x.acessibilidade} | ${x.boas_praticas} | ${x.seo} | ${(x.fcp_ms / 1000).toFixed(1)} s | ${(x.lcp_ms / 1000).toFixed(1)} s | ${x.tbt_ms} ms | ${x.cls} | ${x.peso_kb} KB | ${v.length ? v.map(y => `${y.id} (${y.nos})`).join(", ") : "nenhuma"} | ${rol} |`);
}
writeFileSync(join(SAIDA, "resumo.md"), `# Auditoria de laboratório\n\nServidor local (${BASE}), Lighthouse ${require("lighthouse/package.json").version} perfil mobile, axe-core em 375 px. Dado de laboratório; não há dado de campo (CrUX) neste relatório.\n\n${linhas.join("\n")}\n`);
console.log(linhas.join("\n"));
