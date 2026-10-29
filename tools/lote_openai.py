"""Gera os infográficos pela Batch API da OpenAI (50% mais barata, entrega em até 24 h).

Uso:
  python3 tools/lote_openai.py enviar conteudo/<slug>.json [...]   cria o lote e grava lotes/pendente.json
                                                                   (recusa jogo sem fotos oficiais liberadas; --sem-fotos só com o OK do usuário)
  python3 tools/lote_openai.py buscar                              baixa o lote pendente para <slug>/variacao-1.png
Precisa de OPENAI_API_KEY. As referências vêm de modelos/ já publicados no GitHub Pages.
"""
import base64
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from checar_roteiro import SEM_FOTOS, checar, checar_texto, fotos_liberadas  # noqa: E402
from prompt_infografico import TAMANHO, prompt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://meruvash.github.io/Arcvalion_gospel"
API = "https://api.openai.com/v1"
PENDENTE = ROOT / "lotes" / "pendente.json"
MODELO = os.environ.get("MODELO_IMAGEM", "gpt-image-2.5-flare")


def cabecalho():
    chave = os.environ.get("OPENAI_API_KEY")
    if not chave:
        sys.exit("Defina OPENAI_API_KEY.")
    return {"Authorization": f"Bearer {chave}"}


# Pedido do usuário em 28/10/2026: resenhas sem gerar imagem pela API da OpenAI (sem gastos).
# Só gera com PERMITIR_IMAGEM_GPT=1 no ambiente, e isso só com um novo OK explícito do usuário.
def travar_gasto():
    if os.environ.get("PERMITIR_IMAGEM_GPT") != "1":
        sys.exit("Geração de imagem pela API da OpenAI desligada (pedido do usuário em 28/10/2026). "
                 "As resenhas saem só com as fotos oficiais; nada foi enviado nem cobrado.")


def enviar(arquivos, sem_fotos=False):
    travar_gasto()
    if not sem_fotos:
        faltam = [a for a in arquivos if not fotos_liberadas(json.loads(Path(a).read_text(encoding="utf-8"))["slug"])]
        if faltam:
            sys.exit(f"Lote não enviado: {', '.join(faltam)}: {SEM_FOTOS}.")
    if PENDENTE.exists():
        sys.exit(f"Já existe um lote pendente em {PENDENTE.relative_to(ROOT)}; rode 'buscar' antes.")
    reprovados = {a: (lambda c: checar(c) + checar_texto(c))(json.loads(Path(a).read_text(encoding="utf-8"))) for a in arquivos}
    reprovados = {a: e for a, e in reprovados.items() if e}
    if reprovados:
        for a, erros in reprovados.items():
            print(f"✗ {a}:", *erros, sep="\n   - ")
        sys.exit("Lote não enviado: roteiro fora do PADRAO_EDITORIAL.md (rode tools/checar_roteiro.py).")
    refs = [{"image_url": f"{SITE}/modelos/{p.name}"} for p in sorted((ROOT / "modelos").glob("referencia-*.jpg"))]
    linhas, slugs = [], []
    for a in arquivos:
        c = json.loads(Path(a).read_text(encoding="utf-8"))
        slugs.append(c["slug"])
        corpo = {"model": MODELO, "prompt": prompt(c), "images": refs, "size": TAMANHO, "quality": "high", "n": 1}
        linhas.append(json.dumps({"custom_id": c["slug"], "method": "POST", "url": "/v1/images/edits", "body": corpo}, ensure_ascii=False))
    h = cabecalho()
    f = requests.post(f"{API}/files", headers=h, data={"purpose": "batch"},
                      files={"file": ("lote.jsonl", "\n".join(linhas).encode("utf-8"), "application/jsonl")}, timeout=120).json()
    if "error" in f:
        sys.exit(f"Erro no upload: {f['error'].get('message')}")
    b = requests.post(f"{API}/batches", headers=h, timeout=120,
                      json={"input_file_id": f["id"], "endpoint": "/v1/images/edits", "completion_window": "24h"}).json()
    if "error" in b:
        sys.exit(f"Erro ao criar o lote: {b['error'].get('message')}")
    PENDENTE.parent.mkdir(exist_ok=True)
    PENDENTE.write_text(json.dumps({"batch_id": b["id"], "modelo": MODELO, "slugs": slugs,
                                    "enviado_em": datetime.now(timezone.utc).isoformat(timespec="seconds")}, indent=1) + "\n")
    print("lote enviado", b["id"], slugs)


def buscar():
    if not PENDENTE.exists():
        sys.exit("Nenhum lote pendente.")
    p = json.loads(PENDENTE.read_text())
    h = cabecalho()
    b = requests.get(f"{API}/batches/{p['batch_id']}", headers=h, timeout=60).json()
    print("status:", b.get("status"), b.get("request_counts"))
    if b.get("status") != "completed":
        sys.exit(0 if b.get("status") in ("validating", "in_progress", "finalizing") else 1)
    if b.get("error_file_id"):
        print(requests.get(f"{API}/files/{b['error_file_id']}/content", headers=h, timeout=120).text)
    if b.get("output_file_id"):
        for linha in requests.get(f"{API}/files/{b['output_file_id']}/content", headers=h, timeout=600).text.splitlines():
            r = json.loads(linha)
            corpo = r["response"]["body"]
            if r["response"]["status_code"] != 200:
                print("falhou", r["custom_id"], corpo.get("error", {}).get("message"))
                continue
            destino = ROOT / r["custom_id"] / "variacao-1.png"
            destino.parent.mkdir(exist_ok=True)
            destino.write_bytes(base64.b64decode(corpo["data"][0]["b64_json"]))
            print(destino.relative_to(ROOT))
    PENDENTE.unlink()


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "enviar":
        enviar([a for a in sys.argv[2:] if a != "--sem-fotos"], "--sem-fotos" in sys.argv)
    elif sys.argv[1:] == ["buscar"]:
        buscar()
    else:
        sys.exit(__doc__)
