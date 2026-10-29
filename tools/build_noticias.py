"""Página inicial, arquivo de notícias, páginas de categoria, página de cada notícia e prévias em revisão.

Cópia do tools/build_home.py do Elite Boardgamers: mesmos blocos da home (manchete, Últimas notícias, Destaques,
Agenda, faixa de capas, Financiamentos → Missões e campanhas, Últimas resenhas → Últimos estudos, Comunidade), mesma
página de notícia (selo, Por que importa, Em números, Contexto, No Brasil, O que dizem, Interessa a você se…,
Nossa opinião, Leia também, Fontes, Por que esta notícia entrou) e o mesmo arquivo com quadradinhos e filtro por
categoria. Categorias = editorias de config/editorias.json.
"""
import json
import sys
from datetime import datetime

import portal
import seo
import imagens
from pagina import (MES_CURTO, data_curta, data_longa, e, escrever, pagina, quando, capa_secao)
from layout import (barra_leitura, botao_compartilhar, cabecalho, convite_compartilhar, icone, instagram, arroba, whatsapp,
                    interacoes, rodape, trilha)
from noticias.checar_noticia import checar_dia, problemas

SELO_CLASSE = {"Boa notícia": "compra", "Vale acompanhar": "acompanhar", "Para refletir": "fas", "Motivo de alerta": "ressalvas", "Informativo": "info"}
POR_PAGINA = 30


def ed(slug):
    return portal.editoria(slug) or {"slug": slug, "nome": slug}


def notas(incluir_revisao=False):
    """Notas publicadas (e, se pedido, as em revisão), mais recentes primeiro. Nota fora do padrão derruba o build."""
    ns, ruins = [], {}
    for p in sorted((portal.CONTEUDO / "noticias").glob("*.json")):
        n = json.loads(p.read_text(encoding="utf-8"))
        st = n.get("status", "publicado")
        if st == "publicado" or (incluir_revisao and st == "revisao"):
            erros = problemas(n, publicar=st == "publicado")
            if erros:
                ruins[n["slug"]] = erros
            n.setdefault("publicado_em", f"{n['data']}T08:00:00-03:00")
            ns.append(n)
    if ruins:
        sys.exit("Notícias fora do padrão (rode python3 tools/noticias/checar_noticia.py):\n" +
                 "\n".join(f" - {s}: {'; '.join(x)}" for s, x in ruins.items()))
    pub = [n for n in ns if n.get("status", "publicado") == "publicado"]
    if checar_dia(pub):
        sys.exit("Edição do dia: " + "; ".join(checar_dia(pub)))
    return sorted(ns, key=lambda n: (n["data"], quando(n["publicado_em"]).timestamp(), n["crivo"]["pontos"]), reverse=True)


def img_nota(n, pre):
    return f"{pre}{imagens.publicar(n['imagem']['arquivo'])}" if n.get("imagem") else None


def linha_data(n, data):
    return f"{data} · {e(n['instituicao'])}" if n.get("instituicao") else data


def cat(n, link_pre=None):
    x = ed(n["categoria"])
    return f'<span class="cat ed-{x["slug"]}">{e(x["nome"])}</span>'


def bloco_manchete(m, pre, titulo="h1"):
    dim = imagens.dimensoes(m["imagem"]["arquivo"]) or (1200, 675)
    return f"""<article class="bloco manchete" data-cat="{m['categoria']}"><a href="{pre}noticias/{m['slug']}/">
  <figure><img src="{img_nota(m, pre)}" srcset="{imagens.srcset(m['imagem']['arquivo'], pre)}" sizes="(min-width: 640px) 340px, 100vw" width="{dim[0]}" height="{dim[1]}" alt="{e(m['imagem'].get('alt') or m['titulo'])}" fetchpriority="high"></figure>
  <div class="txt"><span class="kick">Manchete · {e(ed(m['categoria'])['nome'])}</span><{titulo} class="m-tit">{e(m['titulo'])}</{titulo}><p>{e(m['lide'])}</p>
  <p class="opina"><span class="selo {SELO_CLASSE[m['selo']]}">{e(m['selo'])}</span> {e(m['veredito'])}</p>
  <span class="meta">{linha_data(m, data_longa(m['data']))}</span><span class="credito">{e(m['imagem']['credito'])}</span></div>
 </a></article>"""


