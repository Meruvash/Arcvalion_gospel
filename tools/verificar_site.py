"""Verificação noturna do site (22h): confere o que está publicado e lista o que entrou no dia para a revisão editorial.

Uso: python3 tools/verificar_site.py [--data AAAA-MM-DD] [--online]

Checagens automáticas (saem com código 1 se alguma falhar):
  - todo JSON de conteudo/ abre;
  - todas as notícias passam em tools/noticias/checar_noticia.py e têm página em noticias/<slug>/;
  - toda resenha publicada em pauta.json tem conteúdo que passa no texto do PADRAO_EDITORIAL.md, fotos oficiais
    liberadas (ou infográfico), index.html e capa.jpg, e a página bate com o que build_review.py gera hoje;
  - links e imagens internos de todas as páginas apontam para arquivos que existem;
  - canonical, Open Graph e JSON-LD de cada página batem com o conteúdo visível (tools/checar_seo.py);
  - toda página publicada tem canonical para a própria URL e está no sitemap.xml, e robots.txt aponta para o sitemap;
  - com --online, as páginas do dia e a página inicial respondem 200 no site no ar.
No fim, lista as notícias e resenhas publicadas na data (padrão: hoje) com as fontes, para a revisão de fatos.
"""
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from checar_roteiro import checar_texto, fotos_liberadas  # noqa: E402
from noticias.checar_noticia import problemas  # noqa: E402
import checar_seo  # noqa: E402

SITE = "https://meruvash.github.io/Arcvalion_gospel"
FORA = {".git", ".cache", "tools", "modelos", "marca", "lotes", "fontes", "triagem", ".claude", ".impeccable"}
LINK = re.compile(r'(?:href|src)="([^"]+)"')


def checar_json(erros):
    for p in sorted((ROOT / "conteudo").rglob("*.json")):
        try:
            json.loads(p.read_text(encoding="utf-8"))
        except ValueError as ex:
            erros.append(f"JSON inválido: {p.relative_to(ROOT)} ({ex})")


def checar_noticias(erros):
    ns = []
    for p in sorted((ROOT / "conteudo" / "noticias").glob("*.json")):
        n = json.loads(p.read_text(encoding="utf-8"))
        ns.append(n)
        for e in problemas(n):
            erros.append(f"notícia {n['slug']}: {e}")
        if not (ROOT / "noticias" / n["slug"] / "index.html").exists():
            erros.append(f"notícia {n['slug']}: sem página (rode tools/build_home.py)")
        img = n.get("imagem")
        if img and not (ROOT / "noticias" / img["arquivo"]).exists():
            erros.append(f"notícia {n['slug']}: imagem {img['arquivo']} não existe")
    return ns


def checar_resenhas(erros):
    import build_review
    pauta = json.loads((ROOT / "pauta.json").read_text(encoding="utf-8"))
    publicadas = []
    for p in pauta["publicadas"]:
        slug = p["url"].rstrip("/").split("/")[-1]
        arq = ROOT / "conteudo" / f"{slug}.json"
        if not arq.exists():
            erros.append(f"resenha {slug}: falta conteudo/{slug}.json")
            continue
        c = json.loads(arq.read_text(encoding="utf-8"))
        publicadas.append((p, c))
        if c.get("experiencia"):  # só o padrão v2 tem texto conferido; as antigas ficam como estão
            for e in checar_texto(c):
                erros.append(f"resenha {slug}: {e}")
        if not (fotos_liberadas(slug) or (ROOT / slug / "infografico.webp").exists()):
            erros.append(f"resenha {slug}: sem fotos oficiais liberadas e sem infográfico")
        for f, limite in (("index.html", None), ("capa.jpg", 250_000)):
            alvo = ROOT / slug / f
            if not alvo.exists():
                erros.append(f"resenha {slug}: falta {f}")
            elif limite and alvo.stat().st_size > limite * 1.2:
                erros.append(f"resenha {slug}: {f} com {alvo.stat().st_size // 1000} KB (limite ~{limite // 1000} KB)")
        pagina = ROOT / slug / "index.html"
        try:
            if pagina.exists() and pagina.read_text(encoding="utf-8") != build_review.build(c):
                erros.append(f"resenha {slug}: página desatualizada (rode tools/build_review.py conteudo/{slug}.json)")
        except SystemExit as ex:
            erros.append(f"resenha {slug}: build_review.py recusou ({ex})")
        estado = {j["jogo"]: j["status"] for j in pauta["jogos"]}.get(c["jogo"])
        if estado not in (None, "publicado"):
            erros.append(f"resenha {slug}: está em publicadas, mas o status na pauta é {estado!r}")
    return publicadas


