"""Copia o site gerado na raiz (tools/build_home.py) para uma pasta de publicação, sem os arquivos de trabalho.

Uso: python3 tools/montar_publicacao.py [_site]   (o deploy do GitHub Pages usa _site; o do Cloudflare, publico)
Fica de fora o que não é site: tools, conteudo, docs, worker, exemplos, testes, configuração e a lista "exclude"
do _config.yml (arquivos de trabalho que continuam no repositório).
"""
import re
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FORA = {".git", ".github", ".claude", ".cache", ".mcp.json", ".gitignore", "node_modules", "_site", "tools", "conteudo",
        "docs", "worker", "exemplos", "tests", "assets", "config", "img/og/estado.json", "_config.yml", "package.json",
        "package-lock.json", "requirements.txt", "wrangler.jsonc", "CLAUDE.md"}


def fora():
    bloco = (RAIZ / "_config.yml").read_text(encoding="utf-8").split("exclude:", 1)[1]
    return FORA | {m.strip().strip("\"'") for m in re.findall(r"^\s*-\s*(.+)$", bloco, re.M)}


def montar(saida):
    saida = (RAIZ / saida).resolve()
    if RAIZ not in saida.parents:
        sys.exit("a pasta de publicação precisa ficar dentro do repositório")
    excluir = fora() | {saida.relative_to(RAIZ).as_posix()} | {p.name for p in RAIZ.glob("publico*")}

    def ignora(pasta, nomes):
        rel = Path(pasta).resolve().relative_to(RAIZ)
        return [n for n in nomes if (rel / n).as_posix().removeprefix("./") in excluir or n == "__pycache__"]

    shutil.rmtree(saida, ignore_errors=True)
    shutil.copytree(RAIZ, saida, ignore=ignora)
    (saida / ".nojekyll").write_text("")
    return sum(1 for p in saida.rglob("*") if p.is_file())


if __name__ == "__main__":
    destino = sys.argv[1] if len(sys.argv) > 1 else "_site"
    print(f"ok {montar(destino)} arquivos em {destino}/")
