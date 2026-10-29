// Busca do site: diálogo aberto pela lupa do cabeçalho, por "/" ou Ctrl+K (o disparador fica em tools/layout.py).
// Só é baixado quando a busca abre; o índice (busca.json, gerado por tools/busca.py) vem junto.
(() => {
  const GRUPOS = [["n", "Notícias"], ["e", "Editorias"], ["p", "Autores"]];
  const POR_GRUPO = 5;
  const norm = t => " " + t.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
  const esc = t => t.replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
  let pre = "", indice = null, carga = null, dlg, q, lista, status, volta, ativo = -1, opcoes = [], abertos = new Set();

  const css = `
.busca-dlg{border:1px solid #e3e0d8;border-radius:14px;padding:0;margin:8vh auto auto;width:min(640px,calc(100% - 24px));max-height:84vh;background:#fff;color:#16202e;font:16px/1.45 "Public Sans",system-ui,sans-serif;box-shadow:0 20px 60px rgba(0,0,0,.3)}
.busca-dlg::backdrop{background:rgba(18,41,74,.55)}
.busca-dlg .bq-topo{display:flex;align-items:center;gap:8px;padding:10px 10px 10px 14px;border-bottom:1px solid #e3e0d8}
.busca-dlg input{flex:1;min-width:0;font:inherit;font-size:16px;padding:10px 6px;border:0;background:transparent;color:inherit;outline:none}
.busca-dlg input::placeholder{color:#5b6573}
.busca-dlg input::-webkit-search-cancel-button{-webkit-appearance:none;appearance:none}
.busca-dlg .bq-x{flex:none;min-width:44px;min-height:44px;border:1px solid #c9c5ba;border-radius:10px;background:none;color:inherit;font:inherit;font-size:.85rem;font-weight:700;cursor:pointer}
.busca-dlg .bq-x:hover{border-color:#12294a}
.busca-dlg .bq-res{overflow-y:auto;max-height:calc(84vh - 70px);padding:6px 6px 10px;overscroll-behavior:contain}
.busca-dlg .bq-st{padding:14px 10px;color:#5b6573;font-size:.92rem}.busca-dlg .bq-st b{color:#16202e}
.busca-dlg .bq-g{font-size:.74rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:#8a6417;padding:12px 10px 4px}
.busca-dlg [role=option]{display:grid;gap:1px;padding:9px 10px;border-radius:8px;cursor:pointer;border-left:3px solid transparent;min-height:44px}
.busca-dlg [role=option] b{font-weight:700}.busca-dlg [role=option] span{font-size:.84rem;color:#5b6573}
.busca-dlg [role=option][aria-selected=true],.busca-dlg [role=option]:hover{background:#f1efe9;border-left-color:#12294a}
.busca-dlg .bq-mais{color:#1d4f91;font-weight:700;font-size:.9rem}
.busca-dlg .sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
@media (max-width:599px){.busca-dlg{margin:0;width:100%;max-width:none;max-height:100dvh;height:100dvh;border-radius:0;border:0}.busca-dlg .bq-res{max-height:calc(100dvh - 70px)}}`;

  function monta() {
    const st = document.createElement("style"); st.textContent = css; document.head.append(st);
    dlg = document.createElement("dialog");
    dlg.className = "busca-dlg";
    dlg.setAttribute("aria-modal", "true");
    dlg.setAttribute("aria-labelledby", "bq-titulo");
    dlg.innerHTML = `<h2 id="bq-titulo" class="sr">Buscar no site</h2>
<div class="bq-topo"><label for="bq-q" class="sr">Buscar notícias, editorias e autores</label>
<input id="bq-q" type="search" role="combobox" aria-expanded="false" aria-controls="bq-lista" aria-autocomplete="list" autocomplete="off" enterkeyhint="go" placeholder="Assunto, nome ou palavra-chave">
<button type="button" class="bq-x">Fechar</button></div>
<div class="bq-res"><p class="bq-st" role="status"></p><div id="bq-lista" role="listbox" aria-label="Resultados"></div></div>`;
    document.body.append(dlg);
    q = dlg.querySelector("input"); lista = dlg.querySelector("#bq-lista"); status = dlg.querySelector(".bq-st");
    dlg.querySelector(".bq-x").addEventListener("click", () => dlg.close());
    dlg.addEventListener("close", () => { if (volta && volta.focus) volta.focus(); });
    dlg.addEventListener("click", ev => { if (ev.target === dlg) dlg.close(); });
    q.addEventListener("input", () => { abertos.clear(); busca(); });
    q.addEventListener("keydown", tecla);
    lista.addEventListener("click", ev => { const o = ev.target.closest("[role=option]"); if (o) escolhe(o); });
  }

  function carrega() {
    carga = carga || fetch(pre + "busca.json").then(r => { if (!r.ok) throw r; return r.json(); }).then(regs => {
      indice = regs.map(x => ({ ...x, k: norm(`${x.n} ${x.s} ${x.a || ""}`), kn: norm(x.n) }));
    });
    return carga;
  }

  function busca() {
    const texto = q.value.trim(), termos = norm(texto).trim().split(" ").filter(Boolean);
    lista.innerHTML = ""; opcoes = []; ativo = -1; q.removeAttribute("aria-activedescendant");
    if (!indice) { status.textContent = "Carregando a busca…"; return; }
    if (norm(texto).length < 3) {
      status.textContent = "Digite pelo menos três letras: assunto, nome de pessoa, igreja ou palavra-chave.";
      q.setAttribute("aria-expanded", "false"); return;
    }
    const frase = norm(texto);
    const achados = indice.filter(x => termos.every(t => x.k.includes(" " + t))).map((x, i) => ({
      x, i, p: x.kn.startsWith(frase) ? 0 : termos.every(t => x.kn.includes(" " + t)) ? 1 : 2,
    }));
    let html = "", total = 0;
    for (const [t, rotulo] of GRUPOS) {
      const g = achados.filter(a => a.x.t === t).sort((a, b) => a.p - b.p || a.i - b.i);
      if (!g.length) continue;
      total += g.length;
      const mostra = abertos.has(t) ? g : g.slice(0, POR_GRUPO);
      html += `<div role="group" aria-labelledby="bq-g-${t}"><div class="bq-g" id="bq-g-${t}" role="presentation">${rotulo} (${g.length})</div>`;
      mostra.forEach(({ x }) => {
        const id = "bq-o" + opcoes.length; opcoes.push(x);
        html += `<div role="option" id="${id}" aria-selected="false" data-u="${esc(x.u)}"><b>${esc(x.n)}</b><span>${esc(x.s)}</span></div>`;
      });
      if (mostra.length < g.length) {
        const id = "bq-o" + opcoes.length; opcoes.push(null);
        html += `<div role="option" id="${id}" aria-selected="false" data-mais="${t}" class="bq-mais">Ver os ${g.length} resultados em ${rotulo}</div>`;
      }
      html += "</div>";
    }
    lista.innerHTML = html;
    q.setAttribute("aria-expanded", total ? "true" : "false");
    status.innerHTML = total ? `${total} resultado${total > 1 ? "s" : ""}. Use as setas e Enter.`
      : `Nada encontrado para <b>${esc(texto)}</b>. Tente uma palavra só, ou um sinônimo.`;
  }

  function marca(i) {
    const os = lista.querySelectorAll("[role=option]");
    if (!os.length) return;
    ativo = (i + os.length) % os.length;
    os.forEach((o, k) => o.setAttribute("aria-selected", k === ativo ? "true" : "false"));
    q.setAttribute("aria-activedescendant", os[ativo].id);
    os[ativo].scrollIntoView({ block: "nearest" });
  }

  function escolhe(o) {
    if (o.dataset.mais) { abertos.add(o.dataset.mais); busca(); q.focus(); return; }
    const destino = new URL(pre + o.dataset.u, location.href);
    const mesma = destino.pathname === location.pathname && destino.search === location.search;
    location.href = destino.href;
    if (mesma) dlg.close();
  }

  function tecla(ev) {
    // num campo type=search o Esc só apagaria o texto: aqui ele sempre fecha a busca
    if (ev.key === "Escape") { ev.preventDefault(); dlg.close(); }
    else if (ev.key === "ArrowDown") { ev.preventDefault(); marca(ativo + 1); }
    else if (ev.key === "ArrowUp") { ev.preventDefault(); marca(ativo - 1); }
    else if (ev.key === "Enter") {
      ev.preventDefault();
      const os = lista.querySelectorAll("[role=option]");
      if (os.length) escolhe(os[Math.max(ativo, 0)]);
    }
  }

  window.abrirBusca = p => {
    pre = p;
    if (!dlg) monta();
    if (!dlg.open) { volta = document.activeElement; dlg.showModal(); }
    q.focus(); q.select();
    busca();
    if (!indice) carrega().then(busca, () => { status.textContent = "Não foi possível carregar a busca. Verifique a conexão e tente de novo."; carga = null; });
  };
})();
