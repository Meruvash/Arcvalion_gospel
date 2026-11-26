"""Gera hf/index.html: vídeo "Poço artesiano é crime?" (Lei 9.433/1997, arts. 12, 49 e 50; CF, art. 26, I; IGAM-MG), 1080x1080, ~59 s.
100% pintura em código (Grimm, prancha de geologia, Calixto); movimentos com função (docs/video/DIRECAO_MOTION.md). Uso: python3 montar.py
"""
import json, re
from pathlib import Path
P = Path(__file__).resolve().parent / "hf"
T = json.load(open(P / "assets/data/tempos.json", encoding="utf-8"))
FALAS = {f["id"]: f for f in json.load(open(P.parent / "falas.json", encoding="utf-8"))}
FI = {f["fala"]: f for f in T["falas"]}
TOTAL = T["total"]
pw = lambda n: [w for w in T["palavras"] if w["fala"] == n]
def ts(n, palavra, k=1):
    c = 0
    for w in pw(n):
        if w["w"].strip(".,:?!").lower().startswith(palavra.lower()):
            c += 1
            if c == k: return w["s"]
    raise KeyError((n, palavra))
def ts_alt(n, *variantes):
    """Primeira grafia que a transcrição usou (ex.: siglas que o speech-to-text escreve de jeitos diferentes)."""
    for v in variantes:
        try: return ts(n, v)
        except KeyError: pass
    raise KeyError((n, variantes))

# ---------- legendas (blocos de até 3 palavras) ----------
blocos = []
for fid in range(1, 11):
    toks, ws = FALAS[fid]["texto"].split(), pw(fid)
    if len(toks) != len(ws): raise SystemExit(f"fala {fid}: {len(toks)} x {len(ws)}")
    cur = []
    for tok, w in zip(toks, ws):
        cur.append((tok, w))
        if len(cur) == 3 or re.search(r"[.,:?!]$", tok): blocos.append(cur); cur = []
    if cur: blocos.append(cur)
leg = []
for i, b in enumerate(blocos):
    prox = blocos[i + 1][0][1]["s"] if i + 1 < len(blocos) else TOTAL
    leg.append({"txt": " ".join(t for t, _ in b), "ini": round(b[0][1]["s"], 3), "fim": round(min(prox, b[-1][1]["e"] + 0.45), 3)})

# ---------- cortes ----------
import subprocess
dur = lambda s: float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(P / f"assets/art/{s}.mp4")]))
FAL = lambda n: FI[n]["inicio"]
C = {"co": FAL(3) - .25, "gr2": FAL(7) - .25, "ca": FAL(8) - .25, "cartela": FAL(10) - .35}
M = {"poco": ts(1, "poço"), "outorga": ts(2, "outorga"), "permite": ts(3, "permite"), "lei": ts(4, "lei"), "peq": ts(5, "pequeno"), "nao": ts(5, "não"),
     "debaixo": ts(6, "debaixo"), "cad": ts(7, "cadastro"), "internet": ts(7, "internet"), "regul": ts(8, "regularizado"), "na9": ts(9, "Na"),
     "eu": ts(10, "Eu"), "advogado": ts(10, "advogado"), "antes": ts(10, "Na"), "segue": ts(10, "segue")}
XF = 0.5
ORD = [("pc_grimm", 0), ("pc_corte", 0), ("pc_grimm", 10), ("pc_calixto", 0)]
INI = [0, C["co"], C["gr2"], C["ca"], C["cartela"]]
def vid(i, src, ms, a, b, tr):
    b = min(b, a + dur(src) - ms)
    return (f'<video id="{i}" class="clip artv" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-media-start="{ms}" '
            f'data-track-index="{tr}" muted playsinline src="assets/art/{src}.mp4"></video>')
VIDEOS = "\n".join(vid(f"v{k}", s, ms, INI[k], INI[k + 1] + XF + (.6 if k == len(ORD) - 1 else 0), k) for k, (s, ms) in enumerate(ORD))
def ov(i, a, b, html, cls="", tr=10):
    return f'<div id="{i}" class="clip ov {cls}" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="{tr}">{html}</div>'
