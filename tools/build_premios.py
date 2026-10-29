"""Página /premios/: os principais prêmios de jogos de tabuleiro e os vencedores que já têm resenha no site.

Uso: python3 tools/build_premios.py   (também roda no fim de build_home.py e de publicar.py)
Os vencedores vêm do campo "premiacoes" das resenhas publicadas (só resultado "vencedor"); as notícias, da categoria
"Prêmios". A lista completa do Golden Geek fica na Consulta; aqui entram só os jogos que resenhamos.
"""
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import seo  # noqa: E402
from build_guias import CSS_GUIA, cartao, resenhas  # noqa: E402
from build_home import pagina  # noqa: E402
from build_review import ROOT, SITE, data_longa, nome_br  # noqa: E402
from layout import cabecalho, rodape, trilha  # noqa: E402

e = html.escape

# (nome no campo "premiacoes", título da seção, quem decide)
PREMIOS = [
    ("Spiel des Jahres", "Spiel des Jahres", "O prêmio alemão mais conhecido, decidido por um júri de críticos, para jogos de família."),
    ("Kennerspiel des Jahres", "Kennerspiel des Jahres", "A categoria do mesmo júri do Spiel des Jahres para quem já tem experiência com jogos."),
    ("As d'Or", "As d'Or", "O prêmio francês entregue no Festival Internacional de Jogos de Cannes."),
    ("Deutscher Spiele Preis", "Deutscher Spiele Preis", "Prêmio alemão votado pelo público e anunciado na feira de Essen."),
    ("Golden Geek", "Golden Geek", "Votado pela comunidade do BoardGameGeek, com várias categorias por ano."),
]

CSS_PREMIOS = """<style>
.vits{font-size:.84rem;font-weight:700;color:var(--premios);margin-top:6px}
.notas-p li{padding:8px 0;border-top:1px solid var(--paper-line)}.notas-p li:first-child{border-top:0}
.notas-p a{color:var(--link);font-weight:700;text-decoration:none}.notas-p a:hover{text-decoration:underline}
.notas-p time{display:block;font-size:.8rem;color:var(--paper-muted)}
.indice{display:flex;flex-wrap:wrap;gap:8px}.indice a{font-weight:700;color:var(--link);padding:6px 12px;border:1px solid var(--paper-line);border-radius:999px;background:#fff;text-decoration:none}
</style>"""


def build():
    pre = "../"
    url = f"{SITE}/premios/"
    titulo = "Prêmios de jogos de tabuleiro: Spiel des Jahres, Golden Geek e mais"
    todas = resenhas()
    secoes, indice = "", []
    for chave, nome, quem in PREMIOS:
        jogos = []
        for c, d, _ in todas:
            vit = sorted({(a["ano"], a["categoria"]) for a in c["premiacoes"] if a.get("premio") == chave and a.get("resultado") == "vencedor"})
            if vit:
                jogos.append((max(a for a, _ in vit), c, d, vit))
        if not jogos:
            continue
        jogos.sort(key=lambda x: x[0], reverse=True)
        ancora = chave.lower().replace(" ", "-").replace("'", "")
        indice.append(f'<a href="#{ancora}">{e(nome)}</a>')
        itens = ""
        for _, c, d, vit in jogos:
            # "Jogo do Ano 2019, Arte 2019" (no Golden Geek); nos outros a categoria repete o nome do prêmio
            txt = ", ".join(f"{cat} {ano}" if cat != chave else str(ano) for ano, cat in vit)
            itens += cartao(c, d, pre).replace("</div></a></li>", f'<p class="vits">Venceu: {e(txt)}</p></div></a></li>')
        extra = (f' <p class="criterio">A lista completa, com os três primeiros de cada categoria desde 2015, está na '
                 f'<a class="mais-g" href="{pre}consulta/">Consulta Golden Geek</a>.</p>') if chave == "Golden Geek" else ""
        secoes += (f'<section class="bloco" id="{ancora}"><h2>{e(nome)}</h2><p class="criterio">{e(quem)} '
                   f'{len(jogos)} vencedor{"es" if len(jogos) > 1 else ""} com resenha no site.</p><ol class="jogos-g">{itens}</ol>{extra}</section>\n ')
    notas = sorted((json.loads(p.read_text(encoding="utf-8")) for p in (ROOT / "conteudo" / "noticias").glob("*.json")),
                   key=lambda n: (n["data"], n.get("publicado_em", "")), reverse=True)
    notas = [n for n in notas if n["categoria"] == "Prêmios"][:8]
    notas_html = "".join(f'<li><time datetime="{n["data"]}">{data_longa(n["data"])}</time><a href="{pre}noticias/{n["slug"]}/">{e(n["titulo"])}</a></li>' for n in notas)
    corpo = f"""{cabecalho(pre, "Resenhas", sub=True)}
<main id="conteudo" class="in"><div class="nota guia">
 {trilha(("Início", pre), ("Prêmios", ""))}
 <article class="bloco">
  <h1>{e(titulo)}</h1>
  <p class="lide">Os prêmios são um atalho seguro para achar bons jogos: cada um tem um júri ou um público diferente,
  e juntos cobrem de jogos de família a estratégia pesada. Abaixo, o que cada prêmio avalia e os vencedores que já
  resenhamos, com link para a resenha completa.</p>
  <nav class="indice" aria-label="Prêmios nesta página">{"".join(indice)}</nav>
 </article>
 {secoes}{f'<section class="bloco"><h2>Notícias sobre prêmios</h2><ul class="notas-p">{notas_html}</ul></section>' if notas_html else ""}
 <section class="bloco"><h2>Escolha também pelo jeito que você joga</h2><p class="criterio"><a class="mais-g" href="{pre}jogos-de-tabuleiro/">Guia de jogos de tabuleiro →</a></p></section>
</div></main>
{rodape(pre)}"""
    ld = seo.script({"@type": "CollectionPage", "@id": url, "url": url, "name": titulo, "inLanguage": "pt-BR",
                     "about": [{"@type": "Thing", "name": nome} for _, nome, _ in PREMIOS]},
                    seo.trilha(("Início", f"{SITE}/"), ("Prêmios", url)))
    descr = ("Spiel des Jahres, Kennerspiel, As d'Or, Deutscher Spiele Preis e Golden Geek: o que cada prêmio de jogos de "
             "tabuleiro avalia e os vencedores com resenha completa no site.")
    (ROOT / "premios").mkdir(exist_ok=True)
    (ROOT / "premios" / "index.html").write_text(pagina(titulo, descr, url, f"{SITE}/consulta/capa.jpg", pre, corpo,
                                                        head_extra="\n" + CSS_GUIA + CSS_PREMIOS, jsonld=ld), encoding="utf-8")
    return url


if __name__ == "__main__":
    print("ok", build())