def cartao_nota(n, pre):
    if n.get("imagem"):
        img = (f'<img src="{img_nota(n, pre)}" srcset="{imagens.srcset(n["imagem"]["arquivo"], pre, (480,))}" sizes="(min-width: 1000px) 270px, (min-width: 600px) 31vw, 46vw" '
               f'alt="" loading="lazy" decoding="async">')
    else:
        img = f'<span class="sem" aria-hidden="true">{icone("dica")}</span>'
    return (f'<li class="card-n ed-{n["categoria"]}" data-cat="{n["categoria"]}"><a href="{pre}noticias/{n["slug"]}/">'
            f'<span class="ci">{img}</span><span class="cb">{cat(n)}'
            f'<h2>{e(n["titulo"])}</h2><span class="selo {SELO_CLASSE[n["selo"]]}">{e(n["selo"])}</span>'
            f'<span class="resumo">{e(n["por_que_importa"])}</span>'
            f'<span class="meta">{linha_data(n, data_curta(n["data"]))}</span></span></a></li>')


JS_CATEGORIAS = """(()=>{const g=document.querySelector('.cats');if(!g)return;
const lis=[...document.querySelectorAll('.arq [data-cat]')],nota=document.querySelector('.cat-nota');
const aplica=v=>{lis.forEach(li=>{li.hidden=!!v&&li.dataset.cat!==v});
g.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.c===v)));
const u=new URL(location.href);if(v)u.searchParams.set('categoria',v);else u.searchParams.delete('categoria');history.replaceState(null,'',u);
if(nota){const b=g.querySelector('[data-c="'+v+'"]'),a=nota.querySelector('a');nota.hidden=!v;if(v){a.href=b.dataset.pag;a.textContent='Ver todas as notícias de '+b.dataset.t}}};
g.addEventListener('click',ev=>{const b=ev.target.closest('button');if(b)aplica(b.dataset.c)});
const c=new URLSearchParams(location.search).get('categoria');g.hidden=false;aplica(c&&g.querySelector('[data-c="'+c+'"]')?c:'')})()"""


def home_json():
    arq = portal.CONTEUDO / "home.json"
    return json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else {}


