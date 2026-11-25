"""Gera hf/index.html: vídeo "O banco toma o seu sítio?" (pequena propriedade impenhorável; CF art. 5º, XXVI; CPC art. 833;
STF Tema 961; STJ Tema 1.234), 1080x1080, ~54 s. 100% imagem feita em código: óleo com espátula (Lemo-Opuscar, MIT) no sítio e na
porteira; aquarela (p5.brush) com a balança do Supremo e os terrenos vizinhos; pinturas à maneira de Almeida Júnior, Léon
Lhermitte e Jean-Siméon Chardin (huashu-art-motion). Nenhuma imagem gerada por IA e nenhum vídeo de terceiros.
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
dur = lambda s: float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(P / f"assets/art/{s}.mp4")])) if (P / f"assets/art/{s}.mp4").exists() else 6.3
C = {"almeida": FI[3]["inicio"] - .25, "aq": FI[4]["inicio"] - .25, "lher": FI[7]["inicio"] - .25, "chardin": FI[8]["inicio"] - .25, "port": FI[9]["inicio"] - .3, "cartela": FI[10]["inicio"] - .35}
M = {"const": ts(3, "Constitui"), "perdeu": ts(4, "perdeu"), "pro": ts(5, "Pro"), "quatro": ts(6, "quatro"), "propria": ts(7, "própria"), "comprar": ts(7, "comprar"),
     "voce8": ts(8, "você"), "eu": ts(10, "Eu"), "advogado": ts(10, "advogado"), "antes": ts(10, "Na"), "segue": ts(10, "segue")}
XF = 0.45
ORD = [("sitio", 0), ("pp_almeida", 0), ("aq", 0), ("pp_lhermitte", 0), ("pp_chardin", 0), ("porteira", 0)]
INI = [0, C["almeida"], C["aq"], C["lher"], C["chardin"], C["port"], C["cartela"]]
def vid(i, src, ms, a, b, tr):
    b = min(b, a + dur(src) - ms)
    return (f'<video id="{i}" class="clip artv" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-media-start="{ms}" '
            f'data-track-index="{tr}" muted playsinline src="assets/art/{src}.mp4"></video>')
VIDEOS = "\n".join(vid(f"v{k}", s, ms, INI[k], INI[k + 1] + XF + (.6 if k == 5 else 0), k) for k, (s, ms) in enumerate(ORD))
def ov(i, a, b, html, cls="", tr=10):
    return f'<div id="{i}" class="clip ov {cls}" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="{tr}">{html}</div>'
CARD1 = ('<div class="card" id="card1"><div class="cardsrc">Constituição Federal, art. 5º, XXVI · texto publicado pelo Senado Federal</div><div class="cardtxt">“<mark>a pequena propriedade rural, assim definida em lei, desde que trabalhada pela família, não será objeto de penhora</mark> '
         'para pagamento de débitos decorrentes de sua atividade produtiva […]”</div></div>')
CARD2 = ('<div class="card" id="card2"><div class="cardsrc">STF · ARE 1.038.507 (Tema 961) · voto do relator, Min. Edson Fachin, em notícia do STF</div><div class="cardtxt">“A pequena propriedade rural, afinal, é impenhorável. Tal direito fundamental é indisponível, '
         '<mark>pouco importando a gravação do bem em hipoteca</mark>.”</div></div>')
OVS = [
    ov("o-capa", 0, 2.5, '<div class="capa" id="capa"><div class="capa-chip">DÍVIDA E TERRA</div><div class="capa-big">O BANCO<br>TOMA O SEU<br>SÍTIO?</div><div class="capa-sub">nem em garantia (com uma exceção)</div></div>', "", 9),
    ov("o-flash", 0, 1.2, '<div id="flash"></div>', "", 8),
    ov("o-selo", 0.3, 1.6, '<div class="selo" id="selo">PENHORA</div>', "", 7),
    ov("o-selo2", 1.0, C["almeida"] - 1.5, '<div class="selo ouro" id="selo2">IMPENHORÁVEL</div>', "", 6),
    ov("o-cred0", 2.6, C["almeida"], 'PEQUENA PROPRIEDADE (ATÉ 4 MÓDULOS FISCAIS) TRABALHADA PELA FAMÍLIA · ÓLEO COM ESPÁTULA FEITO EM CÓDIGO', "cred", 10),
    ov("o-card1", M["const"] - .1, C["aq"] + .1, CARD1, "", 12),
    ov("o-src1", C["almeida"] + .4, C["aq"], 'CF, ART. 5º, XXVI · CPC, ART. 833, VIII · PINTURA À MANEIRA DE ALMEIDA JÚNIOR', "rod", 13),
    ov("o-card2", M["pro"] - .1, FI[6]["inicio"] - .1, CARD2, "", 15),
    ov("o-src2", C["aq"] + .4, C["lher"], 'STF, TEMA 961 · LEI 8.629/1993, ART. 4º, II · DECISÃO SOBRE HIPOTECA; ALIENAÇÃO FIDUCIÁRIA TEM REGRA PRÓPRIA · ILUSTRAÇÃO', "rod", 16),
    ov("o-tag7", M["propria"] - .1, C["chardin"], '<div class="tag" id="t7">dívida da própria terra</div>', "", 17),
    ov("o-recibo", M["comprar"] - .1, C["chardin"], '<div class="recibo" id="recibo"><b>RECIBO</b><br>compra do sítio<br><span>pago em parcelas ao vendedor</span></div>', "", 18),
    ov("o-src3", C["lher"] + .3, C["chardin"], 'CPC, ART. 833, § 1º · PINTURA À MANEIRA DE LÉON LHERMITTE', "rod", 19),
    ov("o-tag8", M["voce8"] - .1, C["port"], '<div class="tag" id="t8">quem prova: você</div>', "", 20),
    ov("o-src4", C["chardin"] + .3, C["port"], 'STJ, TEMA 1.234 · PINTURA À MANEIRA DE JEAN-SIMÉON CHARDIN', "rod", 21),
    ov("o-cred9", C["port"] + .3, C["cartela"], 'ÓLEO COM ESPÁTULA FEITO EM CÓDIGO', "cred", 22),
]
CART = """<div id="ct-luz"></div><div id="ct-nome">Dr. Pelicioni</div><div id="ct-fil"></div><div id="ct-prof">ADVOGADO</div>
<div id="ct-tese">na pequena propriedade, a lei protege quem trabalha a terra com a família</div><div id="ct-direct">Dúvida? Direct aberto.</div>
<div id="ct-fontes">Fontes: Constituição Federal, art. 5º, XXVI · CPC (Lei 13.105/2015), art. 833, VIII e § 1º · Lei 8.629/1993, art. 4º, II (textos publicados pelo Senado Federal) · STF, ARE 1.038.507 (Tema 961) · STJ, REsp 2.080.023 (Tema 1.234) · pinturas feitas em código: óleo com espátula (Lemo-Opuscar, MIT) e à maneira de Almeida Júnior, Léon Lhermitte e Jean-Siméon Chardin · ilustração em aquarela · trilha original</div>"""
SFX = [("stamp", 0.36, .8, 1.0), ("boom", 0.38, .45, 1.5), ("whoosh", 1.0, .35, 1.0), ("paper", M["const"] - .1, .4, .8), ("whoosh", C["aq"] - .2, .22, 1.0),
       ("stamp", C["aq"] + 4.6, .5, 1.0), ("paper", M["pro"] - .1, .4, .8), ("paper", M["comprar"] - .1, .45, .8), ("boom", C["cartela"] + .1, .22, 1.5)]
sfx = "\n".join(f'<audio id="sx{n}" class="clip" data-start="{s:.3f}" data-duration="{d}" data-track-index="{40 + n}" data-volume="{v}" src="assets/audio/sfx/{f}.mp3"></audio>' for n, (f, s, v, d) in enumerate(SFX))
HTML = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>O banco toma o seu sítio? · impenhorável</title>
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
.selo{{position:absolute;left:0;right:0;margin:auto;top:700px;width:max-content;padding:12px 30px;border:9px solid #c0281a;border-radius:14px;color:#c0281a;font:900 78px 'Inter';letter-spacing:.04em;transform:rotate(-8deg);background:rgba(255,248,236,.88);opacity:0}}
.pres{{position:absolute;right:-10px;bottom:0;width:420px;height:747px;object-fit:cover;opacity:0;z-index:35;-webkit-mask-image:linear-gradient(to right,transparent 0,#000 22%),linear-gradient(to top,transparent 0,#000 9%);-webkit-mask-composite:source-in;mask-image:linear-gradient(to right,transparent 0,#000 22%),linear-gradient(to top,transparent 0,#000 9%);mask-composite:intersect}}
.presbg{{position:absolute;z-index:34;right:-120px;bottom:-140px;width:640px;height:640px;border-radius:50%;background:radial-gradient(circle,rgba(240,194,75,.55),rgba(240,194,75,0) 68%);opacity:0}}
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
// fusões e câmeras lentas (as pinturas do modelo antigo ganham zoom; óleo e aquarela já têm câmera própria)
for (let k = 1; k < 6; k++) tl.fromTo('#v' + k, {{ opacity: 0 }}, {{ opacity: 1, duration: XF, ease: 'none' }}, INI[k]);
[1, 3, 4].forEach(k => tl.fromTo('#v' + k, {{ scale: 1.0 }}, {{ scale: 1.08, duration: INI[k + 1] - INI[k] + XF, ease: 'none' }}, INI[k]));
document.querySelectorAll('.rod, .cred').forEach(el => tl.fromTo(el, {{ opacity: 0 }}, {{ opacity: 1, duration: .5 }}, +el.dataset.start + .05));
// capa: visível desde o quadro 0
tl.set('#capa', {{ opacity: 1 }}, 0); tl.to('#capa', {{ opacity: 0, y: -20, duration: .35, ease: 'power2.in' }}, 2.0);
tl.fromTo('#v0', {{ scale: 1.0 }}, {{ scale: 1.12, duration: INI[1] + XF, ease: 'none' }}, 0);
tl.to('#v0', {{ x: 14, y: -10, duration: .05, yoyo: true, repeat: 5, ease: 'none' }}, 0.4); tl.set('#v0', {{ x: 0, y: 0 }}, 0.71);
tl.fromTo('#capa', {{ scale: 1.0 }}, {{ scale: 1.06, duration: .08, yoyo: true, repeat: 1 }}, 0.4);
tl.fromTo('#flash', {{ opacity: 0 }}, {{ opacity: .55, duration: .05 }}, 0.4); tl.to('#flash', {{ opacity: 0, duration: .35 }}, 0.45);
// o carimbo PENHORA bate e quica de volta; fica o selo dourado IMPENHORÁVEL
tl.fromTo('#selo', {{ opacity: 0, scale: 2.2 }}, {{ opacity: 1, scale: 1, duration: .12, ease: 'power4.in' }}, 0.32);
tl.to('#selo', {{ y: -260, rotation: 14, scale: .7, opacity: 0, duration: .5, ease: 'power2.out' }}, 1.0);
tl.fromTo('#selo2', {{ opacity: 0, scale: 1.6 }}, {{ opacity: 1, scale: 1, duration: .2, ease: 'back.out(2)' }}, 1.1);
tl.to('#selo2', {{ opacity: 0, duration: .3 }}, 2.3);
tl.fromTo('#card1', {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: .4, ease: enter }}, M.const - .1);
tl.fromTo('#card2', {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: .4, ease: enter }}, M.pro - .1);
tl.fromTo('#t7', {{ opacity: 0, x: -24 }}, {{ opacity: 1, x: 0, duration: .35, ease: enter }}, M.propria - .1);
tl.fromTo('#recibo', {{ opacity: 0, y: -120, rotation: -10 }}, {{ opacity: 1, y: 0, rotation: 5, duration: .5, ease: 'bounce.out' }}, M.comprar - .1);
tl.fromTo('#t8', {{ opacity: 0, x: -24 }}, {{ opacity: 1, x: 0, duration: .35, ease: enter }}, M.voce8 - .1);
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
(P / "index.html").write_text(HTML, encoding="utf-8"); (P / "hyperframes.json").write_text('{ "name": "pequena-propriedade" }\n')
print("ok", TOTAL, len(leg), "blocos", {k: round(v, 2) for k, v in C.items()})
