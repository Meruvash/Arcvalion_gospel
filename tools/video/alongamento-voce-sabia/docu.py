"""Vídeo do alongamento de dívida rural em linguagem de web documentário (quadrado 1080x1080, 30 fps).

Nenhuma imagem de IA: fotos reais com licença livre (fotos/creditos.json, crédito na tela), prints das páginas
oficiais (prints/) e grafismos desenhados em código. Movimento e tipografia sóbrios: Ken Burns lento, documento sobre
mesa escura com profundidade de campo, rótulos de arquivo em monoespaçada, linha do tempo, cartela final.
Uso: python3 docu.py <pasta_quadros> [t_ini t_fim]
"""
import difflib
import json
import math
import re
import sys
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

W = H = 1080
FPS = 30
AQUI = Path(__file__).resolve().parent

# ---------- tipografia e cor ----------
SERIF = str(AQUI / "fontes/SourceSerif4-var.ttf")
def serif(tam, peso="Bold"):
    f = ImageFont.truetype(SERIF, tam)
    f.set_variation_by_name(peso)
    return f
INTER = "/usr/share/fonts/opentype/inter/"
def sans(tam, peso="Bold"): return ImageFont.truetype(INTER + f"Inter-{peso}.otf", tam)
MONO = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf"
def mono(tam): return ImageFont.truetype(MONO, tam)

NOITE, NOITE2 = (7, 12, 22), (14, 24, 40)
CREME, CARVAO, MOSTARDA, VERMELHO = (238, 232, 218), (20, 20, 22), (240, 194, 75), (190, 40, 46)

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def lerp(a, b, t): return a + (b - a) * t
def suave(x): x = clamp(x); return x * x * (3 - 2 * x)
def expo(x): x = clamp(x); return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)

# ---------- tempo: falas, palavras do roteiro com tempos da transcrição ----------
LT = json.load(open(AQUI / "linha_do_tempo.json"))
INI = {f["fala"]: f["inicio"] for f in LT["falas"]}
FIM = {f["fala"]: f["fim"] for f in LT["falas"]}
TOTAL = LT["total"]
FALAS = {f["id"]: f for f in json.load(open(AQUI / "falas.json", encoding="utf-8"))}

def norm(w): return re.sub(r"[^\wà-ü]", "", w.lower())

def palavras(fala):
    """Palavras do ROTEIRO (o que vai na legenda) com os tempos da transcrição da voz."""
    stt = [w for w in json.load(open(AQUI / f"voz_v3/stt/proc{fala}.json"))["words"] if w["type"] == "word"]
    rot = FALAS[fala]["texto"].replace('"', "").split()
    a, b = [norm(w) for w in rot], [norm(w["text"]) for w in stt]
    tempos = [None] * len(rot)
    for blk in difflib.SequenceMatcher(None, a, b).get_matching_blocks():
        for k in range(blk.size):
            tempos[blk.a + k] = (stt[blk.b + k]["start"], stt[blk.b + k]["end"])
    # palavras sem par (ex.: "Peraí" x "Pera aí", "Pelicioni" x "Pellicioni"): interpola entre vizinhas
    for i, tp in enumerate(tempos):
        if tp is None:
            ant = next((tempos[j][1] for j in range(i - 1, -1, -1) if tempos[j]), 0.0)
            prox = next((tempos[j][0] for j in range(i + 1, len(tempos)) if tempos[j]), stt[-1]["end"])
            tempos[i] = (ant, max(ant + 0.05, prox))
    return [(w, s + INI[fala], e + INI[fala]) for w, (s, e) in zip(rot, tempos)]

PAL = {f: palavras(f) for f in range(1, 10)}
def t_de(fala, palavra, n=1):
    k = 0
    for w, s, e in PAL[fala]:
        if norm(w) == norm(palavra):
            k += 1
            if k == n:
                return s
    raise KeyError((fala, palavra))

# envelope do áudio (para a forma de onda da 2ª voz)
def envelope(arq):
    with wave.open(str(arq)) as wv:
        sr = wv.getframerate(); n = wv.getnframes(); ch = wv.getnchannels()
        a = np.frombuffer(wv.readframes(n), dtype=np.int16).astype(np.float32)
    if ch > 1:
        a = a.reshape(-1, ch).mean(axis=1)
    passo = sr // FPS
    env = np.array([np.sqrt(np.mean(a[i:i + passo] ** 2)) for i in range(0, len(a) - passo, passo)])
    return env / (env.max() or 1)