CARD1 = ('<div class="card" id="card1"><div class="cardsrc">Lei 9.433/1997, art. 49, V · Planalto</div><div class="cardtxt">“Constitui infração das normas de utilização de recursos hídricos […]: '
         '<mark>perfurar poços para extração de água subterrânea ou operá-los sem a devida autorização</mark>”</div></div>')
CARD2 = ('<div class="card" id="card2"><div class="cardsrc">Constituição Federal, art. 26, I · Planalto</div><div class="cardtxt">“Incluem-se entre os bens dos Estados: '
         '<mark>as águas superficiais ou subterrâneas</mark>, fluentes, emergentes e em depósito […]”</div></div>')
BALDE = ('<svg id="balde" viewBox="0 0 160 160" width="150" height="150" style="position:absolute;left:250px;top:120px">'
         '<path d="M30 50 L130 50 L115 140 L45 140 Z" fill="#9a948c" stroke="#3a3634" stroke-width="5"/><ellipse cx="80" cy="50" rx="50" ry="12" fill="#5fa0c8" stroke="#3a3634" stroke-width="5"/>'
         '<path d="M30 50 Q80 -10 130 50" fill="none" stroke="#3a3634" stroke-width="5"/><rect x="48" y="60" width="10" height="70" fill="rgba(255,255,255,.35)"/></svg>')
PLACA = ('<div id="placa" style="position:absolute;left:600px;top:470px;transform:rotate(-4deg);background:#d8b878;border:5px solid #5a4026;'
         "padding:8px 16px;font:900 34px 'Inter';color:#3a2614;letter-spacing:.04em;box-shadow:0 8px 18px rgba(0,0,0,.35);opacity:0\">REGULARIZADO</div>")
OVS = [
    ov("o-capa", 0, 2.4, '<div class="capa" id="capa"><div class="capa-chip">ÁGUA NA FAZENDA</div><div class="capa-big" style="font-size:100px !important;margin-top:12px">POÇO<br>ARTESIANO<br>É CRIME?</div></div>', "", 9),
    ov("o-flash", 0, 1.2, '<div id="flash"></div>', "", 8),
    ov("o-src0", 2.6, C["co"], 'PINTURA À MANEIRA DE GEORG GRIMM', "rod", 11),
    ov("o-out", M["outorga"] - .1, C["co"], '<div class="anos" id="out" style="font-size:112px;top:120px">OUTORGA</div>', "", 20),
    ov("o-src1", C["co"] + .6, C["gr2"], 'LEI 9.433/1997, ARTS. 12, 49 E 50 · CONSTITUIÇÃO, ART. 26, I · PRANCHA PINTADA EM CÓDIGO', "rod", 12),
    ov("o-card1", M["lei"] - .1, FAL(5) - .15, CARD1, "", 21),
    ov("o-balde", M["peq"] - .1, FAL(6) - .1, BALDE + '<div class="tag" id="tg1" style="top:150px;left:auto;right:60px">USO PEQUENO</div><div class="tag tag2" id="tg2" style="top:250px;left:auto;right:60px">SEM OUTORGA</div>', "", 22),
    ov("o-aq", M["debaixo"] - .2, C["gr2"], '<div id="aq" style="position:absolute;left:0;right:0;top:752px;height:150px;background:linear-gradient(180deg,rgba(150,220,255,0),rgba(150,220,255,.55),rgba(150,220,255,0));mix-blend-mode:screen;opacity:0"></div><div class="anos" id="estado" style="font-size:80px;top:600px">ÁGUA DO ESTADO</div>', "", 23),
    ov("o-card2", M["debaixo"] + .6, C["gr2"], CARD2, "", 24),
    ov("o-cad", M["cad"] - .05, C["ca"], '<div class="tag" id="tg3">CADASTRO SIMPLES</div><div class="tag tag2" id="tg4">PELA INTERNET</div>', "", 25),
    ov("o-src2", C["gr2"] + .5, C["ca"], 'IGAM-MG: CADASTRO DE USO INSIGNIFICANTE · PINTURA À MANEIRA DE GEORG GRIMM', "rod", 13),
    ov("o-placa", M["regul"] - .1, C["cartela"], PLACA, "", 26),
    ov("o-src3", C["ca"] + .5, C["cartela"], 'PINTURA À MANEIRA DE BENEDITO CALIXTO', "rod", 14),
    ov("o-reg", M["na9"] - .05, C["cartela"], '<div class="tag" id="tg6" style="top:40px;left:auto;right:60px">NA SUA REGIÃO?</div>', "", 27),
]
CART = """<div id="ct-luz"></div><div id="ct-nome">Dr. Pelicioni</div><div id="ct-fil"></div><div id="ct-prof">ADVOGADO</div>
<div id="ct-tese">poço em dia é água sem multa</div><div id="ct-direct">Dúvida? Direct aberto.</div>
<div id="ct-fontes">Fontes: Lei 9.433/1997, arts. 12, 49 e 50 (Planalto) · Constituição Federal, art. 26, I · IGAM-MG, cadastro de uso insignificante · pinturas feitas em código à maneira de Georg Grimm e Benedito Calixto · trilha original</div>"""
SFX = [("boom", 0.38, .45, 1.5), ("stamp", M["outorga"] - .1, .5, 1.0), ("whoosh", C["co"] - .2, .3, 1.0), ("paper", M["lei"] - .1, .4, .8),
       ("paper", M["debaixo"] + .6, .4, .8), ("whoosh", C["gr2"] - .2, .25, 1.0), ("whoosh", C["ca"] - .2, .25, 1.0), ("stamp", M["regul"] - .1, .45, 1.0), ("boom", C["cartela"] + .1, .22, 1.5)]
