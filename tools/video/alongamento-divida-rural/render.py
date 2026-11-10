"""Renderiza o vídeo vertical de 10 s sobre alongamento de dívida rural, quadro a quadro, sem imagem gerada por IA.

Tudo é desenhado em código (Pillow): fundo, documentos, títulos. A narração e os efeitos sonoros entram na mixagem (mixar.sh).
Uso: python3 render.py <pasta_saida_quadros>   (lê words.json da narração para sincronizar)
"""
import json
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
DUR = 10.8
AQUI = Path(__file__).resolve().parent
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else AQUI / "quadros")
OUT.mkdir(parents=True, exist_ok=True)

INTER = "/usr/share/fonts/opentype/inter/"
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-"
def f_black(s): return ImageFont.truetype(INTER + "InterDisplay-Black.otf", s)
def f_bold(s): return ImageFont.truetype(INTER + "Inter-Bold.otf", s)
def f_med(s): return ImageFont.truetype(INTER + "Inter-Medium.otf", s)
def f_serif(s, est="Regular"): return ImageFont.truetype(SERIF + est + ".ttf", s)

# paleta do portal (azul no lugar do preto) + vermelho e amarelo do vídeo de referência
AZUL0, AZUL1, AZUL2 = (6, 14, 30), (10, 26, 51), (30, 58, 100)
VERM, AMAR, PAPEL, TINTA = (226, 35, 45), (240, 194, 75), (243, 238, 226), (28, 28, 30)

# tempos das palavras da narração (gerados junto com a voz)
PAL = json.load(open(AQUI / "words.json", encoding="utf-8"))
def t_de(palavra, n=1):
    k = 0
    for w, s, e in PAL:
        if w.strip(".,:?").lower() == palavra.lower():
            k += 1
            if k == n:
                return s
    raise KeyError(palavra)

T_S2 = t_de("Desde") - 0.08          # data + Manual
T_S3 = t_de("por") - 0.12            # trecho da resolução
T_S4 = t_de("Mas") - 0.08            # "Mas a parte mais estranha?"
T_S5 = t_de("O", 2) - 0.10              # Súmula 298

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_inout(x): x = clamp(x); return 3 * x * x - 2 * x * x * x
def back_out(x, s=1.70158):
    x = clamp(x) - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2
def lerp(a, b, t): return a + (b - a) * t

random.seed(7)

# ---------- elementos fixos ----------
def gradiente(c0, c1, h=H, w=W):
    g = Image.new("RGB", (1, h))
    for y in range(h):
        t = y / (h - 1)
        g.putpixel((0, y), tuple(int(lerp(c0[i], c1[i], t)) for i in range(3)))
    return g.resize((w, h))