ENV = envelope(AQUI / "voz_v3/narracao_completa.wav")

# ---------- imagens ----------
CRED = json.load(open(AQUI / "fotos/creditos.json", encoding="utf-8"))
def tratar(foto, sat=0.55, contraste=1.12):
    """Correção de cor única do filme: dessatura, sombras puxadas para o azul, altas luzes quentes."""
    im = ImageEnhance.Color(foto.convert("RGB")).enhance(sat)
    im = ImageEnhance.Contrast(im).enhance(contraste)
    a = np.asarray(im).astype(np.float32) / 255
    lum = a.mean(axis=2, keepdims=True)
    sombra = np.array([0.02, 0.05, 0.12]); luz = np.array([0.06, 0.03, -0.02])
    a = a + (1 - lum) * sombra * 0.9 + lum * luz * 0.7
    a = np.clip(a * 0.94 + 0.015, 0, 1)
    return Image.fromarray((a * 255).astype(np.uint8))

FOTOS = {}
def foto(chave):
    if chave not in FOTOS:
        c = CRED[chave]
        FOTOS[chave] = tratar(Image.open(AQUI / "fotos" / c["arquivo"]), sat=c.get("sat", 0.55))
    return FOTOS[chave]

def ken_burns(img, p, z0=1.0, z1=1.08, c0=(0.5, 0.5), c1=(0.5, 0.5)):
    """Movimento lento de câmera sobre a foto: zoom e deslocamento suaves, sempre preenchendo o quadrado."""
    iw, ih = img.size
    lado = min(iw, ih)
    z = lerp(z0, z1, suave(p))
    tam = lado / z
    cx = lerp(c0[0], c1[0], suave(p)) * iw
    cy = lerp(c0[1], c1[1], suave(p)) * ih
    x0 = clamp(cx - tam / 2, 0, iw - tam); y0 = clamp(cy - tam / 2, 0, ih - tam)
    return img.crop((int(x0), int(y0), int(x0 + tam), int(y0 + tam))).resize((W, H), Image.BICUBIC)

VIN = Image.new("L", (W, H), 0)
ImageDraw.Draw(VIN).ellipse((-260, -260, W + 260, H + 260), fill=255)
VIN = VIN.filter(ImageFilter.GaussianBlur(200))
def vinheta(img, forca=0.55):
    escuro = Image.new("RGB", (W, H), NOITE)
    return Image.composite(img, Image.blend(img, escuro, forca), VIN)