def checar_links(erros):
    for pagina in sorted(ROOT.rglob("index.html")):
        rel = pagina.relative_to(ROOT)
        if rel.parts[0] in FORA:
            continue
        html = pagina.read_text(encoding="utf-8")
        for alvo in set(LINK.findall(html)):
            u = urlparse(alvo)
            # "${...}" é modelo de link montado pelo JavaScript da página, não endereço
            if u.scheme or alvo.startswith(("#", "//", "data:", "mailto:", "tel:", "javascript:")) or not u.path or "${" in alvo:
                continue
            caminho = (ROOT / u.path.lstrip("/")) if u.path.startswith("/") else (pagina.parent / unquote(u.path))
            if u.path.endswith("/") or caminho.is_dir():
                caminho = caminho / "index.html"
            if not caminho.resolve().exists():
                erros.append(f"link quebrado em {rel}: {alvo}")


def checar_sitemap(erros, ns, publicadas):
    sitemap = ROOT / "sitemap.xml"
    if not sitemap.exists() or not (ROOT / "robots.txt").exists():
        erros.append("falta sitemap.xml ou robots.txt (rode python3 tools/build_sitemap.py)")
        return
    no_sitemap = set(re.findall(r"<loc>([^<]+)</loc>", sitemap.read_text(encoding="utf-8")))
    if f"{SITE}/sitemap.xml" not in (ROOT / "robots.txt").read_text(encoding="utf-8"):
        erros.append("robots.txt não aponta para o sitemap.xml")
    urls = [f"{SITE}/", f"{SITE}/noticias/", f"{SITE}/estudos/", f"{SITE}/consulta/", f"{SITE}/politica-editorial/"]
    urls += [f"{SITE}/{g.parent.relative_to(ROOT).as_posix()}/" for g in [*(ROOT / "jogos-de-tabuleiro").glob("**/index.html"), *(ROOT / "premios").glob("index.html")]]
    urls += [f"{SITE}/noticias/{n['slug']}/" for n in ns] + [p["url"] for p, _ in publicadas]
    for url in urls:
        arq = ROOT / url[len(SITE) + 1:] / "index.html"
        if not arq.exists():
            continue
        canon = re.search(r'<link rel="canonical" href="([^"]+)">', arq.read_text(encoding="utf-8"))
        if not canon or canon.group(1) != url:
            erros.append(f"canonical ausente ou errado em {url}")
        if url not in no_sitemap:
            erros.append(f"fora do sitemap.xml: {url} (rode python3 tools/build_sitemap.py)")


def checar_online(erros, urls):
    import requests
    for url in urls:
        try:
            r = requests.get(url, timeout=30, headers={"User-Agent": "PortalCristao-verificacao/1.0"})
            if r.status_code != 200:
                erros.append(f"no ar: {url} respondeu {r.status_code}")
        except requests.RequestException as ex:
            erros.append(f"no ar: {url} não respondeu ({ex.__class__.__name__})")


def main():
    args = sys.argv[1:]
    dia = args[args.index("--data") + 1] if "--data" in args else date.today().isoformat()
    erros = []
    checar_json(erros)
    ns = checar_noticias(erros)
    publicadas = checar_resenhas(erros)
    checar_links(erros)
    checar_sitemap(erros, ns, publicadas)
    checar_seo.checar(erros)

    do_dia_n = [n for n in ns if n["data"] == dia]
    do_dia_r = [(p, c) for p, c in publicadas if p.get("data") == dia]
    if "--online" in args:
        checar_online(erros, [SITE + "/"] + [f"{SITE}/noticias/{n['slug']}/" for n in do_dia_n] + [p["url"] for p, _ in do_dia_r])

    print(f"# Verificação do site · {dia}\n")
    print("## Checagens automáticas\n")
    print("\n".join(f"- ❌ {e}" for e in erros) if erros else "- ✅ tudo certo")
    print(f"\n## Publicado em {dia}: revisar fatos, números e fontes\n")
    for n in do_dia_n:
        manchete = " · MANCHETE" if n.get("manchete") else ""
        print(f"- notícia `conteudo/noticias/{n['slug']}.json`{manchete}: {n['titulo']}")
        for f in n["fontes"]:
            print(f"  - {f['nome']}: {f['url']}")
    for p, c in do_dia_r:
        print(f"- resenha `conteudo/{c['slug']}.json`: {c['jogo']} ({p['url']})")
        for f in c.get("fontes", []):
            nome, url = (f.get("nome"), f.get("url")) if isinstance(f, dict) else (f[0], f[1] if len(f) > 1 else "")
            print(f"  - {nome}: {url}")
    if not (do_dia_n or do_dia_r):
        print("- nada publicado nesta data")
    sys.exit(1 if erros else 0)


if __name__ == "__main__":
    main()
