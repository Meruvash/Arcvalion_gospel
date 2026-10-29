"""Gera o site inteiro em publico/: home, editorias, arquivo, matérias, opinião, autores, institucionais, feeds e sitemaps.

Uso:
  python3 tools/build.py               build local (domínio da configuração; matérias com status "publicado")
  python3 tools/build.py --producao    igual, mas recusa configuração provisória (domínio .example, sem responsável etc.)
  python3 tools/build.py --exemplo     prévia com o conteúdo fictício de exemplos/ em publico-exemplo/ (noindex, faixa de aviso)
  opções: --saida DIR  --hoje AAAA-MM-DD (data de referência da agenda e do sitemap de notícias)  --sem-og

Portado de tools/build_home.py do Elite Boardgamers: mesma ideia (JSON versionado -> HTML estático), mesma moldura,
mesmos componentes (manchete, últimas, grade com filtro por editoria e estado na URL, paginação, "Leia também",
compartilhar, comentários, trilha visível + BreadcrumbList) e a mesma trava: matéria fora do padrão editorial não sai.
Diferença principal: nada é publicado sem revisão humana registrada (status "publicado" + revisor de config/equipe.json).
"""
import argparse
import html
import json
import re
import shutil
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from xml.sax.saxutils import escape as xesc
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
import portal  # noqa: E402
import estilo  # noqa: E402
import imagens  # noqa: E402
import seo  # noqa: E402
import anuncios  # noqa: E402
from layout import (botao_compartilhar, cabecalho, convite_compartilhar, formulario, icone, interacoes,  # noqa: E402
                    barra_leitura, rodape, trilha)
from editorial.checar import checar_conjunto, problemas  # noqa: E402

e = html.escape
def _fuso():
    """Horário de Brasília; sem base de fusos no sistema (alguns servidores de build), usa -03:00 fixo (sem horário de verão desde 2019)."""
    try:
        return ZoneInfo("America/Sao_Paulo")
    except Exception:
        from datetime import timedelta, timezone as tz
        return tz(timedelta(hours=-3), "BRT")


FUSO = _fuso()
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
MES_CURTO = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
HOJE = None
ARQUIVOS_ESCRITOS = []


# ---------- utilidades ----------

def quando(iso):
    return datetime.fromisoformat(iso).astimezone(FUSO)


def data_longa(iso, hora=False):
    d = quando(iso) if "T" in iso else datetime.fromisoformat(iso)
    s = f"{d.day} de {MESES[d.month - 1]} de {d.year}"
    return s + (f", {d.hour}h{d.minute:02d}" if hora and "T" in iso else "")


def data_curta(iso):
    d = quando(iso)
    return f"{d.day:02d}/{d.month:02d}/{d.year}"


def escrever(rel, texto):
    alvo = portal.SAIDA / rel
    alvo.parent.mkdir(parents=True, exist_ok=True)
    alvo.write_text(texto, encoding="utf-8")
    ARQUIVOS_ESCRITOS.append(rel)


def classe_ed(a_ou_slug):
    slug = a_ou_slug if isinstance(a_ou_slug, str) else a_ou_slug["editoria"]
    return f"ed-{slug}"


def nome_ed(slug):
    ed = portal.editoria(slug)
    return ed["nome"] if ed else slug


def autor_nome(a):
    if a.get("colaborador"):
        return a["colaborador"]["nome"]
    p = portal.EQUIPE.get(a.get("autor", ""))
    return p["nome"] if p else f"Redação {portal.NOME}"


def autor_link(a, pre):
    if a.get("autor") in portal.EQUIPE:
        return f'<a href="{pre}autores/{a["autor"]}/">{e(autor_nome(a))}</a>'
    return f"<b>{e(autor_nome(a))}</b>"


def etiquetas(a, pre, link=True):
    ed = portal.editoria(a["editoria"])
    cat = (f'<a class="cat" href="{pre}{a["editoria"]}/">{e(ed["nome"])}</a>' if link else f'<span class="cat">{e(ed["nome"])}</span>')
    t = "" if a["tipo"] == "noticia" else f'<span class="tipo t-{a["tipo"]}">{e(portal.TIPOS[a["tipo"]][0])}</span>'
    return cat + t


def resumo(a):
    return a.get("linha_fina") or a.get("lide", "")


def url_materia(a):
    return f"{portal.SITE}/noticias/{a['slug']}/"


def imagem_og(a):
    import og
    return og.url_cartao(a) or (f"{portal.SITE}/{imagens.publicar(a['imagem']['arquivo'])}" if a.get("imagem") else f"{portal.SITE}/marca/capa.png")


# ---------- página ----------

def pagina(titulo, descricao, url, imagem, pre, corpo, tipo="website", head_extra="", jsonld="", indexavel=True, pub=False):
    cfg = portal.CFG
    robots = "max-image-preview:large" if indexavel and not portal.EXEMPLO else "noindex, follow"
    verif = "".join(f'\n<meta name="{n}" content="{e(cfg["verificacao"][k])}">' for k, n in (("google", "google-site-verification"), ("bing", "msvalidate.01"))
                    if cfg.get("verificacao", {}).get(k))
    an = cfg.get("analytics", {})
    medidor = (f"""<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{{"token": "{e(an["cloudflare_token"])}"}}'></script>"""
               if an.get("cloudflare_token") and not portal.EXEMPLO else "")
    precisa_consent = bool(an.get("ga4_id") or portal.ANUNCIOS.get("adsense_cliente"))
    priv = (f'<script src="{pre}js/privacidade.js" defer data-ga4="{e(an.get("ga4_id", ""))}" data-adsense="{e(portal.ANUNCIOS.get("adsense_cliente", ""))}" '
            f'data-politica="{pre}privacidade/"></script>') if precisa_consent and not portal.EXEMPLO else ""
    js_pub = f'<script src="{pre}js/anuncios.js" defer></script>' if pub else ""
    return f"""<!doctype html>
<html lang="{e(cfg.get('idioma', 'pt-BR'))}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(titulo)}</title>
<meta name="description" content="{e(descricao)}">
{f'<link rel="canonical" href="{url}">' if url else ''}
<meta name="robots" content="{robots}">{verif}
<meta property="og:site_name" content="{e(portal.NOME)}">
<meta property="og:locale" content="pt_BR">
<meta property="og:title" content="{e(titulo)}">
<meta property="og:description" content="{e(descricao)}">
<meta property="og:type" content="{tipo}">
<meta property="og:url" content="{url or portal.SITE + '/'}">
<meta property="og:image" content="{imagem}">
<meta name="twitter:card" content="summary_large_image">{head_extra}
<meta name="theme-color" content="#12294a">
<link rel="icon" href="{pre}marca/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{pre}marca/logo-180.png">
<link rel="alternate" type="application/rss+xml" title="{e(portal.NOME)}" href="{portal.SITE}/feed.xml">
<link rel="preload" href="{pre}fontes/public-sans.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{pre}fontes/source-serif-4-700.woff2" as="font" type="font/woff2" crossorigin>
<style>{estilo.css(pre)}</style>
{jsonld}
</head>
<body>
{corpo}
{priv}{js_pub}{medidor}
</body>
</html>
"""


