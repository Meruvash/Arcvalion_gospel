"""Dados estruturados (JSON-LD) das páginas, num lugar só. Portado de tools/seo.py do Elite Boardgamers.

Regra herdada: só entra o que está visível na página e é verdade. Nada de Review, AggregateRating, Product, Offer
nem FAQPage de pergunta que não aparece no texto. Autor só é Person quando a pessoa está em config/equipe.json
(gente real, com página de autor); sem isso o autor é a Redação (Organization).
"""
import json

import portal


def org_id():
    return f"{portal.SITE}/#organizacao"


def organizacao():
    cfg = portal.CFG
    o = {"@type": "NewsMediaOrganization", "@id": org_id(), "name": portal.NOME, "url": f"{portal.SITE}/",
         "logo": {"@type": "ImageObject", "url": f"{portal.SITE}/marca/logo-512.png", "width": 512, "height": 512},
         "publishingPrinciples": f"{portal.SITE}/politica-editorial/",
         "correctionsPolicy": f"{portal.SITE}/politica-editorial/#correcoes",
         "verificationFactCheckingPolicy": f"{portal.SITE}/politica-editorial/#verificacao",
         "ethicsPolicy": f"{portal.SITE}/politica-editorial/",
         "masthead": f"{portal.SITE}/expediente/"}
    redes = [v for v in cfg.get("redes", {}).values() if v]
    if redes:
        o["sameAs"] = redes
    if cfg.get("email_contato"):
        o["contactPoint"] = {"@type": "ContactPoint", "contactType": "redação", "email": cfg["email_contato"], "availableLanguage": "pt-BR"}
    if cfg.get("fundacao"):
        o["foundingDate"] = cfg["fundacao"]
    return o


def site():
    return {"@type": "WebSite", "@id": f"{portal.SITE}/#site", "url": f"{portal.SITE}/", "name": portal.NOME,
            "description": portal.CFG.get("descricao", ""), "inLanguage": portal.CFG.get("idioma", "pt-BR"), "publisher": {"@id": org_id()}}


def trilha(*itens):
    """BreadcrumbList a partir de pares (nome, url)."""
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i, "name": nome, "item": url} for i, (nome, url) in enumerate(itens, 1)]}


def pessoa(slug):
    p = portal.EQUIPE.get(slug)
    if not p:
        return {"@type": "Organization", "name": f"Redação {portal.NOME}", "url": f"{portal.SITE}/expediente/"}
    d = {"@type": "Person", "@id": f"{portal.SITE}/autores/{slug}/#pessoa", "name": p["nome"], "url": f"{portal.SITE}/autores/{slug}/"}
    if p.get("cargo"):
        d["jobTitle"] = p["cargo"]
    if p.get("redes"):
        d["sameAs"] = p["redes"]
    return d


def artigo(a, url, imagens, secao):
    tipo = portal.TIPOS[a["tipo"]][1]
    d = {"@type": tipo, "@id": f"{url}#artigo", "mainEntityOfPage": url, "headline": a["titulo"],
         "description": a.get("linha_fina") or a.get("lide", ""), "image": imagens, "datePublished": a["publicado_em"],
         "author": [pessoa(a.get("autor", ""))], "publisher": {"@id": org_id()}, "inLanguage": portal.CFG.get("idioma", "pt-BR"),
         "articleSection": secao, "isAccessibleForFree": True}
    if a.get("atualizado_em") and a["atualizado_em"] > a["publicado_em"]:
        d["dateModified"] = a["atualizado_em"]
    if a.get("tags"):
        d["keywords"] = a["tags"]
    if a["tipo"] == "patrocinado":
        # rótulo de conteúdo comercial também nos dados: o texto não é jornalismo da redação
        d["genre"] = "Conteúdo patrocinado"
    return d


def faq(itens):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q["pergunta"],
                                                 "acceptedAnswer": {"@type": "Answer", "text": q["resposta"]}} for q in itens]}


def evento(ev):
    """Event só para evento com data e local confirmados (o mesmo que aparece na agenda)."""
    d = {"@type": "Event", "name": ev["nome"], "startDate": ev["inicio"], "eventStatus": "https://schema.org/EventScheduled",
         "eventAttendanceMode": "https://schema.org/OnlineEventAttendanceMode" if ev.get("online") else "https://schema.org/OfflineEventAttendanceMode"}
    if ev.get("fim"):
        d["endDate"] = ev["fim"]
    if ev.get("online"):
        d["location"] = {"@type": "VirtualLocation", "url": ev.get("url", "")}
    else:
        d["location"] = {"@type": "Place", "name": ev.get("local", ""),
                         "address": {"@type": "PostalAddress", "addressLocality": ev.get("cidade", ""), "addressRegion": ev.get("uf", ""), "addressCountry": "BR"}}
    if ev.get("url"):
        d["url"] = ev["url"]
    if ev.get("organizador"):
        d["organizer"] = {"@type": "Organization", "name": ev["organizador"]}
    return d


def script(*nos):
    """<script type="application/ld+json"> com um @graph; "</" escapado para não fechar o script."""
    dados = {"@context": "https://schema.org", "@graph": [organizacao(), *nos]}
    return '<script type="application/ld+json">' + json.dumps(dados, ensure_ascii=False).replace("</", "<\\/") + "</script>"
