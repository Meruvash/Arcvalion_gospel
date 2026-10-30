// Busca do site: diálogo aberto pela lupa do cabeçalho, por "/" ou Ctrl+K (o disparador fica em tools/layout.py).
// Só é baixado quando a busca abre; o índice (busca.json, gerado por tools/busca.py) vem junto.
(() => {
  const GRUPOS = [["r", "Resenhas"], ["n", "Notícias"], ["g", "Livros da Bíblia"], ["l", "Lançamentos do ano"]];
  const POR_GRUPO = 5;
  const norm = t => " " + t.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
  const esc = t => t.replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
  let pre = "", indice = null, carga = null, dlg, q, lista, status, volta, ativo = -1, opcoes = [], abertos = new Set();

  // Barra fina e translúcida no topo: a página continua à vista por baixo (sem véu escuro nem tela cheia no celular).
  // Os resultados só aparecem a partir de 3 letras, num painel do mesmo vidro, um pouco mais opaco para a leitura.
  const css = `
.busca-dlg{border:0;padding:0;margin:10px auto auto;width:min(560px,calc(100% - 16px));max-height:calc(100dvh - 20px);background:none;color:#fff;overflow:visible;font:16px/1.45 "Public Sans",system-ui,sans-serif}
.busca-dlg[open]{display:grid;gap:6px;align-content:start}
.busca-dlg::backdrop{background:transparent}
.busca-dlg .bq-topo,.busca-dlg .bq-res{background:rgba(2,22,40,.62);border:1px solid rgba(255,255,255,.2);-webkit-backdrop-filter:blur(14px) saturate(140%);backdrop-filter:blur(14px) saturate(140%);box-shadow:0 6px 24px rgba(0,0,0,.25)}
.busca-dlg .bq-topo{display:flex;align-items:center;gap:6px;padding:2px 2px 2px 14px;border-radius:999px}
.busca-dlg .bq-topo svg{flex:none;width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;opacity:.8}
.busca-dlg input{flex:1;min-width:0;font:inherit;font-size:16px;padding:8px 4px;border:0;background:transparent;color:inherit;outline:none}
.busca-dlg input::placeholder{color:rgba(255,255,255,.72)}
.busca-dlg input::-webkit-search-cancel-button{-webkit-appearance:none;appearance:none}
.busca-dlg .bq-topo:focus-within{border-color:rgba(227,178,60,.8)}
.busca-dlg .bq-x{flex:none;display:grid;place-items:center;width:40px;height:40px;padding:0;border:0;border-radius:50%;background:none;color:inherit;cursor:pointer}
.busca-dlg .bq-x:hover,.busca-dlg .bq-x:focus-visible{background:rgba(255,255,255,.14);color:#e3b23c}
.busca-dlg .bq-res{background:rgba(2,22,40,.86);border-radius:14px;overflow-y:auto;max-height:min(60vh,440px);padding:4px 6px 8px;overscroll-behavior:contain}
.busca-dlg.vazio .bq-res{position:absolute;width:1px;height:1px;padding:0;border:0;overflow:hidden;clip-path:inset(50%)}
.busca-dlg .bq-st{margin:0;padding:10px 10px 4px;color:#c3cad4;font-size:.86rem}.busca-dlg .bq-st b{color:#fff}
.busca-dlg .bq-g{font-size:.72rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:#e3b23c;padding:10px 10px 4px}
.busca-dlg [role=option]{display:grid;gap:1px;padding:8px 10px;border-radius:8px;cursor:pointer;border-left:3px solid transparent;min-height:44px}
.busca-dlg [role=option] b{font-weight:700}.busca-dlg [role=option] span{font-size:.84rem;color:#c3cad4}
.busca-dlg [role=option] i{font-style:normal;font-size:.72rem;font-weight:800;color:#5fd18f;margin-left:6px}
.busca-dlg [role=option][aria-selected=true],.busca-dlg [role=option]:hover{background:rgba(255,255,255,.1);border-left-color:#e3b23c}
.busca-dlg .bq-mais{color:#8cb8ff;font-weight:700;font-size:.9rem}
.busca-dlg .sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
@supports not ((backdrop-filter:blur(1px)) or (-webkit-backdrop-filter:blur(1px))){.busca-dlg .bq-topo{background:rgba(2,22,40,.88)}.busca-dlg .bq-res{background:rgba(2,22,40,.96)}}
@media (prefers-reduced-transparency:reduce){.busca-dlg .bq-topo,.busca-dlg .bq-res{background:#0f2242;-webkit-backdrop-filter:none;backdrop-filter:none}}`;

  function monta() {
    const st = document.createElement("style"); st.textContent = css; document.head.append(st);
    dlg = document.createElement("dialog");
    dlg.className = "busca-dlg";
    dlg.setAttribute("aria-modal", "true");
    dlg.setAttribute("aria-labelledby", "bq-titulo");
    dlg.innerHTML = `<h2 id="bq-titulo" class="sr">Buscar no site</h2>
<div class="bq-topo"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg><label for="bq-q" class="sr">Buscar notícias e livros da Bíblia</label>
<input id="bq-q" type="search" role="combobox" aria-expanded="false" aria-controls="bq-lista" aria-autocomplete="list" autocomplete="off" enterkeyhint="go" placeholder="Buscar notícia ou livro da Bíblia">
<button type="button" class="bq-x" aria-label="Fechar a busca"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button></div>
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
    dlg.classList.toggle("vazio", norm(texto).length < 3);
    if (!indice) { status.textContent = "Carregando a busca…"; return; }
    if (norm(texto).length < 3) {
      status.textContent = "Digite ao menos 3 letras.";
      q.setAttribute("aria-expanded", "false"); return;
    }
    const frase = norm(texto);
    const achados = indice.filter(x => termos.every(t => x.k.includes(" " + t))).map((x, i) => ({
      x, i, p: x.kn.startsWith(frase) ? 0 : termos.every(t => x.kn.includes(" " + t)) ? 1 : 2,
    }));
    let html = "", total = 0;
    for (const [t, rotulo] of GRUPOS) {
      const g = achados.filter(a => a.x.t === t).sort((a, b) => a.p - b.p || !!b.x.r - !!a.x.r || a.i - b.i);
      if (!g.length) continue;
      total += g.length;
      const mostra = abertos.has(t) ? g : g.slice(0, POR_GRUPO);
      html += `<div role="group" aria-labelledby="bq-g-${t}"><div class="bq-g" id="bq-g-${t}" role="presentation">${rotulo} (${g.length})</div>`;
      mostra.forEach(({ x }) => {
        const id = "bq-o" + opcoes.length; opcoes.push(x);
        html += `<div role="option" id="${id}" aria-selected="false" data-u="${esc(x.u)}"><b>${esc(x.n)}${x.r && t !== "r" ? "<i>tem resenha</i>" : ""}</b><span>${esc(x.s)}</span></div>`;
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
      : `Nada encontrado para <b>${esc(texto)}</b>. Tente uma palavra só (por exemplo, “reforma” ou “romanos”).`;
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
    if (mesma) location.reload();  // só a âncora muda (#j123 em /lancamentos/): recarrega para a página abrir a ficha
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
