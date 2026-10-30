"""Gera o banner do topo do site (marca/banner-<largura>.webp) a partir da arte original em assets/marca/original/banner.png.

Uso: python3 tools/gerar_banner.py   (rode de novo só quando a arte do banner mudar)
Corta as faixas escuras de cima e de baixo da arte (2048×768), preservando a espada da coroa, e salva quatro larguras
para o srcset do cabeçalho (tools/layout.py): o celular baixa a de 640 px, a tela grande a de 1920.
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ORIGINAL = ROOT / "assets" / "marca" / "original" / "banner.png"
CORTE = (0, 66, 2048, 700)  # x0, y0, x1, y1 na arte de 2048×768: do topo da espada ao fim da imagem
LARGURAS = (640, 960, 1280, 1920)


def main():
    arte = Image.open(ORIGINAL).convert("RGB").crop(CORTE)
    for w in LARGURAS:
        h = round(arte.height * w / arte.width)
        saida = ROOT / "marca" / f"banner-{w}.webp"
        arte.resize((w, h), Image.LANCZOS).save(saida, "WEBP", quality=80, method=6)
        print(f"ok {saida.relative_to(ROOT)}: {w}×{h}, {saida.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