def build_home(ns, estudos, agenda):
    pre = ""
    home = home_json()
    pub = [n for n in ns if n.get("status", "publicado") == "publicado"]
    cands = [n for n in pub if n.get("manchete")] or pub
    m = max(cands, key=lambda n: (n["data"], n["crivo"]["pontos"])) if cands else None
    resto = [n for n in pub if n is not m]

    def item(n):
        im = (f'<img src="{imagens.miniatura(n["imagem"]["arquivo"], pre, 160)}" width="76" height="76" alt="" loading="lazy">' if n.get("imagem")
              else f'<span class="sem">{icone("dica")}</span>')
        return (f"""<li data-cat="{n['categoria']}"><a href="noticias/{n['slug']}/"{'' if n.get("imagem") else ' class="sem-img"'}>{im}
   <div>{cat(n)} <span class="meta">{linha_data(n, data_curta(n['data']))}</span>
   <h3>{e(n['titulo'])}</h3><p><span class="selo {SELO_CLASSE[n['selo']]}">{e(n['selo'])}</span> <span class="resumo">{e(n['por_que_importa'])}</span></p></div></a></li>""")
    itens = "".join(item(n) for n in resto[:8])
    if m:
        manchete = bloco_manchete(m, pre)
    else:
        manchete = (f'<article class="bloco manchete"><div class="txt"><span class="kick">{e(portal.NOME)}</span><h1 class="m-tit">{e(portal.CFG.get("slogan", ""))}</h1>'
                    f'<p>{e(portal.CFG.get("descricao", ""))} As primeiras notícias estão em revisão e entram aqui assim que forem aprovadas.</p></div></article>')
    # Destaques (chave em_alta do home.json, como no Elite): assuntos das notas dos últimos dias, cada um com a nota
    alta = ""
    for j in home.get("em_alta", []):
        slug = j["link"].strip("/").split("/")[-1]
        alvo = next((n for n in pub if n["slug"] == slug), None)
        if not alvo:
            continue
        im = imagens.miniatura(alvo["imagem"]["arquivo"], pre, 96) if alvo.get("imagem") else ""
        alta += f'<li><a href="{e(j["link"])}">{f"<img src={chr(34)}{im}{chr(34)} width=44 height=44 alt={chr(34)}{chr(34)} loading=lazy>" if im else ""}<div><b>{e(j["nome"])}</b><span>{e(j["motivo"])}</span></div></a></li>'
    bloco_alta = (f'<section class="bloco alta"><h2>Destaques <a href="politica-editorial/#destaques" aria-label="Critério dos destaques">Critério</a></h2>'
                  f'<p class="crit-h">Os assuntos mais citados nas nossas notícias dos últimos 7 dias.</p><ol class="hot">{alta}</ol></section>') if alta else ""
    ag = ""
    for a in agenda[:6]:
        d = a["inicio"][:10]
        alvo = f'noticias/{a["materia"]}/' if a.get("materia") else a.get("url", "")
        ext = ' target="_blank" rel="noopener"' if alvo.startswith("http") else ""
        tit = f'<a href="{e(alvo)}"{ext}>{e(a["nome"])}</a>' if alvo else e(a["nome"])
        onde = "On-line" if a.get("online") else ", ".join(x for x in (a.get("cidade"), a.get("uf")) if x)
        ag += (f'<li><span class="q">{data_curta(d)}{"<small>previsto</small>" if not a.get("confirmado", True) else ""}</span>'
               f'<span><b>{tit}</b><br><span class="d">{e(onde)}{" · divulgação paga" if a.get("patrocinado") else ""}</span></span></li>')
    bloco_ag = f'<section class="bloco agenda"><h2>Agenda <a href="agenda/">Ver toda</a></h2><ul>{ag or "<li>Nenhum evento confirmado nos próximos dias.</li>"}</ul></section>'
    # faixa de capas ("Chegando ao Brasil" no Elite): lançamentos gospel com capa e crédito, de conteudo/lancamentos.json
    lanc = json.loads((portal.CONTEUDO / "lancamentos.json").read_text(encoding="utf-8")).get("lancamentos", []) if (portal.CONTEUDO / "lancamentos.json").exists() else []
    capas = "".join(
        f'<li><a href="{e(l.get("link", "#"))}"{" target=_blank rel=noopener" if l.get("link", "").startswith("http") else ""}><img src="{imagens.miniatura(l["imagem"]["arquivo"], pre, 280)}" width="132" height="140" alt="" loading="lazy">'
        f'<span class="st {"lancado" if l.get("status") == "lançado" else ""}">{e(l.get("status", "previsto").capitalize())}</span><b>{e(l["nome"])}</b><span>{e(l.get("artista", ""))}</span></a></li>'
        for l in lanc if l.get("imagem"))
    bloco_lanc = f'<section class="bloco brasil" id="lancamentos"><h2>Lançamentos gospel</h2><ul class="capas">{capas}</ul></section>' if capas else ""
    camp = "".join(
        f'<li><span class="onde">{e(c["onde"])}</span><a href="{e(("noticias/" + c["noticia"] + "/") if c.get("noticia") else c.get("link", "#"))}">{e(c["nome"])}</a>'
        f'<span class="s">{e(c["organizacao"])} · {e(c["situacao"])}</span><span class="f">Fonte: {e(c["fonte"])}</span></li>'
        for c in home.get("campanhas", []))
    bloco_camp = f'<section class="bloco financ"><h2>Missões e campanhas</h2><ul>{camp}</ul></section>' if camp else ""
    res = ""
    for c in [x for x in estudos if x.get("status") == "publicado"][:4]:
        im = c["imagem"]["arquivo"]
        res += (f'<li><a href="estudos/{c["slug"]}/"><img src="{imagens.miniatura(im, pre, 400)}" srcset="{imagens.srcset(im, pre, (400,))}" sizes="(min-width: 640px) 160px, 45vw" '
                f'width="800" height="800" alt="" loading="lazy"><b>{e(c["titulo"])}</b></a></li>')
    bloco_res = f'<section class="bloco resenhas"><h2>Últimos estudos bíblicos <a href="estudos/">Ver todos</a></h2><ul class="res">{res}</ul></section>' if res else ""
    acoes = ((f'<a class="btn zap" href="{whatsapp()}" target="_blank" rel="noopener">{icone("zap")}Entrar no grupo do WhatsApp</a>' if whatsapp() else "")
             + (f'<a class="btn ig" href="{instagram()}" target="_blank" rel="noopener">{icone("insta")}{arroba()}</a>' if instagram() else "")
             + f'<a class="btn ig" href="newsletter/">{icone("email")}Newsletter</a>'
             + botao_compartilhar(f"{portal.NOME}: {portal.CFG.get('descricao', '')}", f"{portal.SITE}/", "Compartilhar o site"))
    edicao = f'<p class="edicao">Edição de {data_longa(max(n["data"] for n in pub))}</p>' if pub else ""
    corpo = f"""{cabecalho(pre, "Início")}
<main id="conteudo" class="in">
 {edicao}
 <div class="grade">
  {manchete}
  {f'<section class="bloco ultimas"><h2>Últimas notícias <a href="noticias/">Ver todas ({len(pub)})</a></h2><ul class="lista-n">{itens}</ul></section>' if itens else ''}
  <aside class="lado">{bloco_alta}
  {bloco_ag}</aside>
  {bloco_lanc}
  {bloco_camp}
  {bloco_res}
  <section class="bloco comunidade"><p>Notícias com fonte e data, estudos bíblicos e a agenda cristã, todos os dias. Entre no grupo para receber as novidades.</p>
   <div class="acoes">{acoes}</div></section>
 </div>
</main>
{rodape(pre)}"""
    titulo = f"{portal.NOME}: {portal.CFG.get('slogan', '').rstrip('.')}"
    descr = (f"{m['titulo']}. " if m else "") + portal.CFG.get("descricao", "")
    import og
    img = (og.url_cartao(f"noticia-{m['slug']}") or f"{portal.SITE}/{imagens.publicar(m['imagem']['arquivo'])}") if m else capa_secao()
    escrever("index.html", pagina(titulo, descr, f"{portal.SITE}/", img, pre, corpo, jsonld=seo.script(seo.site())))
    return m


