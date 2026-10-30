// Teste da busca do site (Playwright). Uso, com o site servido na raiz do repositório:
//   python3 -m http.server 8080 &   e depois   node tools/ux/teste_busca.mjs
// Sai com código 1 se alguma verificação falhar.
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const BASE = process.env.BASE || "http://localhost:8080";
let falhas = 0;
const ok = (cond, msg) => { console.log(`${cond ? "✅" : "❌"} ${msg}`); if (!cond) falhas++; };

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 390, height: 800 } });
await ctx.route(/cloudflareinsights/, r => r.abort());
const page = await ctx.newPage();
const pedidos = [];
page.on("request", r => pedidos.push(r.url()));

// 1. Nada de busca na carga inicial
await page.goto(BASE + "/root/", { waitUntil: "networkidle" });
ok(!pedidos.some(u => /busca\.(js|json)/.test(u)), "carga inicial não baixa busca.js nem busca.json");
ok(await page.locator(".busca-btn").isVisible(), "lupa visível no cabeçalho");

// 2. Abrir pelo teclado ("/"), diálogo acessível
await page.keyboard.press("/");
const dlg = page.locator("dialog.busca-dlg");
await dlg.waitFor({ state: "visible" });
ok(await dlg.getAttribute("aria-modal") === "true", "diálogo com aria-modal");
ok(await page.evaluate(() => document.activeElement.id) === "bq-q", "foco vai para o campo de busca");
ok(await page.getByLabel(/Buscar notícias/).count() === 1, "campo tem rótulo");
ok(pedidos.some(u => u.endsWith("/busca.json")), "índice baixado ao abrir");

const resultados = async termo => {
  await page.fill("#bq-q", termo);
  await page.waitForFunction(() => !/Carregando/.test(document.querySelector(".bq-st").textContent));
  return page.evaluate(() => [...document.querySelectorAll("#bq-lista [role=group]")].map(g => ({
    grupo: g.querySelector(".bq-g").textContent, itens: [...g.querySelectorAll("[role=option] b")].map(b => b.childNodes[0].textContent),
  })));
};
const temResenha = (res, nome) => res.some(g => g.grupo.startsWith("Resenhas") && g.itens.includes(nome));

// 3. Acento, caixa e apelidos PT/EN (só nomes que existem nos dados do site)
const casos = [
  ["santuario", "Santuário"], ["SANTUÁRIO", "Santuário"], ["sanctuary", "Santuário"],
  ["duna imperium", "Dune: Imperium"], ["dune imperium", "Dune: Imperium"],
  ["sina sociedade", "O Senhor dos Anéis: Sina da Sociedade"], ["fate of the fellowship", "O Senhor dos Anéis: Sina da Sociedade"],
  ["ruinas perdidas", "Lost Ruins of Arnak"], ["arnak", "Lost Ruins of Arnak"], ["codigo secreto", "Codenames"],
];
for (const [termo, nome] of casos) ok(temResenha(await resultados(termo), nome), `"${termo}" encontra a resenha ${nome}`);
let r = await resultados("root");
ok(r.map(g => g.grupo.split(" (")[0]).join(",").startsWith("Resenhas"), "resultados agrupados por tipo, resenhas primeiro");
ok(r.some(g => g.grupo.startsWith("Consulta Golden Geek")), "Golden Geek aparece como grupo próprio");
r = await resultados("xyzxyz");
ok(/Nada encontrado/.test(await page.locator(".bq-st").textContent()), "estado vazio com sugestão");

// 4. Esc fecha e devolve o foco; Ctrl+K reabre
await page.keyboard.press("Escape");
ok(!(await dlg.isVisible()), "Esc fecha o diálogo");
await page.keyboard.press("Control+k");
await dlg.waitFor({ state: "visible" });
ok(true, "Ctrl+K abre o diálogo");

// 5. Setas e Enter: busca em inglês por um jogo com resenha em português e navega até ela
await resultados("fellowship");
await page.keyboard.press("ArrowDown");
ok(await page.getAttribute("#bq-q", "aria-activedescendant") === "bq-o0", "seta marca o primeiro resultado");
await Promise.all([page.waitForURL(/fate-of-the-fellowship\/$/), page.keyboard.press("Enter")]);
ok(true, "Enter leva à resenha /fate-of-the-fellowship/");

// 6. Golden Geek leva à Consulta já filtrada pelo jogo
await page.keyboard.press("Control+k");
await dlg.waitFor({ state: "visible" });
await resultados("wingspan");
await Promise.all([page.waitForURL(/consulta\/\?jogo=/), page.locator("#bq-lista [data-u^='consulta/']").first().click()]);
ok(/Jogo: Wingspan/.test(await page.locator("#chipbox").textContent()), "Consulta abre filtrada em Wingspan");

// 7. Lançamento leva à âncora e abre a ficha
await page.keyboard.press("Control+k");
await dlg.waitFor({ state: "visible" });
await resultados("linhagens");
await Promise.all([page.waitForURL(/lancamentos\/#j\d+/), page.locator("#bq-lista [data-u^='lancamentos/']").first().click()]);
await page.locator("dialog#ficha").waitFor({ state: "visible" });
ok(/Linhagens/.test(await page.locator("#ficha-nome").textContent()), "lançamento abre a ficha do jogo em /lancamentos/");

await browser.close();
console.log(falhas ? `\n${falhas} falha(s)` : "\nTudo certo");
process.exit(falhas ? 1 : 0);
