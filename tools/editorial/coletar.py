"""Coleta de pauta: lê os feeds de config/fontes.json e grava uma lista de candidatas para a redação avaliar.

Uso: python3 tools/editorial/coletar.py [--dias 2]
Saída: .cache/pauta/<AAAA-MM-DD>.md (fora do site e do Git). É a rodada 1 da skill noticias. Portado da ideia de tools/noticias/coletar.py do original:
respeita o robots.txt de cada site, identifica o robô no User-Agent e só ordena candidatas (itens dos temas do portal
primeiro, fontes primárias antes). Não escreve matéria nem publica nada: a apuração e a redação seguem o padrão
editorial, e a publicação depende de revisão humana (tools/publicar.py).
"""
import html
import json
import re
import sys
import urllib.error
import urllib.request
import urllib.robotparser
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import portal  # noqa: E402

UA = "OPaladino-pauta/1.0 (+coleta de pauta; respeita robots.txt)"
_ROBOS = {}
POR_FONTE = 6
ABRANGENCIA = {"nacional": "Brasil", "rondonia": "Rondônia", "porto-velho": "Porto Velho", "internacional": "internacional"}


def permitido(url):
    host = urlparse(url)
    base = f"{host.scheme}://{host.netloc}"
    if base not in _ROBOS:
        # lido com o nosso User-Agent: o rp.read() padrão se apresenta como Python-urllib, que muitos CDNs barram com 403,
        # e o robotparser trata 403 como "proíbe tudo"
        rp = urllib.robotparser.RobotFileParser(base + "/robots.txt")
        try:
            rp.parse(baixar(base + "/robots.txt").decode("utf-8", "replace").splitlines())
        except urllib.error.HTTPError as ex:
            if ex.code in (401, 403):
                rp.disallow_all = True  # barrou o nosso robô: é um não
            elif ex.code >= 500:
                rp.disallow_all = True  # servidor fora do ar: não entra (RFC 9309)
            else:
                rp.allow_all = True  # robots.txt ausente: tudo liberado
        except Exception:
            rp = None  # robots.txt inacessível: segue a regra geral (permitido), como os buscadores
        _ROBOS[base] = rp
    rp = _ROBOS[base]
    return rp is None or rp.can_fetch(UA, url)


def baixar(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30) as r:
        return r.read()


def limpo(t):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t or ""))).strip()


def data(item):
    for tag in ("pubDate", "{http://purl.org/dc/elements/1.1/}date", "{http://www.w3.org/2005/Atom}updated", "{http://www.w3.org/2005/Atom}published"):
        el = item.find(tag)
        if el is not None and el.text:
            for ler in (parsedate_to_datetime, lambda t: datetime.fromisoformat(t.strip().replace("Z", "+00:00"))):
                try:  # pubDate às vezes vem em ISO 8601 (News Rondônia), e o Atom às vezes em RFC 822
                    d = ler(el.text)
                    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
                except (TypeError, ValueError, IndexError):
                    pass
    return None


def xml_tolerante(xml):
    """Feeds de portais regionais trazem entidades de HTML (&ocirc;) que o XML não conhece: troca pelo caractere."""
    try:
        return ElementTree.fromstring(xml)
    except ElementTree.ParseError:
        texto = xml.decode("utf-8", "replace") if isinstance(xml, bytes) else xml
        texto = re.sub(r"&(?!(?:amp|lt|gt|quot|apos);)([a-zA-Z][a-zA-Z0-9]*);",
                       lambda m: html.unescape(m.group(0)) if html.unescape(m.group(0)) != m.group(0) else m.group(0), texto)
        texto = re.sub(r"^\s+", "", texto)
        return ElementTree.fromstring(texto.encode("utf-8"))


def itens(xml):
    raiz = xml_tolerante(xml)
    atom = "{http://www.w3.org/2005/Atom}"
    for it in raiz.iter("item"):
        yield (limpo(it.findtext("title")), (it.findtext("link") or "").strip(), limpo(it.findtext("description"))[:300], data(it))
    for it in raiz.iter(f"{atom}entry"):
        link = it.find(f"{atom}link")
        yield (limpo(it.findtext(f"{atom}title")), link.get("href") if link is not None else "", limpo(it.findtext(f"{atom}summary"))[:300], data(it))