# ---------- conteúdo ----------

def carregar(hoje):
    artigos = []
    erros = []
    for p in sorted((portal.CONTEUDO / "artigos").glob("*.json")):
        a = json.loads(p.read_text(encoding="utf-8"))
        a["_arquivo"] = p.name
        artigos.append(a)
    erros += checar_conjunto(artigos)
    publicados = []
    for a in artigos:
        if a.get("status") != "publicado":
            continue
        es = problemas(a, publicar=True)
        if es:
            erros.append(f"{a['_arquivo']}: " + "; ".join(es))
        elif quando(a["publicado_em"]) <= datetime.combine(hoje, datetime.max.time(), FUSO):
            # publicado_em no futuro = agendada: só entra no build do dia
            publicados.append(a)
    if erros:
        sys.exit("Matérias fora do padrão editorial (rode python3 tools/editorial/checar.py):\n - " + "\n - ".join(erros))
    publicados.sort(key=lambda a: quando(a["publicado_em"]), reverse=True)
    return publicados


def agenda(hoje):
    arq = portal.CONTEUDO / "agenda.json"
    if not arq.exists():
        return []
    evs = json.loads(arq.read_text(encoding="utf-8")).get("eventos", [])
    erros = [f"agenda: {ev.get('nome')!r} precisa de nome, inicio (AAAA-MM-DD) e fonte com link"
             for ev in evs if not ev.get("nome") or not re.match(r"\d{4}-\d{2}-\d{2}", ev.get("inicio", "")) or not (ev.get("fonte") or {}).get("url")]
    if erros:
        sys.exit("\n".join(erros))
    futuros = [ev for ev in evs if (ev.get("fim") or ev["inicio"])[:10] >= hoje.isoformat()]
    return sorted(futuros, key=lambda ev: ev["inicio"])


def relacionadas(a, todos, limite=4):
    """'Leia também': primeiro as que dividem tags, depois as da mesma editoria; mais recentes antes. Patrocinado fica fora."""
    tags = set(a.get("tags") or [])
    cands = []
    for o in todos:
        if o is a or o["tipo"] == "patrocinado":
            continue
        comum = len(tags & set(o.get("tags") or []))
        if comum or o["editoria"] == a["editoria"]:
            cands.append((comum, o["publicado_em"], o))
    cands.sort(key=lambda x: (x[0], quando(x[1])), reverse=True)
    return [o for *_, o in cands[:limite]]


# ---------- componentes ----------

def figura(a, pre, sizes, prioridade=False, classe=""):
    im = a.get("imagem")
    if not im:
        return ""
    dim = imagens.dimensoes(im["arquivo"]) or (1200, 675)
    pr = ' fetchpriority="high"' if prioridade else ' loading="lazy" decoding="async"'
    return (f'<figure class="{classe}"><img src="{pre}{imagens.publicar(im["arquivo"])}" srcset="{imagens.srcset(im["arquivo"], pre)}" sizes="{sizes}" '
            f'width="{dim[0]}" height="{dim[1]}" alt="{e(im["alt"])}"{pr}><figcaption class="credito">{e(im["credito"])}</figcaption></figure>')


def bloco_manchete(m, pre, tag="h1"):
    im = m.get("imagem")
    fig = ""
    if im:
        dim = imagens.dimensoes(im["arquivo"]) or (1200, 675)
        fig = (f'<figure><img src="{pre}{imagens.publicar(im["arquivo"])}" srcset="{imagens.srcset(im["arquivo"], pre)}" '
               f'sizes="(min-width: 1180px) 450px, (min-width: 640px) 46vw, 100vw" width="{dim[0]}" height="{dim[1]}" alt="{e(im["alt"])}" fetchpriority="high"></figure>')
    return f"""<article class="bloco manchete {classe_ed(m)}"><a href="{pre}noticias/{m['slug']}/">{fig}
  <div class="txt"><span class="etq">{etiquetas(m, pre, link=False)}</span><{tag} class="titulo m-tit">{e(m['titulo'])}</{tag}>
  <p class="lf">{e(resumo(m))}</p><span class="meta">{data_longa(m['publicado_em'])} · {e(autor_nome(m))}</span>{f'<span class="credito">{e(im["credito"])}</span>' if im else ''}</div>
 </a></article>"""


def item_lista(a, pre):
    im = a.get("imagem")
    img = (f'<img src="{imagens.miniatura(im["arquivo"], pre)}" width="96" height="72" alt="" loading="lazy" decoding="async">' if im
           else f'<span class="sem">{icone("livro")}</span>')
    return (f'<li class="{classe_ed(a)}"><a href="{pre}noticias/{a["slug"]}/"{"" if im else " class=\"sem-img\""}>{img if im else ""}'
            f'<div><span class="etq">{etiquetas(a, pre, link=False)}</span> <span class="meta">{data_curta(a["publicado_em"])}</span>'
            f'<h3 class="l-tit">{e(a["titulo"])}</h3><p>{e(resumo(a))}</p></div></a></li>')


def cartao(a, pre, tag="h2"):
    im = a.get("imagem")
    img = (f'<img src="{pre}{imagens.publicar(im["arquivo"])}" srcset="{imagens.srcset(im["arquivo"], pre, (480,))}" '
           f'sizes="(min-width: 1000px) 270px, (min-width: 600px) 31vw, 46vw" alt="" loading="lazy" decoding="async">' if im
           else f'<span class="sem" aria-hidden="true">{icone("livro")}</span>')
    return (f'<li class="card-n {classe_ed(a)}" data-ed="{a["editoria"]}"><a href="{pre}noticias/{a["slug"]}/">'
            f'<span class="ci">{img}</span><span class="cb"><span class="etq">{etiquetas(a, pre, link=False)}</span>'
            f'<{tag} class="t">{e(a["titulo"])}</{tag}><span class="resumo">{e(resumo(a))}</span>'
            f'<span class="meta">{data_curta(a["publicado_em"])} · {e(autor_nome(a))}</span></span></a></li>')


def mini(a, pre):
    im = a.get("imagem")
    img = (f'<img src="{imagens.miniatura(im["arquivo"], pre, 480)}" alt="" loading="lazy" decoding="async">' if im
           else f'<span class="sem" aria-hidden="true">{icone("livro")}</span>')
    t = "" if a["tipo"] == "noticia" else f'<span class="tipo t-{a["tipo"]}">{e(portal.TIPOS[a["tipo"]][0])}</span>'
    return f'<li class="mini"><a href="{pre}noticias/{a["slug"]}/"><span class="ci">{img}</span>{t}<span class="t">{e(a["titulo"])}</span><span class="meta">{data_curta(a["publicado_em"])}</span></a></li>'


