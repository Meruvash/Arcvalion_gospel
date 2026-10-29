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
import urllib.request
import urllib.robotparser
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import portal  # noqa: E402

UA = "PortalCristao-pauta/1.0 (+coleta de pauta; respeita robots.txt)"
_ROBOS = {}


def permitido(url):
    host = urlparse(url)
    base = f"{host.scheme}://{host.netloc}"
    if base not in _ROBOS:
        # lê o robots.txt com a identificação do robô (o leitor padrão do Python usa outra e alguns sites a bloqueiam)
        rp = urllib.robotparser.RobotFileParser()
        try:
            with urllib.request.urlopen(urllib.request.Request(base + "/robots.txt", headers={"User-Agent": UA}), timeout=30) as r:
                rp.parse(r.read().decode("utf-8", "ignore").splitlines())
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
            try:
                d = parsedate_to_datetime(el.text) if tag == "pubDate" else datetime.fromisoformat(el.text.replace("Z", "+00:00"))
                return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
            except (TypeError, ValueError):
                pass
    return None


def itens(xml):
    raiz = ElementTree.fromstring(xml)
    atom = "{http://www.w3.org/2005/Atom}"
    for it in raiz.iter("item"):
        yield (limpo(it.findtext("title")), (it.findtext("link") or "").strip(), limpo(it.findtext("description"))[:300], data(it))
    for it in raiz.iter(f"{atom}entry"):
        link = it.find(f"{atom}link")
        yield (limpo(it.findtext(f"{atom}title")), link.get("href") if link is not None else "", limpo(it.findtext(f"{atom}summary"))[:300], data(it))


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
            lista = list(itens(baixar(f["url"])))
        except Exception as ex:
            avisos.append(f"{f['nome']}: falhou ({ex.__class__.__name__})")
            continue
        filtro = temas if f.get("filtro") == "temas" else re.compile(f["filtro"], re.I) if f.get("filtro") else None
        for titulo, link, resumo, quando in lista:
            if quando and quando < limite:
                continue
            if filtro and not filtro.search(f"{titulo} {resumo}"):
                continue
            nota = (2 if temas.search(f"{titulo} {resumo}") else 0) + (1 if f.get("tipo") == "primaria" else 0)
            cands.append((nota, quando or limite, f, titulo, link, resumo))
    cands.sort(key=lambda x: (x[0], x[1]), reverse=True)
    hoje = datetime.now().date().isoformat()
    linhas = [f"# Pauta sugerida de {hoje} (últimos {dias} dias)", "",
              "Lista automática, só para orientar a redação. Nenhum item é notícia pronta: confirme na fonte primária, "
              "ouça os envolvidos, escreva com o padrão editorial e publique só com revisão humana.", ""]
    for nota, quando, f, titulo, link, resumo in cands[:80]:
        linhas += [f"## {titulo}", f"- Fonte: {f['nome']} ({'primária' if f.get('tipo') == 'primaria' else 'outro veículo'}) · {quando:%d/%m %H:%M} · editoria sugerida: {f['editoria']} · prioridade {nota}",
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
