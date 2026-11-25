#!/usr/bin/env python3
"""Cartão de lei da novela (inserto na montagem), no mesmo desenho dos cartões da V1.

Uso: python3 tools/video/novela/cartao_lei.py saida.png "TÍTULO · ART. X" "texto literal lido na fonte" "rodapé com a fonte e a data"
O texto vai entre aspas curvas; use […] para trecho omitido. Só texto lido na fonte (regra "nada inventado").
"""
import glob, sys
from PIL import Image, ImageDraw, ImageFont

W = 1080
NAVY, CREME, AZUL_TXT, CINZA = (11, 26, 42, 255), (255, 252, 244, 255), (22, 48, 82, 255), (110, 110, 110, 255)


def fonte(nomes, tam):
    for n in nomes:
        achados = glob.glob(f"/usr/share/fonts/**/{n}", recursive=True)
        if achados:
            return ImageFont.truetype(achados[0], tam)
    return ImageFont.load_default()


def quebra(txt, f, larg):
    linhas, at = [], ""
    for p in txt.split():
        t = (at + " " + p).strip()
        if f.getlength(t) > larg and at:
            linhas.append(at); at = p
        else:
            at = t
    return linhas + [at]


def cartao(saida, titulo, texto, rodape):
    ft = fonte(["Inter-ExtraBold.otf", "DejaVuSans-Bold.ttf"], 30)
    fq = fonte(["LiberationSerif-Regular.ttf", "DejaVuSerif.ttf"], 38)
    fr = fonte(["Inter-Regular.otf", "Inter-Medium.otf", "DejaVuSans.ttf"], 22)
    larg = W - 2 * 66 - 44
    linhas = quebra("“" + texto + "”", fq, larg)
    alt = 46 + 44 + 18 + len(linhas) * 52 + 22 + 30 + 40
    im = Image.new("RGBA", (W, alt + 30), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((50, 14, W - 50, alt + 14), 28, fill=NAVY)
    d.rounded_rectangle((66, 14, W - 50, alt + 14), 28, fill=CREME)
    y = 14 + 46
    d.text((110, y), titulo, font=ft, fill=AZUL_TXT); y += 44 + 18
    for l in linhas:
        d.text((110, y), l, font=fq, fill=(25, 25, 25, 255)); y += 52
    d.text((110, y + 18), rodape, font=fr, fill=CINZA)
    im.save(saida)


if __name__ == "__main__":
    cartao(*sys.argv[1:5])
