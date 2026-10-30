"""Gera sitemap.xml, sitemap-noticias.xml, feed.xml (RSS), robots.txt e o arquivo da chave do IndexNow.

Uso: python3 tools/build_sitemap.py
Roda sozinho no fim de build_home.py, build_review.py e publicar.py, então não precisa ser chamado à mão.

Só entram páginas que existem, cujo canonical é a própria URL e que não têm noindex.
O lastmod de cada página é a última vez que o conteúdo dela mudou de verdade (o JSON de origem), não a última
vez que o HTML foi regerado: mudar o template não mexe no lastmod. O registro fica em conteudo/sitemap_estado.json.
O histórico do git não serve para isso: os clones das rotinas são rasos e todo arquivo antigo aparece no commit-limite.
O sitemap de notícias segue a regra do Google: só notas publicadas nas últimas 48 horas.
"""
import hashlib
import json
import re
import subprocess
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
from endereco import SITE  # noqa: E402  (config/portal.json)
from seo import editoria_nome  # noqa: E402
ESTADO = ROOT / "conteudo" / "sitemap_estado.json"
PORTAL = json.loads((ROOT / "config" / "portal.json").read_text(encoding="utf-8"))
ITENS_FEED = 50
CANONICAL = re.compile(r'<link rel="canonical" href="([^"]+)">')
NOINDEX = re.compile(r'<meta name="robots" content="[^"]*noindex', re.I)

ROBOTS = f"""# O Paladino: todos os robôs de busca e de IA são bem-vindos.
User-agent: *
Allow: /

Sitemap: {SITE}/sitemap.xml
Sitemap: {SITE}/sitemap-noticias.xml
"""


def feed(no_sitemap):
    """RSS 2.0 com as notícias e os estudos no ar (os mais recentes primeiro). É o que leitores de feed, agregadores
    e o Google Publisher Center leem; só entra página que também está no sitemap (publicada e indexável)."""
    itens = []
    for p in (ROOT / "conteudo" / "noticias").glob("*.json"):
        n = json.loads(p.read_text(encoding="utf-8"))
        url = f"{SITE}/noticias/{n['slug']}/"
        if n.get("publicado_em") and url in no_sitemap:
            itens.append((n["publicado_em"], url, n["titulo"], n["lide"], editoria_nome(n.get("categoria", "Notícias"))))
    for p in (ROOT / "conteudo" / "estudos").glob("*.json"):
        c = json.loads(p.read_text(encoding="utf-8"))
        url = f"{SITE}/estudos/{c['slug']}/"
        if c.get("publicado_em") and url in no_sitemap:
            itens.append((c["publicado_em"], url, c["titulo"], c["descricao"], "Estudos bíblicos"))
    itens.sort(key=lambda i: datetime.fromisoformat(i[0]), reverse=True)
    corpo = "".join(
        f"""  <item><title>{escape(t)}</title><link>{escape(u)}</link><guid isPermaLink="true">{escape(u)}</guid>"""
        f"""<pubDate>{format_datetime(datetime.fromisoformat(pub))}</pubDate><category>{escape(cat)}</category>"""
        f"""<description>{escape(d)}</description></item>\n"""
        for pub, u, t, d, cat in itens[:ITENS_FEED])
    ultima = format_datetime(datetime.fromisoformat(itens[0][0])) if itens else format_datetime(agora())
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n<channel>\n'
            f"  <title>O Paladino</title>\n  <link>{SITE}/</link>\n"
            f"""  <atom:link href="{SITE}/feed.xml" rel="self" type="application/rss+xml"/>\n"""
            f"  <description>{escape(PORTAL.get('descricao', ''))}</description>\n  <language>pt-BR</language>\n"
            f"  <lastBuildDate>{ultima}</lastBuildDate>\n" + corpo + "</channel>\n</rss>\n")


def agora():
    return datetime.now(timezone.utc).replace(microsecond=0)


