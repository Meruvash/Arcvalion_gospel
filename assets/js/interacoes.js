// Curtidas e comentários (serviço em worker/, na Cloudflare). Só roda nas páginas com <section class="interacoes">.
// O verificador anti-robô (Turnstile) só é baixado quando a pessoa começa a escrever um comentário.
(() => {
  const sec = document.querySelector(".interacoes");
  if (!sec) return;
  const api = sec.dataset.api, p = sec.dataset.p, chave = sec.dataset.turnstile;
  const $ = s => sec.querySelector(s);
  const esc = t => String(t).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
  const guarda = {
    get: k => { try { return localStorage.getItem(k); } catch { return null; } },
    set: (k, v) => { try { localStorage.setItem(k, v); } catch { /* aba anônima: segue sem lembrar */ } },
  };
  // identificador aleatório deste navegador, só para contar uma curtida por aparelho
  let disp = guarda.get("pc-disp");
  if (!disp) { disp = (crypto.randomUUID ? crypto.randomUUID() : String(Math.random()).slice(2) + Date.now()).replace(/[^a-z0-9-]/gi, ""); guarda.set("pc-disp", disp); }
  const curtidas = new Set(JSON.parse(guarda.get("pc-curtidas") || "[]"));
  // o botão da seção e o da barra de leitura (no rodapé da tela) mostram o mesmo estado
  const btns = [...document.querySelectorAll(".curtir")], nums = [...document.querySelectorAll(".curtir .n")];
  const num = { get textContent() { return nums[0].textContent; }, set textContent(v) { nums.forEach(n => { n.textContent = v; }); } };
  const marca = on => btns.forEach(b => {
    b.setAttribute("aria-pressed", on ? "true" : "false");
    const r = b.querySelector(".rot"); if (r) r.textContent = on ? "Curtido" : "Curtir"; else b.setAttribute("aria-label", on ? "Curtido" : "Curtir");
  });
  const data = iso => { const d = new Date(iso.replace(" ", "T") + "Z"); return d.toLocaleDateString("pt-BR", { day: "numeric", month: "long", year: "numeric" }); };

  const desenha = lista => {
    $(".coms").innerHTML = lista.map(c => `<li><p class="com-quem"><b>${esc(c.nome)}</b> <time>${data(c.criado)}</time></p><p class="com-txt">${esc(c.texto)}</p></li>`).join("");
    $(".coms-vazio").hidden = lista.length > 0;
    $(".coms-n").textContent = lista.length ? `(${lista.length})` : "";
  };
  fetch(`${api}/v1/pagina?p=${encodeURIComponent(p)}`).then(r => r.json()).then(d => {
    num.textContent = d.curtidas; marca(curtidas.has(p)); desenha(d.comentarios || []); sec.classList.add("pronto");
  }).catch(() => { sec.hidden = true; document.querySelectorAll(".barra-lt .curtir, .barra-lt a[href='#comentarios']").forEach(e => e.remove()); });  // serviço fora do ar: a página segue sem a seção

  btns.forEach(b => b.addEventListener("click", async () => {
    const desfazer = curtidas.has(p);
    desfazer ? curtidas.delete(p) : curtidas.add(p);
    guarda.set("pc-curtidas", JSON.stringify([...curtidas]));
    marca(!desfazer); num.textContent = Math.max(0, +num.textContent + (desfazer ? -1 : 1));
    try {
      const r = await fetch(`${api}/v1/curtir`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ p, d: disp, desfazer }) });
      num.textContent = (await r.json()).curtidas;
    } catch { /* sem conexão: fica a contagem otimista */ }
  }));

  // anti-robô: carrega o Turnstile da Cloudflare só quando a pessoa começa a comentar
  const form = $(".com-form"), st = $(".com-st");
  let widget = null, carregado = false;
  const turnstile = () => {
    if (!chave || carregado) return;
    carregado = true;
    window.__pcTs = () => { widget = window.turnstile.render($(".com-ts"), { sitekey: chave, language: "pt-br", theme: "light" }); };
    const s = document.createElement("script");
    s.src = "https://challenges.cloudflare.com/turnstile/v0/api.js?onload=__pcTs&render=explicit";
    s.async = true; document.head.append(s);
  };
  form.addEventListener("focusin", turnstile);
  form.addEventListener("submit", async ev => {
    ev.preventDefault();
    const f = new FormData(form), enviar = form.querySelector("button[type=submit]");
    const corpo = { p, nome: f.get("nome"), email: f.get("email"), texto: f.get("texto"), isca: f.get("site"),
                    turnstile: widget !== null && window.turnstile ? window.turnstile.getResponse(widget) : "" };
    enviar.disabled = true; st.className = "com-st"; st.textContent = "Enviando…";
    try {
      const r = await fetch(`${api}/v1/comentar`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(corpo) });
      const d = await r.json();
      if (!r.ok) throw new Error(d.erro || "Não deu para enviar agora.");
      form.reset(); st.className = "com-st ok";
      st.textContent = "Recebemos o seu comentário! Ele aparece aqui depois da moderação, normalmente em algumas horas.";
    } catch (e) {
      st.className = "com-st erro"; st.textContent = e.message || "Não deu para enviar agora. Tente de novo.";
    } finally {
      enviar.disabled = false;
      if (widget !== null && window.turnstile) window.turnstile.reset(widget);
    }
  });
})();
