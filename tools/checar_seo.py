"""Confere o SEO técnico do site gerado: canonical, Open Graph, um H1, JSON-LD batendo com o visível, links internos.

Uso: python3 tools/checar_seo.py [publico|publico-exemplo] [--exemplo]   (sai com código 1 se algo falhar)
Portado de tools/checar_seo.py do Elite Boardgamers, com as checagens novas do portal (rótulo de patrocinado, autor,
sitemaps, robots.txt e links/imagens internos quebrados).
"""
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
import portal  # noqa: E402

PROIBIDOS = {"Review", "AggregateRating", "Product", "Offer", "Rating"}
LINK = re.compile(r'(?:href|src|srcset)="([^"]+)"')


def tipos(no):
    if isinstance(no, dict):
        t = no.get("@type")
        yield from ([t] if isinstance(t, str) else t or [])
        for v in no.values():
            yield from tipos(v)
    elif isinstance(no, list):
        for v in no:
            yield from tipos(v)


def problemas(url, s, exemplo=False):
    erros = []
    canon = re.search(r'<link rel="canonical" href="([^"]+)">', s)
    og = re.search(r'<meta property="og:url" content="([^"]+)">', s)
    if not canon or canon.group(1) != url:
        erros.append("canonical ausente ou diferente da URL")
    if not og or og.group(1) != url:
        erros.append("og:url diferente da URL")
    if not exemplo and 'name="robots" content="max-image-preview:large"' not in s and 'content="noindex, follow"' not in s:
        erros.append("sem robots max-image-preview:large")
    if exemplo and "noindex" not in s:
        erros.append("prévia de exemplo sem noindex")
    if len(re.findall(r"<h1[\s>]", s)) != 1:
        erros.append("página sem exatamente um H1")
    if not re.search(r'<meta name="description" content="[^"]{30,}"', s):
        erros.append("description ausente ou curta demais")
    blocos = re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)
    if len(blocos) != 1:
        return erros + [f"esperado 1 bloco JSON-LD, achei {len(blocos)}"]
    try:
        ld = json.loads(blocos[0])
    except ValueError as ex:
        return erros + [f"JSON-LD inválido: {ex}"]
    if ld.get("@context") != "https://schema.org":
        erros.append("JSON-LD sem @context schema.org")
    if PROIBIDOS & set(tipos(ld)):
        erros.append(f"JSON-LD com tipo proibido: {', '.join(sorted(PROIBIDOS & set(tipos(ld))))}")
    nos = {n.get("@type"): n for n in ld.get("@graph", [])}
    trilha = nos.get("BreadcrumbList")
    if url != f"{portal.SITE}/" and (not trilha or trilha["itemListElement"][-1]["item"] != url):
        erros.append("BreadcrumbList ausente ou não termina na própria página")
    art = next((nos[t] for t in ("NewsArticle", "AnalysisNewsArticle", "OpinionNewsArticle", "Article") if t in nos), None)
    if art:
        visivel = re.search(r'<time datetime="([^"]+)">', s)
        if not visivel or visivel.group(1) != art["datePublished"]:
            erros.append("datePublished não bate com a data visível (<time>)")
        if art.get("dateModified") and art["dateModified"] < art["datePublished"]:
            erros.append("dateModified anterior a datePublished")
        if art["mainEntityOfPage"] != url:
            erros.append("mainEntityOfPage diferente da URL")
        h1 = html.unescape(re.sub(r"<[^>]+>", "", re.search(r"<h1[^>]*>(.*?)</h1>", s, re.S).group(1))).strip()
        if art["headline"] != h1:
            erros.append("headline diferente do H1")
        if art.get("genre") == "Conteúdo patrocinado" and "Conteúdo patrocinado por" not in s:
            erros.append("patrocinado sem o aviso visível no topo")
        if "Conteúdo patrocinado por" in s and art.get("genre") != "Conteúdo patrocinado":
            erros.append("aviso de patrocinado sem o rótulo nos dados estruturados")
        if 'id="transparencia"' not in s:
            erros.append("matéria sem o quadro 'Como esta matéria foi feita'")
    if "FAQPage" in nos:
        for q in nos["FAQPage"]["mainEntity"]:
            if html.escape(q["name"]) not in s:
                erros.append(f"FAQPage com pergunta que não está visível: {q['name']!r}")
    return erros


def links(saida, rel, s):
    erros = []
    base = (saida / rel).parent
    for alvo in LINK.findall(s):
        for parte in alvo.split(", "):
            u = parte.split(" ")[0]
            if not u or u.startswith(("http://", "https://", "mailto:", "#", "data:", "tel:")):
                continue
            caminho = unquote(urlparse(u).path)
            if portal.BASE and caminho.startswith(portal.BASE + "/"):
                caminho = caminho[len(portal.BASE):]
            dest = (saida / caminho.lstrip("/")) if caminho.startswith("/") else (base / caminho)
            if caminho.endswith("/") or dest.is_dir():
                dest = dest / "index.html"
            if not dest.exists():
                erros.append(f"link quebrado: {u}")
    return erros


def checar(saida, exemplo=False):
    erros = []
    for p in sorted(saida.rglob("*.html")):
        rel = p.relative_to(saida)
        s = p.read_text(encoding="utf-8")
        erros += [f"{rel}: {x}" for x in links(saida, rel, s)]
        if rel.name != "index.html":
            continue
        url = f"{portal.SITE}/" + ("" if rel.parent == Path(".") else f"{rel.parent.as_posix()}/")
        erros += [f"SEO {url}: {x}" for x in problemas(url, s, exemplo)]
    robots = (saida / "robots.txt").read_text(encoding="utf-8")
    if exemplo:
        if "Disallow: /" not in robots:
            erros.append("robots.txt da prévia de exemplo precisa bloquear tudo")
    elif f"Sitemap: {portal.SITE}/sitemap.xml" not in robots:
        erros.append("robots.txt sem o sitemap")
    mapa = (saida / "sitemap.xml").read_text(encoding="utf-8")
    for u in re.findall(r"<loc>([^<]+)</loc>", mapa):
        rel = u[len(portal.SITE) + 1:]
        arq = saida / rel / "index.html" if rel else saida / "index.html"
        if not arq.exists():
            erros.append(f"sitemap aponta para página inexistente: {u}")
        elif "noindex" in arq.read_text(encoding="utf-8") and not exemplo:
            erros.append(f"sitemap com página noindex: {u}")
    return erros


def main(args):
    exemplo = "--exemplo" in args
    args = [x for x in args if x != "--exemplo"]
    pasta = args[0] if args else "publico"
    exemplo = exemplo or "exemplo" in pasta
    if exemplo:
        portal.iniciar(conteudo=portal.ROOT / "exemplos" / "conteudo", config=portal.ROOT / "exemplos" / "config", exemplo=True)
    else:
        portal.iniciar()
    saida = portal.ROOT / pasta
    if not (saida / "index.html").exists():
        sys.exit(f"{pasta}/ não existe: rode python3 tools/build.py{' --exemplo' if exemplo else ''}")
    erros = checar(saida, exemplo)
    print("\n".join(erros) if erros else f"ok {pasta}/: canonical, Open Graph, H1, dados estruturados, sitemap, robots e links internos")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