def item_agenda(ev, pre):
    d = date.fromisoformat(ev["inicio"][:10])
    onde = "On-line" if ev.get("online") else ", ".join(x for x in (ev.get("local"), f"{ev.get('cidade', '')}{' (' + ev['uf'] + ')' if ev.get('uf') else ''}") if x)
    alvo = f'{pre}noticias/{ev["materia"]}/' if ev.get("materia") else ev.get("url", "")
    ext = ' target="_blank" rel="noopener"' if alvo.startswith("http") else ""
    nome = f'<a href="{e(alvo)}"{ext}>{e(ev["nome"])}</a>' if alvo else f"<b>{e(ev['nome'])}</b>"
    fim = f" a {date.fromisoformat(ev['fim'][:10]).day}/{date.fromisoformat(ev['fim'][:10]).month:02d}" if ev.get("fim") and ev["fim"][:10] != ev["inicio"][:10] else ""
    pago = ' · <span class="prev">divulgação paga</span>' if ev.get("patrocinado") else ""
    prev = "" if ev.get("confirmado", True) else ' · <span class="prev">data a confirmar</span>'
    return (f'<li><span class="q"><b>{d.day}</b><small>{MES_CURTO[d.month - 1]}</small></span><span>{nome}'
            f'<span class="d">{e(onde)}{fim}{prev}{pago}</span></span></li>')


JS_FILTRO = """(()=>{const g=document.querySelector('.cats');if(!g)return;
const lis=[...document.querySelectorAll('.arq [data-ed]')],nota=document.querySelector('.cat-nota');
const aplica=v=>{lis.forEach(li=>{li.hidden=!!v&&li.dataset.ed!==v});
g.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.c===v)));
const u=new URL(location.href);if(v)u.searchParams.set('editoria',v);else u.searchParams.delete('editoria');history.replaceState(null,'',u);
if(nota){const b=g.querySelector('[data-c="'+v+'"]'),a=nota.querySelector('a');nota.hidden=!v;if(v){a.href=b.dataset.pag;a.textContent='Ver todas as matérias de '+b.dataset.t}}};
g.addEventListener('click',ev=>{const b=ev.target.closest('button');if(b)aplica(b.dataset.c)});
const c=new URLSearchParams(location.search).get('editoria');g.hidden=false;aplica(c&&g.querySelector('[data-c="'+c+'"]')?c:'')})()"""


def chips(lote, pre, paginado):
    conta = {x["slug"]: sum(1 for a in lote if a["editoria"] == x["slug"]) for x in portal.EDITORIAS}
    bts = "".join(f'<button type="button" data-c="{x["slug"]}" data-t="{e(x["nome"])}" data-pag="{pre}{x["slug"]}/" aria-pressed="false">{e(x["nome"])}<small>{conta[x["slug"]]}</small></button>'
                  for x in portal.EDITORIAS if conta[x["slug"]])
    nota = '<p class="cat-nota" hidden>Esta página mostra só parte do arquivo. <a href="#">Ver todas</a></p>' if paginado else ""
    return f'<div class="cats" role="group" aria-label="Filtrar por editoria" hidden><button type="button" data-c="" aria-pressed="true">Todas<small>{len(lote)}</small></button>{bts}</div>{nota}'


def listagem(lista, base, titulo_h1, descricao_pag, intro, trilha_itens, atual, classe="", extra_topo="", filtro=False, pub_pos=None, ed_pub=None, ld_extra=()):
    """Páginas de lista paginadas (/noticias/, /<editoria>/, /opiniao/): 1ª em /<base>/, as outras em /<base>/pagina/<n>/."""
    por = portal.CFG.get("noticias_por_pagina", 24)
    paginas = [lista[i:i + por] for i in range(0, len(lista), por)] or [[]]
    for num, lote in enumerate(paginas, 1):
        pre = "../" if num == 1 else "../../../"
        rel = f"{base}/" if num == 1 else f"{base}/pagina/{num}/"
        url = portal.url(rel)
        suf = "" if num == 1 else f" (página {num})"
        ant = "" if num == 1 else f'<a href="{pre}{base}/{"" if num == 2 else f"pagina/{num - 1}/"}" rel="prev">← Mais recentes</a>'
        prox = f'<a href="{pre}{base}/pagina/{num + 1}/" rel="next">Mais antigas →</a>' if num < len(paginas) else ""
        nav = f'<nav class="paginas" aria-label="Páginas">{ant}<span>Página {num} de {len(paginas)}</span>{prox}</nav>' if len(paginas) > 1 else ""
        itens = "".join(cartao(a, pre) for a in lote)
        vazio = '' if lote else '<p class="bloco vazio">Ainda não há matérias publicadas aqui. Assine a newsletter para saber quando sair a primeira.</p>'
        pub_html, tem_pub = anuncios.espaco(pub_pos, pre, ed_pub) if pub_pos else ("", False)
        trl = trilha(("Início", pre), *[(r, pre + h) for r, h in trilha_itens], (e(titulo_h1) + suf, ""))
        corpo = f"""{cabecalho(pre, atual, sub=num > 1)}
<main id="conteudo" class="in arq {classe}">{trl}
 <div class="arq-topo"><h1>{e(titulo_h1)}{suf}</h1><p>{intro}</p></div>
 {pub_html}{extra_topo if num == 1 else ''}
 {chips(lote, pre, len(paginas) > 1) if filtro and lote else ''}
 {vazio}<ul class="grade-n">{itens}</ul>
 {nav}
 {f'<script>{JS_FILTRO}</script>' if filtro else ''}
</main>
{rodape(pre)}"""
        ld = seo.script(seo.trilha(("Início", f"{portal.SITE}/"), *[(r, portal.url(h)) for r, h in trilha_itens], (titulo_h1 + suf, url)), *ld_extra)
        escrever(f"{rel}index.html", pagina(f"{titulo_h1}{suf} | {portal.NOME}", descricao_pag + suf, url, f"{portal.SITE}/marca/capa.png",
                                           pre, corpo, jsonld=ld, indexavel=bool(lote), pub=tem_pub))
    return len(paginas)


# ---------- páginas ----------