GRAOS = [Image.effect_noise((W // 2, H // 2), 30).resize((W, H)).convert("RGB") for _ in range(6)]

# ---------- peças de texto ----------
def rotulo(base, txt, x=60, y=64, cor=CREME, barra=MOSTARDA, alfa=1.0, tam=24):
    """Rótulo de arquivo: monoespaçada em caixa-alta espaçada, com filete no acento."""
    if alfa <= 0:
        return
    f = mono(tam)
    txt = txt.upper()
    esp = 2
    larg = sum(f.getlength(c) + esp for c in txt)
    l = Image.new("RGBA", (int(larg) + 40, tam + 22), (0, 0, 0, 0))
    d = ImageDraw.Draw(l)
    d.rectangle((0, 3, 5, tam + 15), fill=barra + (255,))
    xx = 20
    for c in txt:
        d.text((xx, 6), c, font=f, fill=cor + (255,)); xx += f.getlength(c) + esp
    if alfa < 1:
        l.putalpha(l.getchannel("A").point(lambda v: int(v * alfa)))
    sombra = l.getchannel("A").filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * 0.6))
    base.paste((0, 0, 0), (x + 2, y + 2), sombra)
    base.paste(l, (x, y), l)

def credito(base, txt):
    f = sans(17, "Medium")
    d = ImageDraw.Draw(base)
    d.text((W - 40, H - 30), txt, font=f, fill=(210, 210, 205), anchor="rm")

FLEG = sans(46, "Black")
def legenda(base, t):
    """Legenda da referência 1: 1 a 3 palavras, preto sobre caixa amarela, um pouco abaixo do centro."""
    for fala, pals in PAL.items():
        blocos, cur = [], []
        for w in pals:
            cur.append(w)
            if len(cur) == 3 or w[0][-1] in ",.?:":
                blocos.append(cur); cur = []
        if cur:
            blocos.append(cur)
        for i, b in enumerate(blocos):
            ini = b[0][1]
            fim = blocos[i + 1][0][1] if i + 1 < len(blocos) else b[-1][2] + 0.25
            if ini <= t < fim:
                txt = " ".join(w for w, _, _ in b)
                tw = FLEG.getlength(txt)
                l = Image.new("RGBA", (int(tw + 40), 70), (0, 0, 0, 0))
                d = ImageDraw.Draw(l)
                d.rounded_rectangle((0, 0, l.width - 1, 69), 8, fill=MOSTARDA + (255,))
                d.text((20, 35), txt, font=FLEG, fill=CARVAO, anchor="lm")
                esc = lerp(0.92, 1.0, expo((t - ini) / 0.1))
                if esc != 1:
                    l = l.resize((int(l.width * esc), int(l.height * esc)), Image.BICUBIC)
                base.paste(l, (int(W / 2 - l.width / 2), int(860 - l.height / 2)), l)
                return

# ---------- documentos ----------
TR = json.load(open(AQUI / "prints/trechos.json"))
PRINTS = {k: Image.open(AQUI / f"prints/{k}.png").convert("RGB") for k in ("bcb-res-5314", "stj-sumula-298")}
MESA = None
def mesa():
    global MESA
    if MESA is None:
        m = Image.new("RGB", (W, H), NOITE2)
        ruido = Image.effect_noise((W // 3, H // 3), 22).resize((W, H)).convert("RGB")
        m = ImageChops.multiply(m, ruido.point(lambda v: 205 + v // 6))
        luz = Image.new("L", (W, H), 0)
        ImageDraw.Draw(luz).ellipse((80, 40, W - 80, H - 120), fill=255)  # uma luz só, de luminária, vinda de cima
        luz = luz.filter(ImageFilter.GaussianBlur(160))
        MESA = Image.composite(Image.blend(m, Image.new("RGB", (W, H), (60, 66, 76)), 0.35), m, luz)
    return MESA.copy()

def realce(img, rects, frac, ox=0, oy=0):
    """Marcador amarelo por multiplicação (a tinta continua visível), até a fração frac do trecho."""
    m = Image.new("RGB", img.size, (255, 255, 255))
    dm = ImageDraw.Draw(m)
    total = sum(r[2] - r[0] for r in rects)
    falta = frac * total
    for (x0, y0, x1, y1) in rects:
        x0, x1, y0, y1 = x0 - ox - 6, x1 - ox + 6, y0 - oy - 3, y1 - oy + 3
        seg = min(falta, x1 - x0)
        if seg > 0:
            dm.rectangle((x0, y0, x0 + seg, y1), fill=(255, 220, 70))
        falta -= x1 - x0
    return ImageChops.multiply(img, m)

def documento(t, chave, recorte, alvo, realces, z0, z1, p, rot=-1.2, foco_borda=True, entrada=0.0):
    """Folha impressa sobre a mesa escura: sombra de papel, leve giro, câmera aproximando até o alvo,
    profundidade de campo (o que está longe do alvo fica desfocado)."""
    pr = PRINTS[chave]
    x0, y0, x1, y1 = recorte
    folha = pr.crop(recorte)
    for rects, frac in realces:
        folha = realce(folha, rects, frac, x0, y0)
    folha = ImageEnhance.Brightness(folha).enhance(0.93)
    z = lerp(z0, z1, suave(p))
    esc = (W * 0.92 / folha.width) * z
    fw, fh = int(folha.width * esc), int(folha.height * esc)
    fl = folha.resize((fw, fh), Image.BICUBIC).convert("RGBA")
    ax = ((alvo[0] - x0) * esc); ay = ((alvo[1] - y0) * esc)
    # o alvo vai do centro da folha para o centro da tela à medida que a câmera aproxima
    cx = lerp(fw / 2, ax, suave(p)); cy = lerp(fh / 2, ay, suave(p))
    base = mesa()
    sombra = Image.new("L", (fw + 80, fh + 80), 0)
    ImageDraw.Draw(sombra).rectangle((40, 40, fw + 40, fh + 40), fill=200)
    sombra = sombra.filter(ImageFilter.GaussianBlur(24))
    camada = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = int(W / 2 - cx + entrada * 600); py = int(H / 2 - cy)
    camada.paste((0, 0, 0, 255), (px - 40 + 14, py - 40 + 22), sombra)
    camada.paste(fl, (px, py), fl)
    camada = camada.rotate(rot * (1 - 0.4 * suave(p)), center=(W / 2, H / 2), resample=Image.BICUBIC)
    base.paste(camada, (0, 0), camada)
    if foco_borda:
        desf = base.filter(ImageFilter.GaussianBlur(5 + 5 * suave(p)))
        mk = Image.new("L", (W, H), 0)
        ImageDraw.Draw(mk).ellipse((W * 0.05, H * 0.28, W * 0.95, H * 0.72), fill=255)
        mk = mk.filter(ImageFilter.GaussianBlur(110))
        base = Image.composite(base, desf, mk)
    return base

def carimbo(txt, cor=VERMELHO):
    f = sans(34, "Black")
    w = int(f.getlength(txt)) + 60
    l = Image.new("RGBA", (w, 84), (0, 0, 0, 0))
    d = ImageDraw.Draw(l)
    d.rounded_rectangle((5, 5, w - 5, 79), 8, outline=cor + (230,), width=5)
    d.text((w / 2, 42), txt, font=f, fill=cor + (230,), anchor="mm")
    falhas = Image.effect_noise((w, 84), 70).point(lambda v: 0 if v < 80 else 255)
    l.putalpha(ImageChops.multiply(l.getchannel("A"), falhas))
    return l.rotate(-5, expand=True, resample=Image.BICUBIC)

def colar(base, l, cx, cy, esc=1.0, alfa=1.0):
    if alfa <= 0 or esc <= 0:
        return
    if esc != 1:
        l = l.resize((max(1, int(l.width * esc)), max(1, int(l.height * esc))), Image.BICUBIC)
    if alfa < 1:
        l = l.copy(); l.putalpha(l.getchannel("A").point(lambda v: int(v * alfa)))
    base.paste(l, (int(cx - l.width / 2), int(cy - l.height / 2)), l)

CARIMBO_DATA = carimbo("BRASÍLIA · 25/6/2026")
CARIMBO_VIGOR = carimbo("EM VIGOR · 1º/7/2026")

# ---------- cenas ----------
BCB = TR["bcb-res-5314"]["trechos"]; STJ = TR["stj-sumula-298"]["trechos"]
def centro(r): return ((r[0][0] + r[-1][2]) / 2, (r[0][1] + r[-1][3]) / 2)

def frac_fala(t, fala, ini_pal, fim_pal, n_fim=1):
    a = t_de(fala, ini_pal); b = t_de(fala, fim_pal, n_fim) + 0.35
    return clamp((t - a) / (b - a))

def cena_foto(t, a, b, chave, z0=1.0, z1=1.08, c0=(0.5, 0.5), c1=(0.5, 0.5)):
    img = ken_burns(foto(chave), (t - a) / (b - a), z0, z1, c0, c1)
    img = vinheta(img, 0.5)
    credito(img, CRED[chave]["credito"])
    return img

def onda(base, t, a, titulo="A PERGUNTA"):
    """A 2ª voz: tela escura com a forma de onda do áudio, num quadro de monitor antigo (referência 2)."""
    base.paste(Image.blend(base, Image.new("RGB", (W, H), NOITE), 0.72))
    fw, fh = 620, 380
    l = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
    d = ImageDraw.Draw(l)
    d.rounded_rectangle((0, 0, fw - 1, fh - 1), 46, fill=(18, 26, 40, 240), outline=(90, 100, 116, 255), width=4)
    i = int(t * FPS)
    for k in range(48):
        v = ENV[min(len(ENV) - 1, max(0, i - 24 + k))]
        h = 8 + v * 230
        x = 70 + k * 10.5
        d.rounded_rectangle((x, fh / 2 - h / 2, x + 6, fh / 2 + h / 2), 3, fill=MOSTARDA + (255,))
    s = expo((t - a) / 0.25)
    colar(base, l, W / 2, H / 2 - 60, esc=lerp(0.9, 1.0, s), alfa=s)
    rotulo(base, titulo, x=int(W / 2 - 150), y=int(H / 2 - 60 - fh / 2 - 60), alfa=s)

def linha_do_tempo(base, t, a):
    """2004 → 2021 → 2026: o que cada norma diz (lista F, textos literais curtos)."""
    base.paste(mesa())
    d = ImageDraw.Draw(base)
    y = 470
    p = expo((t - a) / 0.5)
    d.line((90, y, 90 + (W - 180) * p, y), fill=(150, 156, 166), width=3)
    marcos = [
        (0.0, "2004", "STJ · SÚMULA 298", "“direito do devedor”"),
        (0.5, "2021", "CMN · RES. 4.905", "banco “autorizado a prorrogar”"),
        (1.0, "2026", "CMN · RES. 5.314", "“por sua conveniência e decisão”"),
    ]
    for k, (pos, ano, quem, diz) in enumerate(marcos):
        s = expo((t - a - 0.25 - k * 0.45) / 0.3)
        if s <= 0:
            continue
        x = 90 + (W - 180) * pos
        cor = MOSTARDA if k != 1 else (200, 204, 210)
        d.ellipse((x - 12, y - 12, x + 12, y + 12), fill=cor)
        anc = "lm" if k == 0 else ("rm" if k == 2 else "mm")
        al = int(255 * s)
        d.text((x, y - 70), ano, font=serif(64, "Bold"), fill=CREME + (al,), anchor={"lm": "ls", "rm": "rs", "mm": "ms"}[anc])
        d.text((x, y + 50), quem, font=mono(22), fill=(190, 196, 206), anchor={"lm": "lt", "rm": "rt", "mm": "mt"}[anc])
        d.text((x, y + 86), diz, font=serif(26, "Medium"), fill=CREME, anchor={"lm": "lt", "rm": "rt", "mm": "mt"}[anc])
    rotulo(base, "LINHA DO TEMPO · MCR 2-6-4 E SÚMULA 298", alfa=p)

def lado_a_lado(base, t, a):
    """Os dois documentos frente a frente, com os dois realces acesos."""
    base.paste(mesa())
    p = expo((t - a) / 0.4)
    for k, (chave, rects, rotu) in enumerate([("bcb-res-5314", BCB["por sua conveniência e decisão"], "MCR 2-6-4 · 2026"),
                                              ("stj-sumula-298", STJ["direito do devedor"], "SÚMULA 298 · 2004")]):
        cx, cy = centro(rects)
        pr = PRINTS[chave]
        rec = (int(cx - 330), int(cy - 150), int(cx + 330), int(cy + 150))
        fl = realce(pr.crop(rec), rects, 1.0, rec[0], rec[1])
        fl = fl.resize((470, 214), Image.BICUBIC).convert("RGBA")
        x = W / 2 + (-250 if k == 0 else 250) + (1 - p) * (-400 if k == 0 else 400)
        y = 420 + k * 70
        sombra = Image.new("RGBA", (fl.width + 60, fl.height + 60), (0, 0, 0, 0))
        ImageDraw.Draw(sombra).rectangle((30, 30, fl.width + 30, fl.height + 30), fill=(0, 0, 0, 180))
        sombra = sombra.filter(ImageFilter.GaussianBlur(16))
        colar(base, sombra, x + 10, y + 16)
        colar(base, fl.rotate(-2 if k == 0 else 2, expand=True, resample=Image.BICUBIC), x, y)
        rotulo(base, rotu, x=int(x - 230), y=int(y - 170), alfa=p, tam=20)

def cartela(base, t, a):
    base.paste(Image.new("RGB", (W, H), NOITE))
    d = ImageDraw.Draw(base)
    s1 = expo((t - a) / 0.5)
    s2 = expo((t - t_de(9, "Aqui")) / 0.5)
    s3 = expo((t - t_de(9, "Me")) / 0.5)
    d.text((W / 2, 380 - 20 * (1 - s1)), "Dr. Pelicioni", font=serif(96, "Bold"), fill=CREME + (int(255 * s1),), anchor="mm")
    d.line((W / 2 - 160 * s1, 450, W / 2 + 160 * s1, 450), fill=MOSTARDA, width=3)
    rotulo(base, "ADVOGADO", x=int(W / 2 - 95), y=476, alfa=s1, barra=MOSTARDA)
    d.text((W / 2, 600), "o que muda no crédito rural, explicado com a fonte", font=serif(32, "Medium"),
           fill=(200, 200, 196, int(255 * s2)), anchor="mm")
    d.text((W / 2, 690), "Dúvida sobre o seu contrato? Direct aberto.", font=sans(30, "Bold"),
           fill=MOSTARDA + (int(255 * s3),), anchor="mm")
    d.text((W / 2, H - 46), "Fontes: Res. CMN 5.314/2026 e 4.905/2021 (bcb.gov.br) · Súmula 298 (scon.stj.jus.br)",
           font=sans(17, "Medium"), fill=(150, 156, 166), anchor="mm")

def titulo_abertura(base, t):
    """Manchete da abertura: serifa branca, a palavra-chave no acento."""
    td = t_de(1, "decisão") - 0.05
    tb = t_de(1, "banco?") - 0.05
    s1, s2 = expo((t - td) / 0.35), expo((t - tb) / 0.35)
    if s1 <= 0:
        return
    l = Image.new("RGBA", (W, 300), (0, 0, 0, 0))
    d = ImageDraw.Draw(l)
    d.text((W / 2, 110 - 18 * (1 - s1)), "Decisão do", font=serif(110, "Bold"), fill=CREME + (int(255 * s1),), anchor="mm")
    d.text((W / 2, 225 - 18 * (1 - s2)), "banco?", font=serif(120, "Black"), fill=MOSTARDA + (int(255 * s2),), anchor="mm")
    sombra = l.getchannel("A").filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.8))
    base.paste((0, 0, 0), (0, 92), sombra)
    base.paste(l, (0, 90), l)

# ---------- roteiro de planos ----------
T = {
    "c1": t_de(1, "prorrogar") + 0.3,          # lavoura seca -> Banco Central
    "c2": INI[2] - 0.05,                       # -> documento (Res. 5.314)
    "c3": INI[3] - 0.08,                       # -> 2ª voz
    "c4": INI[4] - 0.08,                       # -> vigência (Art. 11)
    "c5": INI[5] - 0.1,                        # -> as três situações
    "c5b": t_de(5, "não") - 0.1,
    "c5c": t_de(5, "teve") - 0.1,
    "c6": INI[6] - 0.1,                        # -> STJ
    "c6b": t_de(6, "porque") - 0.1,            # -> Súmula 298
    "c6c": t_de(6, "alongar") - 0.15,          # -> linha do tempo
    "c7": INI[7] - 0.08,                       # -> 2ª voz + lado a lado
    "c7b": t_de(7, "Então") - 0.1,
    "c8": INI[8] - 0.1,                        # -> contrato
    "c9": INI[9] - 0.25,                       # -> cartela
}

def quadro(i):
    t = i / FPS
    if t < T["c1"]:
        img = cena_foto(t, 0, T["c1"], "seca", 1.04, 1.12, (0.5, 0.55), (0.5, 0.5))
        rotulo(img, "Brasil · lavoura", alfa=expo(t / 0.4))
    elif t < T["c2"]:
        img = cena_foto(t, T["c1"], T["c2"], "bcb", 1.0, 1.07, (0.45, 0.5), (0.55, 0.5))
        rotulo(img, "Banco Central do Brasil · Brasília")
    elif t < T["c3"]:
        p = (t - T["c2"]) / (T["c3"] - T["c2"])
        alvo = centro(BCB["por sua conveniência e decisão"])
        frac = frac_fala(t, 2, "por", "decisão")
        ent = 1 - expo((t - T["c2"]) / 0.5)
        img = documento(t, "bcb-res-5314", (60, 600, 1760, 1700), alvo, [(BCB["por sua conveniência e decisão"], frac)],
                        1.0, 1.9, clamp((t - t_de(2, "banco") + 0.3) / 1.6), entrada=ent)
        rotulo(img, "Documento · Resolução CMN nº 5.314 · Banco Central")
        s = expo((t - t_de(2, "manual")) / 0.18)
        colar(img, CARIMBO_DATA, 790, 210, esc=lerp(1.5, 1.0, s), alfa=s * (1 - clamp((t - t_de(2, "banco")) / 0.6)))
    elif t < T["c4"]:
        img = documento(t, "bcb-res-5314", (60, 600, 1760, 1700), centro(BCB["por sua conveniência e decisão"]),
                        [(BCB["por sua conveniência e decisão"], 1.0)], 1.9, 1.9, 1.0)
        onda(img, t, T["c3"])
    elif t < T["c5"]:
        r = BCB["Esta Resolução entra em vigor em 1º de julho de 2026"]
        frac = frac_fala(t, 4, "Mas", "é")
        img = documento(t, "bcb-res-5314", (60, 5200, 1760, 6000), centro(r), [(r, frac)], 1.2, 1.6,
                        (t - T["c4"]) / (T["c5"] - T["c4"]))
        rotulo(img, "Art. 11 · vigência")
        s = expo((t - t_de(4, "não")) / 0.16)
        colar(img, CARIMBO_VIGOR, 760, 300, esc=lerp(1.5, 1.0, s), alfa=s)
    elif t < T["c6"]:
        trechos = [("c5", "c5b", "comercializa", "MCR 2-6-4 · b) frustração de safras, por fatores adversos", "seca2"),
                   ("c5b", "c5c", "armazem", "MCR 2-6-4 · a) dificuldade de comercialização dos produtos", "armazem"),
                   ("c5c", "c6", "dano", "MCR 2-6-4 · c) eventuais ocorrências prejudiciais ao desenvolvimento das explorações", "dano")]
        for a, b, _, txt, chave in trechos:
            if T[a] <= t < T[b]:
                img = cena_foto(t, T[a], T[b], chave, 1.0, 1.1)
                rotulo(img, txt, tam=21)
    elif t < T["c6b"]:
        img = cena_foto(t, T["c6"], T["c6b"], "stj", 1.0, 1.08, (0.5, 0.6), (0.5, 0.45))
        rotulo(img, "Superior Tribunal de Justiça · Brasília")
    elif t < T["c6c"]:
        r = STJ["direito do devedor"]
        frac = frac_fala(t, 6, "direito", "devedor")
        img = documento(t, "stj-sumula-298", (100, 820, 1700, 1180), centro(STJ["O alongamento de dívida originada de crédito rural"]),
                        [(r, frac)], 1.0, 1.25, (t - T["c6b"]) / (T["c6c"] - T["c6b"]), rot=1.0)
        rotulo(img, "Súmula 298 · STJ · DJ 22/11/2004")
    elif t < T["c7"]:
        img = Image.new("RGB", (W, H)); linha_do_tempo(img, t, T["c6c"])
    elif t < T["c8"]:
        img = Image.new("RGB", (W, H)); lado_a_lado(img, t, T["c7"])
        onda_mini = t < T["c7b"]
        if onda_mini:
            rotulo(img, "A pergunta", x=60, y=H - 260)
    elif t < T["c9"]:
        img = cena_foto(t, T["c8"], T["c9"], "contrato", 1.0, 1.1, (0.5, 0.5), (0.52, 0.55))
        rotulo(img, "E o contrato que já foi assinado?")
    else:
        img = Image.new("RGB", (W, H)); cartela(img, t, T["c9"])
    if T["c9"] - 0.1 > t:
        if t < T["c2"]:
            titulo_abertura(img, t)
        legenda(img, t)
    # mergulho curto no preto nas viradas de bloco (corte seco nos outros)
    for c in ("c2", "c6", "c9"):
        dt = t - T[c]
        if -0.1 < dt < 0.12:
            img = Image.blend(img, Image.new("RGB", (W, H)), 1 - abs(dt) / 0.12)
    img = Image.blend(img, GRAOS[i % 6], 0.045)  # granulação de filme
    # leve oscilação de projeção (1 px)
    img = img.transform(img.size, Image.AFFINE, (1, 0, math.sin(i * 1.7) * 0.6, 0, 1, math.cos(i * 1.3) * 0.6),
                        resample=Image.BILINEAR)
    return img

if __name__ == "__main__":
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    t0 = float(sys.argv[2]) if len(sys.argv) > 2 else 0
    t1 = float(sys.argv[3]) if len(sys.argv) > 3 else TOTAL
    idx = [int(x) for x in sys.argv[4:]] or range(int(t0 * FPS), int(t1 * FPS))
    for i in idx:
        quadro(i).save(out / f"q{i:04d}.jpg", quality=92)
    print("ok", len(list(idx)), {k: round(v, 2) for k, v in T.items()})
