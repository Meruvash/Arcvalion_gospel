"""Estudos bíblicos: página de cada estudo e lista com filtros. O equivalente das resenhas do Elite Boardgamers.

A página é o layout v2 da resenha (tools/build_review.py do Elite) com as seções traduzidas:
  Resumo em 30 segundos        → Resumo em 30 segundos (o que o texto ensina, leituras equivocadas, nível, tempo)
  Como funciona (passos)       → Estrutura do texto (as partes da passagem, com referência)
  Como é jogar (faixa + citação) → Para a vida hoje (versículo-chave em destaque)
  O que funciona / Atenção     → O que o texto ensina / Leituras equivocadas (cartões com "Por quê?")
  Para quem é (barras, tiles)  → Para quem é (perfil do estudo, formatos: sozinho, em família, em grupo)
  Edição nacional e preço      → Traduções para ler / Passagens relacionadas
  Se você gosta de…            → Continue estudando
  Veredito                     → Para guardar
  Prêmios / Ficha técnica      → Versículos-chave / Ficha do livro
A lista é a de resenhas (tools/build_lista.py), com a mesma gaveta de filtros e o estado na URL.
"""
import html
import json
import sys

import portal
import seo
import imagens
import estilo_elite as est
from pagina import data_longa, e, escrever, pagina, capa_secao, quando
from layout import (barra_leitura, cabecalho, convite_compartilhar, icone, instagram, arroba, whatsapp, interacoes, rodape, trilha)
from estudos.checar_estudo import NIVEIS, problemas

SELO_CLASSE = {"Ótimo para começar": "", "Ideal para grupos": "grupo", "Para aprofundar": "fundo"}
NIV_PONTOS = {1: "Iniciante", 2: "Intermediário", 3: "Aprofundado"}
CSS_ESTUDO_EXTRA = (".selo.grupo{background:#1f5fae}.selo.fundo{background:#6b4ea3}.nivel.grupo{color:#8cb8ff}.nivel.fundo{color:#c9b3ff}"
                    ".nota.sigla{background:var(--n7);font-size:1.1rem}.vc{font-size:.85rem;color:var(--gold);margin-top:6px}")


def estudos(incluir_revisao=False):
    cs, ruins = [], {}
    for p in sorted((portal.CONTEUDO / "estudos").glob("*.json")):
        c = json.loads(p.read_text(encoding="utf-8"))
        st = c.get("status", "rascunho")
        if st == "publicado" or (incluir_revisao and st == "revisao"):
            erros = problemas(c, publicar=st == "publicado")
            if erros:
                ruins[c["slug"]] = erros
            c.setdefault("publicado_em", None)
            cs.append(c)
    if ruins:
        sys.exit("Estudos fora do padrão (rode python3 tools/estudos/checar_estudo.py):\n" + "\n".join(f" - {s}: {'; '.join(x)}" for s, x in ruins.items()))
    return sorted(cs, key=lambda c: c.get("publicado_em") or "", reverse=True)


def sev_class(s):
    s = s.lower()
    return "grave" if "grave" in s else ("leve" if "leve" in s else "moderada")


def texto_cp(c):
    return f"{c['titulo']}: {c['tagline']} Estudo bíblico do {portal.NOME}"


def faq_estudo(c):
    """Perguntas frequentes que saem só de campos publicados (mesma regra do faq.py do Elite)."""
    p = [(f"O que {c['passagem']} ensina?", f"{c['tagline']} {c['veredito']}")]
    autor = next((v for k, v in c.get("ficha", []) if k.lower() == "autor"), None)
    livro = next((v for k, v in c.get("ficha", []) if k.lower() == "livro"), None)
    if livro:
        p.append((f"Onde fica {c['titulo']} na Bíblia?", f"Em {c['passagem']}, no livro de {livro} ({c['testamento']})."))
    if autor:
        p.append((f"Quem escreveu {livro or c['passagem']}?", f"{autor}."))
    v = c["versiculo_chave"]
    p.append((f"Qual é o versículo-chave de {c['titulo']}?", f"{v['referencia']}: “{v['texto']}” ({v['traducao']})."))
    p.append((f"Quanto tempo leva este estudo?", f"Cerca de {c['tempo_min']} minutos, no nível {NIVEIS[c['nivel']].lower()}."))
    return p


def secao_faq(perguntas):
    itens = "".join(f"<details><summary><h3>{e(q)}</h3></summary><p>{e(r)}</p></details>" for q, r in perguntas)
    return f'<section class="bloco claro faq" id="perguntas"><h2>Perguntas frequentes</h2>{itens}</section>'


