// Formulários de newsletter/cadastro e de contato (comercial, eventos, correções). Enviam só para a API do próprio
// portal (worker/), com consentimento explícito; o verificador anti-robô (Turnstile) só é baixado quando a pessoa
// começa a preencher. Sem JavaScript o formulário não envia nada.
(() => {
  const forms = [...document.querySelectorAll(".form-pc:not(.ok)")];
  if (!forms.length) return;
  let carregado = false;
  const filaTs = [];
  const turnstile = (f, chave) => {
    if (!chave || f._w !== undefined) return;
    f._w = null;
    filaTs.push(() => { f._w = window.turnstile.render(f.querySelector(".f-ts"), { sitekey: chave, language: "pt-br", theme: "light" }); });
    if (window.turnstile) { filaTs.splice(0).forEach(fn => fn()); return; }
    if (carregado) return;
    carregado = true;
    window.__pcTsF = () => filaTs.splice(0).forEach(fn => fn());
    const s = document.createElement("script");
    s.src = "https://challenges.cloudflare.com/turnstile/v0/api.js?onload=__pcTsF&render=explicit";
    s.async = true; document.head.append(s);
  };
  // pré-preenche o pedido de correção vindo do link "Peça uma correção" da matéria
  const q = new URLSearchParams(location.search);
  forms.forEach(f => {
    f.classList.add("ok");
    const { api, tipo, origem, turnstile: chave } = f.dataset;
    if (tipo === "correcao" && q.get("url")) { const d = f.querySelector("[name=detalhe]"); if (d) d.value = q.get("url"); }
    f.addEventListener("focusin", () => turnstile(f, chave));
    const st = f.querySelector(".f-st"), bt = f.querySelector("button[type=submit]");
    f.addEventListener("submit", async ev => {
      ev.preventDefault();
      const d = new FormData(f);
      const corpo = { tipo, origem, pagina: location.pathname, nome: d.get("nome") || "", email: d.get("email") || "", isca: d.get("site") || "",
        consentimento: d.get("consentimento") === "on", texto_consentimento: f.querySelector(".consent span").textContent.trim(),
        turnstile: f._w !== null && f._w !== undefined && window.turnstile ? window.turnstile.getResponse(f._w) : "" };
      if (tipo === "newsletter") corpo.editorias = d.getAll("editorias");
      else Object.assign(corpo, { mensagem: d.get("mensagem") || "", empresa: d.get("empresa") || "", detalhe: d.get("detalhe") || "" });
      bt.disabled = true; st.className = "f-st"; st.textContent = "Enviando…";
      try {
        const r = await fetch(`${api}/v1/${tipo === "newsletter" ? "newsletter" : "contato"}`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(corpo) });
        const j = await r.json();
        if (!r.ok) throw new Error(j.erro || "Não deu para enviar agora.");
        f.reset(); st.className = "f-st ok";
        st.textContent = tipo === "newsletter" ? "Inscrição recebida. Obrigado! Você pode cancelar quando quiser." : "Mensagem recebida. Respondemos pelo e-mail informado.";
      } catch (e) {
        st.className = "f-st erro"; st.textContent = e.message || "Não deu para enviar agora. Tente de novo.";
      } finally {
        bt.disabled = false;
        if (f._w !== null && f._w !== undefined && window.turnstile) window.turnstile.reset(f._w);
      }
    });
  });
})();