def build_home(ps, evs):
    pre = ""
    jornal = [a for a in ps if a["tipo"] != "patrocinado"]
    cands = [a for a in jornal if a.get("manchete")] or [a for a in jornal if a.get("imagem")] or jornal
    m = cands[0] if cands else None
    resto = [a for a in ps if a is not m]
    if m:
        topo = bloco_manchete(m, pre)
        ultimas = "".join(item_lista(a, pre) for a in resto[:8])
        ultimas = f'<section class="bloco ultimas"><h2 class="h-sec">Últimas notícias <a href="noticias/">Ver todas ({len(ps)})</a></h2><ul class="lista-n">{ultimas}</ul></section>' if ultimas else ""
    else:
        topo = (f'<section class="bloco manchete"><div class="txt"><h1 class="titulo m-tit">{e(portal.NOME)}</h1>'
                f'<p class="lf">{e(portal.CFG.get("descricao", ""))} As primeiras matérias estão em preparação e passam por revisão humana antes de ir ao ar.</p>'
                f'<a class="btn" href="newsletter/">{icone("email")}Avise-me quando sair</a></div></section>')
        ultimas = ""
    dest = [a for a in jornal if a.get("destaque") and a is not m][:5]
    destaques = (f'<section class="bloco destaques"><h2 class="h-sec">Destaques <a href="politica-editorial/#destaques">Critério</a></h2><ol>'
                 + "".join(f'<li><a href="noticias/{a["slug"]}/"><span><b>{e(a["titulo"])}</b><span class="meta">{e(nome_ed(a["editoria"]))}</span></span></a></li>' for a in dest)
                 + "</ol></section>") if dest else ""
    ag = "".join(item_agenda(ev, pre) for ev in evs[:5])
    bloco_ag = (f'<section class="bloco agenda ed-eventos"><h2 class="h-sec">Agenda <a href="eventos/">Eventos</a></h2>'
                + (f"<ul>{ag}</ul>" if ag else '<p class="vazio">Nenhum evento confirmado na agenda. <a href="contato/#evento">Divulgue o seu</a>.</p>') + "</section>")
    pub_lat, t1 = anuncios.espaco("lateral", pre)
    pub_topo, t2 = anuncios.espaco("home-topo", pre, classe="pub-topo")
    pub_meio, t3 = anuncios.espaco("home-meio", pre)
    faixas = []
    for x in portal.visiveis():
        lista = [a for a in ps if a["editoria"] == x["slug"] and a is not m][:4]
        if not lista:
            continue
        faixas.append(f'<section class="bloco faixa ed-{x["slug"]}"><h2 class="h-sec">{e(x["nome"])} <a href="{x["slug"]}/">Ver tudo</a></h2>'
                      f'<ul class="cards">{"".join(mini(a, pre) for a in lista)}</ul></section>')
    if len(faixas) >= 2 and pub_meio:
        faixas.insert(2, pub_meio)
    ops = [a for a in ps if a["tipo"] == "opiniao"][:4]
    opinioes = (f'<section class="bloco opinioes"><h2 class="h-sec">Opinião <a href="opiniao/">Ver todas</a></h2><ul>'
                + "".join(f'<li><a href="noticias/{a["slug"]}/"><span class="t">{e(a["titulo"])}</span><span class="quem">{e(autor_nome(a))}</span></a></li>' for a in ops)
                + "</ul></section>") if ops else ""
    texto_portal = f"{portal.NOME}: {portal.CFG.get('descricao', '')}"
    cta = (f'<section class="bloco cta-news"><h2 class="h-sec">Newsletter</h2><p>As principais notícias do dia, com fontes e contexto, no seu e-mail. '
           f'Escolha as editorias que quer receber.</p><a class="btn" href="newsletter/">{icone("email")}Quero receber</a>'
           f'{botao_compartilhar(texto_portal, f"{portal.SITE}/", "Compartilhar o portal")}</section>')
    ultima = data_longa(ps[0]["publicado_em"]) if ps else ""
    corpo = f"""{cabecalho(pre, "inicio")}
<main id="conteudo" class="in">
 {f'<p class="edicao meta">Atualizado em {ultima}</p>' if ultima else ''}
 <div class="grade">
  {topo}
  {pub_topo}
  {ultimas}
  <aside class="lado" aria-label="Destaques e agenda">{destaques}{bloco_ag}{pub_lat}</aside>
  {f'<div class="faixas">{"".join(faixas)}</div>' if faixas else ''}
  {opinioes}
  {cta}
 </div>
</main>
{rodape(pre)}"""
    titulo = f"{portal.NOME}: {portal.CFG.get('slogan', '').rstrip('.')}"
    descr = f"{portal.CFG.get('descricao', '')} " + (f"Em destaque: {m['titulo']}." if m else "")
    img = imagem_og(m) if m else f"{portal.SITE}/marca/capa.png"
    escrever("index.html", pagina(titulo, descr.strip(), f"{portal.SITE}/", img, pre, corpo, jsonld=seo.script(seo.site()), pub=t1 or t2 or t3))