sfx = "\n".join(f'<audio id="sx{n}" class="clip" data-start="{s:.3f}" data-duration="{d}" data-track-index="{40 + n}" data-volume="{v}" src="assets/audio/sfx/{f}.mp3"></audio>' for n, (f, s, v, d) in enumerate(SFX))
HTML = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Poço artesiano é crime?</title>
<script src="assets/lib/gsap.min.js"></script>
<style>
@font-face{{font-family:'Inter';src:url(assets/fonts/inter-latin-900-normal.woff2) format('woff2');font-weight:900}}
@font-face{{font-family:'Newsreader';src:url(assets/fonts/newsreader-latin-500-normal.woff2) format('woff2');font-weight:500}}
@font-face{{font-family:'Newsreader';src:url(assets/fonts/newsreader-latin-600-italic.woff2) format('woff2');font-weight:600;font-style:italic}}
@font-face{{font-family:'IBM Plex Mono';src:url(assets/fonts/ibm-plex-mono-latin-500-normal.woff2) format('woff2');font-weight:500}}
@font-face{{font-family:'Caveat';src:url(assets/fonts/caveat-700.woff2) format('woff2');font-weight:700}}
*{{box-sizing:border-box;margin:0}} html,body{{width:1080px;height:1080px;overflow:hidden;background:#000}}
#root{{position:relative;width:1080px;height:1080px;overflow:hidden;background:#000}}
.artv{{position:absolute;left:0;top:0;width:1080px;height:1080px;object-fit:cover;transform-origin:50% 50%}}
.ov{{position:absolute;inset:0;pointer-events:none}}
.mao{{font-family:'Caveat';font-weight:700;color:#fff6dc;text-shadow:0 3px 14px rgba(10,14,30,.8),0 0 2px rgba(10,14,30,.9)}}
.rod{{top:auto;bottom:0;height:auto;padding:14px 40px 18px;background:rgba(243,234,216,.93);color:#3a3026;font:500 20px/1.35 'IBM Plex Mono';letter-spacing:.03em}}
.cred{{top:auto;bottom:0;height:auto;padding:14px 40px 18px;background:linear-gradient(0deg,rgba(10,14,26,.75),rgba(10,14,26,0));color:#f6efd8;font:500 21px/1.35 'IBM Plex Mono';letter-spacing:.04em}}
.capa{{position:absolute;left:0;right:0;top:40px;text-align:center}}
.capa-chip{{display:inline-block;font:900 34px 'Inter';letter-spacing:.08em;color:#14240f;background:#f0c24b;padding:8px 18px;border-radius:6px}}
.capa-big{{font:900 168px/1 'Inter';color:#fff;margin-top:18px;-webkit-text-stroke:6px #14240f;paint-order:stroke fill;text-shadow:0 10px 30px rgba(0,0,0,.45)}}
.capa-sub{{font:900 46px/1.15 'Inter';color:#fff;margin:18px 60px 0;-webkit-text-stroke:3px #14240f;paint-order:stroke fill}}
.card{{position:absolute;left:70px;right:70px;top:90px;background:#fffdf6;padding:22px 26px 20px;box-shadow:0 18px 40px rgba(0,0,0,.45);transform:rotate(-1deg);opacity:0}}
.cardsrc{{font:500 20px/1.3 'IBM Plex Mono';color:#4a6a3a;letter-spacing:.02em;margin-bottom:12px;border-bottom:1px solid #d8d0bc;padding-bottom:10px}}
.cardtxt{{font:500 27px/1.5 'Newsreader';color:#1e1a16}} .cardtxt mark{{background:#ffd84a;padding:0 3px}}
.big2{{position:absolute;left:0;right:0;top:120px;text-align:center;font-size:76px;line-height:1.05}}
.capa-big{{font-size:118px !important;line-height:1.0 !important}}
#flash{{position:absolute;inset:0;background:#fff8e6;opacity:0}}
.selo{{position:absolute;left:0;right:0;margin:auto;top:700px;width:max-content;padding:12px 30px;border:9px solid #c0281a;border-radius:14px;color:#c0281a;font:900 78px 'Inter';letter-spacing:.04em;transform:rotate(-8deg);background:rgba(255,248,236,.88);opacity:0}}
.pres{{position:absolute;right:-10px;bottom:0;width:420px;height:747px;object-fit:cover;opacity:0;z-index:35;-webkit-mask-image:linear-gradient(to right,transparent 0,#000 22%),linear-gradient(to top,transparent 0,#000 9%);-webkit-mask-composite:source-in;mask-image:linear-gradient(to right,transparent 0,#000 22%),linear-gradient(to top,transparent 0,#000 9%);mask-composite:intersect}}
.presbg{{position:absolute;z-index:34;right:-120px;bottom:-140px;width:640px;height:640px;border-radius:50%;background:radial-gradient(circle,rgba(240,194,75,.55),rgba(240,194,75,0) 68%);opacity:0}}
.anos{{position:absolute;left:0;right:0;margin:auto;top:150px;width:max-content;text-align:center;line-height:1.02;font:900 120px 'Inter';color:#fff6dc;-webkit-text-stroke:5px #2b211a;paint-order:stroke fill;opacity:0}}
.negado{{top:330px !important}}
.ouro{{color:#8a6a10 !important;border-color:#c09a20 !important;background:rgba(255,246,210,.92) !important}}
.recibo{{position:absolute;right:70px;top:300px;width:380px;background:#fffaf0;padding:20px 24px;font:500 36px/1.25 'Newsreader';color:#2b211a;box-shadow:0 14px 34px rgba(0,0,0,.45);transform:rotate(5deg);opacity:0}}
.recibo b{{font:900 40px 'Inter';letter-spacing:.1em;color:#7a2a18}} .recibo span{{font:700 32px 'Caveat';color:#1e3a6a}}
.drtag{{position:absolute;left:44px;top:44px;font:900 30px 'Inter';letter-spacing:.12em;color:#14240f;background:#f0c24b;padding:8px 16px;border-radius:6px;opacity:0}}
.carimbo{{position:absolute;left:130px;top:130px;padding:10px 26px;border:7px solid #c0281a;color:#c0281a;font:900 58px 'Inter';text-transform:uppercase;letter-spacing:.03em;transform:rotate(-6deg);background:rgba(255,248,236,.9);opacity:0}}
.tag{{position:absolute;left:70px;top:140px;font:900 54px/1 'Inter';color:#fff6dc;background:rgba(30,40,60,.84);padding:14px 22px;border-left:8px solid #f0c24b;opacity:0}}
.tag2{{top:250px;border-left-color:#c0281a}}
.cont{{position:absolute;left:50px;top:120px;width:520px}}
.cnum{{position:absolute;left:0;top:0;font:900 92px/1 'Inter';color:#2b211a;background:rgba(243,234,216,.9);padding:10px 18px;border-radius:8px;opacity:0}}
.cnum small{{display:block;font:700 30px/1.2 'Caveat';font-size:34px;margin-top:4px;white-space:normal}}
.c10{{top:0}} .c5{{top:0;color:#7a2a18}}
#cartela{{background:#0b1424}}
#ct-luz{{position:absolute;inset:0;background:radial-gradient(ellipse 60% 45% at 50% 42%,#2a2418 0%,#14100c 60%,#0a0806 100%)}}
#ct-nome{{position:absolute;left:0;right:0;top:250px;text-align:center;font:500 112px 'Newsreader';color:#eee8dc}}
#ct-fil{{position:absolute;left:380px;width:320px;top:400px;height:3px;background:#e0a228}}
#ct-prof{{position:absolute;left:0;right:0;top:428px;text-align:center;font:500 30px 'IBM Plex Mono';letter-spacing:.32em;color:#c9ced6}}
#ct-tese{{position:absolute;left:60px;right:60px;top:520px;text-align:center;font:italic 600 40px 'Newsreader';color:#d8d4c8}}
#ct-direct{{position:absolute;left:0;right:0;top:610px;text-align:center;font:900 34px 'Inter';color:#f0c24b}}
#ct-fontes{{position:absolute;left:60px;right:60px;bottom:14px;text-align:center;font:500 15px/1.35 'IBM Plex Mono';color:#9aa3b3}}
#caps{{position:absolute;inset:0;z-index:30}}
.cap{{position:absolute;left:0;right:0;top:860px;display:flex;justify-content:center;opacity:0}}
.mk{{position:absolute;font:900 60px/1 'Inter';color:#fff6dc;-webkit-text-stroke:4px #2b211a;paint-order:stroke fill;opacity:0;white-space:nowrap}} .mk small{{display:block;font:700 30px 'Caveat';-webkit-text-stroke:0;color:#fff6dc;text-shadow:0 2px 8px rgba(0,0,0,.8)}}
.cap span{{display:inline-block;background:#f0c24b;color:#000;font:900 54px/1.12 'Inter';padding:6px 18px 8px;border-radius:6px;box-shadow:0 6px 18px rgba(0,0,0,.25)}}
</style></head><body>
<div id="root" data-composition-id="video" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1080">
{VIDEOS}
{chr(10).join(OVS)}
<div id="cartela" class="clip ov" data-start="{C['cartela']:.3f}" data-duration="{TOTAL - C['cartela']:.3f}" data-track-index="27">{CART}</div>
<div id="caps" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="28">{''.join(f'<div class="cap{' '}" id="cap{i}"><span>{b["txt"]}</span></div>' for i, b in enumerate(leg))}</div>
<audio id="voz" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="29" data-volume="1" src="assets/audio/narracao.wav"></audio>
<audio id="trilha" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="30" data-volume="1" data-fade-in="0.3" data-fade-out="2.0" src="assets/audio/trilha_mix.wav"></audio>
{sfx}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
const C = {json.dumps(C)}, M = {json.dumps(M)}, LEG = {json.dumps(leg, ensure_ascii=False)}, XF = {XF}, INI = {json.dumps(INI)};
const enter = 'power3.out';
// câmera com função (DIRECAO_MOTION.md)
tl.set('#v0', {{ transformOrigin: '71% 45%' }}, 0);
tl.fromTo('#v0', {{ scale: 1.0 }}, {{ scale: 1.16, duration: 2.6, ease: 'power2.inOut' }}, M.poco);                    // REVELAR: o poço e o cata-vento
tl.to('#v0', {{ yPercent: -70, duration: .9, ease: 'power2.in' }}, INI[1] - .3);                                      // TRANSFORMAR: a câmera desce para dentro da terra…
tl.fromTo('#v1', {{ yPercent: 60, opacity: 0 }}, {{ yPercent: 0, opacity: 1, duration: 1.0, ease: 'power2.out' }}, INI[1]);   // …e o chão vira o corte
tl.set('#v2', {{ transformOrigin: '71% 40%' }}, 0); tl.fromTo('#v2', {{ scale: 1.3 }}, {{ scale: 1.36, duration: INI[3] - INI[2] + XF, ease: 'none' }}, INI[2]);   // outro enquadramento do cata-vento, perto da torre
tl.fromTo('#v2', {{ opacity: 0 }}, {{ opacity: 1, duration: XF, ease: 'none' }}, INI[2]);
tl.fromTo('#v3', {{ opacity: 0 }}, {{ opacity: 1, duration: XF + .2, ease: 'none' }}, INI[3]);
document.querySelectorAll('.rod, .cred').forEach(el => tl.fromTo(el, {{ opacity: 0 }}, {{ opacity: 1, duration: .4 }}, +el.dataset.start + .05));
tl.set('#capa', {{ opacity: 1 }}, 0); tl.to('#capa', {{ opacity: 0, y: -20, duration: .35, ease: 'power2.in' }}, 2.0);
tl.fromTo('#capa', {{ scale: 1.0 }}, {{ scale: 1.05, duration: .08, yoyo: true, repeat: 1 }}, 0.4);
tl.fromTo('#flash', {{ opacity: 0 }}, {{ opacity: .5, duration: .05 }}, 0.4); tl.to('#flash', {{ opacity: 0, duration: .35 }}, 0.45);
const bate = (id, t) => tl.fromTo(id, {{ opacity: 0, scale: 1.6, y: -10 }}, {{ opacity: 1, scale: 1, y: 0, duration: .22, ease: 'back.out(2.2)' }}, t);
const sobe = (id, t) => tl.fromTo(id, {{ opacity: 0, scale: .7 }}, {{ opacity: 1, scale: 1, duration: .35, ease: 'back.out(1.8)' }}, t);
const entra = (id, t) => tl.fromTo(id, {{ opacity: 0, x: -40 }}, {{ opacity: 1, x: 0, duration: .3, ease: 'power3.out' }}, t);
bate('#out', M.outorga - .1);
tl.fromTo('#card1', {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: .45, ease: 'power3.out' }}, M.lei - .1);
sobe('#balde', M.peq - .1); entra('#tg1', M.peq - .05); entra('#tg2', M.nao - .05);                                    // MEDIR: o "pouco" vira um balde
tl.fromTo('#aq', {{ opacity: 0 }}, {{ opacity: 1, duration: .8, ease: 'power2.out' }}, M.debaixo - .2); sobe('#estado', M.debaixo);   // LOCALIZAR: a água de debaixo da terra
tl.fromTo('#card2', {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: .45, ease: 'power3.out' }}, M.debaixo + .6);
entra('#tg3', M.cad - .05); entra('#tg4', M.internet - .05);
tl.fromTo('#placa', {{ opacity: 0, y: -40, rotate: -14 }}, {{ opacity: 1, y: 0, rotate: -4, duration: .5, ease: 'back.out(2)' }}, M.regul - .1);   // COMPARAR: o poço velho regularizado
entra('#tg6', M.na9 - .05);
// cartela
tl.fromTo('#cartela', {{ opacity: 0 }}, {{ opacity: 1, duration: .5 }}, C.cartela);
tl.fromTo('#ct-nome', {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: .6, ease: enter }}, M.eu);
tl.fromTo('#ct-fil', {{ scaleX: 0 }}, {{ scaleX: 1, duration: .6, ease: enter }}, M.eu + .3);
tl.fromTo('#ct-prof', {{ opacity: 0 }}, {{ opacity: 1, duration: .4 }}, M.advogado);
tl.fromTo('#ct-tese', {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: .5, ease: enter }}, M.antes);
tl.fromTo('#ct-direct', {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: .5, ease: enter }}, M.segue);
tl.fromTo('#ct-fontes', {{ opacity: 0 }}, {{ opacity: 1, duration: .6 }}, C.cartela + .8);
// legendas: sobem para o topo no mapa (embaixo fica o Sul do mapa)

LEG.forEach((b, i) => {{ tl.fromTo('#cap' + i, {{ opacity: 0, scale: .92 }}, {{ opacity: 1, scale: 1, duration: .12, ease: 'power2.out' }}, b.ini); tl.set('#cap' + i, {{ opacity: 0 }}, b.fim); }});
tl.to({{}}, {{ duration: {TOTAL} }}, 0);
window.__timelines = window.__timelines || {{}}; window.__timelines['video'] = tl;
</script></body></html>"""
(P / "index.html").write_text(HTML, encoding="utf-8"); (P / "hyperframes.json").write_text('{ "name": "poco-artesiano" }\n')
print("ok", TOTAL, len(leg), "blocos", {k: round(v, 2) for k, v in C.items()})