def fundo_lavoura():
    """Noite sobre lavoura: céu, silos no horizonte e linhas de plantio em perspectiva (desenho vetorial)."""
    S = 1.25  # margem para o push-in
    w, h = int(W * S), int(H * S)
    im = gradiente((4, 10, 24), AZUL2, h=int(h * 0.58), w=w)
    base = Image.new("RGB", (w, h), AZUL0)
    base.paste(im, (0, 0))
    d = ImageDraw.Draw(base)
    for _ in range(260):  # estrelas
        x, y = random.randrange(w), random.randrange(int(h * 0.5))
        r = random.choice([1, 1, 1, 2])
        c = random.randint(120, 230)
        d.ellipse((x, y, x + r, y + r), fill=(c, c, min(255, c + 20)))
    hz = int(h * 0.58)
    # silos e armazém
    silo = (8, 18, 36)
    for i, (x, sw, sh) in enumerate([(int(w * .62), 120, 330), (int(w * .62) + 135, 120, 300), (int(w * .62) + 270, 95, 250)]):
        d.rectangle((x, hz - sh, x + sw, hz), fill=silo)
        d.pieslice((x, hz - sh - sw // 2, x + sw, hz - sh + sw // 2), 180, 360, fill=silo)
        for k in range(6):
            yy = hz - sh + 30 + k * (sh // 7)
            d.line((x, yy, x + sw, yy), fill=(18, 32, 58), width=2)
    d.rectangle((int(w * .62) - 300, hz - 120, int(w * .62) - 20, hz), fill=silo)
    d.polygon([(int(w * .62) - 320, hz - 120), (int(w * .62) - 160, hz - 190), (int(w * .62), hz - 120)], fill=silo)
    luz = Image.new("L", (w, h), 0)
    ImageDraw.Draw(luz).ellipse((int(w * .62) - 200, hz - 150, int(w * .62) - 120, hz - 70), fill=255)
    luz = luz.filter(ImageFilter.GaussianBlur(40))
    base = Image.composite(Image.new("RGB", (w, h), (255, 196, 110)), base, luz.point(lambda v: int(v * .55)))
    d = ImageDraw.Draw(base)
    d.rectangle((int(w * .62) - 168, hz - 98, int(w * .62) - 150, hz - 84), fill=(255, 214, 140))
    # solo e linhas de plantio
    d.rectangle((0, hz, w, h), fill=(9, 20, 22))
    vx, vy = w * 0.45, hz - 10
    for k in range(-40, 41):
        xb = vx + k * 95
        d.line((vx, vy, xb, h), fill=(22, 44, 40), width=3)
    for i in range(1, 40):  # plantas: pontos que crescem com a proximidade
        t = (i / 40) ** 2.2
        y = vy + (h - vy) * t
        for k in range(-40, 41):
            x = vx + (vx + k * 95 - vx) * t
            if 0 <= x < w:
                r = 1 + 9 * t
                d.ellipse((x - r * 1.6, y - r, x + r * 1.6, y + r * .4), fill=(30, 70, 52))
    neb = Image.new("L", (w, h), 0)
    ImageDraw.Draw(neb).rectangle((0, hz - 60, w, hz + 80), fill=90)
    neb = neb.filter(ImageFilter.GaussianBlur(60))
    base = Image.composite(Image.new("RGB", (w, h), (70, 100, 150)), base, neb)
    return base

def vinheta():
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).ellipse((-W * .35, -H * .2, W * 1.35, H * 1.2), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(220))
    return m

GRAOS = []
for _ in range(6):
    n = Image.effect_noise((W // 2, H // 2), 28).resize((W, H))
    GRAOS.append(n)

FUNDO = fundo_lavoura()
VIN = vinheta()
POEIRA = [(random.random() * W, random.random() * H, random.uniform(1, 3.5), random.uniform(-14, 14), random.uniform(-40, -10)) for _ in range(40)]

def camera(img, t, z0, z1, cx=0.5, cy=0.5):
    """Push-in contínuo (como a câmera do vídeo de referência)."""
    z = lerp(z0, z1, t)
    w, h = img.size
    cw = W / z
    ch = H / z
    x0 = (w - cw) * cx
    y0 = (h - ch) * cy
    return img.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.BILINEAR)

def texto_3d(txt, font, face, lado, prof=14, glow=None):
    """Texto com extrusão e brilho, no estilo do título de abertura da referência."""
    bb = font.getbbox(txt)
    tw, th = bb[2] + prof + 60, bb[3] + prof + 60
    lay = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for k in range(prof, 0, -1):
        d.text((30 + k * .6, 30 + k), txt, font=font, fill=lado)
    d.text((30, 30), txt, font=font, fill=face)
    if glow:
        g = Image.new("RGBA", lay.size, (0, 0, 0, 0))
        ImageDraw.Draw(g).text((30, 30), txt, font=font, fill=glow)
        g = g.filter(ImageFilter.GaussianBlur(18))
        lay = Image.alpha_composite(g, lay)
    return lay

def colar(base, lay, cx, cy, escala=1.0, rot=0.0, alfa=1.0):
    if escala <= 0.01 or alfa <= 0:
        return
    l = lay
    if escala != 1.0:
        l = l.resize((max(1, int(l.width * escala)), max(1, int(l.height * escala))), Image.BICUBIC)
    if rot:
        l = l.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alfa < 1:
        a = l.getchannel("A").point(lambda v: int(v * alfa))
        l.putalpha(a)
    base.alpha_composite(l, (int(cx - l.width / 2), int(cy - l.height / 2)))

def quebra(txt, font, largura):
    linhas, cur = [], ""
    for w in txt.split():
        p = (cur + " " + w).strip()
        if font.getlength(p) > largura and cur:
            linhas.append(cur); cur = w
        else:
            cur = p
    linhas.append(cur)
    return linhas

# ---------- peças pré-desenhadas ----------
TIT1 = texto_3d("DÍVIDA RURAL", f_black(118), (245, 245, 250), (120, 130, 150), prof=12, glow=(255, 255, 255, 90))
TIT2a = texto_3d("DECISÃO", f_black(150), VERM, (110, 10, 18), prof=16, glow=(255, 40, 50, 170))
TIT2b = texto_3d("DO BANCO", f_black(150), VERM, (110, 10, 18), prof=16, glow=(255, 40, 50, 170))

def pilula(txt, cor=VERM, fs=86):
    f = f_black(fs)
    bb = f.getbbox(txt)
    w, h = bb[2] + 80, fs + 56
    l = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(l)
    d.rounded_rectangle((20, 26, 20 + w, 26 + h), radius=26, fill=(0, 0, 0, 120))
    d.rounded_rectangle((20, 20, 20 + w, 20 + h), radius=26, fill=cor)
    d.text((20 + 40, 20 + 22 - bb[1] + 6), txt, font=f, fill=(255, 255, 255))
    return l

DATA = pilula("1º/7/2026")

def cartao_mcr():
    """Pasta de norma: o MCR, capítulo 2, seção 6, item 4 (referência, sem logotipo)."""
    w, h = 760, 980
    l = Image.new("RGBA", (w + 60, h + 60), (0, 0, 0, 0))
    sh = Image.new("RGBA", l.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((40, 50, 40 + w, 50 + h), 24, fill=(0, 0, 0, 170))
    l = Image.alpha_composite(l, sh.filter(ImageFilter.GaussianBlur(22)))
    d = ImageDraw.Draw(l)
    d.rounded_rectangle((30, 30, 30 + w, 30 + h), 22, fill=(20, 52, 44))
    d.rounded_rectangle((30, 30, 70, 30 + h), 10, fill=(12, 34, 28))
    d.rectangle((110, 120, 30 + w - 70, 124), fill=AMAR)
    for i, (txt, f) in enumerate([("MANUAL DE", f_black(70)), ("CRÉDITO", f_black(96)), ("RURAL", f_black(96))]):
        d.text((110, 170 + i * 110), txt, font=f, fill=(245, 230, 190))
    d.rectangle((110, 520, 30 + w - 70, 524), fill=AMAR)
    d.text((110, 580), "MCR 2-6-4", font=f_bold(64), fill=AMAR)
    d.text((110, 670), "Capítulo 2 · Seção 6", font=f_med(40), fill=(220, 220, 210))
    d.text((110, 725), "Reembolso · prorrogação", font=f_med(40), fill=(220, 220, 210))
    d.text((110, 900), "Res. CMN 5.314, de 25/6/2026", font=f_med(34), fill=(170, 190, 180))
    return l

MCR = cartao_mcr()

TRECHO_PRE = "4 - Fica a instituição financeira autorizada,"
TRECHO_REALCE = "por sua conveniência e decisão,"
TRECHO_POS = "mediante solicitação do mutuário, a prorrogar a dívida referente à operação de crédito rural (...)"

def documento_resolucao():
    """Folha com o trecho literal do novo MCR 2-6-4 (texto lido na Resolução CMN 5.314/2026, site do BCB)."""
    w, h = 880, 1180
    l = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(l)
    d.rectangle((0, 0, w, h), fill=PAPEL)
    for _ in range(1600):  # textura de papel
        x, y = random.randrange(w), random.randrange(h)
        c = random.randint(215, 240)
        d.point((x, y), fill=(c, c - 4, c - 14))
    d.text((60, 56), "RESOLUÇÃO CMN Nº 5.314,", font=f_serif(52, "Bold"), fill=TINTA)
    d.text((60, 118), "DE 25 DE JUNHO DE 2026", font=f_serif(52, "Bold"), fill=TINTA)
    d.line((60, 196, w - 60, 196), fill=TINTA, width=3)
    d.text((60, 214), "Altera o MCR 2-6-4 · em vigor em 1º de julho de 2026", font=f_serif(32, "Italic"), fill=(70, 70, 70))
    f = f_serif(50)
    pos = []  # retângulos do trecho realçado (para o marcador)
    x, y, lh = 60, 300, 70
    def escreve(txt, marca=False):
        nonlocal x, y
        for p in txt.split():
            pw = f.getlength(p + " ")
            if x + f.getlength(p) > w - 60:
                x, y = 60, y + lh
            if marca:
                pos.append((x - 4, y + 4, x + f.getlength(p) + 6, y + 58))
            d.text((x, y), p, font=f, fill=TINTA)
            x += pw
    escreve(TRECHO_PRE)
    escreve(TRECHO_REALCE, True)
    escreve(TRECHO_POS)
    yb = y + lh + 40
    for k in range(5):  # linhas cinzas: resto do texto, sem inventar palavras
        d.rectangle((60, yb + k * 48, w - 60 - (k % 3) * 140, yb + k * 48 + 16), fill=(205, 200, 188))
    d.text((60, h - 80), "Trecho literal · bcb.gov.br", font=f_med(30), fill=(110, 110, 110))
    return l, pos

DOC, DOC_REALCE = documento_resolucao()

SUMULA_TXT = ("O alongamento de dívida originada de crédito rural não constitui faculdade da instituição "
              "financeira, mas, direito do devedor nos termos da lei.")

def documento_sumula():
    w, h = 900, 900
    l = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(l)
    d.rectangle((0, 0, w, h), fill=PAPEL)
    d.text((60, 56), "SÚMULA 298", font=f_serif(70, "Bold"), fill=TINTA)
    d.text((60, 146), "Superior Tribunal de Justiça · 2ª Seção · 2004", font=f_serif(34, "Italic"), fill=(70, 70, 70))
    d.line((60, 204, w - 60, 204), fill=TINTA, width=3)
    f = f_serif(52)
    y = 240
    marca = []
    for linha in quebra("“" + SUMULA_TXT + "”", f, w - 120):
        x = 60
        for p in linha.split():
            if p.strip("”,.").lower() in ("direito", "devedor") or (p == "do" and "direito do devedor" in linha):
                marca.append((x - 4, y + 4, x + f.getlength(p) + 6, y + 60))
            x += f.getlength(p + " ")
        d.text((60, y), linha, font=f, fill=TINTA)
        y += 72
    d.text((60, h - 80), "Texto literal · scon.stj.jus.br", font=f_med(30), fill=(110, 110, 110))
    return l, marca

SUM, SUM_REALCE = documento_sumula()

def placa(txt1, txt2):
    """Placa amarela que salta, como a "NUCLEAR BILLBOARD" da referência."""
    f1, f2 = f_black(52), f_black(86)
    w = int(max(f1.getlength(txt1), f2.getlength(txt2))) + 120
    h = 250
    l = Image.new("RGBA", (w + 60, h + 60), (0, 0, 0, 0))
    g = Image.new("RGBA", l.size, (0, 0, 0, 0))
    ImageDraw.Draw(g).rounded_rectangle((30, 30, 30 + w, 30 + h), 22, fill=(255, 170, 40, 200))
    l = Image.alpha_composite(l, g.filter(ImageFilter.GaussianBlur(26)))
    d = ImageDraw.Draw(l)
    d.rounded_rectangle((30, 30, 30 + w, 30 + h), 22, fill=AMAR)
    d.rounded_rectangle((44, 44, 16 + w, 16 + h), 16, outline=(140, 90, 10), width=4)
    d.text((30 + (w - f1.getlength(txt1)) / 2, 62), txt1, font=f1, fill=(120, 20, 20))
    d.text((30 + (w - f2.getlength(txt2)) / 2, 122), txt2, font=f2, fill=(120, 20, 20))
    return l

PLACA = placa("SÚMULA 298 DO STJ:", "DIREITO DO DEVEDOR")

def rodape():
    l = Image.new("RGBA", (W, 150), (0, 0, 0, 0))
    d = ImageDraw.Draw(l)
    f = f_med(30)
    linhas = ["Fontes: Resolução CMN 5.314/2026 (Banco Central)", "e Súmula 298 do STJ · opaladino.com.br"]
    for i, s in enumerate(linhas):
        x = (W - f.getlength(s)) / 2
        d.text((x + 2, 32 + i * 42 + 2), s, font=f, fill=(0, 0, 0, 200))
        d.text((x, 32 + i * 42), s, font=f, fill=(225, 230, 240, 235))
    return l

RODAPE = rodape()

# palavras soltas em serifa itálica (cena "Mas a parte mais estranha?")
SOLTAS = [("Mas", 300, 760, 74), ("a", 520, 860, 64), ("parte", 760, 700, 80), ("mais", 360, 1010, 80), ("estranha?", 640, 1130, 104)]

# ---------- cenas ----------
def marcar(doc, rets, prog):
    """Passa o marcador amarelo (multiplicação, a tinta continua visível) até a fração prog dos retângulos."""
    m = Image.new("RGB", doc.size, (255, 255, 255))
    dm = ImageDraw.Draw(m)
    for i, (x0, y0, x1, y1) in enumerate(rets):
        f = clamp(prog - i)
        if f > 0:
            dm.rectangle((x0, y0, x0 + (x1 - x0) * f, y1), fill=(255, 222, 60))
    out = ImageChops.multiply(doc.convert("RGB"), m).convert("RGBA")
    out.putalpha(doc.getchannel("A"))
    return out

def cena1(t, base):
    p = t / T_S2
    bg = camera(FUNDO, ease_inout(p), 1.0, 1.12, cx=0.5, cy=0.62)
    base.paste(bg)
    s = clamp((t - 0.02) / 0.35)
    colar(base, TIT1, W / 2, 360, escala=lerp(1.6, 1.0, ease_out(s)), alfa=s)
    td = t_de("decisão") - 0.06
    s2 = clamp((t - td) / 0.28)
    colar(base, TIT2a, W / 2, 530, escala=back_out(s2) * 1.0, rot=lerp(-6, -3, s2), alfa=s2)
    tb = t_de("banco") - 0.06
    s3 = clamp((t - tb) / 0.28)
    colar(base, TIT2b, W / 2, 700, escala=back_out(s3), rot=lerp(4, -3, s3), alfa=s3)

def cena2(t, base):
    p = (t - T_S2) / (T_S3 - T_S2)
    g = gradiente(AZUL1, AZUL0)
    base.paste(g)
    luz = Image.new("L", (W, H), 0)
    ImageDraw.Draw(luz).ellipse((W * .1, H * .22, W * .9, H * .78), fill=150)
    luz = luz.filter(ImageFilter.GaussianBlur(120))
    base.paste(Image.composite(Image.new("RGB", (W, H), AZUL2), base.convert("RGB"), luz))
    tm = T_S2
    s = clamp((t - tm) / 0.4)
    z = lerp(0.92, 1.04, ease_inout(p))
    colar(base, MCR, W / 2, lerp(1300, 1060, ease_out(s)), escala=z * lerp(0.85, 1, ease_out(s)), rot=lerp(8, 2, ease_out(s)), alfa=s)
    tj = t_de("julho") - 0.05
    s2 = clamp((t - tj) / 0.25)
    colar(base, DATA, W / 2, 380, escala=back_out(s2) * 1.05, rot=-2, alfa=s2)

def cena3(t, base):
    p = (t - T_S3) / (T_S4 - T_S3)
    base.paste(gradiente((38, 26, 18), (14, 10, 8)))  # mesa escura
    d = ImageDraw.Draw(base)
    for k in range(0, H, 34):  # veios da madeira
        d.line((0, k + 10 * math.sin(k / 70), W, k + 18 * math.cos(k / 50)), fill=(48, 33, 22), width=2)
    s = ease_out(clamp((t - T_S3) / 0.32))
    # marcador amarelo passando sobre "por sua conveniência e decisão", no ritmo da fala
    t0, t1 = t_de("por"), t_de("decisão", 2) + 0.4
    n = len(DOC_REALCE)
    prog = clamp((t - t0) / (t1 - t0)) * n
    rgba = marcar(DOC, DOC_REALCE, prog)
    escala = lerp(2.2, 1.0, s) * lerp(1.0, 1.08, ease_inout(p))
    colar(base, rgba, W / 2 + lerp(380, 0, s), lerp(1500, 960, s), escala=escala, rot=lerp(-35, -3, s))

def cena4(t, base):
    base.paste(gradiente((8, 12, 22), (2, 4, 10)))
    d = ImageDraw.Draw(base)
    for (w, x, y, fs) in SOLTAS:
        ts = t_de(w.strip("?")) - 0.04
        a = clamp((t - ts) / 0.22)
        if a <= 0:
            continue
        f = f_serif(fs, "Italic")
        c = int(235 * a)
        dy = (1 - ease_out(a)) * 30
        d.text((x - f.getlength(w) / 2, y + dy), w, font=f, fill=(c, c, min(255, c + 10)))

def cena5(t, base):
    p = (t - T_S5) / (DUR - T_S5)
    bg = camera(FUNDO, ease_inout(p), 1.18, 1.3, cx=0.5, cy=0.7)
    base.paste(bg.point(lambda v: int(v * 0.7)))
    s = ease_out(clamp((t - T_S5) / 0.35))
    td = t_de("direito")
    prog = clamp((t - td) / 0.9) * len(SUM_REALCE)
    doc = marcar(SUM, SUM_REALCE, prog)
    colar(base, doc, W / 2, lerp(1700, 1180, s), escala=lerp(1.0, 1.05, ease_inout(p)), rot=lerp(12, 2, s), alfa=clamp(s * 2))
    tp = t_de("STJ") - 0.1
    s2 = clamp((t - tp) / 0.3)
    shake = math.sin(t * 70) * 6 * (1 - clamp((t - tp) / 0.5)) if s2 > 0 else 0
    colar(base, PLACA, W / 2 + shake, 470, escala=back_out(s2, 2.4) * 0.98, rot=1.5, alfa=s2)

def efeitos(base, t, i):
    # poeira em suspensão
    d = ImageDraw.Draw(base, "RGBA")
    for (x, y, r, vx, vy) in POEIRA:
        xx = (x + vx * t) % W
        yy = (y + vy * t) % H
        d.ellipse((xx - r, yy - r, xx + r, yy + r), fill=(255, 240, 220, 38))
    rgb = base.convert("RGB")
    # vinheta
    rgb = Image.composite(rgb, Image.new("RGB", (W, H), (0, 0, 0)), VIN.point(lambda v: 70 + int(v * 0.73)))
    # flash nas viradas de cena
    flash = 0.0
    for tc in (0.0, T_S2, T_S3, T_S5):
        dt = t - tc
        if 0 <= dt < 0.18:
            flash = max(flash, 1 - dt / 0.18)
    if flash > 0:
        rgb = Image.blend(rgb, Image.new("RGB", (W, H), (255, 250, 240)), flash * 0.75)
    # granulação de filme
    g = GRAOS[i % len(GRAOS)]
    rgb = Image.blend(rgb, Image.merge("RGB", (g, g, g)), 0.07)
    out = rgb.convert("RGBA")
    out.alpha_composite(RODAPE, (0, H - 190))
    return out.convert("RGB")

def quadro(i):
    t = i / FPS
    base = Image.new("RGBA", (W, H), AZUL0 + (255,))
    if t < T_S2:
        cena1(t, base)
    elif t < T_S3:
        cena2(t, base)
    elif t < T_S4:
        cena3(t, base)
    elif t < T_S5:
        cena4(t, base)
    else:
        cena5(t, base)
    # tremor de câmera curto no impacto de abertura
    if t < 0.4:
        a = (0.4 - t) / 0.4 * 14
        base = base.transform(base.size, Image.AFFINE, (1, 0, math.sin(t * 90) * a, 0, 1, math.cos(t * 77) * a))
    return efeitos(base, t, i)

if __name__ == "__main__":
    so = sys.argv[2:]  # opcional: lista de quadros (prévia)
    idx = [int(x) for x in so] if so else range(int(DUR * FPS))
    for i in idx:
        quadro(i).save(OUT / f"q{i:04d}.jpg", quality=92)
    print("ok", len(list(idx)), "quadros; cenas em", round(T_S2, 2), round(T_S3, 2), round(T_S4, 2), round(T_S5, 2))