def build_materia(a, todos):
    pre = "../../"
    url = url_materia(a)
    ed = portal.editoria(a["editoria"])
    texto_cp = f"{a['titulo']} ({portal.NOME})"
    pub_meio, t1 = ("", False) if a["tipo"] == "patrocinado" or a.get("sem_anuncios") else anuncios.espaco("artigo-meio", pre, a["editoria"])
    pub_fim, t2 = ("", False) if a["tipo"] == "patrocinado" or a.get("sem_anuncios") else anuncios.espaco("artigo-fim", pre, a["editoria"])
    blocos, pars = [], 0
    if a.get("lide"):
        blocos.append(f'<p class="lide">{e(a["lide"])}</p>')
    if a.get("analise"):
        blocos.append(f'<aside class="analise" aria-label="Análise da redação"><span class="r">Por que importa · análise da redação</span><p>{e(a["analise"])}</p></aside>')
    for b in a["corpo"]:
        if isinstance(b, str):
            blocos.append(f"<p>{e(b)}</p>")
            pars += 1
            if pars == 3 and pub_meio:
                blocos.append(pub_meio)
                pub_meio = ""
        elif "intertitulo" in b:
            blocos.append(f'<h2>{e(b["intertitulo"])}</h2>')
        elif "citacao" in b:
            f = a["fontes"][b["fonte"]]
            quem = e(b["autor"]) + (f", {e(b['cargo'])}" if b.get("cargo") else "")
            blocos.append(f'<blockquote><p>“{e(b["citacao"])}”</p><footer>{quem}, em <a href="{e(f["url"])}" target="_blank" rel="noopener">{e(f["nome"])}</a></footer></blockquote>')
    if pub_meio:
        blocos.append(pub_meio)
    aviso = ""
    if a["tipo"] == "patrocinado":
        pat = a["patrocinador"]
        nome_p = f'<a href="{e(pat["url"])}" target="_blank" rel="sponsored noopener">{e(pat["nome"])}</a>' if pat.get("url") else e(pat["nome"])
        aviso = (f'<div class="aviso-pat" role="note"><b>Conteúdo patrocinado por {nome_p}.</b>'
                 f'<span>Este texto é publicidade: foi pago pelo anunciante e não é produzido pela redação. Saiba mais na <a href="{pre}politica-editorial/#publicidade">política editorial</a>.</span></div>')
    elif a["tipo"] == "opiniao":
        col = a.get("colaborador")
        quem = f" {e(col['nome'])}, {e(col['descricao'])}." if col else ""
        aviso = (f'<div class="analise" role="note"><span class="r">Opinião</span><p>Este é um artigo de opinião.{quem} As ideias são de responsabilidade de quem assina '
                 f'e não representam necessariamente a posição do {e(portal.NOME)}.</p></div>')
    corr = a.get("correcoes") or []
    nota_corr = f' · <a href="#correcoes">Corrigida em {data_longa(corr[-1]["data"])}</a>' if corr else ""
    atual = (f' · Atualizado em <time datetime="{a["atualizado_em"]}">{data_longa(a["atualizado_em"], hora=True)}</time>'
             if a.get("atualizado_em") and a["atualizado_em"] > a["publicado_em"] else "")
    bib = a.get("referencias_biblicas") or []
    bloco_bib = (f'<section class="biblia"><h2>Passagens citadas</h2><ul>{"".join(f"<li>{e(r)}</li>" for r in bib)}</ul>'
                 + (f'<small>Tradução: {e(a["versao_biblica"])}.</small>' if a.get("versao_biblica") else "") + "</section>") if bib else ""
    faq = a.get("faq") or []
    bloco_faq = (f'<section class="bloco faq" id="perguntas"><h2>Perguntas frequentes</h2>'
                 + "".join(f'<details><summary>{e(q["pergunta"])}</summary><p>{e(q["resposta"])}</p></details>' for q in faq) + "</section>") if faq else ""
    afil = a.get("afiliados") or []
    bloco_afil = (f'<section class="bloco afiliados"><h2>Onde encontrar</h2><p>Links de afiliado: se você comprar por eles, o {e(portal.NOME)} pode receber uma comissão, '
                  f'sem custo extra para você. A recomendação é editorial e não depende da comissão.</p><ul>'
                  + "".join(f'<li><a href="{e(l["url"])}" target="_blank" rel="sponsored nofollow noopener">{e(l["texto"])}</a> ({e(l["loja"])})</li>' for l in afil)
                  + "</ul></section>") if afil else ""
    bloco_corr = (f'<section class="bloco correcoes" id="correcoes"><h2>Correções</h2><ul>'
                  + "".join(f'<li><time datetime="{c["data"]}">{data_longa(c["data"])}</time>: {e(c["texto"])}</li>' for c in corr) + "</ul></section>") if corr else ""
    tags = "".join(f"<li>{e(t)}</li>" for t in a.get("tags") or [])
    leia = "".join(f'<li><a href="{pre}noticias/{o["slug"]}/">{e(o["titulo"])}</a></li>' for o in relacionadas(a, todos))
    rev = portal.EQUIPE.get(a["revisao"]["revisor"], {})
    ia = a["ia"]
    uso_ia = (f"Produzida com apoio de ferramentas de inteligência artificial ({e(ia['uso'])}). O texto foi conferido contra as fontes e revisado por uma pessoa da redação antes da publicação."
              if ia["usada"] else "Produzida sem uso de ferramentas de inteligência artificial.")
    natureza = {"noticia": "Notícia: relato de fatos verificados, sem opinião da redação fora do quadro de análise.",
                "analise": "Análise: interpretação de fatos verificados, assinada, com as fontes abaixo.",
                "opiniao": "Opinião: ponto de vista de quem assina.",
                "explicativo": "Explica: conteúdo de referência, atualizado quando há fato novo.",
                "patrocinado": "Conteúdo patrocinado: publicidade paga, identificada em todas as partes da página."}[a["tipo"]]
    fontes = "".join(f'<li><a href="{e(f["url"])}" target="_blank" rel="noopener">{e(f["nome"])}</a> <span>{"fonte primária" if f["tipo"] == "primaria" else "outro veículo"} · consulta em {e(f["data"])}</span></li>'
                     for f in a.get("fontes") or [])
    corrigir = f'{pre}contato/?assunto=correcao&url={url}#correcao'
    transp = f"""<section class="bloco transp" id="transparencia"><h2>Como esta matéria foi feita</h2><dl>
  <dt>Tipo de conteúdo</dt><dd>{natureza}</dd>
  {f'<dt>Fontes</dt><dd><ul class="fontes">{fontes}</ul></dd>' if fontes else ''}
  <dt>Revisão</dt><dd>Revisada por {e(rev.get("nome", ""))} em {data_longa(a["revisao"]["data"])}.</dd>
  <dt>Uso de inteligência artificial</dt><dd>{uso_ia}</dd>
  <dt>Encontrou um erro?</dt><dd><a href="{e(corrigir)}">Peça uma correção</a>. Erros confirmados são corrigidos nesta página, com data. Veja a <a href="{pre}politica-editorial/">política editorial</a>.</dd>
 </dl></section>"""
    corpo = f"""{cabecalho(pre, a["editoria"] if a["tipo"] != "opiniao" else "opiniao", sub=True)}
<main id="conteudo" class="in"><div class="materia {classe_ed(a)}">
 {trilha(("Início", pre), (e(ed["nome"]), f"{pre}{a['editoria']}/"), (e(a["titulo"]), ""))}
 <article class="bloco cab">
  <span class="etq">{etiquetas(a, pre)}</span>
  <h1>{e(a['titulo'])}</h1>
  <p class="lf">{e(a['linha_fina'])}</p>
  {aviso}
  <p class="assinatura">Por {autor_link(a, pre)} · <time datetime="{a['publicado_em']}">{data_longa(a['publicado_em'], hora=True)}</time>{atual}{nota_corr}</p>
 </article>
 {f'<div class="bloco">{figura(a, pre, "(min-width: 760px) 720px, 100vw", prioridade=True)}</div>' if a.get("imagem") else ''}
 <div class="bloco"><div class="texto">{"".join(blocos)}</div></div>
 {bloco_bib}{bloco_faq}{bloco_afil}{bloco_corr}
 {f'<div class="bloco"><ul class="tags" aria-label="Assuntos">{tags}</ul></div>' if tags else ''}
 {pub_fim}
 {convite_compartilhar(texto_cp, url, "Esta matéria pode ajudar alguém?", "Envie para quem precisa ler.")}
 {interacoes(pre, f"/noticias/{a['slug']}/")}
 {f'<section class="bloco relac"><h2>Leia também</h2><ul>{leia}</ul></section>' if leia else ''}
 {transp}
</div></main>
{rodape(pre, barra_leitura(texto_cp, url, pre=pre))}"""
    imgs = []
    if a.get("imagem"):
        try:
            imgs.append(f"{portal.SITE}/{imagens.larga(a['imagem']['arquivo'])}")
        except Exception as ex:  # imagem com problema não segura a matéria
            print(f"  aviso: sem versão larga para {a['slug']} ({ex.__class__.__name__})")
        orig = f"{portal.SITE}/{imagens.publicar(a['imagem']['arquivo'])}"
        if orig not in imgs:
            imgs.append(orig)
    nos = [seo.artigo(a, url, imgs or [f"{portal.SITE}/marca/capa.png"], ed["nome"]),
           seo.trilha(("Início", f"{portal.SITE}/"), (ed["nome"], portal.url(f"{a['editoria']}/")), (a["titulo"], url))]
    if faq:
        nos.append(seo.faq(faq))
    t_busca = a.get("titulo_seo") or a["titulo"]
    t_busca = t_busca if len(t_busca) > 50 else f"{t_busca} | {portal.NOME}"
    extra = (f'\n<meta property="article:published_time" content="{a["publicado_em"]}">'
             + (f'\n<meta property="article:modified_time" content="{a["atualizado_em"]}">' if a.get("atualizado_em") else "")
             + f'\n<meta property="article:section" content="{e(ed["nome"])}">'
             + "".join(f'\n<meta property="article:tag" content="{e(t)}">' for t in a.get("tags") or []))
    escrever(f"noticias/{a['slug']}/index.html", pagina(t_busca, resumo(a), url, imagem_og(a), pre, corpo, "article", extra, seo.script(*nos), pub=t1 or t2))