def foto_html(c, pre, classe="foto capa foto-capa", lazy=False):
    im = c["imagem"]
    w, h = imagens.dimensoes(im["arquivo"]) or (1200, 800)
    return (f'<figure class="{classe}"><img src="{pre}{imagens.publicar(im["arquivo"])}" srcset="{imagens.srcset(im["arquivo"], pre)}" '
            f'sizes="(min-width: 860px) 420px, calc(100vw - 32px)" width="{w}" height="{h}" alt="{e(im["alt"])}"'
            f'{" loading=lazy" if lazy else " fetchpriority=high"}><figcaption>{e(im["credito"])}</figcaption></figure>')


def mais_estudos(c, todos, n=6):
    cards = []
    for o in todos:
        if o["slug"] == c["slug"] or o.get("status") != "publicado":
            continue
        cards.append(f'<li><a href="../{o["slug"]}/"><img src="{imagens.miniatura(o["imagem"]["arquivo"], "../../", 400)}" width="800" height="800" alt="" loading="lazy">'
                     f'<b>{e(o["titulo"])}</b><span class="selo {SELO_CLASSE.get(o["selo"], "")}">{e(o["selo"])}</span></a></li>')
        if len(cards) == n:
            break
    if not cards:
        return ""
    total = sum(1 for o in todos if o.get("status") == "publicado")
    return (f'<section class="bloco claro mais-res" id="mais-estudos"><h2>Continue lendo</h2><p class="sub">Outros estudos bíblicos do {e(portal.NOME)}.</p>'
            f'<ul>{"".join(cards)}</ul><a class="ver-todas" href="../">Ver todos os {total} estudos</a></section>')


def noticias_relacionadas(c, ns, n=5):
    lista = [x for x in ns if x.get("status", "publicado") == "publicado" and any(j.get("estudo") == c["slug"] for j in x.get("estudos", []))]
    if not lista:
        return ""
    itens = "".join(f'<li><time datetime="{x["data"]}">{data_longa(x["data"])}</time><a href="../../noticias/{x["slug"]}/">{e(x["titulo"])}</a></li>' for x in lista[:n])
    return f'<section class="bloco claro nj" id="noticias-do-estudo"><h2>Notícias relacionadas</h2><ul>{itens}</ul></section>'


