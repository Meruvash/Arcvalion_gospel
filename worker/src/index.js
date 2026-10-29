// Serviço de interações do portal (Cloudflare Worker + banco D1): curtidas, comentários moderados, newsletter,
// formulários de contato e métricas agregadas dos espaços de anúncio. Recursos próprios, sem nada em comum com
// qualquer outro projeto: banco, segredos, domínio e origem são configurados em wrangler.toml e `wrangler secret`.
//
// Público (CORS só para o site em ORIGEM):
//   GET  /v1/pagina?p=/caminho/            curtidas e comentários aprovados da página
//   POST /v1/curtir     {p, d, desfazer}   d = identificador aleatório do navegador
//   POST /v1/comentar   {p, nome, texto, email, isca, turnstile}           entra na fila de moderação
//   POST /v1/newsletter {email, nome, editorias[], consentimento, texto_consentimento, origem, isca, turnstile}
//   GET  /v1/newsletter/sair?t=<token>     descadastro (link do rodapé das mensagens)
//   POST /v1/contato    {tipo, nome, email, mensagem, empresa, detalhe, consentimento, texto_consentimento, pagina, isca, turnstile}
//   POST /v1/metricas   {espaco, evento: impressao|clique, ed, p, casa}  contador agregado por dia, sem dados de pessoa
// Administração (cabeçalho Authorization: Bearer <MODERACAO_TOKEN>):
//   GET  /v1/moderacao/fila | /v1/moderacao/recentes      POST /v1/moderacao/decidir {id, estado, parecer, por}
//   GET  /v1/admin/contatos?estado=novo   POST /v1/admin/contato {id, estado}
//   GET  /v1/admin/inscritos              GET /v1/admin/metricas?dias=30
//   GET  /painel                          painel de moderação (pede a senha no navegador)
//
// Variáveis: DB (D1), ORIGEM e NOME (wrangler.toml); MODERACAO_TOKEN e TURNSTILE_SECRET (segredos); DEV=1 só no teste local.

const MAX_POR_HORA = 5;
const PAGINA = /^\/[a-z0-9\-/]{1,180}\/$/;
const ESTADOS = new Set(["pendente", "aprovado", "reprovado", "duvidoso"]);
const TIPOS_CONTATO = new Set(["comercial", "evento", "correcao", "geral"]);
const EVENTOS_PUB = new Set(["impressao", "clique"]);
const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const json = (dados, status = 200, extra = {}) =>
  new Response(JSON.stringify(dados), { status, headers: { "content-type": "application/json; charset=utf-8", ...extra } });

function cors(req, env) {
  const origem = req.headers.get("origin") || "";
  const ok = origem === env.ORIGEM || (env.DEV === "1" && origem.startsWith("http://localhost"));
  return ok ? { "access-control-allow-origin": origem, "access-control-allow-methods": "GET,POST,OPTIONS",
                "access-control-allow-headers": "content-type,authorization", "vary": "origin" } : {};
}

async function sha256(texto) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(texto));
  return [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, "0")).join("");
}

// IP nunca é guardado: só o hash com um sal do dia, para limitar abuso
async function ipHash(req, env) {
  const ip = req.headers.get("cf-connecting-ip") || "local";
  return sha256(`${ip}|${new Date().toISOString().slice(0, 10)}|${env.MODERACAO_TOKEN || "dev"}`);
}

async function turnstileOk(token, req, env) {
  if (env.DEV === "1" && !env.TURNSTILE_SECRET) return true;
  if (!token || !env.TURNSTILE_SECRET) return false;
  const r = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
    method: "POST", body: new URLSearchParams({ secret: env.TURNSTILE_SECRET, response: token, remoteip: req.headers.get("cf-connecting-ip") || "" }),
  });
  return (await r.json()).success === true;
}

async function limite(env, tabela, ip) {
  const n = await env.DB.prepare(`SELECT COUNT(*) AS n FROM ${tabela} WHERE ip_hash = ? AND criado > datetime('now', '-1 hour')`).bind(ip).first("n");
  return n >= MAX_POR_HORA;
}

const texto = (v, max) => String(v || "").trim().replace(/\s+/g, " ").slice(0, max);

