"""Dados estruturados (JSON-LD) das páginas, num lugar só.

Regra: só entra o que está visível na página e é verdade. Nada de Review, AggregateRating ou Product:
o site não dá nota própria (a nota BGG é de terceiros) e não vende jogos.
"""
import json

SITE = "https://meruvash.github.io/Arcvalion_gospel"
ORG_ID = f"{SITE}/#organizacao"
SITE_ID = f"{SITE}/#site"
# Medidor de visitas sem cookies (Cloudflare Web Analytics); vai no fim do <body> de todas as páginas.
ANALYTICS = ""  # Cloudflare Web Analytics do portal: colar aqui o script com o token do site novo
REDACAO = {"@type": "Organization", "name": "Redação Portal Cristão", "url": f"{SITE}/politica-editorial/"}


def organizacao():
    return {
        "@type": "Organization", "@id": ORG_ID, "name": "Portal Cristão", "url": f"{SITE}/",
        "logo": {"@type": "ImageObject", "url": f"{SITE}/marca/portal-cristao.webp", "width": 318, "height": 254},
        "sameAs": [],
    }


def site():
    return {"@type": "WebSite", "@id": SITE_ID, "url": f"{SITE}/", "name": "Portal Cristão", "inLanguage": "pt-BR", "publisher": {"@id": ORG_ID}}


def trilha(*itens):
    """BreadcrumbList a partir de pares (nome, url)."""
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i, "name": nome, "item": url} for i, (nome, url) in enumerate(itens, 1)]}


def artigo(tipo, url, titulo, descricao, imagem, publicado, modificado=None, sobre=None):
    a = {"@type": tipo, "@id": f"{url}#artigo", "mainEntityOfPage": url, "headline": titulo, "description": descricao,
         "image": imagem if isinstance(imagem, list) else [imagem], "datePublished": publicado, "author": REDACAO, "publisher": {"@id": ORG_ID}, "inLanguage": "pt-BR"}
    if modificado and modificado > publicado:
        a["dateModified"] = modificado
    if sobre:
        a["about"] = sobre
    return a


def script(*nos):
    """<script type="application/ld+json"> com um @graph; "</" escapado para não fechar o script."""
    dados = {"@context": "https://schema.org", "@graph": [organizacao(), *nos]}
    return '<script type="application/ld+json">' + json.dumps(dados, ensure_ascii=False).replace("</", "<\\/") + "</script>"