def build_arquivo(ns):
    pub = [n for n in ns if n.get("status", "publicado") == "publicado"]
    m = max((n for n in pub if n.get("manchete")), key=lambda n: n["data"], default=pub[0] if pub else None)
    paginas = [pub[i:i + POR_PAGINA] for i in range(0, len(pub), POR_PAGINA)] or [[]]
    # páginas de categoria: no Elite só existiam com o arquivo paginado; aqui as editorias têm página sempre
    for x in portal.visiveis():
        lista = [n for n in pub if n["categoria"] == x["slug"]]
        if not lista:
            continue
        c_pre, url_c = "../../../", f"{portal.SITE}/noticias/categoria/{x['slug']}/"
        corpo_c = f"""{cabecalho(c_pre, "Notícias", sub=True)}
<main id="conteudo" class="in arq">{trilha(("Início", c_pre), ("Notícias", f"{c_pre}noticias/"), (e(x["nome"]), ""))}
 <div class="arq-topo"><h1>{e(x["nome"])}</h1><p>{e(x["descricao"])} {len(lista)} notícia{"s" if len(lista) > 1 else ""}.</p></div>
 <ul class="grade-n">{"".join(cartao_nota(n, c_pre) for n in lista)}</ul>
</main>
{rodape(c_pre)}"""
        escrever(f"noticias/categoria/{x['slug']}/index.html", pagina(f"{x['nome']}: notícias | {portal.NOME}", x["descricao"], url_c, capa_secao(), c_pre, corpo_c,
                                                                     jsonld=seo.script(seo.trilha(("Início", f"{portal.SITE}/"), ("Notícias", f"{portal.SITE}/noticias/"), (x["nome"], url_c)))))

    def chips(lote, p_pre):
        conta = {x["slug"]: sum(1 for n in lote if n["categoria"] == x["slug"]) for x in portal.EDITORIAS}
        bts = "".join(f'<button type="button" data-c="{x["slug"]}" data-t="{e(x["nome"])}" data-pag="{p_pre}noticias/categoria/{x["slug"]}/" aria-pressed="false">{e(x["nome"])}<small>{conta[x["slug"]]}</small></button>'
                      for x in portal.EDITORIAS if conta[x["slug"]])
        nota = '<p class="cat-nota" hidden>Esta página mostra só parte do arquivo. <a href="#">Ver todas</a></p>' if len(paginas) > 1 else ""
        return f'<div class="cats" role="group" aria-label="Filtrar por categoria" hidden><button type="button" data-c="" aria-pressed="true">Todas<small>{len(lote)}</small></button>{bts}</div>{nota}'

    for num, lote in enumerate(paginas, 1):
        p_pre = "../" if num == 1 else "../../../"
        url = f"{portal.SITE}/noticias/" if num == 1 else f"{portal.SITE}/noticias/pagina/{num}/"
        destaque = bloco_manchete(m, p_pre, "h2") if num == 1 and m else ""
        arquivo = "".join(cartao_nota(n, p_pre) for n in lote if not (num == 1 and n is m))
        ant = "" if num == 1 else f'<a href="{p_pre}noticias/{"" if num == 2 else f"pagina/{num - 1}/"}" rel="prev">← Mais recentes</a>'
        prox = f'<a href="{p_pre}noticias/pagina/{num + 1}/" rel="next">Mais antigas →</a>' if num < len(paginas) else ""
        nav = f'<nav class="paginas" aria-label="Páginas de notícias">{ant}<span>Página {num} de {len(paginas)}</span>{prox}</nav>' if len(paginas) > 1 else ""
        suf = "" if num == 1 else f" (página {num})"
        corpo = f"""{cabecalho(p_pre, "Notícias", sub=num > 1)}
<main id="conteudo" class="in arq">
 <div class="arq-topo"><h1>Notícias{suf}</h1><p>Com fonte, data e a nossa opinião separada do fato. {len(pub)} notícia{"s" if len(pub) != 1 else ""} publicada{"s" if len(pub) != 1 else ""}.</p></div>
 {chips(lote, p_pre) if lote else '<p class="cat-nota">As primeiras notícias estão em revisão e aparecem aqui assim que forem aprovadas.</p>'}
 {destaque}
 <ul class="grade-n">{arquivo}</ul>
 {nav}
 <script>{JS_CATEGORIAS}</script>
</main>
{rodape(p_pre)}"""
        trilha_ld = [("Início", f"{portal.SITE}/"), ("Notícias", f"{portal.SITE}/noticias/")] + ([] if num == 1 else [(f"Página {num}", url)])
        destino = "noticias/index.html" if num == 1 else f"noticias/pagina/{num}/index.html"
        escrever(destino, pagina(f"Notícias{suf} | {portal.NOME}", f"Notícias do {portal.NOME}, com fonte, data e opinião separada do fato{suf}.", url,
                                 capa_secao(), p_pre, corpo, jsonld=seo.script(seo.trilha(*trilha_ld))))