def itens_sitemap_news(xml):
    """Sitemap de notícias do Google (news:title, news:publication_date): portais sem RSS, como a Rondônia Dinâmica."""
    raiz = xml_tolerante(xml)
    sm, nw = "{http://www.sitemaps.org/schemas/sitemap/0.9}", "{http://www.google.com/schemas/sitemap-news/0.9}"
    for u in raiz.iter(f"{sm}url"):
        titulo = limpo(u.findtext(f".//{nw}title"))
        quando = None
        t = u.findtext(f".//{nw}publication_date") or u.findtext(f"{sm}lastmod")
        if t:
            try:
                quando = datetime.fromisoformat(t.strip().replace("Z", "+00:00"))
                quando = quando if quando.tzinfo else quando.replace(tzinfo=timezone.utc)
            except ValueError:
                pass
        yield titulo, (u.findtext(f"{sm}loc") or "").strip(), "", quando


def itens_pagina(conteudo, padrao, base):
    """Manchetes da página inicial de um portal cujo RSS parou (Rondoniaovivo): links que casam com o padrão, com a
    data tirada do próprio endereço (/AAAA/MM/DD/). Só a página inicial, que o robots.txt permite; nada de raspar."""
    texto = conteudo.decode("utf-8", "replace") if isinstance(conteudo, bytes) else conteudo
    vistos = set()
    for href, miolo in re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', texto, re.S):
        link = href if href.startswith("http") else base.rstrip("/") + "/" + href.lstrip("/")
        m = re.search(padrao, link)
        titulo = limpo(miolo)
        if not m or link in vistos or len(titulo) < 25:
            continue
        vistos.add(link)
        a, mes, d = (int(x) for x in m.groups()[:3])
        yield titulo, link, "", datetime(a, mes, d, 12, tzinfo=timezone(timedelta(hours=-4)))


MESES_ABREV = {"jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6, "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12}


def itens_mural(conteudo):
    """Mural de pautas sugeridas pelo público de um criador de conteúdo (Ancapsu): cada cartão traz o título, a data e o
    link da matéria original de outro veículo. É termômetro do que o nosso público está comentando, nunca fonte: o link
    leva ao veículo que deu a notícia, e o fato ainda pede a fonte primária."""
    texto = conteudo.decode("utf-8", "replace") if isinstance(conteudo, bytes) else conteudo
    for cartao in texto.split('<div class="card col-lg-3')[1:]:
        titulo = re.search(r'card-title[^"]*">(.*?)</h5>', cartao, re.S)
        link = re.search(r'href="([^"]+)" target="_blank" class="btn btn-outline-success', cartao)
        data_ = re.search(r'(\d{1,2}) (\w{3})\. (\d{4})', cartao)
        resumo = re.search(r'card-text">(.*?)</p>', cartao, re.S)
        if not titulo or not link:
            continue
        quando = None
        if data_ and data_.group(2).lower() in MESES_ABREV:
            quando = datetime(int(data_.group(3)), MESES_ABREV[data_.group(2).lower()], int(data_.group(1)), 12,
                              tzinfo=timezone(timedelta(hours=-3)))
        yield limpo(titulo.group(1)), html.unescape(link.group(1)), limpo(resumo.group(1)) if resumo else "", quando


def itens_sapl(f, limite):
    """Casa legislativa no SAPL (Câmara de Porto Velho, Assembleia de Rondônia): leis publicadas e projetos apresentados
    no período, pela API pública de dados abertos. É fonte primária: a pauta é a decisão (ou a proposta) do próprio
    parlamento; o filtro de temas da fonte separa o que é de fé, família, vida, liberdade ou educação."""
    base, ano = f["url"].rstrip("/"), limite.year
    consultas = [(f"{base}/api/norma/normajuridica/?ano={ano}&o=-data&page_size=100", "data", f.get("normas", "."), "norma")]
    consultas += [(f"{base}/api/materia/materialegislativa/?ano={ano}&tipo={t}&o=-data_apresentacao&page_size=100",
                   "data_apresentacao", ".", "materia") for t in f.get("tipos_materia", [])]
    for url, campo, padrao, rota in consultas:
        if not permitido(url):
            continue
        try:
            resultados = json.loads(baixar(url))["results"]
        except Exception:  # conexão instável numa consulta não derruba as outras da mesma casa
            try:
                resultados = json.loads(baixar(url))["results"]
            except Exception:
                continue
        for x in resultados:
            if not x.get(campo) or not re.match(padrao, x.get("__str__", "")):
                continue
            quando = datetime.fromisoformat(x[campo]).replace(hour=12, tzinfo=timezone(timedelta(hours=-4)))
            yield f"{x['__str__']}: {limpo(x.get('ementa', ''))}", f"{base}/{rota}/{x['id']}", "", quando