def build_estudo(c, todos, ns, previa=False):
    slug = c["slug"]
    base = f"previa/estudos/{slug}/" if previa else f"estudos/{slug}/"
    pre = "../../../" if previa else "../../"
    url = f"{portal.SITE}/estudos/{slug}/"
    pf = lambda t: f'<li>{icone("ok", "ic ok")}<span>{e(t)}</span></li>'  # noqa: E731
    pn = lambda t: f'<li>{icone("nao", "ic no")}<span>{e(t)}</span></li>'  # noqa: E731
    nivel = c["nivel"]
    medidor = (f'<div class="medidor"><span class="m-k">Nível</span><span class="m-bar" role="img" aria-label="Nível {nivel} de 3">'
               f'<i style="width:{nivel / 3 * 100:.0f}%"></i></span><b>{NIVEIS[nivel]}</b></div>')
    v = c["versiculo_chave"]
    resumo = f"""<section class="bloco r30" id="resumo">
   <h2 class="kick">Resumo em 30 segundos</h2>
   <div class="r30-grid">
    <div><h3>O que o texto ensina</h3><ul class="mini">{"".join(pf(t) for t, _ in c["destaques"][:3])}</ul></div>
    <div><h3>Cuidado com</h3><ul class="mini">{"".join(pn(t) for _, t, _ in c["atencao"][:3])}</ul></div>
   </div>
   <div class="r30-pe">{medidor}<div class="r30-preco">{icone("relogio")}<span><b>{c["tempo_min"]} minutos</b> de leitura e estudo</span></div></div>
   <p class="r30-premio"><span class="med" aria-hidden="true"></span><span><b>{e(v["referencia"])}</b>: “{e(v["texto"])}”</span></p>
   <p class="r30-quem"><b>Para quem:</b> {e("; ".join(x[0].lower() + x[1:] for x in c["para_quem"][:2]))}.</p>
  </section>"""
    passos = "".join(f'<li><span class="n">{i}</span><div><h3>{e(t)}</h3><p>{e(x)}</p></div></li>' for i, (t, x) in enumerate(c["estrutura"], 1))
    estrutura = f"""<section class="bloco claro" id="estrutura"><h2>Estrutura de {e(c["passagem"])}</h2>
   {f'<p class="sub">{e(c["estrutura_resumo"])}</p>' if c.get("estrutura_resumo") else ""}
   <ol class="passos">{passos}</ol>
   <details class="mais"><summary>Ler o contexto completo</summary><div class="leitura">{"".join(f"<p>{e(x)}</p>" for x in c["contexto"])}</div></details>
  </section>"""
    aplic = c.get("aplicacao") or []
    vida = f"""<section class="bloco faixa" id="para-a-vida"><h2>Para a vida hoje</h2>
   <blockquote class="cit"><p>“{e(v["texto"])}”</p><cite>{e(v["referencia"])} · {e(v["traducao"])}</cite></blockquote>
   {f'<div class="leitura"><p>{e(aplic[0])}</p></div>' if aplic else ""}
   {f'<details class="mais"><summary>Continuar lendo</summary><div class="leitura">{"".join(f"<p>{e(x)}</p>" for x in aplic[1:])}</div></details>' if len(aplic) > 1 else ""}
  </section>"""

    def cartao(classe, ic, titulo, texto, sev=""):
        return (f'<li class="pcc {classe}">{icone(ic, "ic " + classe)}<details><summary><h3>{e(titulo)}{sev}</h3><span class="lm">Por quê?</span></summary>'
                f"<p>{e(texto)}</p></details></li>")
    pros = "".join(cartao("ok", "ok", t, x) for t, x in c["destaques"])
    contras = "".join(cartao("no", "nao", t, x, f' <span class="sev {sev_class(sv)}">{e(sv)}</span>') for sv, t, x in c["atencao"])
    pc = f"""<section class="bloco claro pc2" id="ensinos">
   <div><h2>O que o texto ensina</h2><ul>{pros}</ul></div>
   <div><h2>Leituras equivocadas</h2><ul>{contras}</ul></div>
  </section>"""
    barras = "".join(f'<li><span>{e(k)}</span><span class="bar" role="img" aria-label="{n} de 5"><i style="width:{n * 20}%"></i></span><b>{n}</b></li>' for k, n in c.get("perfil", []))
    tiles = "".join(f'<li><span class="tn">{e(nj)}</span><span class="pontos" role="img" aria-label="{NIV_PONTOS.get(nv, "")}">'
                    + "".join(f'<i class="{"on" if k < nv else ""}"></i>' for k in range(3))
                    + f'</span><b class="nv">{["", "Possível", "Bom", "Ótimo"][nv]}</b><p>{e(x)}</p></li>' for nj, x, nv in c.get("formatos", []))
    quem = f"""<section class="bloco claro" id="para-quem"><h2>Para quem é</h2>
   {f'<h3 class="h3s">Perfil do estudo</h3><ul class="barras">{barras}</ul>' if barras else ""}
   {f'<h3 class="h3s">Como estudar</h3><ul class="tiles" aria-hidden="true">{tiles}</ul><ul class="tiles-txt">{"".join(f"<li><b>{e(nj)}:</b> {e(x)}</li>" for nj, x, nv in c.get("formatos", []))}</ul>' if tiles else ""}
   <div class="quem quem2">
    <div><h3 class="h3s">É para você se…</h3><ul>{"".join(f"<li>{e(x)}</li>" for x in c["para_quem"])}</ul></div>
    {f'<div class="nao"><h3 class="h3s">Talvez não seja o momento se…</h3><ul>{"".join(f"<li>{e(x)}</li>" for x in c["nao_e_para"])}</ul></div>' if c.get("nao_e_para") else ""}
   </div>
   {f'<details class="dica"><summary>{icone("dica")}<b>Dica para começar</b></summary><p>{e(c["dica"])}</p></details>' if c.get("dica") else ""}
  </section>"""
    traducoes = f"""<section class="bloco claro duo" id="traducoes">
   <div class="preco-card"><h2>Traduções para ler</h2><p>{e(c.get("traducoes", ""))}</p></div>
   <details class="mais dobra" open><summary><h2>Passagens relacionadas</h2></summary><p>{e(c.get("relacionadas", ""))}</p></details>
  </section>""" if c.get("traducoes") or c.get("relacionadas") else ""
    comp = "".join(
        (f'<li><a class="cc" href="../{sl}/"><img src="{imagens.miniatura(next(o for o in todos if o["slug"] == sl)["imagem"]["arquivo"], pre, 160)}" width="800" height="800" alt="" loading="lazy">'
         f'<span><b>{e(j)}</b><span>{e(x)}</span><span class="vr">Ler o estudo →</span></span></a></li>')
        if sl and any(o["slug"] == sl and o.get("status") == "publicado" for o in todos)
        else f'<li><div class="cc"><span class="cc-ph" aria-hidden="true">{e(j[0])}</span><span><b>{e(j)}</b><span>{e(x)}</span></span></div></li>'
        for j, sl, x in c.get("comparacoes", []))
    compara = f'<section class="bloco claro" id="continue"><h2>Continue estudando</h2><ul class="cards">{comp}</ul></section>' if comp else ""
    sc = SELO_CLASSE.get(c["selo"], "")
    veredito = f"""<section class="bloco fecho" id="para-guardar">
   <h2>Para guardar: {e(c["titulo"])}</h2>
   <span class="selo {sc}">{e(c["selo"])}</span>
   <p>{e(c["veredito"])}</p>
   <p class="tagline">{e(c["tagline"])}</p>
  </section>
  {convite_compartilhar(texto_cp(c), url, "Conhece alguém que vai gostar deste estudo?", "Mande para o seu grupo, célula ou família.", "bloco claro")}
  {interacoes(pre, f"/estudos/{slug}/", "bloco claro")}"""
    acoes = ((f'<a class="zap" href="{whatsapp()}" target="_blank" rel="noopener">{icone("zap", "ic zi")}<span><b>Entrar no grupo do WhatsApp</b></span></a>' if whatsapp() else "")
             + (f'<a class="ig-btn" href="{instagram()}" target="_blank" rel="noopener">{icone("insta")}<span>Seguir {arroba()}</span></a>' if instagram() else "")
             + f'<a class="ig-btn" href="{pre}newsletter/">{icone("email")}<span>Receber a newsletter</span></a>')
    comunidade = (f'<section class="bloco comunidade"><h2>Gostou do estudo?</h2><p>O {e(portal.NOME)} publica estudos bíblicos e notícias com fonte. '
                  f'Entre no grupo e acompanhe as próximas publicações.</p><div class="acoes">{acoes}</div></section>')
    fontes = "".join(f'<li><a href="{e(u)}" target="_blank" rel="noopener">{e(n)}</a> <span>{e(uso)}</span></li>' for n, u, uso in c["fontes"])
    fontes_bloco = (f'<section class="bloco claro fontes" id="fontes"><details class="mais"><summary><h2>Fontes ({len(c["fontes"])})</h2></summary><ul>{fontes}</ul>'
                    f'<p class="note">Consulta às fontes em {e(c.get("consulta", ""))}.</p></details></section>')
    chave = "".join(f'<li class="pr win"><span class="pr-m" aria-hidden="true"></span><span class="pr-t"><b>{e(r)}</b><span>{e(t)}</span></span></li>'
                    for r, t in c.get("versiculos", []))
    versiculos = (f'<section class="bloco claro" id="versiculos"><details class="mais dobra" open><summary><h2>Versículos-chave</h2> '
                  f'<span class="resumo">{len(c["versiculos"])} passagens para memorizar</span></summary><ul>{chave}</ul></details></section>') if chave else ""
    ficha = "".join(f'<div><dt>{e(k)}</dt><dd{" class=na" if "não confirmad" in vv.lower() else ""}>{e(vv)}</dd></div>' for k, vv in c.get("ficha", []))
    zap_meio = (f'<a class="zap zap-meio" href="{whatsapp()}" target="_blank" rel="noopener">{icone("zap", "ic zi")}<span><b>Entre no grupo do WhatsApp</b>'
                f'<small>Converse sobre {e(c["titulo"])} e receba os próximos estudos</small></span></a>') if whatsapp() else ""
    leg = c.get("legenda", "")
    legenda = (f'<section class="bloco info-meio" id="legenda-ig"><h2>Legenda para o Instagram</h2><div class="post"><button type="button" class="post-btn" id="b-legenda" aria-expanded="false" aria-controls="legenda">{icone("copiar")}Legenda</button></div>'
               f'<div class="legenda" id="legenda" hidden><p class="leg-st" role="status"></p><div class="leg-txt" id="leg-txt" tabindex="0" aria-label="Legenda para o Instagram">{e(leg)}</div>'
               f'<div class="leg-acoes"><button type="button" class="post-btn" id="b-copiar">{icone("copiar")}Copiar de novo</button>'
               f'<button type="button" class="post-btn" id="b-compartilhar" hidden>{icone("compartilhar")}Compartilhar legenda</button></div>'
               f'<p class="leg-dica">Não colou? Toque em “Compartilhar legenda” e escolha “Copiar”, ou segure o dedo no texto acima.</p></div></section>') if leg else ""
    perguntas = faq_estudo(c)
    abas = "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in (("resumo", "Resumo"), ("estrutura", "Estrutura"), ("para-a-vida", "Para a vida"), ("ensinos", "Ensinos"),
                                                                    ("para-quem", "Para quem é"), *((("traducoes", "Traduções"),) if traducoes else ()),
                                                                    ("para-guardar", "Para guardar"), ("mais-estudos", "Mais estudos"), ("ficha", "Ficha")))
    main = f"""<main id="conteudo" class="v2" style="--acc:{e(c.get("cor", "#e3b23c"))}">
 <div class="col">
  {resumo}
  {estrutura}
  {vida}
  {pc}
  {zap_meio}
  {legenda}
  {quem}
  {traducoes}
  {compara}
  {veredito}
  {noticias_relacionadas(c, ns)}{mais_estudos(c, todos)}
  {comunidade}
  {secao_faq(perguntas)}
  {fontes_bloco}
 </div>
 <aside>
  {versiculos}
  <section class="bloco claro" id="ficha"><details class="mais dobra" open><summary><h2>Ficha do livro</h2></summary><dl>{ficha}</dl>{f'<p class="note">{e(c["nota_ficha"])}</p>' if c.get("nota_ficha") else ""}</details></section>
 </aside>
</main>
<div class="progresso" aria-hidden="true"><i></i></div>
<a class="voltar-topo" href="#topo" aria-label="Voltar ao topo">{icone("topo")}</a>"""
    regua = [("livro", c["passagem"], "Passagem"), ("relogio", f'{c["tempo_min"]} min', "Leitura e estudo"), ("nivel", NIVEIS[nivel], "Nível"),
             ("grupo", max(c.get("formatos", [["Sozinho", "", 1]]), key=lambda f: f[2])[0], "Melhor formato")]
    regua_html = "".join(f'<li>{icone(n)}<span class="r-v">{e(vv)}</span><span class="r-k">{k}</span></li>' for n, vv, k in regua)
    pub = (f'<p class="pub">Estudo publicado em <time datetime="{c["publicado_em"]}">{data_longa(c["publicado_em"])}</time> · Redação {e(portal.NOME)} · '
           f'com base em <a href="#fontes">{len(c["fontes"])} fontes</a></p>') if c.get("publicado_em") else ""
    aviso = ('<div class="previa-aviso" role="note"><b>Prévia em revisão.</b> Este estudo ainda não foi publicado.</div>') if previa else ""
    css = (est.CSS_ESTUDO.replace("url(../fontes/", f"url({pre}fontes/") + est.CSS_FAQ + CSS_ESTUDO_EXTRA)
    corpo = f"""{aviso}<a class="skip" href="#conteudo">Pular para o conteúdo</a>
{cabecalho(pre, "Estudos bíblicos", sub=True)}

<section class="jogo"><div class="in">
 {trilha(("Início", pre), ("Estudos bíblicos", f"{pre}estudos/"), (e(c["titulo"]), ""))}
 {foto_html(c, pre)}
 <div>
  <div class="topo">
   <h1>{e(c["titulo"])}</h1>
   <div class="nota-box"><div class="nota sigla" role="img" aria-label="{e(c["passagem"])}"><span>{e(c.get("sigla", c["passagem"][:2]))}</span></div><p class="nota-k">{e(c["testamento"].split()[0])} Test.</p></div>
   <p class="linha">{e(c["passagem"])} · {e(c["genero"])}</p>
  </div>
  <div class="veredito"><span class="selo {sc}">{e(c["selo"])}</span><p>{e(c["tagline"])}</p><p class="nivel {sc or "sim"}">Nível: {NIVEIS[nivel]}</p></div>
  <ul class="regua">{regua_html}</ul>
  <p class="lede">{e(c["lede"])}</p>
  {pub}
 </div>
</div>
</section>
<nav class="abas" aria-label="Seções do estudo"><ul>
<li class="li-volta"><a class="volta" href="{pre}estudos/">{icone("voltar")}Estudos</a></li>
{abas}
</ul></nav>

{main}

{rodape(pre, barra_leitura(texto_cp(c), url))}
<script>{JS_ESTUDO}</script>"""
    img = f"{portal.SITE}/{imagens.publicar(c['imagem']['arquivo'])}"
    nos = [{"@type": "Article", "@id": f"{url}#artigo", "mainEntityOfPage": url, "headline": c["titulo"], "description": c["descricao"], "image": [img],
            "datePublished": c.get("publicado_em") or "", "author": [seo.pessoa(c.get("autor", ""))], "publisher": {"@id": seo.org_id()}, "inLanguage": "pt-BR",
            "about": {"@type": "CreativeWork", "name": c["passagem"], "isPartOf": {"@type": "Book", "name": "Bíblia"}}},
           seo.faq([{"pergunta": q, "resposta": r} for q, r in perguntas]),
           seo.trilha(("Início", f"{portal.SITE}/"), ("Estudos bíblicos", f"{portal.SITE}/estudos/"), (c["titulo"], url))]
    import og
    titulo = c.get("titulo_busca") or f"{c['titulo']}: estudo bíblico de {c['passagem']}"
    titulo = titulo if len(titulo) > 42 else f"{titulo} | {portal.NOME}"
    escrever(f"{base}index.html", pagina(titulo, c["descricao"], url if not previa else "", og.url_cartao(f"estudo-{slug}") or img, pre, corpo, "article",
                                         jsonld=seo.script(*nos), css=css, indexavel=not previa))


