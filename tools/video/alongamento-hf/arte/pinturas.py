"""Cenas pintadas em código (sem gerador de imagem) para o vídeo do alongamento de dívida rural.

Usa a skill claude-drawing (lib anime + core, numpy + Pillow): céu em degradê, luz de hora dourada, perspectiva,
partículas, bloom e vinheta. Paleta de documentário: dessaturada, quente na luz e fria na sombra.
Uso: python3 arte/pinturas.py <pasta_da_lib_claude_drawing> [cena ...]  ->  assets/img/pint-<cena>.png (1200x1200)
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, sys.argv[1])
from anime import Anime, hexc  # noqa: E402
from core import blur, noise2d, smoothstep, blob_pts, polygon_mask  # noqa: E402

S = 1200
AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(AQUI, "..", "assets", "img")
os.makedirs(OUT, exist_ok=True)


def tom(a, sat=0.78, contraste=1.06, quente=(1.03, 1.0, 0.95)):
    """grade de documentário: tira saturação, abre contraste, aquece levemente"""
    img = a.img
    lum = img.mean(2, keepdims=True)
    img = lum + (img - lum) * sat
    img = (img - 0.5) * contraste + 0.5
    img = img * np.array(quente, np.float32)
    a.img = np.clip(img, 0, 1)


def grao(a, quanto=0.025, seed=3):
    r = np.random.default_rng(seed)
    a.img = np.clip(a.img + r.normal(0, quanto, a.img.shape[:2])[..., None], 0, 1)


def fileiras(a, topo, vx, cores, n=46, luz=None):
    """lavoura em perspectiva: faixas que convergem ao ponto de fuga, alternando dois verdes"""
    H = a.H
    base = a.poly([(-200, H), (S + 200, H), (S + 200, topo), (-200, topo)])
    a.gradient(base, cores[0], cores[1], topo, H)
    for i in range(-n, n + 1):
        x_base = vx + i * (S * 2.2 / n)
        larg = S * 2.2 / n * 0.42
        pts = [(vx + i * 1.4, topo), (vx + i * 1.4 + 1.2, topo), (x_base + larg, H + 40), (x_base - larg, H + 40)]
        m = a.poly(pts) * (a.YY >= topo)
        a.fill(m, cores[2], 0.55)
    # profundidade: o longe se mistura com o ar
    nevoa = np.clip(1 - (a.YY - topo) / ((H - topo) * 0.55), 0, 1) * (a.YY >= topo)
    a.fill(nevoa, cores[3], 0.55)
    if luz is not None:  # luz rasante quente vinda do sol
        a.screen(np.clip(1 - np.abs(a.XX - luz) / (S * 0.6), 0, 1) * (a.YY >= topo) * 0.6, '#ffb76b', 0.35)


def pe_de_soja(a, x, y, esc, cor, borda, seed):
    r = np.random.default_rng(seed)
    for k in range(7):
        ang = r.uniform(-2.4, -0.7)
        cx = x + math.cos(ang) * 26 * esc * r.uniform(0.5, 1.1)
        cy = y + math.sin(ang) * 30 * esc * r.uniform(0.6, 1.2)
        pts = blob_pts(cx, cy, 16 * esc, 10 * esc, rough=0.15, n=24, seed=int(r.integers(1 << 30)), rot=ang)
        m = a.poly(pts)
        a.fill(m, cor)
        a.fill(m * (a.XX > cx + 4 * esc), borda, 0.5)  # luz de contorno
    a.lines([(x, y + 26 * esc), (x, y - 10 * esc)], max(1.5, 3 * esc), cor)


def silos(a, x0, base, alt, n=3, cor='#2a2a33', luz='#c98a55'):
    for k in range(n):
        x = x0 + k * alt * 0.42
        w = alt * 0.32
        corpo = a.poly([(x, base), (x, base - alt), (x + w, base - alt), (x + w, base)])
        a.fill(corpo, cor)
        a.fill(corpo * (a.XX > x + w * 0.62), luz, 0.35)
        cone = a.poly([(x - 2, base - alt), (x + w / 2, base - alt - w * 0.42), (x + w + 2, base - alt)])
        a.fill(cone, cor)
    # galpão
    gx = x0 + n * alt * 0.42 + 12
    a.fill(a.poly([(gx, base), (gx, base - alt * 0.42), (gx + alt * 0.5, base - alt * 0.6), (gx + alt * 1.0, base - alt * 0.42), (gx + alt * 1.0, base)]), cor)


def linha_de_arvores(a, y, cor, seed, alt=26):
    r = np.random.default_rng(seed)
    x = -40
    while x < S + 40:
        w = r.uniform(30, 90); h = r.uniform(alt * 0.6, alt * 1.4)
        a.fill(a.poly(blob_pts(x, y - h * 0.4, w * 0.6, h * 0.6, rough=0.12, n=30, seed=int(r.integers(1 << 30)))), cor)
        x += w * 0.7
    a.fill(a.poly([(-40, y - 6), (S + 40, y - 6), (S + 40, y + 4), (-40, y + 4)]), cor)


def salva(a, nome):
    tom(a); grao(a)
    a.composite().save(os.path.join(OUT, f"pint-{nome}.png"))
    print("ok", nome)


# ---------------------------------------------------------------- cenas
def lavoura():
    a = Anime(S, S, seed=11)
    hz = 560
    a.sky('#24314f', '#b8774a', '#f2c487', horizon=hz)
    a.cumulus(330, 430, 520, 170, light=(0.8, -0.3), lit='#ffd6a3', mid='#e9b88c', shadow='#7d6a78', deep='#5e5068', puffs=40, seed=4)
    a.cumulus(980, 470, 420, 120, light=(-0.9, -0.2), lit='#ffcf98', mid='#e3ae84', shadow='#7a6474', deep='#5a4b62', puffs=30, seed=9)
    a.sun_flare(860, hz - 30, strength=0.9, rays=7, flare=False)
    linha_de_arvores(a, hz + 6, '#3b3a3a', 5, alt=22)
    silos(a, 140, hz + 4, 120)
    fileiras(a, hz + 6, 860, ('#6f6a3a', '#3e4a26', '#2f3a1e', '#c9925f'), luz=860)
    r = np.random.default_rng(2)
    for _ in range(26):  # pés de soja do primeiro plano, com luz de contorno
        x = r.uniform(-20, S + 20); y = r.uniform(960, 1230)
        pe_de_soja(a, x, y, r.uniform(1.6, 2.6), '#26301a', '#d99a5a', int(r.integers(1 << 30)))
    a.sparkles(70, box=(0, 380, S, 900), size=(1.0, 2.4), colour='#ffd9a8')
    a.bloom(0.78, 22, 0.35); a.vignette(0.32)
    salva(a, "lavoura")


def colheitadeira():
    """sprite com fundo transparente: colheitadeira em contraluz, com borda iluminada"""
    w, h = 520, 300
    im = Image.new("RGBA", (w * 2, h * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    cor = (34, 30, 30, 255); luz = (230, 160, 95, 255)
    d.rectangle((160, 170, 760, 420), fill=cor)                 # corpo
    d.rectangle((520, 70, 700, 200), fill=cor)                  # cabine
    d.rectangle((540, 90, 690, 170), fill=(70, 58, 50, 255))    # vidro
    d.polygon([(20, 380), (220, 330), (220, 450), (0, 470)], fill=cor)  # plataforma de corte
    d.rectangle((300, 60, 330, 180), fill=cor); d.rectangle((300, 50, 520, 80), fill=cor)  # tubo descarregador
    for cx, r in ((300, 105), (700, 75)):
        d.ellipse((cx - r, 470 - r, cx + r, 470 + r), fill=(22, 20, 20, 255))
        d.ellipse((cx - r * 0.45, 470 - r * 0.45, cx + r * 0.45, 470 + r * 0.45), fill=(60, 52, 46, 255))
    d.line((700, 70, 700, 420), fill=luz, width=6); d.line((760, 170, 760, 420), fill=luz, width=6)  # borda iluminada
    im = im.resize((w, h), Image.LANCZOS)
    im.save(os.path.join(OUT, "sprite-colheitadeira.png")); print("ok colheitadeira")


def banco():
    a = Anime(S, S, seed=21)
    a.sky('#0f1a33', '#3a4a72', '#d08a5a', horizon=700)
    a.cumulus(900, 360, 600, 140, light=(-0.6, 0.8), lit='#e2a27a', mid='#9b7486', shadow='#3e3f5c', deep='#2c2e48', puffs=36, seed=3)
    rua = 930
    a.fill(a.poly([(-10, rua), (S + 10, rua), (S + 10, S), (-10, S)]), '#1d1f26')
    # prédio da agência: fachada com colunas e janelas acesas
    x0, x1, topo = 170, 1030, 300
    a.gradient(a.poly([(x0, rua), (x0, topo), (x1, topo), (x1, rua)]), '#4b4a52', '#2c2c33', topo, rua)
    a.fill(a.poly([(x0 - 30, topo), (x1 + 30, topo), (x1 + 30, topo + 50), (x0 - 30, topo + 50)]), '#5b5a62')
    a.fill(a.poly([(x0 - 30, topo + 50), (x1 + 30, topo + 50), (x1 + 30, topo + 62), (x0 - 30, topo + 62)]), '#26262c')
    for k in range(6):
        cx = x0 + 70 + k * 155
        a.fill(a.poly([(cx, rua - 40), (cx, topo + 80), (cx + 38, topo + 80), (cx + 38, rua - 40)]), '#6a6870')
        a.fill(a.poly([(cx + 26, rua - 40), (cx + 26, topo + 80), (cx + 38, topo + 80), (cx + 38, rua - 40)]), '#3a3940')
    for k in range(5):
        jx = x0 + 120 + k * 155
        jan = a.poly([(jx, rua - 60), (jx, topo + 140), (jx + 92, topo + 140), (jx + 92, rua - 60)])
        a.fill(jan, '#f2b46a' if k != 2 else '#1a1a1e')
        a.screen(blur(jan, 18), '#ffb062', 0.35)
    porta = a.poly([(x0 + 430, rua), (x0 + 430, rua - 260), (x0 + 530, rua - 260), (x0 + 530, rua)])
    a.fill(porta, '#0f0f12')
    a.fill(a.poly([(x0 - 40, rua), (x1 + 40, rua), (x1 + 60, rua + 24), (x0 - 60, rua + 24)]), '#3a3a40')  # degrau
    # poste de luz e reflexo na calçada molhada
    a.lines([(110, S), (110, 520)], 10, '#141418'); a.lines([(110, 520), (190, 520)], 7, '#141418')
    a.screen(np.exp(-((a.XX - 190) ** 2 + (a.YY - 532) ** 2) / (2 * 30 ** 2)), '#ffd08a', 1.0)
    a.screen(np.exp(-((a.XX - 190) ** 2 + (a.YY - 560) ** 2) / (2 * 220 ** 2)), '#ffb35e', 0.35)
    a.screen(blur((a.YY > rua + 30).astype(np.float32) * np.exp(-((a.XX - 520) ** 2) / (2 * 300 ** 2)), 6), '#f2a45c', 0.18)
    a.bloom(0.75, 20, 0.4); a.vignette(0.38)
    salva(a, "banco")


def seca():
    a = Anime(S, S, seed=31)
    hz = 520
    a.sky('#8fa3b5', '#d8d0bd', '#efe2c4', horizon=hz)
    a.sun_flare(860, 150, strength=1.1, rays=5, flare=False)
    linha_de_arvores(a, hz + 4, '#7a7766', 8, alt=14)
    a.gradient(a.poly([(-10, hz + 4), (S + 10, hz + 4), (S + 10, S), (-10, S)]), '#c8b28a', '#8c6d48', hz, S)
    # chão rachado: células de Voronoi (rachaduras escuras), mais largas perto da câmera
    r = np.random.default_rng(7)
    pts = np.stack([r.uniform(-50, S + 50, 420), hz + (S - hz) * r.uniform(0, 1, 420) ** 0.55], 1)
    ys, xs = np.mgrid[hz:S:2, 0:S:2]
    d1 = np.full(ys.shape, 1e9, np.float32); d2 = d1.copy()
    for px, py in pts:
        sy = 1 + (py - hz) / (S - hz) * 2.5
        dd = np.hypot((xs - px) / sy, (ys - py) / (sy * 0.45))
        nd2 = np.where(dd < d1, d1, np.minimum(d2, dd)); d1 = np.minimum(d1, dd); d2 = nd2
    fenda = np.clip(1 - (d2 - d1) / 2.2, 0, 1).astype(np.float32)
    fenda = np.asarray(Image.fromarray((fenda * 255).astype(np.uint8)).resize((S, S - hz), Image.BILINEAR), np.float32) / 255
    m = np.zeros((S, S), np.float32); m[hz:, :] = fenda
    a.fill(m, '#3d2a1a', 0.85)
    a.fill(blur(m, 3) * (a.YY > hz), '#f3dcb0', 0.12)
    # pés de soja secos, curvados
    for _ in range(18):
        x = r.uniform(0, S); y = r.uniform(820, 1180); e = r.uniform(1.2, 2.2)
        pe_de_soja(a, x, y, e, '#6b5233', '#c9a36b', int(r.integers(1 << 30)))
    a.screen(np.clip(1 - a.YY / hz, 0, 1) * 0.5, '#fff4dc', 0.4)  # calor no ar
    a.vignette(0.3)
    salva(a, "seca")


def caminhoes():
    a = Anime(S, S, seed=41)
    hz = 600
    a.sky('#1b2340', '#7b5a63', '#e39a5f', horizon=hz)
    a.sun_flare(1020, hz - 10, strength=0.8, rays=5, flare=False)
    linha_de_arvores(a, hz + 4, '#2a2628', 13, alt=18)
    silos(a, 840, hz + 2, 170, n=4, cor='#25232a', luz='#d98d55')
    a.gradient(a.poly([(-10, hz + 4), (S + 10, hz + 4), (S + 10, S), (-10, S)]), '#4d3d2f', '#1f1a18', hz, S)
    # estrada em perspectiva até o silo
    a.fill(a.poly([(930, hz + 6), (980, hz + 6), (S + 400, S), (-200, S)]), '#2b2729')
    a.screen(blur(a.poly([(930, hz + 6), (980, hz + 6), (S + 400, S), (-200, S)]), 30) * np.clip((a.YY - hz) / 600, 0, 1), '#e39a5f', 0.12)
    # fila de caminhões (do longe para perto)
    for k, (cx, e) in enumerate([(930, 0.18), (860, 0.3), (740, 0.48), (540, 0.78), (190, 1.25)]):
        y = hz + 8 + (S - hz) * (e ** 1.1) * 0.62
        w, h = 360 * e, 150 * e
        cab = a.poly([(cx, y), (cx, y - h), (cx + w * 0.28, y - h), (cx + w * 0.28, y)])
        car = a.poly([(cx + w * 0.3, y - h * 0.15), (cx + w * 0.3, y - h * 0.95), (cx + w, y - h * 0.95), (cx + w, y - h * 0.15)])
        a.fill(cab, '#17151a'); a.fill(car, '#211e22')
        a.fill(car * (a.YY < y - h * 0.8), '#d98d55', 0.25)
        for fx in (cx + w * 0.05, cx + w * 0.22):  # faróis
            a.screen(np.exp(-((a.XX - fx) ** 2 + (a.YY - (y - h * 0.25)) ** 2) / (2 * (6 + 30 * e) ** 2)), '#fff1c4', 1.0)
        a.screen(blur(a.poly([(cx, y - h * 0.3), (cx - 400 * e, y + 30 * e), (cx - 400 * e, y - 60 * e)]), 12), '#ffe2a2', 0.18)
    a.sparkles(60, box=(0, 560, S, 900), size=(1.0, 2.2), colour='#ffcf98')  # poeira contra a luz
    a.bloom(0.74, 20, 0.4); a.vignette(0.35)
    salva(a, "caminhoes")


def tempestade():
    a = Anime(S, S, seed=51)
    hz = 600
    a.sky('#141922', '#3a4250', '#6b7280', horizon=hz)
    for cx, y, w in ((260, 300, 760), (900, 260, 820), (600, 420, 900)):
        a.cumulus(cx, y, w, 260, light=(0.2, -1), lit='#7c8492', mid='#5c6472', shadow='#2b313c', deep='#1c2028', puffs=46)
    # raio
    r = np.random.default_rng(5)
    x, y = 780, 300; pts = [(x, y)]
    while y < hz:
        x += r.uniform(-40, 40); y += r.uniform(30, 60); pts.append((x, y))
    a.lines(pts, 4, '#f4f2ff'); m = np.zeros((S, S), np.float32)
    a.screen(np.exp(-((a.XX - 780) ** 2 + (a.YY - 420) ** 2) / (2 * 260 ** 2)), '#c9d2ff', 0.35)
    linha_de_arvores(a, hz + 4, '#1d2026', 17, alt=20)
    fileiras(a, hz + 6, 600, ('#2f3a2a', '#1a2016', '#121710', '#5a6370'))
    # água empoçada nos sulcos, refletindo o céu
    agua = (noise2d(S, S, 80, 3, 9) > 0.58).astype(np.float32) * (a.YY > hz + 120)
    a.fill(blur(agua, 2), '#6f7a8a', 0.6)
    # chuva
    for _ in range(900):
        x0 = r.uniform(-100, S); y0 = r.uniform(-50, S); ln = r.uniform(30, 70)
        a.lines([(x0, y0), (x0 + ln * 0.28, y0 + ln)], 1.1, '#aab4c4', 0.22)
    a.vignette(0.4)
    salva(a, "tempestade")


def justica():
    a = Anime(S, S, seed=61)
    a.img[:] = hexc('#0b0f18')
    mesa = 760
    a.gradient(a.poly([(-10, mesa), (S + 10, mesa), (S + 10, S), (-10, S)]), '#3a2618', '#1a110b', mesa, S)
    veio = noise2d(S, S, 20, 3, 4); a.fill((a.YY > mesa) * (veio > 0.55), '#5a3a22', 0.25)
    # cone de luz da luminária
    luz = a.poly([(520, 120), (640, 120), (1050, mesa + 60), (110, mesa + 60)])
    a.screen(blur(luz, 40), '#ffcf8a', 0.22)
    a.screen(np.exp(-((a.XX - 580) ** 2 + ((a.YY - (mesa + 40)) * 2.4) ** 2) / (2 * 300 ** 2)), '#ffbe6e', 0.55)
    # luminária
    a.fill(a.poly([(500, 120), (660, 120), (620, 50), (540, 50)]), '#1c1c20')
    a.lines([(580, 50), (580, -10)], 8, '#1c1c20')
    # papéis sobre a mesa
    for k, (x, y, rot) in enumerate([(300, mesa + 40, -6), (420, mesa + 70, 4)]):
        pts = [(x, y), (x + 360, y - 20), (x + 380, y + 150), (x + 20, y + 170)]
        a.fill(a.poly(pts), '#e9e1cf' if k else '#d9d0bc')
        for j in range(6):
            a.lines([(x + 40, y + 30 + j * 20), (x + 300, y + 16 + j * 20)], 3, '#8d8576', 0.6)
    # martelo (base + cabeça + cabo)
    a.fill(a.poly(blob_pts(860, mesa + 70, 110, 26, rough=0.02, n=40, seed=3)), '#2a1a10')
    a.fill(a.poly([(760, mesa - 40), (930, mesa - 95), (955, mesa - 30), (785, mesa + 25)]), '#4a2c18')
    a.fill(a.poly([(760, mesa - 40), (930, mesa - 95), (935, mesa - 82), (765, mesa - 27)]), '#d08a4f', 0.55)
    a.lines([(860, mesa - 50), (1080, mesa + 60)], 16, '#3a2414')
    # balança ao fundo, em contraluz
    a.lines([(250, mesa - 10), (250, 330)], 8, '#20202a'); a.lines([(120, 360), (380, 360)], 6, '#20202a')
    for cx in (130, 370):
        a.lines([(cx, 360), (cx - 40, 480), (cx + 40, 480), (cx, 360)], 3, '#20202a')
        a.fill(a.poly([(cx - 55, 480), (cx + 55, 480), (cx + 40, 500), (cx - 40, 500)]), '#20202a')
    a.fill(a.poly([(210, mesa), (290, mesa), (270, mesa - 18), (230, mesa - 18)]), '#20202a')
    a.screen(blur(a.poly([(120, 356), (380, 356), (380, 362), (120, 362)]), 2), '#d9a46a', 0.6)
    a.sparkles(40, box=(200, 120, 1000, 760), size=(0.8, 1.8), colour='#ffd8a0')  # poeira no feixe de luz
    a.bloom(0.7, 18, 0.35); a.vignette(0.45)
    salva(a, "justica")


CENAS = {"lavoura": lavoura, "colheitadeira": colheitadeira, "banco": banco, "seca": seca,
         "caminhoes": caminhoes, "tempestade": tempestade, "justica": justica}
if __name__ == "__main__":
    for nome in (sys.argv[2:] or CENAS):
        CENAS[nome]()
