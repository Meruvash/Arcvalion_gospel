"""Confere SEO técnico das páginas geradas: canonical, Open Graph e dados estruturados batendo com o que está visível.

Uso: python3 tools/checar_seo.py    (sai com código 1 se algo falhar; também roda dentro de verificar_site.py)
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
from endereco import SITE  # noqa: E402  (config/portal.json)
PROIBIDOS = {"Review", "AggregateRating", "Product", "Offer", "Rating"}
FORA = {".git", ".cache", ".claude", ".impeccable", "tools", "conteudo", "modelos", "lotes", "triagem", "exemplos", "node_modules", "docs", "worker", "_site"}


def tipos(no):
    """Todos os @type de um JSON-LD, em qualquer nível."""
    if isinstance(no, dict):
        t = no.get("@type")
        yield from ([t] if isinstance(t, str) else t or [])
        for v in no.values():
            yield from tipos(v)
    elif isinstance(no, list):
        for v in no:
            yield from tipos(v)


def problemas(url, s):
    erros = []
    canon = re.search(r'<link rel="canonical" href="([^"]+)">', s)
    og = re.search(r'<meta property="og:url" content="([^"]+)">', s)
    if not canon or canon.group(1) != url:
        erros.append("canonical ausente ou diferente da URL")
    if not og or og.group(1) != url:
        erros.append("og:url diferente da URL")
    if 'content="max-image-preview:large"' not in s:
        erros.append("sem <meta name=\"robots\" content=\"max-image-preview:large\"> (imagem grande no Google Discover)")
    if len(re.findall(r"<h1[\s>]", s)) != 1:
        erros.append("página sem exatamente um H1")
    blocos = re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)
    if len(blocos) != 1:
        return erros + [f"esperado 1 bloco JSON-LD, achei {len(blocos)}"]
    try:
        ld = json.loads(blocos[0])
    except ValueError as ex:
        return erros + [f"JSON-LD inválido: {ex}"]
    if ld.get("@context") != "https://schema.org":
        erros.append("JSON-LD sem @context schema.org")
    proib = PROIBIDOS & set(tipos(ld))
    if proib:
        erros.append(f"JSON-LD com tipo proibido pelo padrão do site: {', '.join(sorted(proib))}")
    nos = {n.get("@type"): n for n in ld.get("@graph", [])}
    trilha = nos.get("BreadcrumbList")
    if url != f"{SITE}/" and (not trilha or trilha["itemListElement"][-1]["item"] != url):
        erros.append("BreadcrumbList ausente ou não termina na própria página")
    art = nos.get("NewsArticle") or nos.get("Article")
    if art:
        visivel = re.search(r'<time datetime="([^"]+)">', s)
        if not visivel or visivel.group(1) != art["datePublished"]:
            erros.append("datePublished não bate com a data visível (<time>)")
        if art.get("dateModified") and art["dateModified"] < art["datePublished"]:
            erros.append("dateModified anterior a datePublished")
        if art["mainEntityOfPage"] != url:
            erros.append("mainEntityOfPage diferente da URL")
        if nos.get("NewsArticle"):
            h1 = html.unescape(re.sub(r"<[^>]+>", "", re.search(r"<h1[^>]*>(.*?)</h1>", s, re.S).group(1))).strip()
            if art["headline"] != h1:
                erros.append("headline diferente do H1")
    return erros


def checar(erros):
    for p in sorted(ROOT.rglob("index.html")):
        rel = p.relative_to(ROOT)
        if FORA & set(rel.parts):
            continue
        if rel.parts[0] == "previa":  # prévia de revisão: não vai para busca, então só precisa do noindex
            if 'content="noindex"' not in p.read_text(encoding="utf-8"):
                erros.append(f"SEO {rel}: prévia de revisão sem noindex")
            continue
        url = f"{SITE}/" + ("" if rel.parent == Path(".") else f"{rel.parent.as_posix()}/")
        erros += [f"SEO {url}: {x}" for x in problemas(url, p.read_text(encoding="utf-8"))]


if __name__ == "__main__":
    erros = []
    checar(erros)
    print("\n".join(erros) if erros else "ok: canonical, Open Graph e dados estruturados de todas as páginas")
    sys.exit(1 if erros else 0)
