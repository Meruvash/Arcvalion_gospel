// Validação de layout e interação em várias larguras (Playwright).
// Uso, com o site servido na raiz:  BASE=http://localhost:8765 node tools/ux/validar.mjs [pasta-de-saida]
// (padrão: as páginas da prévia de exemplo; PAGINAS="/,/noticias/" troca a lista)
// Para cada página e largura: rolagem horizontal, alvos de toque menores que 24×24 px (WCAG 2.2, 2.5.8) e foco
// visível nos primeiros elementos alcançados pelo Tab. Links dentro de frases contam como exceção da 2.5.8.
import { createRequire } from "node:module";
import { mkdirSync, writeFileSync } from "node:fs";
const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const BASE = process.env.BASE || "http://localhost:8080";
const SAIDA = process.argv[2];
const PAGINAS = (process.env.PAGINAS || "/,/noticias/,/noticias-gospel/,/eventos/,/opiniao/,/noticias/exemplo-manchete-gospel/,/noticias/exemplo-explica-biblia/,/noticias/exemplo-patrocinado/,/contato/,/newsletter/,/politica-editorial/,/autores/autora-exemplo/").split(",");
const LARGURAS = [320, 375, 390, 768, 1024, 1440];
const TABS = 25;

const browser = await chromium.launch();
const resultado = [];
for (const w of LARGURAS) {
  const ctx = await browser.newContext({ viewport: { width: w, height: 800 } });
  await ctx.route(/cloudflareinsights|exemplo\.invalid|googlesyndication|googletagmanager/, r => r.abort());
  const page = await ctx.newPage();
  for (const url of PAGINAS) {
    await page.goto(BASE + url, { waitUntil: "load" });
    const r = await page.evaluate(() => {
      const visivel = el => { const b = el.getBoundingClientRect(), s = getComputedStyle(el); return b.width > 0 && b.height > 0 && s.visibility !== "hidden" && !el.closest("[hidden],dialog:not([open])"); };
      // link dentro de texto corrido (parágrafo ou item com mais texto que o próprio link): exceção "inline" da 2.5.8
      const emFrase = el => el.tagName === "A" && getComputedStyle(el).display === "inline" && (el.parentElement.textContent.trim().length > el.textContent.trim().length + 3);
      const pequenos = [...document.querySelectorAll("a[href],button,input:not([type=hidden]),select,summary,[role=option]")]
        .filter(el => visivel(el) && !emFrase(el))
        .map(el => ({ el, b: el.getBoundingClientRect() }))
        .filter(({ b }) => b.width < 24 || b.height < 24)
        .map(({ el, b }) => `${el.tagName.toLowerCase()}${el.className ? "." + String(el.className).split(" ")[0] : ""} "${(el.textContent || el.getAttribute("aria-label") || "").trim().slice(0, 30)}" ${Math.round(b.width)}×${Math.round(b.height)}`);
      return { rolagem: document.documentElement.scrollWidth > innerWidth, pequenos: [...new Set(pequenos)] };
    });
    // foco visível: Tab pelos primeiros elementos e confere contorno ou sombra
    const semFoco = [];
    await page.locator("body").click({ position: { x: 1, y: 1 } }).catch(() => {});
    for (let i = 0; i < TABS; i++) {
      await page.keyboard.press("Tab");
      const f = await page.evaluate(() => {
        const el = document.activeElement; if (!el || el === document.body) return null;
        const s = getComputedStyle(el);
        const ok = (s.outlineStyle !== "none" && parseFloat(s.outlineWidth) >= 2) || s.boxShadow !== "none";
        return ok ? null : `${el.tagName.toLowerCase()}.${String(el.className).split(" ")[0]} "${(el.textContent || el.getAttribute("aria-label") || "").trim().slice(0, 30)}"`;
      });
      if (f) semFoco.push(f);
    }
    resultado.push({ largura: w, pagina: url, ...r, sem_foco: [...new Set(semFoco)] });
  }
  await ctx.close();
}
await browser.close();

const problemas = resultado.filter(x => x.rolagem || x.pequenos.length || x.sem_foco.length);
for (const x of problemas) console.log(`${x.largura} ${x.pagina}: ${x.rolagem ? "ROLAGEM " : ""}${x.pequenos.length ? "pequenos=" + JSON.stringify(x.pequenos) : ""} ${x.sem_foco.length ? "sem_foco=" + JSON.stringify(x.sem_foco) : ""}`);
console.log(`${resultado.length} combinações página×largura; ${problemas.length} com problema`);
if (SAIDA) { mkdirSync(SAIDA, { recursive: true }); writeFileSync(`${SAIDA}/validacao.json`, JSON.stringify(resultado, null, 1)); }
