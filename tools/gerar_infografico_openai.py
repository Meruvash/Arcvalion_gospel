"""Gera o infográfico quadrado de uma resenha na API de imagens da OpenAI.

Uso: OPENAI_API_KEY=... python3 tools/gerar_infografico_openai.py conteudo/<slug>.json [--modelo gpt-image-2] [--n 1] [--qualidade high] [--dry-run]
Saída: <slug>/variacao-<i>.png. Confira o texto da imagem contra o roteiro antes de aprovar (etapa 5 da skill /resenha).
Usa as imagens de modelos/ como referência de estilo (endpoint /v1/images/edits).
"""
import argparse
import base64
import json
import os
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from checar_roteiro import SEM_FOTOS, checar, fotos_liberadas  # noqa: E402
from prompt_infografico import TAMANHO, prompt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
URL = "https://api.openai.com/v1/images/edits"


# Pedido do usuário em 28/10/2026: resenhas sem gerar imagem pela API da OpenAI (sem gastos).
# Só gera com PERMITIR_IMAGEM_GPT=1 no ambiente, e isso só com um novo OK explícito do usuário.
def travar_gasto():
    if os.environ.get("PERMITIR_IMAGEM_GPT") != "1":
        sys.exit("Geração de imagem pela API da OpenAI desligada (pedido do usuário em 28/10/2026). "
                 "As resenhas saem só com as fotos oficiais; nada foi enviado nem cobrado.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("conteudo")
    ap.add_argument("--modelo", default="gpt-image-2")
    ap.add_argument("--n", type=int, default=1)
    ap.add_argument("--tamanho", default=TAMANHO)
    ap.add_argument("--qualidade", default="high", choices=["low", "medium", "high"])
    ap.add_argument("--dry-run", action="store_true", help="só mostra o prompt, sem chamar a API")
    ap.add_argument("--sem-fotos", action="store_true", help="gera mesmo sem fotos oficiais (só com o OK do usuário)")
    a = ap.parse_args()

    c = json.load(open(a.conteudo, encoding="utf-8"))
    erros = checar(c)
    if erros:
        print(*erros, sep="\n - ")
        sys.exit("Roteiro fora do PADRAO_EDITORIAL.md; imagem não gerada.")
    texto = prompt(c)
    if not a.dry_run:
        travar_gasto()
    if not (a.dry_run or a.sem_fotos or fotos_liberadas(c["slug"])):
        sys.exit(f"{c['slug']}: {SEM_FOTOS}. Imagem não gerada.")
    if a.dry_run:
        print(texto)
        return

    chave = os.environ.get("OPENAI_API_KEY")
    if not chave:
        sys.exit("Defina OPENAI_API_KEY.")
    refs = sorted((ROOT / "modelos").glob("referencia-*.jpg"))
    r = requests.post(
        URL,
        headers={"Authorization": f"Bearer {chave}"},
        data={"model": a.modelo, "prompt": texto, "n": a.n, "size": a.tamanho, "quality": a.qualidade},
        files=[("image[]", (p.name, p.read_bytes(), "image/jpeg")) for p in refs],
        timeout=900,
    )
    d = r.json()
    if "error" in d:
        sys.exit(f"Erro da OpenAI ({r.status_code}): {d['error'].get('message')}")

    saida = ROOT / c["slug"]
    saida.mkdir(exist_ok=True)
    for i, img in enumerate(d["data"], 1):
        p = saida / f"variacao-{i}.png"
        p.write_bytes(base64.b64decode(img["b64_json"]))
        print(p)


if __name__ == "__main__":
    main()
