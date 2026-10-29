// Espaços publicitários: o espaço já tem a altura reservada no HTML. Este script
// 1) troca o anúncio da casa pelo Google AdSense só depois do consentimento de publicidade (privacidade.js);
// 2) conta, de forma agregada, impressões visíveis (50% do espaço por 1 segundo, padrão IAB) e cliques por espaço,
//    enviando só {espaço, evento, editoria, página} para a API do próprio portal. Nenhum identificador de pessoa.
(() => {
  const espacos = [...document.querySelectorAll(".pub[data-espaco]")];
  if (!espacos.length) return;
  const envia = (el, evento) => {
    const api = el.dataset.api; if (!api) return;
    const corpo = JSON.stringify({ espaco: el.dataset.espaco, evento, ed: el.dataset.ed || "", p: location.pathname, casa: !!el.querySelector("[data-casa]") });
    try { navigator.sendBeacon ? navigator.sendBeacon(`${api}/v1/metricas`, new Blob([corpo], { type: "application/json" }))
      : fetch(`${api}/v1/metricas`, { method: "POST", body: corpo, headers: { "content-type": "application/json" }, keepalive: true }); } catch { /* medição nunca atrapalha a leitura */ }
  };
  const vistos = new WeakSet(), timers = new WeakMap();
  const io = new IntersectionObserver(es => es.forEach(x => {
    if (x.isIntersecting && x.intersectionRatio >= 0.5 && !vistos.has(x.target)) {
      timers.set(x.target, setTimeout(() => { vistos.add(x.target); envia(x.target, "impressao"); io.unobserve(x.target); }, 1000));
    } else clearTimeout(timers.get(x.target));
  }), { threshold: [0, 0.5] });
  espacos.forEach(el => { io.observe(el); el.addEventListener("click", ev => { if (ev.target.closest("a")) envia(el, "clique"); }); });

  let scriptGoogle = false;
  const liga = c => {
    if (!c || !c.publicidade) return;
    espacos.forEach(el => {
      const cliente = el.dataset.cliente, slot = el.dataset.slot;
      if (!cliente || !slot || el.dataset.ligado) return;
      el.dataset.ligado = "1";
      const box = el.querySelector(".pub-in");
      box.innerHTML = `<ins class="adsbygoogle" style="display:block;width:100%;min-height:inherit" data-ad-client="${cliente}" data-ad-slot="${slot}" data-ad-format="auto" data-full-width-responsive="true"></ins>`;
      if (!scriptGoogle) {
        scriptGoogle = true;
        const s = document.createElement("script"); s.async = true; s.crossOrigin = "anonymous";
        s.src = "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=" + encodeURIComponent(cliente);
        document.head.append(s);
      }
      (window.adsbygoogle = window.adsbygoogle || []).push({});
    });
  };
  document.addEventListener("consentimento", ev => liga(ev.detail));
  liga(window.__consentimento);
})();
