"""Colagem Vox desenhada em código (sem imagem de IA) para o vídeo do alongamento de dívida rural.

Tema `newsprint-editorial` da skill vox-director sobre o azul do portal: recortes de papel com borda rasgada, fita,
retícula, sombra de papel; prints oficiais entram como recortes colados. Quadrado 1080x1080, 30 fps.
Uso: python3 colagem.py <pasta_quadros> <t_ini> <t_fim>     (ex.: teste de 10 s = 0 10)
Lê linha_do_tempo.json (montar_voz.py), voz_v3/stt/proc*.json (tempos das palavras) e prints/.
"""
import json
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

W = H = 1080
FPS = 30
AQUI = Path(__file__).resolve().parent
INTER = "/usr/share/fonts/opentype/inter/"
def fonte(peso, tam): return ImageFont.truetype(INTER + {"black": "InterDisplay-Black.otf", "bold": "Inter-Bold.otf",
                                                          "med": "Inter-Medium.otf"}[peso], tam)
MONO = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf"

AZUL0, AZUL1 = (8, 20, 40), (16, 36, 66)
CREME, CARVAO, MOSTARDA, VERMELHO = (243, 236, 220), (28, 28, 30), (240, 194, 75), (179, 32, 42)
VERDES = [(46, 92, 58), (62, 118, 70), (84, 140, 78), (110, 160, 90)]
random.seed(11)

# ---------- tempo ----------
LT = json.load(open(AQUI / "linha_do_tempo.json"))
INI = {f["fala"]: f["inicio"] for f in LT["falas"]}
def palavras(fala):
    p = AQUI / f"voz_v3/stt/proc{fala}.json"
    d = json.load(open(p))
    return [(w["text"], w["start"] + INI[fala], w["end"] + INI[fala]) for w in d["words"] if w["type"] == "word"]
PAL = palavras(1) + palavras(2)
def t_de(txt, fala_ini=0.0):
    for w, s, e in PAL:
        if s >= fala_ini and w.strip(".,:?!\"").lower() == txt.lower():
            return s
    raise KeyError(txt)

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def expo(x): x = clamp(x); return 1 - 2 ** (-10 * x) if x < 1 else 1.0   # cubic-bezier(0.16,1,0.3,1) aproximada
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def lerp(a, b, t): return a + (b - a) * t
def back(x, s=1.6): x = clamp(x) - 1; return 1 + (s + 1) * x ** 3 + s * x ** 2