# menu de seções, barra de progresso, voltar ao topo e legenda: os scripts da resenha do Elite, sem o "Salvar na galeria"
JS_ESTUDO = """(() => {
  const links = [...document.querySelectorAll(".abas a[href^='#']")];
  const alvo = new Map(links.map(a => [a.getAttribute("href").slice(1), a]));
  if ("IntersectionObserver" in window && links.length) {
    const obs = new IntersectionObserver(ents => {
      ents.forEach(en => {
        if (!en.isIntersecting) return;
        links.forEach(l => l.classList.remove("ativo"));
        const l = alvo.get(en.target.id);
        if (l) { l.classList.add("ativo"); const ul = l.closest("ul"); ul.scrollTo({ left: l.parentElement.offsetLeft - ul.clientWidth / 2 + l.parentElement.clientWidth / 2 }); }
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    alvo.forEach((_, id) => { const s = document.getElementById(id); if (s) obs.observe(s); });
  }
  if (innerWidth < 860) document.querySelectorAll("details.dobra").forEach(d => d.removeAttribute("open"));
  const barra = document.querySelector(".progresso i"), topo = document.querySelector(".voltar-topo");
  if (barra) {
    const atualiza = () => {
      const h = document.documentElement.scrollHeight - innerHeight;
      barra.style.width = (h > 0 ? scrollY / h * 100 : 0) + "%";
      topo.classList.toggle("on", scrollY > innerHeight * 1.5);
    };
    addEventListener("scroll", atualiza, { passive: true }); atualiza();
  }
})();
(() => {
  const caixa = document.getElementById("legenda");
  if (!caixa) return;
  const txt = document.getElementById("leg-txt"), lst = caixa.querySelector(".leg-st"), btn = document.getElementById("b-legenda");
  const texto = txt.textContent;
  const copiar = async () => {
    const r = document.createRange(); r.selectNodeContents(txt);
    const sel = getSelection(); sel.removeAllRanges(); sel.addRange(r);
    let ok = false;
    try { ok = document.execCommand("copy"); } catch {}
    try { await navigator.clipboard.writeText(texto); ok = true; } catch {}
    lst.textContent = ok ? "Legenda copiada! É só colar no Instagram." : "Não deu para copiar automático: use “Compartilhar legenda” ou segure o dedo no texto.";
  };
  btn.addEventListener("click", () => { caixa.hidden = false; btn.setAttribute("aria-expanded", "true"); copiar(); });
  document.getElementById("b-copiar").addEventListener("click", copiar);
  const comp = document.getElementById("b-compartilhar");
  if (navigator.share) { comp.hidden = false; comp.addEventListener("click", () => navigator.share({ text: texto }).catch(() => {})); }
})();"""


