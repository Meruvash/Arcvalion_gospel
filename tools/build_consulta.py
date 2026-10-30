"""Monta consulta/index.html, a página do Versículo diário.

Uso: python3 tools/build_consulta.py   (também roda no fim de build_home.py)
Os versículos vêm de conteudo/versiculos.json (texto literal da tradução de João Ferreira de Almeida, em domínio
público, com o endereço de onde cada um foi lido). Este script grava a lista no JavaScript da página (const VERSOS),
escreve no HTML o versículo do dia da geração (para buscadores e robôs de IA que não executam JavaScript) e a nota
de fonte. O bloco RAW dos livros da Bíblia continua na própria página: dá o testamento de cada livro e alimenta a busca.
Também reescreve o cabeçalho, o menu e o rodapé com a moldura comum de tools/layout.py.
"""
import json
import re
import sys
from datetime import date, datetime, timedelta, timezone
from math import gcd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from layout import CSS_BUSCA, barra_leitura, cabecalho, rodape  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARQ = ROOT / "consulta" / "index.html"
VERSICULOS = ROOT / "conteudo" / "versiculos.json"


def esc(s):
    """Mesmo esc() do JavaScript das páginas."""
    return "".join({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}.get(ch, ch) for ch in s)


def livros(s):
    """[(testamento, grupo, livro, capítulos)] do bloco RAW, na ordem da Bíblia."""
    raw = re.search(r"const RAW = `(.*?)`", s, re.S).group(1)
    out = []
    for linha in raw.strip().split("\n"):
        y, c, g = linha.strip().split(" | ")
        for x in g.split("; "):
            n, k = x.split("=")
            out.append((y, c, n, int(k)))
    return out


def total(lista):
    caps = sum(x[3] for x in lista)
    return f'{len(lista)} {"livro" if len(lista) == 1 else "livros"} · {caps:,} {"capítulo" if caps == 1 else "capítulos"}'.replace(",", ".")


def carregar(nomes):
    """Versículos na ordem da Bíblia, conferidos contra os livros e capítulos do RAW."""
    dados = json.loads(VERSICULOS.read_text(encoding="utf-8"))
    ordem = {n: i for i, (_, _, n, _) in enumerate(nomes)}
    caps = {n: k for _, _, n, k in nomes}
    vs = dados["versiculos"]
    for v in vs:
        if v["livro"] not in ordem or not 1 <= v["capitulo"] <= caps[v["livro"]] or not v["texto"].strip():
            raise SystemExit(f"versículo inválido em {VERSICULOS.name}: {v}")
    return dados, sorted(vs, key=lambda v: (ordem[v["livro"]], v["capitulo"], v["versiculo"]))


def dia_do_versiculo(n, hoje):
    """Mesma conta do JavaScript da página: dia desde 1970 vezes um passo primo com n, módulo n."""
    p = 97
    while gcd(p, n) != 1:
        p += 1
    return ((hoje - date(1970, 1, 1)).days * p) % n


def build():
    s = ARQ.read_text(encoding="utf-8")
    nomes = livros(s)
    dados, vs = carregar(nomes)
    lista = [[v["livro"], v["capitulo"], v["versiculo"], v["texto"]] for v in vs]
    novo = re.sub(r"^const VERSOS = .*;$", lambda _: "const VERSOS = " + json.dumps(lista, ensure_ascii=False, separators=(",", ":")) + ";",
                  s, count=1, flags=re.M)
    # versículo do dia da geração, já no HTML (o JavaScript troca pelo do dia de quem lê)
    hoje = datetime.now(timezone(timedelta(hours=-3))).date()
    v = lista[dia_do_versiculo(len(lista), hoje)]
    fig = (f'<figure class="verso" id="verso"><p class="selo" id="selo">Versículo do dia</p><blockquote id="vt">{esc(v[3])}</blockquote>'
           f'<figcaption id="vr">{esc(v[0])} {v[1]}:{v[2]}<small>Almeida, domínio público</small></figcaption></figure>')
    novo = re.sub(r"<!--verso-->.*?<!--/verso-->", lambda _: f"<!--verso-->{fig}<!--/verso-->", novo, count=1, flags=re.S)
    f = dados["fonte"]
    fonte = (f'<p id="fonte">Fonte: {esc(f["traducao"])} ({esc(f["licenca"])}), texto lido em '
             f'<a href="{esc(f["url"])}" target="_blank" rel="noopener">{esc(f["site"])}</a> em {esc(f["consulta"])}. '
             f'Seleção de {len(lista)} versículos feita pela redação.</p>')
    novo = re.sub(r'<p id="fonte">.*?</p>', lambda _: fonte, novo, count=1, flags=re.S)
    # moldura comum do site (tools/layout.py)
    # (o script do menu que segue o </nav> entra junto, para não se repetir a cada geração)
    novo = re.sub(r'<header class="(?:top)?bar".*?</nav>(?:\s*<script>\(\(\)=>\{const n=document\.querySelector\(\'\.nav\'\).*?</script>)*',
                  lambda _: cabecalho("../", "Versículo diário"), novo, count=1, flags=re.S)
    novo = re.sub(r'(?:<style id="moldura">.*?</style>\n)?</head>', lambda _: f'<style id="moldura">{CSS_BUSCA}</style>\n</head>', novo, count=1, flags=re.S)
    # rodapé + barra de compartilhar do pé da tela (entre marcadores, para ser trocada inteira na próxima geração)
    novo = re.sub(r'<footer>.*?</footer>(?:\s*<!--lt-->.*?<!--/lt-->)?', lambda _: rodape("../", "\n<!--lt-->" + barra_leitura(interacao=False) + "<!--/lt-->"),
                  novo, count=1, flags=re.S)
    t = total(nomes)
    novo = re.sub(r'<span id="count" class="count">[^<]*</span>', f'<span id="count" class="count">{t}</span>', novo, count=1)
    if novo != s:
        ARQ.write_text(novo, encoding="utf-8")
    return f"{len(lista)} versículos · {t}"


if __name__ == "__main__":
    print("ok consulta/index.html:", build())