# ---------- papel ----------
def textura_papel(w, h, cor, fibras=True, sem=0):
    rnd = random.Random(sem)
    base = Image.new("RGB", (w, h), cor)
    ruido = Image.effect_noise((max(1, w // 2), max(1, h // 2)), 18).resize((w, h)).convert("RGB")
    base = Image.blend(base, ImageChops.multiply(base, ruido.point(lambda v: 200 + v // 5)), 0.6)
    if fibras:
        d = ImageDraw.Draw(base)
        for _ in range(w * h // 9000):
            x, y = rnd.randrange(w), rnd.randrange(h)
            c = tuple(max(0, k - rnd.randint(8, 22)) for k in cor)
            d.line((x, y, x + rnd.randint(-14, 14), y + rnd.randint(-5, 5)), fill=c, width=1)
    return base

def mascara_rasgada(w, h, margem=10, aspereza=7, sem=0, lados="tblr"):
    """Contorno de papel rasgado à mão (só nos lados pedidos; os outros ficam cortados a tesoura)."""
    rnd = random.Random(sem)
    pts = []
    def borda(p0, p1, rasga, n):
        for i in range(n):
            t = i / n
            x, y = lerp(p0[0], p1[0], t), lerp(p0[1], p1[1], t)
            if rasga:
                dx, dy = (p1[1] - p0[1]), -(p1[0] - p0[0])
                L = math.hypot(dx, dy) or 1
                k = rnd.uniform(-aspereza, aspereza) + aspereza * 0.3 * math.sin(i * 0.7)
                x, y = x + dx / L * k, y + dy / L * k
            pts.append((x, y))
    m = margem
    borda((m, m), (w - m, m), "t" in lados, max(8, w // 9))
    borda((w - m, m), (w - m, h - m), "r" in lados, max(8, h // 9))
    borda((w - m, h - m), (m, h - m), "b" in lados, max(8, w // 9))
    borda((m, h - m), (m, m), "l" in lados, max(8, h // 9))
    mk = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mk).polygon(pts, fill=255)
    return mk

def recorte(img_rgb, sem=0, lados="tblr", borda_branca=True, sombra=True):
    """Transforma uma imagem num recorte de papel: borda rasgada com fibra branca + sombra de papel."""
    w, h = img_rgb.size
    pad = 26
    tela = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    mk = mascara_rasgada(w, h, margem=6, aspereza=6, sem=sem, lados=lados)
    forma = img_rgb.getchannel("A") if img_rgb.mode == "RGBA" else None
    if forma is not None:  # recorte com forma própria (sol, nuvem, morro): a borda rasgada segue a forma
        mk = ImageChops.multiply(mk, forma.filter(ImageFilter.MinFilter(5)))
    if borda_branca:  # a fibra branca que aparece no papel rasgado
        branca = mascara_rasgada(w, h, margem=2, aspereza=7, sem=sem + 1, lados=lados)
        if forma is not None:
            branca = ImageChops.multiply(branca, forma)
        fib = Image.new("RGBA", (w, h), (250, 247, 238, 255)); fib.putalpha(branca)
        tela.alpha_composite(fib, (pad, pad))
    peca = img_rgb.convert("RGBA"); peca.putalpha(mk)
    tela.alpha_composite(peca, (pad, pad))
    if sombra:
        a = tela.getchannel("A").filter(ImageFilter.GaussianBlur(9))
        s = Image.new("RGBA", tela.size, (0, 0, 0, 0)); s.putalpha(a.point(lambda v: int(v * 0.55)))
        out = Image.new("RGBA", tela.size, (0, 0, 0, 0))
        out.alpha_composite(s, (8, 12))
        out.alpha_composite(tela)
        return out
    return tela

def fita(w=170, h=50, ang=0, sem=0):
    rnd = random.Random(sem)
    l = Image.new("RGBA", (w, h), (236, 226, 190, 150))
    d = ImageDraw.Draw(l)
    for x in range(0, w, 3):  # serrilhado das pontas
        d.rectangle((x, 0, x + 1, rnd.randint(0, 4)), fill=(0, 0, 0, 0))
        d.rectangle((x, h - rnd.randint(0, 4), x + 1, h), fill=(0, 0, 0, 0))
    return l.rotate(ang, expand=True, resample=Image.BICUBIC)

def reticula(w, h, passo=9, cor=(0, 0, 0), alfa=40, ang_luz=(0.3, 0.2)):
    """Retícula de impressão: pontos maiores onde a luz é menor."""
    l = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(l)
    for y in range(0, h, passo):
        for x in range((y // passo % 2) * passo // 2, w, passo):
            v = clamp((x / w) * ang_luz[0] + (y / h) * ang_luz[1] + 0.15)
            r = passo * 0.42 * v
            if r > 0.6:
                d.ellipse((x - r, y - r, x + r, y + r), fill=cor + (alfa,))
    return l

def colar(base, lay, cx, cy, esc=1.0, rot=0.0, alfa=1.0):
    if esc <= 0.01 or alfa <= 0.01:
        return
    l = lay if esc == 1 else lay.resize((max(1, int(lay.width * esc)), max(1, int(lay.height * esc))), Image.BICUBIC)
    if rot:
        l = l.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alfa < 1:
        l = l.copy(); l.putalpha(l.getchannel("A").point(lambda v: int(v * alfa)))
    base.alpha_composite(l, (int(cx - l.width / 2), int(cy - l.height / 2)))

# ---------- fundo (mesa azul) ----------
FUNDO = textura_papel(W + 200, H + 200, AZUL1, sem=1)
vin = Image.new("L", FUNDO.size, 0)
ImageDraw.Draw(vin).ellipse((-300, -300, FUNDO.width + 300, FUNDO.height + 300), fill=255)
vin = vin.filter(ImageFilter.GaussianBlur(220))
FUNDO = Image.composite(FUNDO, Image.new("RGB", FUNDO.size, AZUL0), vin).convert("RGBA")
FUNDO.alpha_composite(reticula(FUNDO.width, FUNDO.height, passo=12, cor=(255, 255, 255), alfa=10))

# ---------- cena 1a: lavoura de papel ----------
def planta(esc=1.0, cor=VERDES[2], sem=0, seca=0.0):
    """Pé de soja recortado: haste + trifólios. seca=1 deixa marrom e caído."""
    rnd = random.Random(sem)
    w, h = int(120 * esc), int(170 * esc)
    l = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(l)
    c = tuple(int(lerp(cor[i], (150, 118, 62)[i], seca)) for i in range(3))
    d.line((w / 2, h, w / 2, h * 0.25), fill=tuple(k - 25 for k in c), width=max(2, int(5 * esc)))
    for j, yy in enumerate((0.3, 0.5, 0.68)):
        for lado in (-1, 1):
            cx, cy = w / 2 + lado * w * 0.22, h * yy
            rx, ry = w * 0.2, h * 0.07
            d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=c)
    d.ellipse((w / 2 - w * 0.15, h * 0.12, w / 2 + w * 0.15, h * 0.26), fill=c)
    return l

def cena_lavoura():
    """Camadas: céu creme, sol mostarda, morros de papel, fileiras de soja (parte delas murcha com o tempo)."""
    S = 1.12
    w, h = int(W * S), int(H * S)
    camadas = {}
    ceu = textura_papel(w, int(h * 0.55), (226, 214, 186), sem=3)
    ceu_r = Image.new("RGBA", (w, h), (0, 0, 0, 0)); ceu_r.paste(ceu.convert("RGBA"), (0, 0))
    ceu_r.alpha_composite(reticula(w, int(h * 0.55), passo=10, cor=(150, 110, 60), alfa=35, ang_luz=(0.6, -0.2)))
    camadas["ceu"] = ceu_r
    sol = textura_papel(260, 260, MOSTARDA, sem=4).convert("RGBA")
    mk = Image.new("L", (260, 260), 0); ImageDraw.Draw(mk).ellipse((10, 10, 250, 250), fill=255)
    sol.putalpha(mk)
    camadas["sol"] = recorte(sol, sem=5)
    morros = []
    for k, (cor, y0) in enumerate([((70, 96, 62), 0.48), ((58, 84, 54), 0.56)]):
        pap = textura_papel(w, int(h * 0.6), cor, sem=6 + k).convert("RGBA")
        mk = Image.new("L", pap.size, 0)
        pts = [(0, pap.height)] + [(x, 60 + 40 * math.sin(x / (170 + 60 * k) + k) + random.Random(k).uniform(-6, 6))
                                   for x in range(0, w + 20, 20)] + [(w, pap.height)]
        ImageDraw.Draw(mk).polygon(pts, fill=255)
        pap.putalpha(mk)
        morros.append((recorte(pap, sem=8 + k, lados="t", borda_branca=True), y0))
    camadas["morros"] = morros
    return camadas, (w, h)

LAV, LAV_TAM = cena_lavoura()
_nv = textura_papel(300, 140, (236, 230, 214), sem=12).convert("RGBA")
_mk = Image.new("L", (300, 140), 0)
for _cx, _cy, _r in ((80, 85, 45), (150, 65, 60), (220, 85, 45)):
    ImageDraw.Draw(_mk).ellipse((_cx - _r, _cy - _r, _cx + _r, _cy + _r), fill=255)
_nv.putalpha(_mk)
NUVEM = recorte(_nv, sem=13)
PLANTAS = []  # (x, y, esc, lado_direito)
for fileira in range(4):
    y = 0.70 + fileira * 0.085
    esc = 0.75 + fileira * 0.35
    passo = 92 + fileira * 40
    for x in range(-40, LAV_TAM[0] + 40, passo):
        PLANTAS.append((x + (fileira % 2) * passo / 2, y, esc, x > LAV_TAM[0] * 0.48, random.random()))

def desenha_lavoura(t, base, t0, t1):
    p = (t - t0) / (t1 - t0)
    w, h = LAV_TAM
    tela = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    tela.alpha_composite(LAV["ceu"])
    colar(tela, LAV["sol"], w * 0.72, h * 0.22 + 6 * math.sin(t * 2), 1.0, rot=t * 6)
    for k, (m, y0) in enumerate(LAV["morros"]):
        tela.alpha_composite(m, (-26 + int(8 * math.sin(t * 1.3 + k)), int(h * y0) - 26))
    # chão de terra
    ImageDraw.Draw(tela).rectangle((0, int(h * 0.68), w, h), fill=(92, 66, 40, 255))
    tela.alpha_composite(reticula(w, h - int(h * 0.68), passo=8, cor=(40, 26, 14), alfa=60), (0, int(h * 0.68)))
    t_seca = t_de("prorrogar") - 0.3   # a metade direita murcha enquanto a pergunta avança
    for (x, yy, esc, direita, r) in PLANTAS:
        seca = ease((t - t_seca - r * 0.6) / 0.5) if direita else 0.0
        pl = planta(esc, VERDES[int(r * 4) % 4], sem=int(r * 1000), seca=seca)
        rot = -70 * seca * (1 if r > 0.5 else -1)
        balanço = 3 * math.sin(t * 3 + x / 50) * (1 - seca)
        colar(tela, pl, x, h * yy - pl.height / 2 + 30 * seca, 1.0, rot=rot + balanço)
    # a nuvem seca que atravessa a tela (o único "voador" do vídeo)
    colar(tela, NUVEM, lerp(-200, w + 200, clamp((t - t0) / 2.6)), h * 0.3, 1.0)
    z = lerp(1.0, 1.07, ease(p))  # câmera: aproxima
    cw, ch = W / z, H / z
    x0, y0 = (w - cw) / 2, (h - ch) * 0.55
    base.alpha_composite(tela.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.BICUBIC))

# ---------- cena 1b: agência recortada de jornal ----------
def jornal(w, h, sem=0):
    """Papel-jornal com colunas de texto ilegível (traços), sem palavras inventadas."""
    rnd = random.Random(sem)
    p = textura_papel(w, h, (228, 222, 206), sem=sem)
    d = ImageDraw.Draw(p)
    col = max(1, w // 150)
    cw = (w - 20) / col
    for c in range(col):
        x0 = 10 + c * cw + 6
        y = 12
        while y < h - 10:
            ln = rnd.uniform(0.55, 1.0) * (cw - 16)
            d.rectangle((x0, y, x0 + ln, y + 3), fill=(120, 116, 108))
            y += 9
    return p

def predio():
    w, h = 760, 640
    corpo = jornal(w, h, sem=21)
    l = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    l.paste(corpo.convert("RGBA"), (0, 0))
    l.alpha_composite(reticula(w, h, passo=9, cor=(20, 20, 30), alfa=70, ang_luz=(0.8, 0.3)))
    d = ImageDraw.Draw(l)
    for i in range(5):  # colunas
        x = 60 + i * 150
        d.rectangle((x, 200, x + 46, h - 30), fill=(246, 241, 228, 255), outline=(60, 56, 50, 255), width=3)
    d.polygon([(0, 190), (w / 2, 40), (w, 190)], fill=(210, 202, 184, 255), outline=(60, 56, 50, 255))
    placa = Image.new("RGBA", (360, 70), CARVAO + (255,))
    ImageDraw.Draw(placa).text((180, 36), "AGÊNCIA", font=fonte("black", 46), fill=CREME, anchor="mm")
    l.alpha_composite(placa, (w // 2 - 180, 112))
    return recorte(l.convert("RGB"), sem=22)

PREDIO = predio()

def porta(w=150, h=230):
    p = textura_papel(w, h, (120, 40, 36), sem=31)
    d = ImageDraw.Draw(p)
    d.rectangle((14, 14, w - 14, h - 14), outline=(70, 20, 18), width=4)
    d.ellipse((w - 34, h / 2 - 8, w - 18, h / 2 + 8), fill=MOSTARDA)
    return recorte(p, sem=32)

PORTA = porta()

def letra_recortada(ch, tam, fundo, tinta, sem):
    """Letra de manchete em retalho de papel (bilhete de colagem), tamanho e giro levemente diferentes."""
    rnd = random.Random(sem)
    f = fonte("black", int(tam * rnd.uniform(0.92, 1.08)))
    bb = f.getbbox(ch)
    w, h = bb[2] - bb[0] + 30, int(tam * 1.25)
    p = textura_papel(w, h, fundo, sem=sem)
    ImageDraw.Draw(p).text((w / 2, h / 2), ch, font=f, fill=tinta, anchor="mm")
    return recorte(p, sem=sem, sombra=True).rotate(rnd.uniform(-6, 6), expand=True, resample=Image.BICUBIC)

def palavra_recortada(txt, tam, sem, destaque=False):
    letras = []
    for i, ch in enumerate(txt):
        if ch == " ":
            letras.append(None); continue
        fundo = MOSTARDA if destaque and i % 2 == 0 else (CREME if not destaque or i % 3 else (232, 220, 190))
        letras.append(letra_recortada(ch, tam, fundo, CARVAO, sem + i))
    larg = sum((l.width - 34 if l else tam // 3) for l in letras)
    alt = max(l.height for l in letras if l)
    out = Image.new("RGBA", (larg + 40, alt), (0, 0, 0, 0))
    x = 0
    for l in letras:
        if l is None:
            x += tam // 3; continue
        out.alpha_composite(l, (x, (alt - l.height) // 2))
        x += l.width - 34
    return out

TIT_DECISAO = palavra_recortada("DECISÃO", 92, 100, destaque=False)
TIT_BANCO = palavra_recortada("DO BANCO?", 92, 200, destaque=True)

def desenha_agencia(t, base, t0, t1):
    p = (t - t0) / (t1 - t0)
    camada = Image.new("RGBA", (W + 160, H), (0, 0, 0, 0))
    colar(camada, PREDIO, (W + 160) / 2, 640)
    t_bate = t_de("decisão") - 0.05
    s = expo((t - t_bate) / 0.18)  # a porta de papel bate (slap)
    pw = int(lerp(18, PORTA.width, s))
    pt = PORTA.resize((max(1, pw), PORTA.height))
    colar(camada, pt, (W + 160) / 2, 800)
    x = int(lerp(0, 160, ease(p)))  # câmera: desliza para o lado
    base.alpha_composite(camada.crop((x, 0, x + W, H)))
    # tremor no impacto da porta
    return math.sin(t * 80) * 10 * (1 - clamp((t - t_bate) / 0.3)) if t >= t_bate else 0

def desenha_titulo(t, base):
    td, tb = t_de("decisão") - 0.06, t_de("do") - 0.04
    s1, s2 = clamp((t - td) / 0.22), clamp((t - tb) / 0.22)
    if s1 > 0:
        colar(base, TIT_DECISAO, W / 2, 170, esc=lerp(1.5, 1.0, expo(s1)), rot=-2, alfa=s1)
    if s2 > 0:
        colar(base, TIT_BANCO, W / 2, 300, esc=lerp(1.5, 1.0, expo(s2)), rot=2, alfa=s2)

# ---------- cena 2: print da resolução como recorte ----------
TR = json.load(open(AQUI / "prints/trechos.json"))
PRINT = Image.open(AQUI / "prints/bcb-res-5314.png").convert("RGB")
CROP = (40, 300, 1780, 1560)   # do título da norma até o fim do parágrafo do item 4
REALCE = TR["bcb-res-5314"]["trechos"]["por sua conveniência e decisão"]
PEDACO = PRINT.crop(CROP)

def print_realcado(frac):
    """Passa o marcador amarelo (multiplicação: a tinta continua visível) até a fração frac do trecho."""
    pe = PEDACO.copy()
    m = Image.new("RGB", pe.size, (255, 255, 255))
    dm = ImageDraw.Draw(m)
    total = sum(r[2] - r[0] for r in REALCE)
    falta = frac * total
    for (x0, y0, x1, y1) in REALCE:
        x0, x1, y0, y1 = x0 - CROP[0] - 6, x1 - CROP[0] + 6, y0 - CROP[1] - 2, y1 - CROP[1] + 2
        seg = min(falta, x1 - x0)
        if seg > 0:
            dm.rectangle((x0, y0, x0 + seg, y1), fill=(255, 222, 60))
        falta -= x1 - x0
    return ImageChops.multiply(pe, m)

REC_CACHE = {}
def recorte_print(frac):
    k = round(frac, 2)
    if k not in REC_CACHE:
        REC_CACHE.clear()
        pe = print_realcado(k)
        REC_CACHE[k] = recorte(pe, sem=41)
    return REC_CACHE[k]

def selo(txt):
    f = fonte("black", 40)
    w = int(f.getlength(txt)) + 70
    l = Image.new("RGBA", (w, 96), (0, 0, 0, 0))
    d = ImageDraw.Draw(l)
    d.rounded_rectangle((6, 6, w - 6, 90), 10, outline=VERMELHO + (235,), width=6)
    d.text((w / 2, 48), txt, font=f, fill=VERMELHO + (235,), anchor="mm")
    falhas = Image.effect_noise((w, 96), 60).point(lambda v: 0 if v < 70 else 255)  # tinta de carimbo falhada
    l.putalpha(ImageChops.multiply(l.getchannel("A"), falhas))
    return l.rotate(-6, expand=True, resample=Image.BICUBIC)

SELO = selo("BRASÍLIA · 25/6/2026")
FITA1, FITA2 = fita(190, 54, 32, 1), fita(190, 54, -28, 2)

def desenha_print(t, base, t0, t1):
    s = expo((t - t0) / 0.45)  # entra voando (fly_in) e assenta
    t_ini, t_fim = t_de("por", t0), t_de("decisão", t0) + 0.4
    frac = clamp((t - t_ini) / (t_fim - t_ini))
    rec = recorte_print(frac)
    # câmera: do enquadramento geral até o trecho realçado
    t_foco = t_de("banco", t0) - 0.2
    foco = ease((t - t_foco) / 1.3)
    esc_base = (W * 0.86) / rec.width
    esc = esc_base * lerp(1.0, 1.75, foco)
    yc_trecho = (REALCE[0][1] + REALCE[0][3]) / 2 - CROP[1] + 26
    dy = (yc_trecho - rec.height / 2) * esc * foco
    dx = ((REALCE[0][0] + REALCE[0][2]) / 2 - CROP[0] + 26 - rec.width / 2) * esc * foco
    cx = lerp(W + 500, W / 2, s) - dx
    cy = lerp(H / 2 + 200, H / 2, s) - dy
    rot = lerp(-18, -2, s)
    colar(base, rec, cx, cy, esc=esc, rot=rot)
    if s > 0.9:  # fitas presas nos cantos de cima
        colar(base, FITA1, cx - rec.width * esc * 0.42, cy - rec.height * esc * 0.47, esc=lerp(1, 1.3, foco), rot=0)
        colar(base, FITA2, cx + rec.width * esc * 0.42, cy - rec.height * esc * 0.45, esc=lerp(1, 1.3, foco), rot=0)
    ts = t_de("manual", t0)  # carimbo de lugar e data, preso no canto do papel (vai junto no zoom)
    s2 = clamp((t - ts) / 0.16)
    if s2 > 0:
        sx = cx + rec.width * esc * 0.30
        sy = cy - rec.height * esc * 0.40
        colar(base, SELO, sx, sy, esc=lerp(1.6, 1.0, expo(s2)) * esc / esc_base, alfa=s2)

# ---------- legenda (estilo da referência 1) ----------
def blocos_legenda():
    out, cur = [], []
    for (w, s, e) in PAL:
        cur.append((w, s, e))
        if len(cur) == 3 or w[-1] in ",.?:":
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    return out
BLOCOS = blocos_legenda()
FLEG = fonte("black", 54)

def desenha_legenda(t, base):
    for i, b in enumerate(BLOCOS):
        ini = b[0][1]
        fim = BLOCOS[i + 1][0][1] if i + 1 < len(BLOCOS) else b[-1][2] + 0.3
        if ini <= t < fim:
            txt = " ".join(w.strip('"') for w, _, _ in b)
            tw = FLEG.getlength(txt)
            x0, y0 = W / 2 - tw / 2 - 22, 820
            l = Image.new("RGBA", (int(tw + 44), 84), (0, 0, 0, 0))
            d = ImageDraw.Draw(l)
            d.rounded_rectangle((0, 0, l.width - 1, 83), 10, fill=MOSTARDA + (255,))
            d.text((22, 42), txt, font=FLEG, fill=CARVAO, anchor="lm")
            esc = lerp(0.9, 1.0, expo((t - ini) / 0.12))
            colar(base, l, W / 2, y0 + 42, esc=esc)
            return

# ---------- composição ----------
CORTE_1B = t_de("prorrogar") + 0.55   # lavoura -> agência
CORTE_2 = INI[2] - 0.05                # agência -> print da norma
GRAOS = [Image.effect_noise((W // 2, H // 2), 26).resize((W, H)).convert("RGB") for _ in range(5)]
FONTE_TXT = "Fonte: Resolução CMN 5.314/2026 · bcb.gov.br · print de 10/11/2026"

def quadro(i):
    t = i / FPS
    base = FUNDO.crop((100, 100, 100 + W, 100 + H)).copy()
    tremor = 0
    if t < CORTE_1B:
        desenha_lavoura(t, base, 0, CORTE_1B)
    elif t < CORTE_2:
        tremor = desenha_agencia(t, base, CORTE_1B, CORTE_2)
    else:
        desenha_print(t, base, CORTE_2, LT["falas"][1]["fim"] + 0.4)
        ImageDraw.Draw(base).text((W / 2, 1050), FONTE_TXT, font=fonte("med", 24), fill=CREME + (220,), anchor="mm")
    if t < CORTE_2 + 0.1:
        desenha_titulo(t, base)
    desenha_legenda(t, base)
    # transição de chicote (whip) nos cortes: borrão de movimento curto
    for tc in (CORTE_1B, CORTE_2):
        dt = t - tc
        if -0.07 < dt < 0.1:
            base = base.filter(ImageFilter.BoxBlur(10))
    if tremor:
        base = base.transform(base.size, Image.AFFINE, (1, 0, tremor, 0, 1, tremor * 0.6))
    rgb = base.convert("RGB")
    rgb = Image.blend(rgb, GRAOS[i % 5], 0.05)  # granulação de filme
    return rgb

if __name__ == "__main__":
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    t0, t1 = float(sys.argv[2]), float(sys.argv[3])
    idx = [int(x) for x in sys.argv[4:]] or range(int(t0 * FPS), int(t1 * FPS))
    for i in idx:
        quadro(i).save(out / f"q{i:04d}.jpg", quality=92)
    print("ok", len(list(idx)), "quadros · cortes em", round(CORTE_1B, 2), round(CORTE_2, 2))