def relacionadas(n, ns, limite=3):
    """'Leia também' (igual ao Elite): primeiro as que citam o mesmo estudo, depois as da mesma categoria."""
    est = {j.get("estudo") or j["nome"] for j in n.get("estudos", [])}
    cands = []
    for o in ns:
        if o["slug"] == n["slug"] or o.get("status", "publicado") != "publicado":
            continue
        comum = len(est & {j.get("estudo") or j["nome"] for j in o.get("estudos", [])})
        if comum or o["categoria"] == n["categoria"]:
            cands.append((comum, o["data"], o.get("publicado_em", ""), o))
    cands.sort(key=lambda x: x[:3], reverse=True)
    return [o for *_, o in cands[:limite]]


def build_nota(n, ns, previa=False):
    """Página da notícia. Em revisão: sai em /previa/noticias/<slug>/, fora do índice, com aviso no topo."""
    base = f"previa/noticias/{n['slug']}/" if previa else f"noticias/{n['slug']}/"
    pre = "../../../" if previa else "../../"
    url = f"{portal.SITE}/noticias/{n['slug']}/"
    texto_cp = f"{n['titulo']} (via {portal.NOME})"
    im = n.get("imagem")
    fig = (f'<figure><img src="{img_nota(n, pre)}" srcset="{imagens.srcset(im["arquivo"], pre)}" sizes="(min-width: 760px) 720px, 100vw" alt="{e(im.get("alt") or n["titulo"])}">'
           f'<figcaption class="credito">{e(im["credito"])}</figcaption></figure>') if im else ""
    est = "".join(f'<a href="{pre}estudos/{j["estudo"]}/">Estudo: {e(j["nome"])}</a>' for j in n.get("estudos", []) if j.get("estudo"))
    fontes = "".join(f'<li><a href="{e(f["url"])}" target="_blank" rel="noopener">{e(f["nome"])}</a> <span>consulta em {e(f["data"])}</span></li>' for f in n["fontes"])
    numeros = "".join(f'<li><b>{e(v)}</b><span>{e(r)}</span><small>{e(f)}</small></li>' for v, r, f in n["numeros"])
    critica = "".join((f'<li class="cit"><q>{e(c["texto"])}</q><cite>{e(c["fonte"])}</cite></li>' if c.get("citacao")
                       else f'<li><p>{e(c["texto"])}</p></li>') for c in n["critica"])
    sim = "".join(f"<li>{e(x)}</li>" for x in n["para_quem"])
    nao = "".join(f"<li>{e(x)}</li>" for x in n.get("nao_e_para", []))
    sc = SELO_CLASSE[n["selo"]]
    leia = "".join(f'<li><a href="{pre}noticias/{o["slug"]}/">{e(o["titulo"])}</a></li>' for o in relacionadas(n, ns))
    correcoes = "".join(f'<p><b>Correção em {data_curta(c["data"])}/{c["data"][:4]}:</b> {e(c["texto"])}</p>' for c in n.get("correcoes", []))
    rev = portal.EQUIPE.get((n.get("revisao") or {}).get("revisor", ""), {})
    ia = n.get("ia") or {}
    transp = (f'<p class="transp"><b>Como foi feita:</b> {"redigida com apoio de inteligência artificial (" + e(ia.get("uso", "")) + ") e " if ia.get("usada") else ""}'
              f'{"revisada por " + e(rev["nome"]) if rev.get("nome") else "aguardando revisão humana"} antes da publicação. '
              f'<a href="{pre}politica-editorial/">Política editorial</a> · <a href="{pre}contato/#correcao">Pedir correção</a></p>')
    aviso = ('<div class="previa-aviso" role="note"><b>Prévia em revisão.</b> Esta notícia ainda não foi publicada: está esperando a revisão '
             'humana da redação. Não compartilhe.</div>') if previa else ""
    corpo = f"""{aviso}{cabecalho(pre, "Notícias", sub=True)}
<main id="conteudo" class="in"><div class="nota">
 {trilha(("Início", pre), ("Notícias", f"{pre}noticias/"), (e(n["titulo"]), ""))}
 <article class="bloco">
  {cat(n)} <span class="selo {sc}">{e(n['selo'])}</span>
  <h1>{e(n['titulo'])}</h1>
  <p class="meta"><time datetime="{n['publicado_em']}">{data_longa(n['data'])}</time> · Redação {e(portal.NOME)}</p>
 </article>
 <div class="bloco abre">{fig}<p class="lide">{e(n['lide'])}</p></div>
 <section class="bloco importa"><h2>Por que importa</h2><p>{e(n['por_que_importa'])}</p><p class="assina">Análise {e(portal.NOME)}</p></section>
 <section class="bloco"><h2>Em números</h2><ul class="nums">{numeros}</ul></section>
 <section class="bloco"><h2>Contexto</h2><div class="corpo">{"".join(f"<p>{e(p)}</p>" for p in n['corpo'])}{correcoes}</div></section>
 <section class="bloco brasil-n"><h2>No Brasil</h2><p>{e(n['no_brasil'])}</p></section>
 <section class="bloco"><h2>O que dizem</h2>{f'<ul class="crit">{critica}</ul>' if critica else '<p class="corpo">Ainda não encontramos posicionamento público de lideranças ou instituições sobre o assunto.</p>'}</section>
 <section class="bloco quem"><div><h2>Interessa a você se…</h2><ul class="ok">{sim}</ul></div>{f'<div><h2>Pense duas vezes se…</h2><ul class="no">{nao}</ul></div>' if nao else ""}</section>
 <section class="bloco veredito {sc}"><h2>Nossa opinião</h2><span class="selo {sc}">{e(n['selo'])}</span><p>{e(n['veredito'])}</p></section>
 {convite_compartilhar(texto_cp, url, "Conhece alguém que precisa ler isto?", "Mande esta notícia para o seu grupo.")}
 {interacoes(pre, f"/noticias/{n['slug']}/")}
 {f'<section class="bloco"><h2>Estudos citados</h2><div class="jogos">{est}</div></section>' if est else ""}
 {f'<section class="bloco leia"><h2>Leia também</h2><ul>{leia}</ul></section>' if leia else ""}
 <section class="bloco fontes"><h2>Fontes</h2><ul>{fontes}</ul></section>
 <section class="bloco crivo"><h2>Por que esta notícia entrou</h2><p><b>{n['crivo']['pontos']} pontos no crivo editorial</b>{":" if n['crivo']['criterios'] else ""} {e("; ".join(n['crivo']['criterios']) or "(nenhum critério de pontuação)")}.</p>{transp}</section>
</div></main>
{rodape(pre, barra_leitura(texto_cp, url))}"""
    imgs = []
    if im:
        try:
            imgs.append(f"{portal.SITE}/{imagens.larga(im['arquivo'])}")
        except Exception as ex:
            print(f"  aviso: sem versão larga para {n['slug']} ({ex.__class__.__name__})")
        orig = f"{portal.SITE}/{imagens.publicar(im['arquivo'])}"
        if orig not in imgs:
            imgs.append(orig)
    art = {"@type": "NewsArticle", "@id": f"{url}#artigo", "mainEntityOfPage": url, "headline": n["titulo"], "description": n["lide"],
           "image": imgs or [capa_secao()], "datePublished": n["publicado_em"], "author": [seo.pessoa((n.get("autor") or ""))],
           "publisher": {"@id": seo.org_id()}, "inLanguage": "pt-BR", "articleSection": ed(n["categoria"])["nome"]}
    if n.get("atualizado_em") and n["atualizado_em"] > n["publicado_em"]:
        art["dateModified"] = n["atualizado_em"]
    ld = seo.script(art, seo.trilha(("Início", f"{portal.SITE}/"), ("Notícias", f"{portal.SITE}/noticias/"), (n["titulo"], url)))
    t_busca = n.get("titulo_seo") or n["titulo"]
    t_busca = t_busca if len(t_busca) > 42 else f"{t_busca} | {portal.NOME}"
    import og
    escrever(f"{base}index.html", pagina(t_busca, n["lide"], url if not previa else "", og.url_cartao(f"noticia-{n['slug']}") or (imgs[-1] if imgs else capa_secao()),
                                         pre, corpo, "article", f'\n<meta property="article:published_time" content="{n["publicado_em"]}">', ld,
                                         indexavel=not previa, largura=(1200, 630) if og.url_cartao(f"noticia-{n['slug']}") else None))


