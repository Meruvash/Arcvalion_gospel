"""Gera hf/index.html: vídeo "Comprou a terra e não é dono?" (registro × escritura; CC arts. 1.245 e 1.246), 1080x1080, ~50 s.
100% imagem feita em código: óleo com espátula (Lemo-Opuscar, MIT) no sítio, de dia e no fim de tarde; mapa em aquarela
(p5.brush) com os dois compradores; pinturas à maneira de Gerard ter Borch e Samuel van Hoogstraten (huashu-art-motion).
Cartões com o texto literal do Código Civil. Nenhuma imagem gerada por IA e nenhum vídeo de terceiros.
Uso: python3 montar.py
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
C = {"cartorio": FI[3]["inicio"] - .25, "mapa": FI[5]["inicio"] - .25, "gaveta": FI[8]["inicio"] - .25, "fim": FI[9]["inicio"] - .3, "cartela": FI[10]["inicio"] - .35}
M = {"contrato": ts(3, "contrato"), "registro3": ts(3, "registro"), "diz": ts(4, "diz"), "registro6": ts(6, "registro"),
     "eu": ts(10, "Eu"), "advogado": ts(10, "advogado"), "antes": ts(10, "Na"), "segue": ts(10, "segue")}
XF = 0.45
ORD = [("sitio", 0), ("es_terborch", 0), ("mapa", 0), ("es_hoogstraten", 0), ("sitio_fim", 0)]
INI = [0, C["cartorio"], C["mapa"], C["gaveta"], C["fim"], C["cartela"]]
def vid(i, src, ms, a, b, tr):
    b = min(b, a + dur(src) - ms)
    return (f'<video id="{i}" class="clip artv" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-media-start="{ms}" '
            f'data-track-index="{tr}" muted playsinline src="assets/art/{src}.mp4"></video>')
VIDEOS = "\n".join(vid(f"v{k}", s, ms, INI[k], INI[k + 1] + XF + (.2 if k == 4 else 0), k) for k, (s, ms) in enumerate(ORD))
def ov(i, a, b, html, cls="", tr=10):
    return f'<div id="{i}" class="clip ov {cls}" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="{tr}">{html}</div>'
SRC_CC = 'Código Civil (Lei 10.406/2002) · texto publicado pelo Senado Federal'
CARD1 = (f'<div class="card" id="card1"><div class="cardsrc">{SRC_CC}</div><div class="cardtxt">“Art. 1.245. Transfere-se entre vivos a propriedade mediante o registro do '
         'título translativo no Registro de Imóveis. § 1º <mark>Enquanto não se registrar o título translativo, o alienante continua a ser havido como dono do imóvel.</mark>”</div></div>')
CARD2 = (f'<div class="card" id="card2"><div class="cardsrc">{SRC_CC}</div><div class="cardtxt">“Art. 1.246. <mark>O registro é eficaz desde o momento em que se apresentar o '
         'título ao oficial do registro</mark>, e este o prenotar no protocolo.”</div></div>')
OVS = [
    ov("o-capa", 0, 2.5, '<div class="capa" id="capa"><div class="capa-chip">TERRA E ESCRITURA</div><div class="capa-big">COMPROU<br>E NÃO<br>É DONO?</div><div class="capa-sub">escritura na gaveta não basta</div></div>', "", 9),
    ov("o-flash", 0, 1.2, '<div id="flash"></div>', "", 8),
    ov("o-selo", 0.3, C["cartorio"], '<div class="selo" id="selo">SEM REGISTRO</div>', "", 7),
    ov("o-cred0", 2.6, C["cartorio"], 'PINTURA A ÓLEO COM ESPÁTULA, FEITA EM CÓDIGO', "cred", 10),
    ov("o-tags", M["contrato"] - .15, M["diz"] - .1, '<div class="tag" id="t1">escritura = contrato</div><div class="tag tag2" id="t2">registro = dono</div>', "", 11),
    ov("o-card1", M["diz"] - .1, C["mapa"] + .1, CARD1, "", 12),
    ov("o-src1", C["cartorio"] + .4, C["mapa"], 'CÓDIGO CIVIL, ART. 1.245 · PINTURA À MANEIRA DE GERARD TER BORCH', "rod", 13),
    ov("o-dr1", C["mapa"] + .1, FI[6]["inicio"] - .1, '<div class="drtag" id="dr1">DR. PELICIONI</div>', "", 14),
    ov("o-card2", M["registro6"] - .1, FI[7]["inicio"] - .1, CARD2, "", 15),
    ov("o-src2", C["mapa"] + .4, C["gaveta"], 'CÓDIGO CIVIL, ARTS. 1.245 E 1.246 · LEI 6.015/1973, ART. 169 · MAPA ILUSTRATIVO EM AQUARELA', "rod", 16),
    ov("o-dr2", C["gaveta"] + .1, C["fim"], '<div class="drtag" id="dr2">DR. PELICIONI</div>', "", 17),
    ov("o-src3", C["gaveta"] + .3, C["fim"], 'PINTURA À MANEIRA DE SAMUEL VAN HOOGSTRATEN', "rod", 18),
    ov("o-cred9", C["fim"] + .3, C["cartela"], 'PINTURA A ÓLEO COM ESPÁTULA, FEITA EM CÓDIGO', "cred", 19),
]
CART = """<div id="ct-luz"></div><div id="ct-nome">Dr. Pelicioni</div><div id="ct-fil"></div><div id="ct-prof">ADVOGADO</div>
<div id="ct-tese">na compra de terra, quem não registra não é dono</div><div id="ct-direct">Dúvida? Direct aberto.</div>
<div id="ct-fontes">Fontes: Código Civil (Lei 10.406/2002), arts. 108, 1.245 e 1.246, texto publicado pelo Senado Federal · Lei 6.015/1973, art. 169 · pinturas feitas em código: óleo com espátula (motor Lemo-Opuscar, MIT) e à maneira de Gerard ter Borch e Samuel van Hoogstraten · mapa ilustrativo · trilha original</div>"""
SFX = [("boom", 0.38, .5, 1.5), ("paper", M["diz"] - .1, .4, .8), ("whoosh", C["mapa"] - .2, .22, 1.0), ("paper", M["registro6"] - .1, .4, .8), ("boom", C["cartela"] + .1, .22, 1.5)]
sfx = "\n".join(f'<audio id="sx{n}" class="clip" data-start="{s:.3f}" data-duration="{d}" data-track-index="{40 + n}" data-volume="{v}" src="assets/audio/sfx/{f}.mp3"></audio>' for n, (f, s, v, d) in enumerate(SFX))
HTML = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Comprou a terra e não é dono? · registro</title>
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
.capa{{position:absolute;left:0;right:0;top:120px;text-align:center}}
.capa-chip{{display:inline-block;font:900 34px 'Inter';letter-spacing:.08em;color:#14240f;background:#f0c24b;padding:8px 18px;border-radius:6px}}
.capa-big{{font:900 168px/1 'Inter';color:#fff;margin-top:18px;-webkit-text-stroke:6px #14240f;paint-order:stroke fill;text-shadow:0 10px 30px rgba(0,0,0,.45)}}
.capa-sub{{font:900 46px/1.15 'Inter';color:#fff;margin:18px 60px 0;-webkit-text-stroke:3px #14240f;paint-order:stroke fill}}
.card{{position:absolute;left:70px;right:70px;top:90px;background:#fffdf6;padding:22px 26px 20px;box-shadow:0 18px 40px rgba(0,0,0,.45);transform:rotate(-1deg);opacity:0}}
.cardsrc{{font:500 20px/1.3 'IBM Plex Mono';color:#4a6a3a;letter-spacing:.02em;margin-bottom:12px;border-bottom:1px solid #d8d0bc;padding-bottom:10px}}
.cardtxt{{font:500 27px/1.5 'Newsreader';color:#1e1a16}} .cardtxt mark{{background:#ffd84a;padding:0 3px}}
.big2{{position:absolute;left:0;right:0;top:120px;text-align:center;font-size:76px;line-height:1.05}}
.capa-big{{font-size:118px !important;line-height:1.0 !important}}
#flash{{position:absolute;inset:0;background:#fff8e6;opacity:0}}
.selo{{position:absolute;left:0;right:0;margin:auto;top:640px;width:max-content;padding:12px 30px;border:9px solid #c0281a;border-radius:14px;color:#c0281a;font:900 78px 'Inter';letter-spacing:.04em;transform:rotate(-8deg);background:rgba(255,248,236,.88);opacity:0}}
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
.cap span{{display:inline-block;background:#f0c24b;color:#000;font:900 54px/1.12 'Inter';padding:6px 18px 8px;border-radius:6px;box-shadow:0 6px 18px rgba(0,0,0,.25)}}
</style></head><body>
<div id="root" data-composition-id="video" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1080">
{VIDEOS}
{chr(10).join(OVS)}
<div id="cartela" class="clip ov" data-start="{C['cartela']:.3f}" data-duration="{TOTAL - C['cartela']:.3f}" data-track-index="27">{CART}</div>
<div id="caps" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="28">{''.join(f'<div class="cap" id="cap{i}"><span>{b["txt"]}</span></div>' for i, b in enumerate(leg))}</div>
<audio id="voz" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="29" data-volume="1" src="assets/audio/narracao.wav"></audio>
<audio id="trilha" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="30" data-volume="1" data-fade-in="0.3" data-fade-out="2.0" src="assets/audio/trilha_mix.wav"></audio>
{sfx}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
const C = {json.dumps(C)}, M = {json.dumps(M)}, LEG = {json.dumps(leg, ensure_ascii=False)}, XF = {XF}, INI = {json.dumps(INI)};
const enter = 'power3.out';
// fusões e câmeras lentas (as pinturas do modelo antigo ganham zoom; as do Opuscar já têm câmera própria)
for (let k = 1; k < 5; k++) tl.fromTo('#v' + k, {{ opacity: 0 }}, {{ opacity: 1, duration: XF, ease: 'none' }}, INI[k]);
[1, 3].forEach(k => tl.fromTo('#v' + k, {{ scale: 1.0 }}, {{ scale: 1.08, duration: INI[k + 1] - INI[k] + XF, ease: 'none' }}, INI[k]));
document.querySelectorAll('.rod, .cred').forEach(el => tl.fromTo(el, {{ opacity: 0 }}, {{ opacity: 1, duration: .5 }}, +el.dataset.start + .05));
// capa: visível desde o quadro 0 e sai antes do número de abertura
tl.set('#capa', {{ opacity: 1 }}, 0); tl.to('#capa', {{ opacity: 0, y: -20, duration: .35, ease: 'power2.in' }}, 2.0);
tl.fromTo('#v0', {{ scale: 1.0 }}, {{ scale: 1.18, duration: INI[1] + XF, ease: 'none' }}, 0);
tl.to('#v0', {{ x: 14, y: -10, duration: .05, yoyo: true, repeat: 5, ease: 'none' }}, 0.4); tl.set('#v0', {{ x: 0, y: 0 }}, 0.71);
tl.fromTo('#capa', {{ scale: 1.0 }}, {{ scale: 1.06, duration: .08, yoyo: true, repeat: 1 }}, 0.4);
tl.fromTo('#flash', {{ opacity: 0 }}, {{ opacity: .55, duration: .05 }}, 0.4); tl.to('#flash', {{ opacity: 0, duration: .35 }}, 0.45);
// carimbo, reações do editor e cartões
tl.fromTo('#selo', {{ opacity: 0, scale: 2.2 }}, {{ opacity: 1, scale: 1, duration: .12, ease: 'power4.in' }}, 0.32);
tl.to('#selo', {{ opacity: 0, duration: .3 }}, 2.3);
['#dr1', '#dr2'].forEach(s => tl.fromTo(s, {{ opacity: 0, y: -10 }}, {{ opacity: 1, y: 0, duration: .3, ease: enter }}, +document.querySelector(s).parentElement.dataset.start + .05));
tl.fromTo('#t1', {{ opacity: 0, x: -24 }}, {{ opacity: 1, x: 0, duration: .35, ease: enter }}, M.contrato - .1);
tl.fromTo('#t2', {{ opacity: 0, x: -24 }}, {{ opacity: 1, x: 0, duration: .35, ease: enter }}, M.registro3 - .1);
tl.fromTo('#card1', {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: .4, ease: enter }}, M.diz - .1);
tl.fromTo('#card2', {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: .4, ease: enter }}, M.registro6 - .1);
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
(P / "index.html").write_text(HTML, encoding="utf-8"); (P / "hyperframes.json").write_text('{ "name": "escritura-sem-registro" }\n')
print("ok", TOTAL, len(leg), "blocos", {k: round(v, 2) for k, v in C.items()})
