// Fluxos interativos na prévia de exemplo: busca (atalho "/"), filtro por editoria com estado na URL, menu de
// compartilhar e ausência de erro de JavaScript. Uso: BASE=http://localhost:8765 node tools/ux/fluxos.mjs
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const BASE = process.env.BASE || "http://localhost:8765";
const falhas = [];
const ok = (cond, msg) => { console.log((cond ? "✅ " : "❌ ") + msg); if (!cond) falhas.push(msg); };

const b = await chromium.launch();
const ctx = await b.newContext({ viewport: { width: 1280, height: 900 } });
await ctx.route(/exemplo\.invalid|cloudflareinsights|google/, r => r.abort());
const p = await ctx.newPage();
const erros = [];
p.on("pageerror", e => erros.push(e.message));

await p.goto(BASE + "/", { waitUntil: "load" });
await p.keyboard.press("/");
await p.waitForSelector(".busca-dlg[open]");
await p.keyboard.type("manchete");
await p.waitForSelector("[role=option]");
ok((await p.locator("[role=option]").count()) >= 1, "busca acha a matéria pelo título");
await p.keyboard.press("Enter");
await p.waitForURL(/exemplo-manchete-gospel/);
ok(true, "Enter na busca abre a matéria");

await p.goto(BASE + "/noticias/", { waitUntil: "load" });
await p.click('.cats button[data-c="fe-e-biblia"]');
const visiveis = await p.locator(".card-n:not([hidden])").count();
ok(visiveis === 1 && p.url().includes("editoria=fe-e-biblia"), "filtro por editoria esconde as outras e guarda o estado na URL");
await p.goto(BASE + "/noticias/?editoria=eventos", { waitUntil: "load" });
ok((await p.locator(".card-n:not([hidden])").count()) === 1, "filtro abre já aplicado a partir da URL");

await p.goto(BASE + "/noticias/exemplo-familia/", { waitUntil: "load" });
await p.click(".convite .cp");
ok(await p.locator(".convite .cp-menu").isVisible(), "compartilhar abre o menu (WhatsApp, Telegram, Copiar)");
await p.keyboard.press("Escape");
ok(await p.locator(".convite .cp-menu").isHidden(), "Esc fecha o menu de compartilhar");

ok(erros.length === 0, "sem erro de JavaScript" + (erros.length ? ": " + erros.join(" | ") : ""));
await b.close();
process.exit(falhas.length ? 1 : 0);
