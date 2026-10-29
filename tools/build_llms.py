"""Gera /llms.txt: um resumo do site em texto simples para assistentes de IA (ChatGPT, Claude, Perplexity, Gemini).

Uso: python3 tools/build_llms.py   (roda sozinho no fim de build_home.py e de publicar.py)
É experimental (proposta em llmstxt.org): nenhuma IA grande confirmou que lê o arquivo, mas ele não atrapalha nada e
aponta para as páginas que respondem melhor. Tudo sai do que já está publicado: guias, resenhas, notícias recentes.
Aprovado pelo usuário em 29/10/2026.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_guias import BASE, GUIAS, MINIMO, resenhas, selecao  # noqa: E402
from build_review import ROOT, SITE, nome_br  # noqa: E402

NOTICIAS = 20


def build():
    todas = resenhas()
    linhas = [
        "# Portal Cristão",
        "",
        "> Portal brasileiro de notícias e resenhas de jogos de tabuleiro modernos (board games), em português. Resenhas de "
        "jogos premiados (Spiel des Jahres, Kennerspiel, As d'Or, Deutscher Spiele Preis, Golden Geek) com selo de "
        "recomendação, para quem é cada jogo, preço em lojas brasileiras com data e verificação de edição nacional; "
        "notícias diárias de lançamentos, pré-vendas e financiamentos no Brasil.",
        "",
        "Responsável editorial: Anderson Pelicioni de Castro, que lê e verifica pessoalmente tudo o que é publicado. "
        "Toda resenha e notícia lista as fontes consultadas, com data. Preços e disponibilidade valem para a data indicada "
        "na página.",
        "",
        "## Guias para escolher um jogo",
        "",
        f"- [Guia de jogos de tabuleiro]({SITE}/{BASE}/): como escolher pelo número de jogadores, duração e complexidade",
    ]
    for perfil, (slug, titulo, sub, *_resto) in GUIAS.items():
        if len(selecao(perfil, todas)) >= MINIMO:
            linhas.append(f"- [{titulo}]({SITE}/{BASE}/{slug}/): {sub}")
    linhas += [f"- [Prêmios de jogos de tabuleiro]({SITE}/premios/): o que cada prêmio avalia e os vencedores resenhados",
               "", "## Resenhas", ""]
    for c, _, _ in sorted(todas, key=lambda x: nome_br(x[0]).lower()):
        selo = f" Selo: {c['selo']}." if c.get("selo") else ""
        linhas.append(f"- [{nome_br(c)}]({SITE}/{c['slug']}/): {c.get('tagline', '').rstrip('.')}.{selo}")
    ns = sorted((json.loads(p.read_text(encoding="utf-8")) for p in (ROOT / "conteudo" / "noticias").glob("*.json")),
                key=lambda n: n.get("publicado_em") or n["data"], reverse=True)[:NOTICIAS]
    linhas += ["", "## Notícias recentes", ""]
    linhas += [f"- [{n['titulo']}]({SITE}/noticias/{n['slug']}/) ({n['data']})" for n in ns]
    linhas += ["", "## Ferramentas e referências", "",
               f"- [Todas as resenhas, com filtros]({SITE}/estudos/)",
               f"- [Arquivo de notícias]({SITE}/noticias/)",
               f"- [Calendário de lançamentos no Brasil]({SITE}/lancamentos/)",
               f"- [Consulta Golden Geek]({SITE}/consulta/): os três primeiros de cada categoria desde 2015",
               f"- [Política editorial]({SITE}/politica-editorial/): como pesquisamos, escolhemos e corrigimos", ""]
    (ROOT / "llms.txt").write_text("\n".join(linhas), encoding="utf-8")
    return f"{SITE}/llms.txt"


if __name__ == "__main__":
    print("ok", build())