async function pagina(url, env, h) {
  const p = url.searchParams.get("p") || "";
  if (!PAGINA.test(p)) return json({ erro: "página inválida" }, 400, h);
  const n = await env.DB.prepare("SELECT COUNT(*) AS n FROM curtidas WHERE pagina = ?").bind(p).first("n");
  const { results } = await env.DB.prepare(
    "SELECT id, nome, texto, criado FROM comentarios WHERE pagina = ? AND estado = 'aprovado' ORDER BY criado ASC LIMIT 300").bind(p).all();
  return json({ curtidas: n || 0, comentarios: results }, 200, { ...h, "cache-control": "no-store" });
}

async function curtir(req, env, h) {
  const { p, d, desfazer } = await req.json().catch(() => ({}));
  if (!PAGINA.test(p || "") || !/^[a-z0-9-]{16,64}$/i.test(d || "")) return json({ erro: "dados inválidos" }, 400, h);
  if (desfazer) await env.DB.prepare("DELETE FROM curtidas WHERE pagina = ? AND dispositivo = ?").bind(p, d).run();
  else await env.DB.prepare("INSERT OR IGNORE INTO curtidas (pagina, dispositivo) VALUES (?, ?)").bind(p, d).run();
  const n = await env.DB.prepare("SELECT COUNT(*) AS n FROM curtidas WHERE pagina = ?").bind(p).first("n");
  return json({ curtidas: n || 0 }, 200, h);
}

async function comentar(req, env, h) {
  const b = await req.json().catch(() => ({}));
  const nome = texto(b.nome, 200), corpo = String(b.texto || "").trim(), email = String(b.email || "").trim();
  if (b.isca) return json({ ok: true, estado: "pendente" }, 200, h);  // robô preencheu o campo escondido: finge que deu certo
  if (!PAGINA.test(b.p || "")) return json({ erro: "página inválida" }, 400, h);
  if (nome.length < 2 || nome.length > 60) return json({ erro: "Escreva um nome entre 2 e 60 letras." }, 400, h);
  if (corpo.length < 3 || corpo.length > 1500) return json({ erro: "O comentário precisa ter entre 3 e 1.500 caracteres." }, 400, h);
  if (email && (email.length > 120 || !EMAIL.test(email))) return json({ erro: "Esse e-mail não parece válido (ele é opcional)." }, 400, h);
  if (!(await turnstileOk(b.turnstile, req, env))) return json({ erro: "Não conseguimos confirmar que você não é um robô. Tente de novo." }, 400, h);
  const ip = await ipHash(req, env);
  if (await limite(env, "comentarios", ip)) return json({ erro: "Muitos comentários seguidos. Tente de novo daqui a pouco." }, 429, h);
  await env.DB.prepare("INSERT INTO comentarios (pagina, nome, email, texto, ip_hash) VALUES (?, ?, ?, ?, ?)").bind(b.p, nome, email || null, corpo, ip).run();
  return json({ ok: true, estado: "pendente" }, 200, h);
}

async function newsletter(req, env, h) {
  const b = await req.json().catch(() => ({}));
  if (b.isca) return json({ ok: true }, 200, h);
  const email = String(b.email || "").trim().toLowerCase();
  if (!EMAIL.test(email) || email.length > 120) return json({ erro: "Esse e-mail não parece válido." }, 400, h);
  // LGPD: consentimento explícito, guardado com a data e o texto exato que a pessoa aceitou
  if (b.consentimento !== true || !b.texto_consentimento) return json({ erro: "Marque a caixa de consentimento para se inscrever." }, 400, h);
  if (!(await turnstileOk(b.turnstile, req, env))) return json({ erro: "Não conseguimos confirmar que você não é um robô. Tente de novo." }, 400, h);
  const ip = await ipHash(req, env);
  if (await limite(env, "inscritos", ip)) return json({ erro: "Muitas tentativas seguidas. Tente de novo daqui a pouco." }, 429, h);
  const eds = (Array.isArray(b.editorias) ? b.editorias : []).filter(x => /^[a-z0-9-]{2,60}$/.test(x)).slice(0, 20).join(",");
  const token = crypto.randomUUID().replace(/-/g, "") + crypto.randomUUID().replace(/-/g, "");
  await env.DB.prepare(
    `INSERT INTO inscritos (email, nome, editorias, consentimento_texto, origem, token, ip_hash) VALUES (?, ?, ?, ?, ?, ?, ?)
     ON CONFLICT(email) DO UPDATE SET nome = excluded.nome, editorias = excluded.editorias, consentimento_texto = excluded.consentimento_texto,
       consentimento_em = datetime('now'), estado = 'ativo', saiu_em = NULL`)
    .bind(email, texto(b.nome, 80) || null, eds, texto(b.texto_consentimento, 600), texto(b.origem, 60), token, ip).run();
  return json({ ok: true }, 200, h);
}

