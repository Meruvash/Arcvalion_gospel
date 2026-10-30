// Teste da busca do site (Playwright). Uso, com o site servido na raiz do repositório:
//   python3 -m http.server 8080 &   e depois   node tools/ux/teste_busca.mjs
// Sai com código 1 se alguma verificação falhar. Usa só o que existe em busca.json (gerado por tools/busca.py).
import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const BASE = process.env.BASE || "http://localhost:8080";
const INDICE = JSON.parse(readFileSync(new URL("../../busca.json", import.meta.url)));
let falhas = 0;
const ok = (cond, msg) => { console.log(`${cond ? "✅" : "❌"} ${msg}`); if (!cond) falhas++; };

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 390, height: 800 } });
await ctx.route(/cloudflareinsights/, r => r.abort());
const page = await ctx.newPage();
const pedidos = [];
page.on("request", r => pedidos.push(r.url()));

// 1. Nada de busca na carga inicial
await page.goto(BASE + "/", { waitUntil: "networkidle" });
ok(!pedidos.some(u => /busca\.(js|json)/.test(u)), "carga inicial não baixa busca.js nem busca.json");
ok(await page.locator(".busca-btn").isVisible(), "lupa visível no cabeçalho");

// 2. Abre pelo teclado; sem véu escuro; a lupa some atrás da barra; sugestões das mais recentes
await page.keyboard.press("/");
const dlg = page.locator("dialog.busca-dlg");
await dlg.waitFor({ state: "visible" });
ok(await dlg.getAttribute("aria-modal") === "true", "diálogo com aria-modal");
ok(await page.evaluate(() => document.activeElement.id) === "bq-q", "foco vai para o campo de busca");
ok(await page.getByLabel(/Buscar notícias, estudos/).count() === 1, "campo tem rótulo");
ok(await page.evaluate(() => getComputedStyle(document.querySelector(".busca-dlg"), "::backdrop").backgroundColor) === "rgba(0, 0, 0, 0)", "fundo transparente: a página continua visível");
ok(!(await page.locator(".bar .busca-btn").isVisible()), "lupa do cabeçalho escondida com a busca aberta");
await page.waitForFunction(() => !/Carregando/.test(document.querySelector(".bq-st").textContent));
const recentes = await page.locator("#bq-lista [role=option]").count();
ok(recentes > 0, `busca vazia sugere as mais recentes (${recentes})`);

const resultados = async termo => {
  await page.fill("#bq-q", termo);
  return page.evaluate(() => [...document.querySelectorAll("#bq-lista [role=group]")].map(g => ({
    grupo: g.querySelector(".bq-g").textContent, itens: [...g.querySelectorAll("[role=option] b")].map(b => b.textContent),
  })));
};
const acha = (res, grupo, nome) => res.some(g => g.grupo.startsWith(grupo) && g.itens.includes(nome));

// 3. Autocompletar a partir de 2 letras, sem acento, com a última palavra pela metade
const estudo = INDICE.find(x => x.t === "e"), noticia = INDICE.find(x => x.t === "n");
let r = await resultados("ro");
ok(acha(r, "Livros da Bíblia", "Romanos"), '"ro" já sugere o livro de Romanos');
ok(await page.locator("#bq-lista mark").count() > 0, "trecho digitado destacado nos títulos");
r = await resultados("ROMANOS");
ok(acha(r, "Livros da Bíblia", "Romanos"), "maiúsculas não atrapalham");
if (estudo) {
  const palavra = estudo.n.split(/\s+/).map(p => p.replace(/[^\p{L}]/gu, "")).find(p => p.length > 5);
  r = await resultados(palavra.slice(0, 4));
  ok(acha(r, "Estudos bíblicos", estudo.n), `começo de "${palavra}" encontra o estudo`);
}
if (noticia) {
  r = await resultados(noticia.n.split(/\s+/).slice(0, 2).join(" "));
  ok(acha(r, "Notícias", noticia.n), "duas primeiras palavras encontram a notícia");
}
const peloResumo = INDICE.find(x => x.p && x.t === "n");
if (peloResumo) {
  const p = peloResumo.p.split(/\s+/).map(w => w.replace(/[^\p{L}]/gu, "")).find(w => w.length > 6 && !peloResumo.n.includes(w));
  if (p) { r = await resultados(p); ok(acha(r, "Notícias", peloResumo.n), `"${p}" (só no resumo) encontra a notícia`); }
}
await resultados("xyzxyz");
ok(/Nada encontrado/.test(await page.locator(".bq-st").textContent()), "estado vazio com sugestão");

// 4. Esc fecha e devolve a lupa; Ctrl+K reabre
await page.keyboard.press("Escape");
ok(!(await dlg.isVisible()), "Esc fecha o diálogo");
ok(await page.locator(".bar .busca-btn").waitFor({ state: "visible", timeout: 2000 }).then(() => true, () => false), "lupa volta ao fechar");
await page.keyboard.press("Control+k");
await dlg.waitFor({ state: "visible" });
ok(true, "Ctrl+K abre o diálogo");

// 5. Setas e Enter levam ao livro
await resultados("romanos");
await page.keyboard.press("ArrowDown");
ok(await page.getAttribute("#bq-q", "aria-activedescendant") === "bq-o0", "seta marca o primeiro resultado");
const destino = await page.getAttribute("#bq-o0", "data-u");
await Promise.all([page.waitForURL(u => u.href.includes(destino.split("?")[0])), page.keyboard.press("Enter")]);
ok(true, `Enter leva a ${destino}`);

await browser.close();
console.log(falhas ? `\n${falhas} falha(s)` : "\ntudo certo");
process.exit(falhas ? 1 : 0);