def build_listas(ps, evs):
    listagem(ps, "noticias", "Todas as notícias", f"Arquivo de notícias do {portal.NOME}, com fontes e data.",
             f"Tudo o que o {e(portal.NOME)} publicou, da mais recente para a mais antiga. Fato e opinião sempre separados.",
             [], "", filtro=True)
    for x in portal.EDITORIAS:
        if not x.get("visivel", True):
            continue
        lista = [a for a in ps if a["editoria"] == x["slug"]]
        extra, ld = "", ()
        if x["slug"] == "eventos":
            ag = "".join(item_agenda(ev, "../") for ev in evs)
            extra = (f'<section class="bloco agenda ed-eventos" id="agenda"><h2 class="h-sec">Agenda de eventos <a href="../contato/#evento">Divulgue o seu evento</a></h2>'
                     + (f"<ul>{ag}</ul>" if ag else '<p class="vazio">Nenhum evento confirmado no momento.</p>') + "</section>")
            ld = tuple(seo.evento(ev) for ev in evs if ev.get("confirmado", True) and not ev.get("patrocinado"))
        listagem(lista, x["slug"], x["nome"], x["descricao"], e(x["descricao"]), [], x["slug"], classe=f"ed-{x['slug']}",
                 extra_topo=extra, pub_pos="editoria-topo", ed_pub=x["slug"], ld_extra=ld)
    listagem([a for a in ps if a["tipo"] == "opiniao"], "opiniao", "Opinião", f"Artigos de opinião publicados no {portal.NOME}.",
             f"Artigos assinados. As ideias são de quem escreve e não representam necessariamente a posição do {e(portal.NOME)}; "
             "o noticiário fica separado, nas editorias.", [], "opiniao")


def build_autores(ps):
    for slug, p in portal.EQUIPE.items():
        pre = "../../"
        url = portal.url(f"autores/{slug}/")
        dele = [a for a in ps if a.get("autor") == slug]
        itens = "".join(cartao(a, pre, "h3") for a in dele)
        redes = "".join(f'<li><a href="{e(r)}" target="_blank" rel="noopener me">{e(r)}</a></li>' for r in p.get("redes", []))
        corpo = f"""{cabecalho(pre, "", sub=True)}
<main id="conteudo" class="in"><div class="doc">
 {trilha(("Início", pre), ("Expediente", f"{pre}expediente/"), (e(p["nome"]), ""))}
 <article class="bloco"><h1>{e(p["nome"])}</h1><p class="lf">{e(p.get("cargo", ""))}</p></article>
 <section class="bloco"><h2>Sobre</h2><div class="corpo"><p>{e(p.get("bio", ""))}</p>{f'<ul>{redes}</ul>' if redes else ''}</div></section>
 <section class="bloco"><h2>Matérias assinadas</h2>{f'<ul class="grade-n">{itens}</ul>' if itens else '<p class="vazio">Nenhuma matéria assinada ainda.</p>'}</section>
</div></main>
{rodape(pre)}"""
        ld = {"@type": "ProfilePage", "@id": url, "url": url, "name": p["nome"], "mainEntity": seo.pessoa(slug)}
        escrever(f"autores/{slug}/index.html", pagina(f"{p['nome']} | {portal.NOME}", f"{p['nome']}, {p.get('cargo', '')} do {portal.NOME}.", url,
                                                     f"{portal.SITE}/marca/capa.png", pre, corpo, "profile",
                                                     jsonld=seo.script(ld, seo.trilha(("Início", f"{portal.SITE}/"), ("Expediente", portal.url("expediente/")), (p["nome"], url)))))


def preencher(texto, pre="../"):
    """Troca {campo} pelos dados de config/portal.json; campo vazio vira um aviso visível de pendência."""
    cfg = portal.CFG
    valores = {"nome": portal.NOME, "url": portal.SITE, "descricao": cfg.get("descricao", ""), "slogan": cfg.get("slogan", ""),
               "email_contato": cfg.get("email_contato", ""), "email_comercial": cfg.get("email_comercial") or cfg.get("email_contato", ""),
               "email_correcoes": cfg.get("email_correcoes") or cfg.get("email_contato", ""),
               "responsavel": cfg.get("responsavel_editorial", {}).get("nome", ""), "razao_social": cfg.get("razao_social") or portal.NOME,
               "cnpj": cfg.get("cnpj", ""), "fundacao": cfg.get("fundacao", "")}

    def troca(m):
        v = valores.get(m.group(1))
        if v is None:
            return m.group(0)
        if not v:
            return '<span class="pend">a definir</span>'
        if m.group(1).startswith("email"):
            return f'<a href="mailto:{e(v)}">{e(v)}</a>'
        return e(v)
    s = re.sub(r"\{([a-z_]+)\}", troca, e(texto).replace("&#x27;", "'"))
    # links simples no texto das páginas: [rótulo](/caminho/) ou [rótulo](https://...)
    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: f'<a href="{pre + m.group(2)[1:] if m.group(2).startswith("/") else m.group(2)}">{m.group(1)}</a>', s)


def build_institucionais():
    feitas = []
    pasta = portal.CONTEUDO / "paginas" if (portal.CONTEUDO / "paginas").exists() else portal.ROOT / "conteudo" / "paginas"
    for arq in sorted(pasta.glob("*.json")):
        p = json.loads(arq.read_text(encoding="utf-8"))
        if p.get("so_com_api") and not (portal.CFG.get("interacoes") or {}).get("api"):
            continue
        pre = "../"
        url = portal.url(f"{p['slug']}/")
        secoes = []
        for s in p.get("secoes", []):
            if s.get("so_com_api") and not (portal.CFG.get("interacoes") or {}).get("api"):
                continue
            pars = "".join(f"<p>{preencher(x, pre)}</p>" for x in s.get("paragrafos", []))
            lista = "".join(f"<li>{preencher(x, pre)}</li>" for x in s.get("lista", []))
            form = formulario(s["formulario"], pre, p["slug"]) if s.get("formulario") else ""
            gerado = gerados(s["gerado"], pre) if s.get("gerado") else ""
            secoes.append(f'<section class="bloco"{f" id=\"{s["id"]}\"" if s.get("id") else ""}><h2>{e(s["titulo"])}</h2><div class="corpo">{pars}{f"<ul>{lista}</ul>" if lista else ""}{gerado}{form}</div></section>')
        corpo = f"""{cabecalho(pre, "")}
<main id="conteudo" class="in"><div class="doc">
 {trilha(("Início", pre), (e(p["titulo"]), ""))}
 <article class="bloco"><h1>{e(p["titulo"])}</h1><p class="lf">{preencher(p["lide"], pre)}</p>{f'<p class="meta">Atualizada em {data_longa(p["atualizado_em"])}</p>' if p.get("atualizado_em") else ''}</article>
 {"".join(secoes)}
</div></main>
{rodape(pre)}"""
        ld = seo.script({"@type": p.get("schema", "WebPage"), "@id": url, "url": url, "name": p["titulo"], "inLanguage": "pt-BR", "publisher": {"@id": seo.org_id()}},
                        seo.trilha(("Início", f"{portal.SITE}/"), (p["titulo"], url)))
        escrever(f"{p['slug']}/index.html", pagina(f"{p['titulo']} | {portal.NOME}", re.sub(r"\{[a-z_]+\}", portal.NOME, p["descricao"]), url,
                                                  f"{portal.SITE}/marca/capa.png", pre, corpo, jsonld=ld))
        feitas.append((p["slug"], p.get("atualizado_em")))
    return feitas


