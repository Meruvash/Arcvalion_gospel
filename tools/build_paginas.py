"""Gera as páginas institucionais a partir de conteudo/paginas/<slug>.json (hoje: Quem somos, em sobre/).

Uso: python3 tools/build_paginas.py   (build_home.py chama)
Cada página tem `titulo`, `descricao`, `lide` e `secoes` ({titulo, paragrafos} ou {titulo, lista}). Nos textos,
{nome} e {responsavel} viram o nome do portal e o responsável editorial; [texto](/caminho/) vira link.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import portal  # noqa: E402
import seo  # noqa: E402
from build_home import ROOT, SITE, e, pagina  # noqa: E402
from layout import cabecalho, rodape, trilha  # noqa: E402

PUBLICADAS = ["sobre"]  # as outras de conteudo/paginas/ ainda não têm conteúdo revisado para ir ao ar


def texto(t, pre):
    t = e(t.replace("{nome}", portal.NOME).replace("{responsavel}", responsavel()))
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
                  lambda m: f'<a href="{m[2] if m[2].startswith("http") else pre + m[2].lstrip("/")}"'
                            f'{" target=_blank rel=noopener" if m[2].startswith("http") else ""}>{m[1]}</a>', t)


def responsavel():
    p = next((p for p in portal.EQUIPE.values() if p.get("revisor")), None)
    return f'{p["nome"]}, {p["bio"].split(".")[0].lower()}' if p else portal.NOME


def build(slug):
    c = json.loads((ROOT / "conteudo" / "paginas" / f"{slug}.json").read_text(encoding="utf-8"))
    pre = "../"
    url = f"{SITE}/{slug}/"
    secoes = "".join(
        f'<section class="bloco"><h2>{e(s["titulo"])}</h2>'
        + (f'<div class="corpo">{"".join(f"<p>{texto(p, pre)}</p>" for p in s["paragrafos"])}</div>' if s.get("paragrafos") else "")
        + (f'<ul class="marcas">{"".join(f"<li>{texto(x, pre)}</li>" for x in s["lista"])}</ul>' if s.get("lista") else "")
        + "</section>" for s in c["secoes"])
    css = """<style>
.nota ul.marcas{display:grid;gap:10px}.nota ul.marcas li{padding-left:16px;position:relative}
.nota ul.marcas li:before{content:"";position:absolute;left:0;top:.6em;width:7px;height:7px;border-radius:50%;background:var(--gold)}
.nota .corpo a,.nota .marcas a{color:var(--link)}
</style>"""
    corpo = f"""{cabecalho(pre, "")}
<main id="conteudo" class="in"><div class="nota">
 {trilha(("Início", pre), (e(c["titulo"]), ""))}
 <article class="bloco"><h1>{e(c["titulo"])}</h1><p class="lide">{texto(c["lide"], pre)}</p></article>
 {secoes}
 <p class="note" style="color:var(--muted);font-size:.85rem">Atualizado em {"/".join(reversed(c["atualizado_em"].split("-")))}.</p>
</div></main>
{rodape(pre)}"""
    ld = seo.script({"@type": c.get("schema", "WebPage"), "@id": f"{url}#pagina", "url": url, "name": c["titulo"],
                     "description": c["descricao"], "inLanguage": "pt-BR", "isPartOf": {"@id": f"{SITE}/#organizacao"}},
                    seo.trilha(("Início", f"{SITE}/"), (c["titulo"], url)))
    (ROOT / slug).mkdir(exist_ok=True)
    (ROOT / slug / "index.html").write_text(
        pagina(f'{c["titulo"]} | O Paladino', c["descricao"], url, f"{SITE}/estudos/capa.jpg", pre, corpo, "website", css, ld), encoding="utf-8")
    return ROOT / slug / "index.html"


def todas():
    portal.iniciar()
    return [build(s) for s in PUBLICADAS]


if __name__ == "__main__":
    for f in todas():
        print("ok", f.relative_to(ROOT))