# ---------- lista de estudos (resenhas/ do Elite) ----------

def derivar(c):
    """Dados de filtro de cada cartão (o derivar() do filtros_resenha.py do Elite)."""
    return {"nome": " ".join(dict.fromkeys(x for x in (c["titulo"], c["passagem"], c.get("titulo_busca", "")) if x)),
            "testamento": "AT" if c["testamento"].startswith("Antigo") else "NT", "genero": c["genero"], "nivel": c["nivel"],
            "tempo": c["tempo_min"], "formatos": [f[0] for f in c.get("formatos", []) if f[2] >= 2], "data": c.get("publicado_em") or ""}


JS_FILTROS = r"""
(() => {
  const form = document.getElementById("filtros"), lista = document.getElementById("lista"), dlg = document.getElementById("dlg-f");
  if (!dlg.showModal || !lista.children.length) return;
  const itens = [...lista.children].map((li, i) => ({li, i, d: JSON.parse(li.dataset.f)}));
  const total = itens.length, $ = id => document.getElementById(id);
  const norm = t => t.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  const esc = t => String(t).replace(/[&<>"]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"})[c]);
  const chips = {};
  const NOMES = {q: "Nome", testamento: "Testamento", genero: "Gênero", nivel: "Nível", tempo: "Tempo", formato: "Formato"};
  const grupo = k => form.querySelector(`.chips[data-campo="${k}"]`);
  const ler = () => { const v = Object.fromEntries(new FormData(form)); form.querySelectorAll(".chips").forEach(g => v[g.dataset.campo] = chips[g.dataset.campo] || ""); return v; };
  const passa = (d, v) => {
    if (v.q && !norm(d.nome).includes(norm(v.q.trim()))) return false;
    if (v.testamento && d.testamento !== v.testamento) return false;
    if (v.genero && d.genero !== v.genero) return false;
    if (v.nivel && d.nivel !== +v.nivel) return false;
    if (v.tempo) { const lim = {"15": [0, 15], "30": [16, 30], "60": [31, 60], "999": [61, 9999]}[v.tempo]; if (d.tempo < lim[0] || d.tempo > lim[1]) return false; }
    if (v.formato && !d.formatos.includes(v.formato)) return false;
    return true;
  };
  const conta = v => itens.reduce((n, x) => n + passa(x.d, v), 0);
  const ORDEM = { curto: (a, b) => a.d.tempo - b.d.tempo, nivel: (a, b) => a.d.nivel - b.d.nivel, fundo: (a, b) => b.d.nivel - a.d.nivel };
  const ativosDe = v => Object.entries(v).filter(([k, x]) => x && k !== "ordem");
  const rotulo = (k, val) => { if (k === "q") return `“${val}”`; const g = grupo(k); return g ? ([...g.querySelectorAll("button")].find(b => b.dataset.v === val)?.dataset.t || val) : ""; };
  const sem = (v, k) => ({...v, [k]: ""});
  const contagens = v => form.querySelectorAll(".chips").forEach(g => {
    const k = g.dataset.campo;
    g.querySelectorAll("button").forEach(b => { const on = chips[k] === b.dataset.v, n = conta({...v, [k]: b.dataset.v}); b.querySelector(".n").textContent = n; b.disabled = !on && n === 0; });
  });
  const aplicar = (gravar = true) => {
    const v = ler(), ativos = ativosDe(v);
    let n = 0;
    itens.forEach(x => { const ok = passa(x.d, v); x.li.hidden = !ok; n += ok; });
    [...itens].sort(ORDEM[v.ordem] || ((a, b) => a.i - b.i)).forEach(x => lista.append(x.li));
    contagens(v);
    $("n-ativos").hidden = !ativos.length; $("n-ativos").textContent = ativos.length;
    $("resumo-f").textContent = ativos.length ? `${n} de ${total} estudos` : `${total} estudos`;
    $("ativos").innerHTML = ativos.map(([k, x]) => { const r = rotulo(k, x), t = NOMES[k] + (r ? ": " + r : ""); return `<button type="button" class="chip-at" data-k="${k}" aria-label="Remover filtro ${esc(t)}">${esc(t)}<span aria-hidden="true">×</span></button>`; }).join("")
      + (ativos.length > 1 ? '<button type="button" class="limpar" data-k="*">Limpar tudo</button>' : "");
    $("ativos").hidden = !ativos.length;
    $("ver-f").textContent = n ? `Ver ${n} estudo${n === 1 ? "" : "s"}` : "Nenhum estudo"; $("ver-f").disabled = !n;
    $("vazio").hidden = n > 0;
    $("sugere").innerHTML = n ? "" : ativos.map(([k, x]) => [k, x, conta(sem(v, k))]).filter(a => a[2]).sort((a, b) => b[2] - a[2]).slice(0, 3)
      .map(([k, x, c]) => `<button type="button" class="chip-at" data-k="${k}">Tirar ${esc(NOMES[k] + ": " + rotulo(k, x))} (${c})</button>`).join("");
    if (gravar) { const q = new URLSearchParams(Object.entries(v).filter(([, x]) => x)); history.replaceState(null, "", q.toString() ? "?" + q : location.pathname); }
  };
  const marcar = (g, val) => g.querySelectorAll("button").forEach(b => b.setAttribute("aria-pressed", b.dataset.v === val));
  const remover = k => { if (k === "*") return form.reset(); if (grupo(k)) { chips[k] = ""; marcar(grupo(k), ""); } else form.elements[k].value = ""; aplicar(); };
  form.querySelectorAll(".chips").forEach(g => g.addEventListener("click", ev => {
    const b = ev.target.closest("button"); if (!b || b.disabled) return;
    chips[g.dataset.campo] = chips[g.dataset.campo] === b.dataset.v ? "" : b.dataset.v; marcar(g, chips[g.dataset.campo]); aplicar();
  }));
  form.addEventListener("input", () => aplicar());
  form.addEventListener("submit", ev => { ev.preventDefault(); dlg.close(); });
  form.addEventListener("reset", () => setTimeout(() => { Object.keys(chips).forEach(k => chips[k] = ""); form.querySelectorAll(".chips").forEach(g => marcar(g, "")); aplicar(); }));
  const tirar = ev => { const b = ev.target.closest("[data-k]"); if (b) remover(b.dataset.k); };
  $("ativos").addEventListener("click", tirar); $("sugere").addEventListener("click", tirar); $("limpar2").addEventListener("click", () => form.reset());
  $("abrir-f").addEventListener("click", () => dlg.showModal()); $("fechar-f").addEventListener("click", () => dlg.close());
  $("ver-f").addEventListener("click", () => { dlg.close(); $("barra-f").scrollIntoView({block: "start"}); });
  dlg.addEventListener("click", ev => { if (ev.target === dlg) dlg.close(); });
  new URLSearchParams(location.search).forEach((val, k) => { const g = grupo(k); if (g) { chips[k] = val; marcar(g, val); return; } const el = form.elements[k]; if (el) el.value = val; });
  $("barra-f").hidden = false;
  aplicar(false);
})();
"""