def gerados(tipo, pre):
    """Partes das páginas institucionais que saem da configuração (expediente, espaços de anúncio, editorias)."""
    if tipo == "equipe":
        cfg = portal.CFG
        resp = cfg.get("responsavel_editorial", {})
        itens = "".join(f'<li><a href="{pre}autores/{s}/">{e(p["nome"])}</a>, {e(p.get("cargo", ""))}</li>' for s, p in portal.EQUIPE.items())
        r = (f'<p><b>{e(resp.get("cargo", "Responsável editorial"))}:</b> {e(resp["nome"])}</p>' if resp.get("nome")
             else '<p class="pend">Responsável editorial a definir em config/portal.json.</p>')
        return r + (f'<ul class="equipe">{itens}</ul>' if itens else '<p class="pend">Equipe a cadastrar em config/equipe.json (somente pessoas reais).</p>')
    if tipo == "espacos":
        es = [x for x in portal.ANUNCIOS.get("espacos", []) if x.get("descricao")]
        return "<ul>" + "".join(f'<li><b>{e(x["descricao"])}</b>: {x["altura_celular"] or "–"} px de altura no celular, {x["altura_computador"]} px no computador</li>' for x in es) + "</ul>"
    if tipo == "editorias":
        return "<ul>" + "".join(f'<li><a href="{pre}{x["slug"]}/">{e(x["nome"])}</a>: {e(x["descricao"])}</li>' for x in portal.visiveis()) + "</ul>"
    return ""


def build_404():
    # servida em qualquer profundidade: caminhos absolutos a partir da raiz do site (com o caminho-base, se houver)
    pre = portal.BASE + "/"
    corpo = f"""{cabecalho(pre, "")}
<main id="conteudo" class="in"><div class="doc"><section class="bloco">
 <h1>Página não encontrada</h1>
 <p class="lf">O endereço pode ter mudado ou sido digitado errado.</p>
 <div class="corpo"><ul><li><a href="{pre}">Página inicial</a></li><li><a href="{pre}noticias/">Todas as notícias</a></li>{"".join(f'<li><a href="{pre}{x["slug"]}/">{e(x["nome"])}</a></li>' for x in portal.visiveis())}</ul></div>
</section></div></main>
{rodape(pre, "")}"""
    escrever("404.html", pagina(f"Página não encontrada | {portal.NOME}", "Página não encontrada.", "", f"{portal.SITE}/marca/capa.png", pre, corpo, indexavel=False))


# ---------- arquivos para buscadores e leitores de feed ----------

