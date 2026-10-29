"""Converte a variação aprovada em infografico.webp e capa.jpg e apaga as variações.

Uso: python3 tools/salvar_imagem.py <slug> [variacao]   (padrão: variacao-1.png)
infografico.webp: 1600 px de largura, proporção original, até ~800 KB (o botão Salvar na galeria parte dela, então o texto pequeno precisa continuar nítido).
capa.jpg: 800×800 para o og:image e a lista, recortada do topo (título, caixa e números).
"""
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent


def salvar(slug, variacao="variacao-1.png"):
    pasta = ROOT / slug
    im = Image.open(pasta / variacao).convert("RGB")
    w, h = im.size
    alto = round(1600 * h / w)
    for q in range(88, 67, -4):
        im.resize((1600, alto), Image.LANCZOS).save(pasta / "infografico.webp", quality=q, method=6)
        if (pasta / "infografico.webp").stat().st_size <= 800_000:
            break
    capa = im.crop((0, 0, w, w)) if h > w else im
    for q in range(85, 55, -5):
        capa.resize((800, 800), Image.LANCZOS).save(pasta / "capa.jpg", quality=q, optimize=True, progressive=True)
        if (pasta / "capa.jpg").stat().st_size <= 250_000:
            break
    for v in pasta.glob("variacao-*.png"):
        v.unlink()
    print(slug, f"1600x{alto}", (pasta / "infografico.webp").stat().st_size, (pasta / "capa.jpg").stat().st_size)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    salvar(*sys.argv[1:3])