async function sair(url, env) {
  const t = url.searchParams.get("t") || "";
  if (/^[a-f0-9]{64}$/.test(t)) await env.DB.prepare("UPDATE inscritos SET estado = 'cancelado', saiu_em = datetime('now') WHERE token = ?").bind(t).run();
  const nome = env.NOME || "o portal";
  return new Response(`<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex">
<title>Inscrição cancelada</title><body style="font:17px/1.6 system-ui,sans-serif;max-width:560px;margin:10vh auto;padding:0 16px">
<h1>Inscrição cancelada</h1><p>Você não vai mais receber a newsletter de ${nome}. Se foi engano, inscreva-se de novo no site.</p></body></html>`,
    { headers: { "content-type": "text/html; charset=utf-8" } });
}

async function contato(req, env, h) {
  const b = await req.json().catch(() => ({}));
  if (b.isca) return json({ ok: true }, 200, h);
  const tipo = TIPOS_CONTATO.has(b.tipo) ? b.tipo : null, email = String(b.email || "").trim(), msg = String(b.mensagem || "").trim();
  if (!tipo) return json({ erro: "assunto inválido" }, 400, h);
  if (texto(b.nome, 200).length < 2) return json({ erro: "Escreva o seu nome." }, 400, h);
  if (!EMAIL.test(email) || email.length > 120) return json({ erro: "Esse e-mail não parece válido." }, 400, h);
  if (msg.length < 10 || msg.length > 3000) return json({ erro: "A mensagem precisa ter entre 10 e 3.000 caracteres." }, 400, h);
  if (b.consentimento !== true) return json({ erro: "Marque a caixa de autorização para enviar." }, 400, h);
  if (!(await turnstileOk(b.turnstile, req, env))) return json({ erro: "Não conseguimos confirmar que você não é um robô. Tente de novo." }, 400, h);
  const ip = await ipHash(req, env);
  if (await limite(env, "contatos", ip)) return json({ erro: "Muitas mensagens seguidas. Tente de novo daqui a pouco." }, 429, h);
  await env.DB.prepare("INSERT INTO contatos (tipo, nome, email, empresa, detalhe, mensagem, pagina, consentimento_texto, ip_hash) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)")
    .bind(tipo, texto(b.nome, 80), email, texto(b.empresa, 120) || null, texto(b.detalhe, 300) || null, msg, texto(b.pagina, 200), texto(b.texto_consentimento, 600), ip).run();
  return json({ ok: true }, 200, h);
}

async function metricas(req, env, h) {
  const b = await (async () => { try { return JSON.parse(await req.text()); } catch { return {}; } })();
  if (!/^[a-z0-9-]{2,40}$/.test(b.espaco || "") || !EVENTOS_PUB.has(b.evento)) return json({ erro: "dados inválidos" }, 400, h);
  const ed = /^[a-z0-9-]{0,60}$/.test(b.ed || "") ? b.ed || "" : "";
  await env.DB.prepare(
    `INSERT INTO metricas_anuncios (dia, espaco, editoria, evento, casa, n) VALUES (date('now'), ?, ?, ?, ?, 1)
     ON CONFLICT(dia, espaco, editoria, evento, casa) DO UPDATE SET n = n + 1`).bind(b.espaco, ed, b.evento, b.casa ? 1 : 0).run();
  return new Response(null, { status: 204, headers: h });
}

function autorizado(req, env) {
  const t = (req.headers.get("authorization") || "").replace(/^Bearer\s+/i, "");
  return env.MODERACAO_TOKEN && t.length > 20 && t === env.MODERACAO_TOKEN;
}

