"""Escreve no HTML de consulta/index.html a lista dos livros da Bíblia que o JavaScript monta no navegador.

Uso: python3 tools/build_consulta.py   (também roda no fim de build_home.py)
Também reescreve o cabeçalho, o menu e o rodapé com a moldura comum de tools/layout.py.
A fonte continua sendo o bloco RAW dentro da própria página. Este script repete, em Python, o render() do estado
inicial (sem filtros) e grava o resultado dentro de <div id="out">, para que buscadores e robôs de IA que não
executam JavaScript leiam a lista inteira. No navegador, o render() troca esse conteúdo por um idêntico.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from layout import CSS_BUSCA, barra_leitura, botao_compartilhar, cabecalho, rodape  # noqa: E402
from busca import chave, resenhas_por_nome  # noqa: E402
import json  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARQ = ROOT / "consulta" / "index.html"


def esc(s):
    """Mesmo esc() do JavaScript da página."""
    return "".join({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}.get(ch, ch) for ch in s)


def mapa_resenhas(nomes):
    """Livros da Bíblia que têm estudo (mesmo nome normalizado que um apelido da resenha): slug e outros nomes."""
    por_nome = resenhas_por_nome()
    mapa = {}
    for n in nomes:
        if chave(n) in por_nome:
            slug, apelidos = por_nome[chave(n)]
            mapa[n] = {"r": slug, "a": " ".join(a for a in apelidos if chave(a) != chave(n))}
    return mapa


def tabela(s, resenhas):
    raw = re.search(r"const RAW = `(.*?)`", s, re.S).group(1)
    oficial = dict(re.findall(r'^\s*"(.+?)": "(.+?)",?$', re.search(r"const OFFICIAL = \{(.*?)\};", s, re.S).group(1), re.M))
    rows = []
    for linha in raw.strip().split("\n"):
        linha = linha.strip()
        if not linha:
            continue
        y, c, g = linha.split(" | ")
        for x in g.split("; "):
            n, k = x.split("=")
            rows.append({"y": y, "c": c, "p": len(rows) + 1, "n": n, "k": int(k)})
    plural = lambda q, um, varios: f"{q} {um if q == 1 else varios}"
    body, key = "", None
    for r in rows:
        k = r["y"] + "|" + r["c"]
        if k != key:
            if key is not None:
                body += "</tbody>"
            key = k
            grupo = [x for x in rows if x["y"] == r["y"] and x["c"] == r["c"]]
            en = oficial.get(r["c"]) or f'{plural(len(grupo), "livro", "livros")} · {plural(sum(x["k"] for x in grupo), "capítulo", "capítulos")}'
            body += f'<tbody><tr class="grp"><th colspan="2"><span class="gy">{r["y"]}</span><span class="gc">{esc(r["c"])}</span><span class="ge">{esc(en)}</span></th></tr>'
        res = f'<a class="res" href="../{resenhas[r["n"]]["r"]}/">Ler estudo</a>' if r["n"] in resenhas else ""
        body += (f'<tr class="row"><td class="pos">{r["p"]}º</td><td class="g">{esc(r["n"])}{res}'
                 f'<span class="cap">{plural(r["k"], "capítulo", "capítulos")}</span></td></tr>')
    body += "</tbody>"
    caps = sum(r["k"] for r in rows)
    total = f'{plural(len(rows), "livro", "livros")} · {caps:,} {"capítulo" if caps == 1 else "capítulos"}'.replace(",", ".")
    return f"<table><thead><tr><th>Ordem</th><th>Livro</th></tr></thead>{body}</table>", total


def build():
    s = ARQ.read_text(encoding="utf-8")
    raw = re.search(r"const RAW = `(.*?)`", s, re.S).group(1)
    resenhas = mapa_resenhas({x.split("=")[0] for linha in raw.strip().split("\n") if linha.strip() for x in linha.strip().split(" | ")[2].split("; ")})
    html_tabela, total = tabela(s, resenhas)
    novo = re.sub(r'<div id="out">.*?</div>(?=\s*(?:<a class="zap"|<section class="notas">))', lambda _: f'<div id="out">{html_tabela}</div>', s, count=1, flags=re.S)
    # moldura comum do site (tools/layout.py)
    # (o script do menu que segue o </nav> entra junto, para não se repetir a cada geração)
    novo = re.sub(r'<header class="(?:top)?bar".*?</nav>(?:\s*<script>\(\(\)=>\{const n=document\.querySelector\(\'\.nav\'\).*?</script>)*',
                  lambda _: cabecalho("../", "Livros da Bíblia"), novo, count=1, flags=re.S)
    novo = re.sub(r'(?:<style id="moldura">.*?</style>\n)?</head>', lambda _: f'<style id="moldura">{CSS_BUSCA}</style>\n</head>', novo, count=1, flags=re.S)
    # compartilhar a lista do jeito que está filtrada (o endereço guarda ano, categoria e pesquisa)
    cp = botao_compartilhar("Livros da Bíblia em O Paladino", "", "Compartilhar", mini=True)
    novo = re.sub(r'<!--cp-->.*?<!--/cp-->', lambda _: f'<!--cp-->{cp}<!--/cp-->', novo, count=1, flags=re.S)
    # rodapé + barra de compartilhar do pé da tela (entre marcadores, para ser trocada inteira na próxima geração)
    novo = re.sub(r'<footer>.*?</footer>(?:\s*<!--lt-->.*?<!--/lt-->)?', lambda _: rodape("../", "\n<!--lt-->" + barra_leitura(interacao=False) + "<!--/lt-->"),
                  novo, count=1, flags=re.S)
    novo = re.sub(r'^const RESENHAS = .*;$', lambda _: "const RESENHAS = " + json.dumps(resenhas, ensure_ascii=False, sort_keys=True) + ";", novo, count=1, flags=re.M)
    novo = re.sub(r'<span id="count" class="count">[^<]*</span>', f'<span id="count" class="count">{total}</span>', novo, count=1)
    if novo != s:
        ARQ.write_text(novo, encoding="utf-8")
    return total


if __name__ == "__main__":
    print("ok consulta/index.html:", build())