def build_lista(todos):
    pub = [c for c in todos if c.get("status") == "publicado"]
    pre = "../"
    cards = ""
    for c in pub:
        dados = e(json.dumps(derivar(c), ensure_ascii=False, separators=(",", ":")))
        im = c["imagem"]["arquivo"]
        cards += f"""  <li data-f="{dados}"><a class="card" href="{c["slug"]}/">
   <span class="capa"><img src="{imagens.miniatura(im, pre, 800)}" srcset="{imagens.srcset(im, pre, (400,))}" sizes="(min-width: 700px) 360px, 50vw" width="800" height="800" alt="{e(c["imagem"]["alt"])}" loading="lazy"><span class="nota n7" aria-label="{e(c["passagem"])}">{e(c.get("sigla", ""))}</span></span>
   <span class="corpo">
    <span class="selo {SELO_CLASSE.get(c["selo"], "")}">{e(c["selo"])}</span>
    <h2>{e(c["titulo"])}</h2>
    <span class="tag">{e(c["tagline"])}</span>
    <span class="vit">{e(c["passagem"])} · {c["tempo_min"]} min</span>
   </span>
  </a></li>
"""
    generos = sorted({c["genero"] for c in pub})
    chip = lambda campo, itens: (f'<div class="chips" data-campo="{campo}">' + "".join(  # noqa: E731
        f'<button type="button" data-v="{v}" data-t="{e(str(t))}" aria-pressed="false">{t}<small class="n"></small></button>' for v, t in itens) + "</div>")
    n = len(pub)
    filtros = f"""<div class="barra-f" id="barra-f" hidden>
  <button type="button" class="btn-filtro" id="abrir-f" aria-haspopup="dialog" aria-controls="dlg-f">
   <svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6h16M7 12h10M10 18h4"/></svg><span>Filtrar estudos</span><b class="badge" id="n-ativos" hidden></b>
  </button>
  <span class="resumo-f" id="resumo-f" aria-live="polite">{n} estudos</span>
 </div>
 <div class="ativos" id="ativos" aria-label="Filtros ativos" role="group" hidden></div>
 <dialog class="folha" id="dlg-f" aria-labelledby="t-f">
  <form class="filtros" id="filtros" role="search">
   <header class="folha-h"><h2 id="t-f">Filtrar estudos</h2><button type="button" class="fechar" id="fechar-f" aria-label="Fechar filtros"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button></header>
   <div class="folha-b">
    <input class="busca" type="search" name="q" placeholder="Buscar por tema ou passagem" autocomplete="off" aria-label="Buscar por tema ou passagem">
    <fieldset><legend>Testamento</legend>{chip("testamento", [("AT", "Antigo"), ("NT", "Novo")])}</fieldset>
    <fieldset><legend>Gênero do texto</legend>{chip("genero", [(g, g) for g in generos])}</fieldset>
    <fieldset><legend>Nível</legend>{chip("nivel", [(1, "Iniciante"), (2, "Intermediário"), (3, "Aprofundado")])}</fieldset>
    <fieldset><legend>Tempo</legend>{chip("tempo", [(15, "Até 15 min"), (30, "15 a 30 min"), (60, "30 a 60 min"), (999, "Mais de 1 h")])}</fieldset>
    <fieldset><legend>Bom para estudar</legend>{chip("formato", [("Sozinho", "Sozinho"), ("Em família", "Em família"), ("Em grupo", "Em grupo")])}</fieldset>
    <label class="f">Ordenar por<select name="ordem"><option value="">Mais recentes</option><option value="curto">Mais curto</option><option value="nivel">Mais simples</option><option value="fundo">Mais aprofundado</option></select></label>
   </div>
   <footer class="folha-p"><button type="reset" class="limpar">Limpar</button><button type="button" class="ver" id="ver-f">Ver {n} estudos</button></footer>
  </form>
 </dialog>
 <div class="vazio" id="vazio" hidden><p>Nenhum estudo com esses filtros.</p><div class="sugere" id="sugere"></div><button type="button" class="limpar" id="limpar2">Limpar todos os filtros</button></div>"""
    zap = (f'<a class="zap zap-fim" href="{whatsapp()}" target="_blank" rel="noopener">{icone("zap")}<span><b>Entre no grupo do WhatsApp</b><small>Receba os novos estudos</small></span></a>'
           if whatsapp() else "")
    corpo = f"""{cabecalho(pre, "Estudos bíblicos")}
<main class="in" id="conteudo">
 <section class="topo">
  <h1>Estudos bíblicos</h1>
  <p class="lede">{f"{n} estudos" if n else "Estudos"} com fontes: a estrutura do texto, o contexto histórico, o que a passagem ensina, as leituras equivocadas mais comuns e como estudar sozinho, em família ou em grupo.</p>
 </section>
 {filtros if n else '<p class="lede">Os primeiros estudos estão em revisão e aparecem aqui assim que forem aprovados.</p>'}
 <ul class="grid" id="lista">
{cards} </ul>
 {zap}
</main>
{rodape(pre)}
<script>{JS_FILTROS}</script>"""
    css = est.CSS_LISTA + ".selo.grupo{background:#1f5fae}.selo.fundo{background:#6b4ea3}.nota{font-size:.95rem}"
    escrever("estudos/index.html", pagina(f"Estudos bíblicos | {portal.NOME}", f"Estudos bíblicos do {portal.NOME}, com fontes, contexto histórico e aplicação.",
                                          f"{portal.SITE}/estudos/", capa_secao(), pre, corpo, css=css, indexavel=bool(n),
                                          jsonld=seo.script(seo.trilha(("Início", f"{portal.SITE}/"), ("Estudos bíblicos", f"{portal.SITE}/estudos/")))))