async function admin(req, url, env) {
  if (!autorizado(req, env)) return json({ erro: "não autorizado" }, 401);
  const r = url.pathname;
  if (r === "/v1/moderacao/fila") {
    const { results } = await env.DB.prepare(
      "SELECT id, pagina, nome, email, texto, criado, estado, parecer FROM comentarios WHERE estado IN ('pendente', 'duvidoso') ORDER BY criado ASC LIMIT 200").all();
    return json({ comentarios: results });
  }
  if (r === "/v1/moderacao/recentes") {
    const { results } = await env.DB.prepare(
      "SELECT id, pagina, nome, email, texto, criado, estado, parecer, decidido_por, decidido_em FROM comentarios ORDER BY criado DESC LIMIT 200").all();
    return json({ comentarios: results });
  }
  if (r === "/v1/moderacao/decidir" && req.method === "POST") {
    const { id, estado, parecer, por } = await req.json().catch(() => ({}));
    if (!Number.isInteger(id) || !ESTADOS.has(estado)) return json({ erro: "dados inválidos" }, 400);
    await env.DB.prepare("UPDATE comentarios SET estado = ?, parecer = COALESCE(?, parecer), decidido_por = ?, decidido_em = datetime('now') WHERE id = ?")
      .bind(estado, parecer ? String(parecer).slice(0, 500) : null, por === "ia" ? "ia" : "editor", id).run();
    return json({ ok: true });
  }
  if (r === "/v1/admin/contatos") {
    const estado = url.searchParams.get("estado") || "novo";
    const { results } = await env.DB.prepare("SELECT * FROM contatos WHERE estado = ? ORDER BY criado DESC LIMIT 300").bind(estado).all();
    return json({ contatos: results.map(({ ip_hash, ...c }) => c) });
  }
  if (r === "/v1/admin/contato" && req.method === "POST") {
    const { id, estado } = await req.json().catch(() => ({}));
    if (!Number.isInteger(id) || !["novo", "respondido", "arquivado"].includes(estado)) return json({ erro: "dados inválidos" }, 400);
    await env.DB.prepare("UPDATE contatos SET estado = ? WHERE id = ?").bind(estado, id).run();
    return json({ ok: true });
  }
  if (r === "/v1/admin/inscritos") {
    const { results } = await env.DB.prepare("SELECT email, nome, editorias, consentimento_em, consentimento_texto, origem, token FROM inscritos WHERE estado = 'ativo' ORDER BY consentimento_em").all();
    return json({ inscritos: results });
  }
  if (r === "/v1/admin/metricas") {
    const dias = Math.min(Math.max(parseInt(url.searchParams.get("dias") || "30", 10) || 30, 1), 365);
    const { results } = await env.DB.prepare(
      `SELECT espaco, editoria, casa, SUM(CASE WHEN evento = 'impressao' THEN n ELSE 0 END) AS impressoes,
              SUM(CASE WHEN evento = 'clique' THEN n ELSE 0 END) AS cliques FROM metricas_anuncios
       WHERE dia >= date('now', ?) GROUP BY espaco, editoria, casa ORDER BY impressoes DESC`).bind(`-${dias} days`).all();
    return json({ dias, espacos: results.map(x => ({ ...x, ctr: x.impressoes ? +(100 * x.cliques / x.impressoes).toFixed(2) : 0 })) });
  }
  return json({ erro: "rota desconhecida" }, 404);
}

export default {
  async fetch(req, env) {
    const url = new URL(req.url), h = cors(req, env);
    try {
      if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: h });
      if (url.pathname === "/painel") return new Response(PAINEL.replaceAll("__NOME__", env.NOME || "Portal").replaceAll("__ORIGEM__", env.ORIGEM || ""),
        { headers: { "content-type": "text/html; charset=utf-8", "x-robots-tag": "noindex" } });
      if (url.pathname.startsWith("/v1/moderacao/") || url.pathname.startsWith("/v1/admin/")) return admin(req, url, env);
      if (url.pathname === "/v1/pagina" && req.method === "GET") return pagina(url, env, h);
      if (url.pathname === "/v1/curtir" && req.method === "POST") return curtir(req, env, h);
      if (url.pathname === "/v1/comentar" && req.method === "POST") return comentar(req, env, h);
      if (url.pathname === "/v1/newsletter" && req.method === "POST") return newsletter(req, env, h);
      if (url.pathname === "/v1/newsletter/sair" && req.method === "GET") return sair(url, env);
      if (url.pathname === "/v1/contato" && req.method === "POST") return contato(req, env, h);
      if (url.pathname === "/v1/metricas" && req.method === "POST") return metricas(req, env, h);
      return json({ erro: "rota desconhecida" }, 404, h);
    } catch (e) {
      return json({ erro: "falha interna" }, 500, h);
    }
  },
};

