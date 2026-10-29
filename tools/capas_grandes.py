"""Capas das notícias em tamanho bom para o Google (Discover pede imagem com pelo menos 1200 px de largura).

É preferência, não regra: nada aqui bloqueia a publicação. Sem versão cheia, fica a média; sem capa, nada acontece.

Uso: python3 tools/capas_grandes.py   troca as capas da Ludopedia em versão média (_m, ~500 px) pela versão cheia (~1000 px)
larga(arquivo) devolve uma versão 1200×675 (16:9) da imagem: a capa inteira no centro, sem esticar, e as laterais
preenchidas com a própria capa desfocada. Sem texto por cima; serve só para a imagem do NewsArticle (JSON-LD).
Ficam em img/discover/<nome>-<hash>-1200.jpg; o hash muda se a capa mudar.
"""
import hashlib
import io
import re
import sys
import urllib.request
from pathlib import Path

from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
CAPAS = ROOT / "noticias" / "capas"
DESTINO = ROOT / "img" / "discover"
LUDO = "https://storage.googleapis.com/ludopedia-capas/{id}.jpg"
LARG, ALT = 1200, 675


def larga(arquivo):
    """Path da versão 1200×675; imagens que já têm 1200 px de largura voltam como estão."""
    arquivo = Path(arquivo)
    with Image.open(arquivo) as im:
        if im.width >= LARG:
            return arquivo
        h = hashlib.sha256(arquivo.read_bytes()).hexdigest()[:8]
        alvo = DESTINO / f"{arquivo.stem}-{h}-{LARG}.jpg"
        if alvo.exists():
            return alvo
        im = im.convert("RGB")
        # fundo: a própria capa cobrindo o quadro inteiro, desfocada e escurecida
        esc = max(LARG / im.width, ALT / im.height)
        fundo = im.resize((round(im.width * esc), round(im.height * esc)), Image.LANCZOS)
        fundo = fundo.crop(((fundo.width - LARG) // 2, (fundo.height - ALT) // 2, (fundo.width - LARG) // 2 + LARG, (fundo.height - ALT) // 2 + ALT))
        fundo = fundo.filter(ImageFilter.GaussianBlur(28)).point(lambda v: int(v * 0.55))
        # frente: a capa inteira, sem ampliar além do tamanho original
        f = min(ALT / im.height, LARG / im.width, 1.0) if im.height > ALT else min(ALT / im.height, 1.35)
        frente = im.resize((round(im.width * f), round(im.height * f)), Image.LANCZOS)
        fundo.paste(frente, ((LARG - frente.width) // 2, (ALT - frente.height) // 2))
        DESTINO.mkdir(parents=True, exist_ok=True)
        fundo.save(alvo, "JPEG", quality=84, optimize=True, progressive=True)
        return alvo


def atualizar():
    """Troca capas da Ludopedia em versão média pela cheia; devolve quantas foram trocadas."""
    trocadas = 0
    for p in sorted(CAPAS.glob("*.jpg")):
        if not re.fullmatch(r"\d+", p.stem):
            continue
        try:
            with Image.open(p) as im:
                if im.width > 520:
                    continue
                atual = im.width
            with urllib.request.urlopen(urllib.request.Request(LUDO.format(id=p.stem), headers={"User-Agent": "PortalCristao/1.0"}), timeout=30) as r:
                dados = r.read()
            nova = Image.open(io.BytesIO(dados))
            nova.verify()
        except Exception as ex:  # sem versão cheia: fica a média
            print(f"  {p.name}: mantida ({ex.__class__.__name__})", file=sys.stderr)
            continue
        if Image.open(io.BytesIO(dados)).width > atual:
            p.write_bytes(dados)
            trocadas += 1
    return trocadas


if __name__ == "__main__":
    print("capas trocadas pela versão cheia:", atualizar())
