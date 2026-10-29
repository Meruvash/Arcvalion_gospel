"""Ferramenta da rotina /comentarios: lê a fila de moderação e registra decisões no serviço de interações.

Uso:
  python3 tools/comentarios/moderar.py fila                      # JSON com pendentes e duvidosos
  python3 tools/comentarios/moderar.py decidir <id> <estado> "<parecer>"
      estado: aprovado | reprovado | duvidoso   (a IA usa 'duvidoso' para deixar com o editor)
Precisa de MODERACAO_SENHA no ambiente; o endereço da API vem de conteudo/interacoes.json.
"""
import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def chamar(caminho, corpo=None):
    api = json.loads((ROOT / "conteudo" / "interacoes.json").read_text(encoding="utf-8")).get("api")
    senha = os.environ.get("MODERACAO_SENHA")
    if not api or not senha:
        sys.exit("Serviço não instalado (conteudo/interacoes.json sem api) ou MODERACAO_SENHA ausente.")
    req = urllib.request.Request(f"{api}/v1/moderacao/{caminho}", method="POST" if corpo else "GET",
                                 data=json.dumps(corpo).encode() if corpo else None,
                                 headers={"Authorization": f"Bearer {senha}", "Content-Type": "application/json",
                                          # a Cloudflare barra o identificador padrão do Python (Python-urllib)
                                          "User-Agent": "PortalCristao-moderacao/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "fila":
        print(json.dumps(chamar("fila"), ensure_ascii=False, indent=1))
    elif len(sys.argv) == 5 and sys.argv[1] == "decidir" and sys.argv[3] in ("aprovado", "reprovado", "duvidoso"):
        print(chamar("decidir", {"id": int(sys.argv[2]), "estado": sys.argv[3], "parecer": sys.argv[4], "por": "ia"}))
    else:
        sys.exit(__doc__)