// Painel de moderação: página única que guarda a senha só nesta aba (sessionStorage) e conversa com a API acima.
const PAINEL = `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex"><title>Moderação de comentários · __NOME__</title><style>
*{box-sizing:border-box}body{margin:0;background:#f5f3ee;color:#16202e;font:15px/1.5 system-ui,sans-serif}main{max-width:900px;margin:0 auto;padding:20px 16px 60px}
h1{font-size:1.5rem;margin:0 0 4px;border-top:4px solid #12294a;padding-top:10px}p.sub{color:#5b6573;margin:0 0 16px}
.abas{display:flex;gap:8px;margin:12px 0;flex-wrap:wrap}.abas button,.b{font:inherit;font-weight:700;min-height:44px;padding:6px 14px;border-radius:999px;border:1px solid #c9c5ba;background:#fff;color:#16202e;cursor:pointer}
.abas button[aria-pressed=true]{background:#12294a;color:#fff;border-color:#12294a}
.c{background:#fff;border:1px solid #e3e0d8;border-left:4px solid #5b6573;border-radius:10px;padding:14px;margin:10px 0}
.c.pendente{border-left-color:#d6b25e}.c.duvidoso{border-left-color:#a3223a}.c.aprovado{border-left-color:#2c6447}.c.reprovado{opacity:.7}
.meta{font:12px ui-monospace,monospace;color:#5b6573;text-transform:uppercase;letter-spacing:.04em}.meta a{color:#1d4f91}
.txt{white-space:pre-wrap;margin:8px 0;font-size:1rem}.parecer{font-size:.9rem;color:#5f3b86;margin:6px 0}
.acoes{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}.b.ok{background:#2c6447;border-color:#2c6447;color:#fff}.b.no{background:#7a2335;border-color:#7a2335;color:#fff}
input{font:inherit;padding:10px 12px;border-radius:8px;border:1px solid #c9c5ba;width:min(420px,100%)}
.vazio{color:#5b6573;padding:20px 0}</style></head><body><main>
<h1>Moderação de comentários</h1><p class="sub">__NOME__ · nada aparece no site sem estar aprovado.</p>
<form id="login" hidden><p>Senha de moderação:</p><input id="senha" type="password" autocomplete="current-password"> <button class="b">Entrar</button></form>
<div id="app" hidden><div class="abas"><button data-aba="fila" aria-pressed="true">Esperando decisão</button><button data-aba="recentes" aria-pressed="false">Todos os recentes</button><button class="b" id="sair" type="button">Sair</button></div><div id="lista"></div></div>
<script>
const $=s=>document.querySelector(s),esc=t=>String(t??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'})[c]);
let aba='fila';const tok=()=>sessionStorage.getItem('mod');
const api=(c,o={})=>fetch('/v1/moderacao/'+c,{...o,headers:{'authorization':'Bearer '+tok(),'content-type':'application/json'}});
async function carrega(){const r=await api(aba);if(r.status===401){sessionStorage.removeItem('mod');return entrar()}
 const {comentarios}=await r.json();$('#app').hidden=false;$('#login').hidden=true;
 $('#lista').innerHTML=comentarios.length?comentarios.map(c=>'<div class="c '+c.estado+'" data-id="'+c.id+'"><div class="meta">'+esc(c.estado)+' · '+esc(c.criado)+' UTC · <a href="__ORIGEM__'+esc(c.pagina)+'" target="_blank">'+esc(c.pagina)+'</a></div>'
 +'<div><b>'+esc(c.nome)+'</b>'+(c.email?' · '+esc(c.email):'')+'</div><div class="txt">'+esc(c.texto)+'</div>'+(c.parecer?'<div class="parecer">Parecer: '+esc(c.parecer)+(c.decidido_por?' ('+esc(c.decidido_por)+')':'')+'</div>':'')
 +'<div class="acoes"><button class="b ok" data-e="aprovado">Aprovar</button><button class="b no" data-e="reprovado">Reprovar</button></div></div>').join(''):'<p class="vazio">Nenhum comentário esperando decisão.</p>'}
function entrar(){$('#app').hidden=true;$('#login').hidden=false;$('#senha').focus()}
$('#login').addEventListener('submit',e=>{e.preventDefault();sessionStorage.setItem('mod',$('#senha').value);carrega()});
$('#sair').addEventListener('click',()=>{sessionStorage.removeItem('mod');entrar()});
document.querySelectorAll('[data-aba]').forEach(b=>b.addEventListener('click',()=>{aba=b.dataset.aba;document.querySelectorAll('[data-aba]').forEach(x=>x.setAttribute('aria-pressed',x===b));carrega()}));
$('#lista').addEventListener('click',async e=>{const b=e.target.closest('[data-e]');if(!b)return;const id=+b.closest('.c').dataset.id;
 b.disabled=true;await api('decidir',{method:'POST',body:JSON.stringify({id,estado:b.dataset.e,por:'editor'})});carrega()});
tok()?carrega():entrar();
</script></main></body></html>`;
