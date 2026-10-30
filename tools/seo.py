"""Dados estruturados (JSON-LD) das páginas, num lugar só.

Regra: só entra o que está visível na página e é verdade. Nada de Review, AggregateRating ou Product:
o site não dá nota própria (a nota BGG é de terceiros) e não vende jogos.
"""
import json
from html import escape
from pathlib import Path

from endereco import SITE  # noqa: E402  (config/portal.json)
CFG = json.loads((Path(__file__).resolve().parent.parent / "config" / "portal.json").read_text(encoding="utf-8"))
ORG_ID = f"{SITE}/#organizacao"
SITE_ID = f"{SITE}/#site"
# Medidor de visitas sem cookies (Cloudflare Web Analytics); vai no fim do <body> de todas as páginas.
# Sai do analytics.cloudflare_token de config/portal.json; vazio = sem medidor.
_TOKEN = (CFG.get("analytics") or {}).get("cloudflare_token", "")
ANALYTICS = (f'<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon=\'{{"token": "{escape(_TOKEN)}"}}\'></script>'
             if _TOKEN else "")
FEED = f"{SITE}/feed.xml"
# nome de cada editoria pelo slug: há notas que guardam a editoria pelo slug ("politica-e-sociedade") e outras pelo nome
_EDITORIAS = {x["slug"]: x["nome"] for x in json.loads((Path(__file__).resolve().parent.parent / "config" / "editorias.json").read_text(encoding="utf-8"))["editorias"]}


def editoria_nome(cat):
    return _EDITORIAS.get(cat, cat)
REDACAO = {"@type": "Organization", "name": "Redação O Paladino", "url": f"{SITE}/politica-editorial/"}


def organizacao():
    return {
        "@type": "Organization", "@id": ORG_ID, "name": "O Paladino", "url": f"{SITE}/",
        "logo": {"@type": "ImageObject", "url": f"{SITE}/marca/o-paladino.webp", "width": 320, "height": 320},
        "sameAs": [u for u in (CFG.get("redes") or {}).values() if u.startswith("https://")],
        "publishingPrinciples": f"{SITE}/politica-editorial/", "foundingDate": CFG.get("fundacao", ""),
    }


def cabeca():
    """Linhas do <head> comuns a todas as páginas: feed RSS e códigos de verificação do Search Console e do Bing
    (verificacao.google / verificacao.bing de config/portal.json; vazios não saem)."""
    v = CFG.get("verificacao") or {}
    linhas = [f'<link rel="alternate" type="application/rss+xml" title="O Paladino" href="{FEED}">']
    if v.get("google"):
        linhas.append(f'<meta name="google-site-verification" content="{escape(v["google"])}">')
    if v.get("bing"):
        linhas.append(f'<meta name="msvalidate.01" content="{escape(v["bing"])}">')
    return "\n".join(linhas)


def site():
    return {"@type": "WebSite", "@id": SITE_ID, "url": f"{SITE}/", "name": "O Paladino", "inLanguage": "pt-BR", "publisher": {"@id": ORG_ID}}


def trilha(*itens):
    """BreadcrumbList a partir de pares (nome, url)."""
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i, "name": nome, "item": url} for i, (nome, url) in enumerate(itens, 1)]}


def artigo(tipo, url, titulo, descricao, imagem, publicado, modificado=None, sobre=None, secao=None):
    a = {"@type": tipo, "@id": f"{url}#artigo", "mainEntityOfPage": url, "headline": titulo, "description": descricao,
         "image": imagem if isinstance(imagem, list) else [imagem], "datePublished": publicado, "author": REDACAO, "publisher": {"@id": ORG_ID}, "inLanguage": "pt-BR"}
    if modificado and modificado > publicado:
        a["dateModified"] = modificado
    if sobre:
        a["about"] = sobre
    if secao:
        a["articleSection"] = secao
    a["isAccessibleForFree"] = True
    return a


def script(*nos):
    """<script type="application/ld+json"> com um @graph; "</" escapado para não fechar o script."""
    dados = {"@context": "https://schema.org", "@graph": [organizacao(), *nos]}
    return '<script type="application/ld+json">' + json.dumps(dados, ensure_ascii=False).replace("</", "<\\/") + "</script>"
