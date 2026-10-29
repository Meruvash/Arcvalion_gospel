// Consentimento (LGPD, art. 7º e 8º): só existe quando o portal usa algo opcional (Google Analytics ou AdSense).
// Nada opcional carrega antes da escolha; "Recusar" vale tanto quanto "Aceitar"; a escolha pode ser mudada a qualquer
// momento pelo link "Preferências de privacidade" do rodapé. A escolha fica só neste navegador (localStorage).
(() => {
  const eu = document.currentScript, ga4 = eu.dataset.ga4, adsense = eu.dataset.adsense, politica = eu.dataset.politica;
  const CHAVE = "pc-consentimento", VERSAO = 1;
  const le = () => { try { const c = JSON.parse(localStorage.getItem(CHAVE)); return c && c.v === VERSAO ? c : null; } catch { return null; } };
  const grava = c => { try { localStorage.setItem(CHAVE, JSON.stringify({ ...c, v: VERSAO, data: new Date().toISOString() })); } catch { /* aba anônima */ } };

  // Google Consent Mode v2: tudo negado até a escolha
  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
  gtag("consent", "default", { ad_storage: "denied", ad_user_data: "denied", ad_personalization: "denied", analytics_storage: "denied", wait_for_update: 500 });

  let gaCarregado = false;
  const aplica = c => {
    gtag("consent", "update", { analytics_storage: c.medicao ? "granted" : "denied", ad_storage: c.publicidade ? "granted" : "denied",
      ad_user_data: c.publicidade ? "granted" : "denied", ad_personalization: c.publicidade ? "granted" : "denied" });
    if (ga4 && c.medicao && !gaCarregado) {
      gaCarregado = true;
      const s = document.createElement("script"); s.async = true; s.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(ga4);
      document.head.append(s); gtag("js", new Date()); gtag("config", ga4, { anonymize_ip: true });
    }
    window.__consentimento = c;
    document.dispatchEvent(new CustomEvent("consentimento", { detail: c }));
  };

  const caixa = document.createElement("section");
  caixa.className = "priv"; caixa.hidden = true; caixa.setAttribute("aria-labelledby", "priv-t");
  caixa.innerHTML = `<h2 id="priv-t">Sua privacidade</h2>
<p>Usamos o essencial para o site funcionar. ${ga4 ? "Com a sua permissão, também medimos a audiência com o Google Analytics" : ""}${ga4 && adsense ? " e " : ga4 ? "." : ""}${adsense ? (ga4 ? "" : "Com a sua permissão, ") + "mostramos anúncios do Google, que podem usar cookies." : ""} Veja a <a href="${politica}">Política de Privacidade</a>.</p>
<div class="ops" hidden>${ga4 ? '<label><input type="checkbox" name="medicao"> Medição de audiência (Google Analytics)</label>' : ""}${adsense ? '<label><input type="checkbox" name="publicidade"> Anúncios do Google (cookies de publicidade)</label>' : ""}</div>
<div class="acoes"><button type="button" class="pri" data-a="aceitar">Aceitar</button><button type="button" class="pri" data-a="recusar">Recusar</button><button type="button" data-a="escolher">Escolher</button></div>`;
  document.body.append(caixa);
  const ops = caixa.querySelector(".ops");
  const abre = () => { const c = le() || {}; ops.querySelectorAll("input").forEach(i => { i.checked = !!c[i.name]; }); caixa.hidden = false; caixa.querySelector("button").focus(); };
  caixa.addEventListener("click", ev => {
    const a = ev.target.closest("button")?.dataset.a; if (!a) return;
    if (a === "escolher" && ops.hidden) { ops.hidden = false; ev.target.textContent = "Salvar escolha"; return; }
    const c = a === "aceitar" ? { medicao: !!ga4, publicidade: !!adsense } : a === "recusar" ? { medicao: false, publicidade: false }
      : { medicao: !!ops.querySelector("[name=medicao]")?.checked, publicidade: !!ops.querySelector("[name=publicidade]")?.checked };
    grava(c); caixa.hidden = true; aplica(c);
  });
  document.querySelectorAll(".pref-priv").forEach(b => { b.hidden = false; b.addEventListener("click", abre); });
  const c = le();
  if (c) aplica(c); else caixa.hidden = false;
})();