def assinatura(dados):
    return hashlib.sha256(json.dumps(dados, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:16]


def data_git(arq):
    """Data do último commit que mexeu no arquivo, ou None se ele cai no limite de um clone raso (data falsa)."""
    rasos = (ROOT / ".git" / "shallow").read_text().split() if (ROOT / ".git" / "shallow").exists() else []
    r = subprocess.run(["git", "log", "-1", "--format=%H %cI", "--", str(arq.relative_to(ROOT))], cwd=ROOT, capture_output=True, text=True)
    if r.returncode or not r.stdout.strip():
        return None
    h, quando = r.stdout.split()
    return None if h in rasos else quando


def lastmod_registrado(url, dados):
    """Última mudança de conteúdo já registrada para a página, ou None se o conteúdo mudou desde o registro
    (a data nova entra no próximo build, junto com o sitemap)."""
    estado = json.loads(ESTADO.read_text(encoding="utf-8")) if ESTADO.exists() else {}
    reg = estado.get(url)
    return reg["lastmod"] if reg and reg["hash"] == assinatura(dados) else None


def lista_consulta(texto):
    raw = re.search(r"const RAW = `(.*?)`", texto, re.S)
    return raw.group(1) if raw else ""


def data_lista_consulta(arq):
    """Data do último commit que mudou a lista de vencedores da consulta (mudança de template não conta)."""
    rasos = (ROOT / ".git" / "shallow").read_text().split() if (ROOT / ".git" / "shallow").exists() else []
    rel = str(arq.relative_to(ROOT))
    r = subprocess.run(["git", "log", "--format=%H %cI", "--", rel], cwd=ROOT, capture_output=True, text=True)
    atual = lista_consulta(arq.read_text(encoding="utf-8"))
    for linha in r.stdout.split("\n"):
        if not linha:
            continue
        h, quando = linha.split()
        if h in rasos:
            return None
        pai = subprocess.run(["git", "show", f"{h}^:{rel}"], cwd=ROOT, capture_output=True, text=True)
        if pai.returncode or lista_consulta(pai.stdout) != atual:
            return quando
    return None


def fontes():
    """(url, caminho do HTML, assinatura do conteúdo, data inicial) de cada página do site."""
    pauta = json.loads((ROOT / "pauta.json").read_text(encoding="utf-8"))
    paginas = []
    for p in sorted((ROOT / "conteudo" / "noticias").glob("*.json")):
        n = json.loads(p.read_text(encoding="utf-8"))
        if n.get("status", "publicado") != "publicado":  # nota em revisão fica só na prévia (noindex)
            continue
        n.pop("publicado_em", None)
        n_pub = json.loads(p.read_text(encoding="utf-8")).get("publicado_em")
        paginas.append(("noticia", f"{SITE}/noticias/{n['slug']}/", ROOT / "noticias" / n["slug"] / "index.html", assinatura(n), n_pub))
    for pub in pauta["publicadas"]:
        slug = pub["url"].rstrip("/").split("/")[-1]
        arq = ROOT / "conteudo" / f"{slug}.json"
        c = json.loads(arq.read_text(encoding="utf-8"))
        inicial = max(filter(None, [pub.get("data"), data_git(arq)]))
        paginas.append(("resenha", f"{SITE}/{slug}/", ROOT / slug / "index.html", assinatura(c), inicial))
    for p in sorted((ROOT / "conteudo" / "estudos").glob("*.json")):
        c = json.loads(p.read_text(encoding="utf-8"))
        if c.get("status") != "publicado":  # estudo em revisão fica só na prévia (noindex)
            continue
        pub = c.pop("publicado_em", None)
        paginas.append(("resenha", f"{SITE}/estudos/{c['slug']}/", ROOT / "estudos" / c["slug"] / "index.html", assinatura(c), pub))
    for pag in sorted((ROOT / "noticias" / "pagina").glob("*/index.html"), key=lambda x: int(x.parent.name)):
        # página do arquivo de notícias: muda quando entra nota nova; data = a da nota mais recente nela
        datas = re.findall(r'href="\.\./\.\./\.\./noticias/([^/"]+)/"', pag.read_text(encoding="utf-8"))
        paginas.append(("arquivo", f"{SITE}/noticias/pagina/{pag.parent.name}/", pag, assinatura(datas), None))
    # páginas de categoria do arquivo (só existem quando o arquivo de notícias tem mais de uma página)
    for pag in sorted((ROOT / "noticias" / "categoria").glob("*/index.html")):
        notas = re.findall(r'href="\.\./\.\./\.\./noticias/([^/"]+)/"', pag.read_text(encoding="utf-8"))
        paginas.append(("arquivo", f"{SITE}/noticias/categoria/{pag.parent.name}/", pag, assinatura(notas), None))
    for guia in sorted([*(ROOT / "jogos-de-tabuleiro").glob("**/index.html"), *(ROOT / "premios").glob("index.html")]):
        rel = guia.parent.relative_to(ROOT).as_posix()
        texto = re.search(r"<main.*?</main>", guia.read_text(encoding="utf-8"), re.S).group(0)
        paginas.append(("guia", f"{SITE}/{rel}/", guia, assinatura(texto), data_git(guia) or agora().isoformat()))
    for inst in ("politica-editorial", "sobre"):
        politica = ROOT / inst / "index.html"
        if politica.exists():
            texto = re.search(r"<main.*?</main>", politica.read_text(encoding="utf-8"), re.S).group(0)
            paginas.append(("institucional", f"{SITE}/{inst}/", politica, assinatura(texto), data_git(politica) or agora().isoformat()))
    calendario = ROOT / "lancamentos" / "index.html"
    if calendario.exists():
        # muda quando a lista de jogos muda (a contagem e os ids dos lançamentos)
        ids = re.findall(r'<li id="j(\d+)"', calendario.read_text(encoding="utf-8"))
        paginas.append(("calendario", f"{SITE}/lancamentos/", calendario, assinatura(ids), None))
    consulta = ROOT / "consulta" / "index.html"
    paginas.append(("consulta", f"{SITE}/consulta/", consulta, assinatura(lista_consulta(consulta.read_text(encoding="utf-8"))), data_lista_consulta(consulta)))
    return paginas


def indexavel(url, html_arq):
    if not html_arq.exists():
        return False
    s = html_arq.read_text(encoding="utf-8")
    c = CANONICAL.search(s)
    return bool(c and c.group(1) == url and not NOINDEX.search(s))


def build():
    estado = json.loads(ESTADO.read_text(encoding="utf-8")) if ESTADO.exists() else {}
    hoje = agora()
    novo, entradas, fora, mudaram = {}, [], [], []
    for tipo, url, arq, ass, inicial in fontes():
        if not indexavel(url, arq):
            fora.append(url)
            continue
        antes = estado.get(url)
        if antes and antes["hash"] == ass:
            lastmod = antes["lastmod"]
        else:
            # primeira vez: data real de publicação; depois, a hora em que o conteúdo mudou
            lastmod = inicial if not antes else hoje.isoformat()
            if antes:
                mudaram.append(url)
        novo[url] = {"hash": ass, "lastmod": lastmod}
        entradas.append((tipo, url, lastmod))

    def maior(tipos):
        datas = [lm for t, _, lm in entradas if t in tipos and lm]
        return max(datas, key=lambda d: datetime.fromisoformat(d if "T" in d else d + "T00:00:00+00:00")) if datas else None

    secoes = [(f"{SITE}/", maior({"noticia", "resenha"})), (f"{SITE}/noticias/", maior({"noticia"})), (f"{SITE}/estudos/", maior({"resenha"}))]
    for url, lm in reversed(secoes):
        rel = url[len(SITE) + 1:]
        if indexavel(url, ROOT / rel / "index.html"):
            entradas.insert(0, ("secao", url, lm))
        else:
            fora.append(url)

    linhas = [f"  <url><loc>{escape(u)}</loc>{f'<lastmod>{lm}</lastmod>' if lm else ''}</url>" for _, u, lm in entradas]
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                      + "\n".join(linhas) + "\n</urlset>\n", encoding="utf-8")

    limite = hoje - timedelta(hours=48)
    recentes = []
    for p in sorted((ROOT / "conteudo" / "noticias").glob("*.json")):
        n = json.loads(p.read_text(encoding="utf-8"))
        url = f"{SITE}/noticias/{n['slug']}/"
        if n.get("status", "publicado") == "publicado" and n.get("publicado_em") and url in novo and datetime.fromisoformat(n["publicado_em"]) >= limite:
            recentes.append((n["publicado_em"], url, n["titulo"]))
    noticias = "".join(
        f"""  <url><loc>{escape(u)}</loc><news:news><news:publication><news:name>O Paladino</news:name><news:language>pt</news:language></news:publication>"""
        f"""<news:publication_date>{pub}</news:publication_date><news:title>{escape(t)}</news:title></news:news></url>\n"""
        for pub, u, t in sorted(recentes, reverse=True))
    (ROOT / "sitemap-noticias.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
                                               'xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">\n' + noticias + "</urlset>\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(ROBOTS, encoding="utf-8")
    (ROOT / "feed.xml").write_text(feed(novo), encoding="utf-8")
    # IndexNow: o buscador confere a chave em <SITE>/<chave>.txt antes de aceitar os avisos de tools/indexnow.py
    if PORTAL.get("indexnow_chave"):
        (ROOT / f"{PORTAL['indexnow_chave']}.txt").write_text(PORTAL["indexnow_chave"], encoding="utf-8")
    ESTADO.write_text(json.dumps(novo, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return len(entradas), len(recentes), fora, mudaram


def atualizar():
    """build() e, em seguida, regera as notícias e resenhas cujo conteúdo mudou nesta rodada, para o
    dateModified do JSON-LD sair já com a data nova (a página foi gerada antes do registro ser atualizado)."""
    total, recentes, fora, mudaram = build()
    if mudaram:
        import build_home
        import build_review
        for url in mudaram:
            slug = url.rstrip("/").split("/")[-1]
            if "/noticias/" in url:
                for p in (ROOT / "conteudo" / "noticias").glob(f"*{slug}.json"):
                    n = json.loads(p.read_text(encoding="utf-8"))
                    if n["slug"] == slug and n.get("status", "publicado") == "publicado":
                        build_home.build_nota(n)
            elif (ROOT / "conteudo" / f"{slug}.json").exists():
                c = json.loads((ROOT / "conteudo" / f"{slug}.json").read_text(encoding="utf-8"))
                (ROOT / slug / "index.html").write_text(build_review.build(c), encoding="utf-8")
    return total, recentes, fora, mudaram


if __name__ == "__main__":
    total, recentes, fora, _ = atualizar()
    print(f"ok sitemap.xml ({total} URLs), sitemap-noticias.xml ({recentes} das últimas 48 h), robots.txt")
    for u in fora:
        print("  fora do sitemap (sem página, canonical diferente ou noindex):", u)