def build_feed(ps):
    itens = []
    for a in [a for a in ps if a["tipo"] != "patrocinado"][:30]:
        d = quando(a["publicado_em"])
        img = f'<enclosure url="{xesc(portal.SITE + "/" + imagens.publicar(a["imagem"]["arquivo"]))}" type="image/jpeg" length="0"/>' if a.get("imagem") else ""
        itens.append(f"""<item><title>{xesc(a['titulo'])}</title><link>{xesc(url_materia(a))}</link><guid isPermaLink="true">{xesc(url_materia(a))}</guid>
<pubDate>{d.strftime('%a, %d %b %Y %H:%M:%S %z')}</pubDate><category>{xesc(nome_ed(a['editoria']))}</category><dc:creator>{xesc(autor_nome(a))}</dc:creator>
<description>{xesc(resumo(a))}</description>{img}</item>""")
    escrever("feed.xml", f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:atom="http://www.w3.org/2005/Atom"><channel>
<title>{xesc(portal.NOME)}</title><link>{xesc(portal.SITE)}/</link><description>{xesc(portal.CFG.get('descricao', ''))}</description><language>pt-br</language>
<atom:link href="{xesc(portal.SITE)}/feed.xml" rel="self" type="application/rss+xml"/>
{chr(10).join(itens)}
</channel></rss>
""")


def build_sitemaps(ps, institucionais, hoje):
    """sitemap.xml (todas as páginas indexáveis) e sitemap-noticias.xml (últimas 48 h, regra do Google News).

    O lastmod vem do próprio conteúdo (atualizado_em ou publicado_em), não da hora do build: mudar o template não
    mexe no lastmod. Páginas vazias (noindex) ficam fora."""
    def lm(a):
        return a.get("atualizado_em") or a["publicado_em"]
    maior = lambda lista: max((lm(a) for a in lista), key=lambda x: quando(x), default=None)  # noqa: E731
    entradas = [(f"{portal.SITE}/", maior(ps)), (portal.url("noticias/"), maior(ps))] if ps else [(f"{portal.SITE}/", None)]
    for x in portal.visiveis():
        lista = [a for a in ps if a["editoria"] == x["slug"]]
        if lista:
            entradas.append((portal.url(f"{x['slug']}/"), maior(lista)))
    ops = [a for a in ps if a["tipo"] == "opiniao"]
    if ops:
        entradas.append((portal.url("opiniao/"), maior(ops)))
    entradas += [(url_materia(a), lm(a)) for a in ps]
    entradas += [(portal.url(f"autores/{s}/"), maior([a for a in ps if a.get("autor") == s])) for s in portal.EQUIPE]
    entradas += [(portal.url(f"{s}/"), d) for s, d in institucionais]
    linhas = "\n".join(f"  <url><loc>{xesc(u)}</loc>{f'<lastmod>{d}</lastmod>' if d else ''}</url>" for u, d in entradas)
    escrever("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{linhas}\n</urlset>\n')
    limite = datetime.combine(hoje, datetime.max.time(), FUSO) - timedelta(hours=48)
    recentes = [a for a in ps if portal.TIPOS[a["tipo"]][2] and quando(a["publicado_em"]) >= limite]
    news = "".join(f"""  <url><loc>{xesc(url_materia(a))}</loc><news:news><news:publication><news:name>{xesc(portal.NOME)}</news:name><news:language>pt</news:language></news:publication>"""
                   f"""<news:publication_date>{a['publicado_em']}</news:publication_date><news:title>{xesc(a['titulo'])}</news:title></news:news></url>\n""" for a in recentes)
    escrever("sitemap-noticias.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
             f'xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">\n{news}</urlset>\n')
    return len(entradas), len(recentes)


# robôs que coletam texto para treinar modelos (não citam a fonte na resposta); buscadores e assistentes ficam liberados
TREINO_IA = ["GPTBot", "Google-Extended", "CCBot", "ClaudeBot", "anthropic-ai", "Applebot-Extended", "Bytespider", "meta-externalagent", "cohere-training-data-crawler"]


def build_robots():
    if portal.EXEMPLO:
        escrever("robots.txt", "# Prévia de exemplo: nada aqui deve ser indexado.\nUser-agent: *\nDisallow: /\n")
        return
    bloqueio = ""
    if portal.CFG.get("robots", {}).get("bloquear_treino_ia"):
        bloqueio = "\n# Coleta para treino de modelos de IA: não autorizada (config/portal.json, robots.bloquear_treino_ia)\n" + \
                   "".join(f"User-agent: {b}\n" for b in TREINO_IA) + "Disallow: /\n"
    escrever("robots.txt", f"""# {portal.NOME}: buscadores e assistentes de IA que citam a fonte são bem-vindos.
User-agent: *
Allow: /
{bloqueio}
Sitemap: {portal.SITE}/sitemap.xml
Sitemap: {portal.SITE}/sitemap-noticias.xml
""")


def build_llms(ps):
    """llms.txt (proposta de llmstxt.org): resumo em texto simples para assistentes de IA. Só o que está publicado."""
    cfg = portal.CFG
    linhas = [f"# {portal.NOME}", "", f"> {cfg.get('descricao', '')} Veículo jornalístico cristão, em português do Brasil.", "",
              "Toda notícia lista as fontes consultadas, com link e data, separa fato de opinião e passa por revisão humana antes de publicar. "
              "Conteúdo patrocinado é sempre identificado. Correções ficam registradas na própria página.", "", "## Editorias", ""]
    linhas += [f"- [{x['nome']}]({portal.url(x['slug'] + '/')}): {x['descricao']}" for x in portal.visiveis()]
    linhas += ["", "## Matérias recentes", ""]
    linhas += [f"- [{a['titulo']}]({url_materia(a)}) ({quando(a['publicado_em']).date().isoformat()}, {portal.TIPOS[a['tipo']][0].lower()})"
               for a in ps if a["tipo"] != "patrocinado"][:30]
    linhas += ["", "## Sobre o veículo", "", f"- [Política editorial]({portal.url('politica-editorial/')}): como apuramos, separamos fato de opinião e corrigimos",
               f"- [Expediente]({portal.url('expediente/')})", f"- [Quem somos]({portal.url('sobre/')})", ""]
    escrever("llms.txt", "\n".join(linhas))


def build_busca(ps):
    regs = [{"t": "n", "n": a["titulo"], "s": f"{nome_ed(a['editoria'])} · {data_curta(a['publicado_em'])}", "u": f"noticias/{a['slug']}/",
             "a": " ".join(a.get("tags") or [])} for a in ps]
    regs += [{"t": "e", "n": x["nome"], "s": x["descricao"], "u": f"{x['slug']}/"} for x in portal.visiveis()]
    regs += [{"t": "p", "n": p["nome"], "s": p.get("cargo", ""), "u": f"autores/{s}/"} for s, p in portal.EQUIPE.items()]
    escrever("busca.json", json.dumps(regs, ensure_ascii=False, separators=(",", ":")))
    return len(regs)


def copiar_estaticos():
    for pasta in ("fontes", "marca", "js"):
        src = portal.ROOT / "assets" / pasta
        if src.exists():
            shutil.copytree(src, portal.SAIDA / pasta, dirs_exist_ok=True)
    chave = portal.CFG.get("indexnow_chave")
    if chave and not portal.EXEMPLO:
        escrever(f"{chave}.txt", chave)
    escrever(".nojekyll", "")
    # ads.txt: declara quem pode vender os espaços do portal (exigido pelo AdSense); só existe com conta configurada
    cliente = portal.ANUNCIOS.get("adsense_cliente", "")
    if cliente and not portal.EXEMPLO:
        escrever("ads.txt", f"google.com, {cliente.removeprefix('ca-')}, DIRECT, f08c47fec0942fa0\n")


def limpar_saida():
    s = portal.SAIDA.resolve()
    # trava: só apaga pastas de saída do próprio projeto
    if s.parent != portal.ROOT.resolve() or not s.name.startswith("publico"):
        sys.exit(f"Saída recusada: {s} (use uma pasta publico* dentro do projeto)")
    if s.exists():
        shutil.rmtree(s)
    s.mkdir()


def main(argv=None):
    global HOJE
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--producao", action="store_true")
    ap.add_argument("--exemplo", action="store_true")
    ap.add_argument("--saida")
    ap.add_argument("--hoje")
    ap.add_argument("--sem-og", action="store_true")
    ar = ap.parse_args(argv)
    if ar.exemplo and ar.producao:
        sys.exit("--exemplo e --producao não combinam")
    ex = portal.ROOT / "exemplos"
    saida = Path(ar.saida) if ar.saida else portal.ROOT / ("publico-exemplo" if ar.exemplo else "publico")
    if not saida.is_absolute():
        saida = portal.ROOT / saida
    portal.iniciar(conteudo=ex / "conteudo" if ar.exemplo else None, config=ex / "config" if ar.exemplo else None, saida=saida, exemplo=ar.exemplo)
    erros = portal.problemas_config(producao=ar.producao)
    if erros:
        sys.exit("Configuração com problema:\n - " + "\n - ".join(erros))
    for aviso in portal.avisos_config() if not ar.exemplo else []:
        print("⚠️ " + aviso)
    HOJE = date.fromisoformat(ar.hoje) if ar.hoje else datetime.now(FUSO).date()
    if ar.sem_og:
        import og
        og.DESLIGADO = True
    ARQUIVOS_ESCRITOS.clear()
    ps = carregar(HOJE)
    evs = agenda(HOJE)
    limpar_saida()
    copiar_estaticos()
    import og
    og.gerar(ps)
    build_home(ps, evs)
    for a in ps:
        build_materia(a, ps)
    build_listas(ps, evs)
    build_autores(ps)
    inst = build_institucionais()
    build_404()
    build_feed(ps)
    total, recentes = build_sitemaps(ps, inst, HOJE)
    build_robots()
    build_llms(ps)
    n_busca = build_busca(ps)
    print(f"ok {portal.SAIDA.name}/: {len(ps)} matérias publicadas, {total} URLs no sitemap, {recentes} no sitemap de notícias, "
          f"{n_busca} registros na busca, {len(ARQUIVOS_ESCRITOS)} arquivos")
    return ps


if __name__ == "__main__":
    main()
