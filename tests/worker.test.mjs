// Testes do Worker com um D1 simulado sobre node:sqlite (Node 22+). Uso: node --test tests/
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { DatabaseSync } from "node:sqlite";
import worker from "../worker/src/index.js";

function d1() {
  const db = new DatabaseSync(":memory:");
  db.exec(readFileSync(new URL("../worker/schema.sql", import.meta.url), "utf8"));
  return {
    prepare(sql) {
      let args = [];
      const st = () => db.prepare(sql);
      const o = {
        bind(...a) { args = a; return o; },
        async first(col) { const r = st().get(...args); return r ? (col ? r[col] : r) : null; },
        async all() { return { results: st().all(...args) }; },
        async run() { st().run(...args); return { success: true }; },
      };
      return o;
    },
    _db: db,
  };
}

const ORIGEM = "https://portal.teste";
const env = () => ({ DB: d1(), ORIGEM, NOME: "Portal Teste", DEV: "1", MODERACAO_TOKEN: "x".repeat(32) });
const post = (rota, corpo, extra = {}) => new Request("https://api.teste" + rota, { method: "POST", headers: { "content-type": "application/json", origin: ORIGEM, ...extra }, body: JSON.stringify(corpo) });

test("comentário entra pendente e só aparece depois de aprovado", async () => {
  const e = env();
  let r = await worker.fetch(post("/v1/comentar", { p: "/noticias/x/", nome: "Maria", texto: "Ótima matéria" }), e);
  assert.equal(r.status, 200);
  assert.equal(r.headers.get("access-control-allow-origin"), ORIGEM);
  r = await worker.fetch(new Request("https://api.teste/v1/pagina?p=/noticias/x/"), e);
  assert.equal((await r.json()).comentarios.length, 0);
  r = await worker.fetch(post("/v1/moderacao/decidir", { id: 1, estado: "aprovado", por: "editor" }, { authorization: "Bearer " + "x".repeat(32) }), e);
  assert.equal(r.status, 200);
  r = await worker.fetch(new Request("https://api.teste/v1/pagina?p=/noticias/x/"), e);
  assert.equal((await r.json()).comentarios[0].nome, "Maria");
});

test("moderação exige token", async () => {
  const r = await worker.fetch(new Request("https://api.teste/v1/moderacao/fila"), env());
  assert.equal(r.status, 401);
});

test("newsletter exige consentimento explícito e guarda o texto aceito", async () => {
  const e = env();
  let r = await worker.fetch(post("/v1/newsletter", { email: "a@b.com", consentimento: false }), e);
  assert.equal(r.status, 400);
  r = await worker.fetch(post("/v1/newsletter", { email: "A@B.com", consentimento: true, texto_consentimento: "Quero receber", editorias: ["fe-e-biblia", "<x>"] }), e);
  assert.equal(r.status, 200);
  const linha = e.DB._db.prepare("SELECT * FROM inscritos").get();
  assert.equal(linha.email, "a@b.com");
  assert.equal(linha.editorias, "fe-e-biblia");
  assert.equal(linha.consentimento_texto, "Quero receber");
  r = await worker.fetch(new Request("https://api.teste/v1/newsletter/sair?t=" + linha.token), e);
  assert.equal(r.status, 200);
  assert.equal(e.DB._db.prepare("SELECT estado FROM inscritos").get().estado, "cancelado");
});

test("contato valida tipo e consentimento", async () => {
  const e = env();
  let r = await worker.fetch(post("/v1/contato", { tipo: "spam", nome: "Jo", email: "a@b.com", mensagem: "mensagem longa o bastante", consentimento: true }), e);
  assert.equal(r.status, 400);
  r = await worker.fetch(post("/v1/contato", { tipo: "comercial", nome: "Jo", email: "a@b.com", mensagem: "Quero anunciar no portal", consentimento: true, empresa: "Igreja X" }), e);
  assert.equal(r.status, 200);
  r = await worker.fetch(new Request("https://api.teste/v1/admin/contatos", { headers: { authorization: "Bearer " + "x".repeat(32) } }), e);
  const { contatos } = await r.json();
  assert.equal(contatos[0].empresa, "Igreja X");
  assert.equal("ip_hash" in contatos[0], false);
});

test("métricas de anúncio só somam contadores agregados", async () => {
  const e = env();
  for (const ev of ["impressao", "impressao", "clique"]) await worker.fetch(post("/v1/metricas", { espaco: "home-topo", evento: ev, ed: "" }), e);
  assert.equal((await worker.fetch(post("/v1/metricas", { espaco: "home-topo", evento: "hack" }), e)).status, 400);
  const r = await worker.fetch(new Request("https://api.teste/v1/admin/metricas", { headers: { authorization: "Bearer " + "x".repeat(32) } }), e);
  const { espacos } = await r.json();
  assert.deepEqual([espacos[0].impressoes, espacos[0].cliques, espacos[0].ctr], [2, 1, 50]);
});

test("campo-isca de robô finge sucesso e não grava", async () => {
  const e = env();
  const r = await worker.fetch(post("/v1/comentar", { p: "/noticias/x/", nome: "Bot", texto: "compre já", isca: "http://spam" }), e);
  assert.equal(r.status, 200);
  assert.equal(e.DB._db.prepare("SELECT COUNT(*) AS n FROM comentarios").get().n, 0);
});