def ler_fonte(f, limite=None):
    if f.get("formato") == "sapl":
        return list(itens_sapl(f, limite or datetime.now(timezone.utc) - timedelta(days=2)))
    conteudo = baixar(f["url"])
    if f.get("formato") == "sitemap-news":
        return list(itens_sitemap_news(conteudo))
    if f.get("formato") == "mural":
        return list(itens_mural(conteudo))
    if f.get("formato") == "pagina":
        return list(itens_pagina(conteudo, f["padrao"], f["url"]))
    return list(itens(conteudo))


def main(args):
    portal.iniciar()
    dias = int(args[args.index("--dias") + 1]) if "--dias" in args else 2
    cfg = json.loads((portal.ROOT / "config" / "fontes.json").read_text(encoding="utf-8"))
    temas = re.compile(cfg.get("temas", "."), re.I)
    limite = datetime.now(timezone.utc) - timedelta(days=dias)
    cands, avisos = [], []
    for f in cfg["feeds"]:
        if not permitido(f["url"]):
            avisos.append(f"{f['nome']}: robots.txt não permite a leitura automática; consulte só manualmente")
            continue
        try:
            lista = ler_fonte(f, limite)
        except Exception as ex:
            avisos.append(f"{f['nome']}: falhou ({ex.__class__.__name__})")
            continue
        filtro = f.get("filtro")
        filtro = re.compile(filtro.replace("temas", temas.pattern), re.I) if filtro else None
        ignorar = re.compile(f["ignorar"], re.I) if f.get("ignorar") else None
        abr = f.get("abrangencia", "nacional")
        for titulo, link, resumo, quando in lista:
            if quando and quando < limite:
                continue
            if filtro and not filtro.search(f"{titulo} {resumo}"):
                continue
            if ignorar and ignorar.search(titulo):  # rotina legislativa sem pauta: crédito suplementar, título, nome de rua
                continue
            # prioridade geográfica (docs/CRIVO_NOTICIAS.md): nacional e Rondônia/Porto Velho sobem, internacional não;
            # portal conservador brasileiro sobe um ponto. O fato ainda pede a fonte primária.
            nota = ((2 if temas.search(f"{titulo} {resumo}") else 0) + (1 if f.get("tipo") == "primaria" else 0)
                    + (1 if f.get("conservador") and abr != "internacional" else 0)
                    + {"nacional": 1, "rondonia": 1, "porto-velho": 2}.get(abr, 0)
                    + (1 if f.get("local_confiavel") else 0) + f.get("bonus", 0))
            cands.append((nota, quando or limite, f, titulo, link, resumo))
    cands.sort(key=lambda x: (x[0], x[1]), reverse=True)
    # no máximo POR_FONTE itens de cada feed, para um agregador que publica muito não tomar a pauta toda
    vistos = {}
    cands = [c for c in cands if vistos.setdefault(c[2]["nome"], []).append(1) or len(vistos[c[2]["nome"]]) <= c[2].get("max", POR_FONTE)]
    hoje = datetime.now().date().isoformat()
    linhas = [f"# Pauta sugerida de {hoje} (últimos {dias} dias)", "",
              "Lista automática, só para orientar a redação. Nenhum item é notícia pronta: confirme na fonte primária, "
              "ouça os envolvidos, escreva com o padrão editorial e publique só com revisão humana.", ""]
    for nota, quando, f, titulo, link, resumo in cands[:80]:
        linhas += [f"## {titulo}", f"- Fonte: {f['nome']} ({'primária' if f.get('tipo') == 'primaria' else 'outro veículo'}{', portal conservador' if f.get('conservador') else ''}{', veículo local confiável' if f.get('local_confiavel') else ''}) · {ABRANGENCIA.get(f.get('abrangencia', 'nacional'))} · {quando:%d/%m %H:%M} · editoria sugerida: {f['editoria']} · prioridade {nota}",
                   f"- Link: {link}", f"- {resumo}" if resumo else "", ""]
    if avisos:
        linhas += ["## Avisos da coleta", ""] + [f"- {a}" for a in avisos]
    saida = portal.ROOT / ".cache" / "pauta" / f"{hoje}.md"
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"ok {saida.relative_to(portal.ROOT)}: {len(cands)} candidatas, {len(avisos)} aviso(s)")
    for a in avisos:
        print("  aviso:", a)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