def build_previa_indice(ns, estudos):
    """/previa/: lista do que espera revisão humana (fora do índice e do sitemap), para a redação conferir no celular."""
    rev_n = [n for n in ns if n.get("status") == "revisao"]
    rev_e = [c for c in estudos if c.get("status") == "revisao"]
    pre = "../"
    itens = "".join(f'<li><a href="noticias/{n["slug"]}/">{e(n["titulo"])}</a> <span>{e(ed(n["categoria"])["nome"])} · {n["crivo"]["pontos"]} pontos</span></li>' for n in rev_n)
    itens += "".join(f'<li><a href="estudos/{c["slug"]}/">Estudo: {e(c["titulo"])}</a></li>' for c in rev_e)
    corpo = f"""<div class="previa-aviso" role="note"><b>Área de revisão.</b> Nada aqui está publicado.</div>{cabecalho(pre, "")}
<main id="conteudo" class="in"><div class="nota"><section class="bloco"><h1>Em revisão</h1>
 <p class="lide">Matérias prontas esperando a aprovação de uma pessoa da redação. Para publicar: <code>python3 tools/publicar.py aprovar &lt;arquivo&gt; --revisor &lt;slug&gt;</code>.</p>
 <ul class="fontes">{itens or "<li>Nada esperando revisão.</li>"}</ul></section></div></main>
{rodape(pre, "")}"""
    escrever("previa/index.html", pagina(f"Em revisão | {portal.NOME}", "Área de revisão.", "", capa_secao(), pre, corpo, indexavel=False))
