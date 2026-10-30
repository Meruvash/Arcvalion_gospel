"""Gera /llms.txt: um resumo do site em texto simples para assistentes de IA (ChatGPT, Claude, Perplexity, Gemini).

Uso: python3 tools/build_llms.py   (roda sozinho no fim de build_home.py e de publicar.py)
É experimental (proposta em llmstxt.org): nenhuma IA grande confirmou que lê o arquivo, mas ele não atrapalha nada e
aponta para as páginas que respondem melhor. Tudo sai do que já está publicado (nota em revisão fica fora).
Aprovado pelo usuário em 29/10/2026.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_review import ROOT, SITE  # noqa: E402

NOTICIAS = 20


def build():
    linhas = [
        "# O Paladino",
        "",
        "> Portal brasileiro de notícias com fonte e data e de estudos bíblicos, em português, com uma perspectiva cristã "
        "sobre o Brasil e o mundo: fé e igreja, política e sociedade, família e valores, economia, música e cultura "
        "cristã e eventos.",
        "",
        "Responsável editorial: Anderson Pelicioni de Castro, que confere o site diariamente. "
        "Toda notícia e todo estudo listam as fontes consultadas, com data, e passam por checagem automática do padrão "
        "editorial antes de ir ao ar.",
    ]
    ns = sorted((n for n in (json.loads(p.read_text(encoding="utf-8")) for p in (ROOT / "conteudo" / "noticias").glob("*.json"))
                 if n.get("status", "publicado") == "publicado"),  # nota em revisão fica fora
                key=lambda n: n.get("publicado_em") or n["data"], reverse=True)[:NOTICIAS]
    if ns:
        linhas += ["", "## Notícias recentes", ""]
        linhas += [f"- [{n['titulo']}]({SITE}/noticias/{n['slug']}/) ({n['data']})" for n in ns]
    linhas += ["", "## Seções e referências", "",
               f"- [Arquivo de notícias]({SITE}/noticias/)",
               f"- [Estudos bíblicos]({SITE}/estudos/)",
               f"- [Agenda cristã]({SITE}/lancamentos/): eventos e lançamentos com data confirmada",
               f"- [Versículo diário]({SITE}/consulta/): o versículo do dia e um sorteio de versículos da Bíblia (Almeida, domínio público) a cada clique",
               f"- [Política editorial]({SITE}/politica-editorial/): como pesquisamos, escolhemos e corrigimos", ""]
    (ROOT / "llms.txt").write_text("\n".join(linhas), encoding="utf-8")
    return f"{SITE}/llms.txt"


if __name__ == "__main__":
    print("ok", build())
