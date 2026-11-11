"""Gera hf/index.html: vídeo "Cinco por dia" (recuperação judicial no agro), 1080x1080, ~59 s.
Pinturas em código (Van Gogh, Millet) + mapa e gráficos em aquarela (p5.brush) + legenda amarela + trilha original de moda de viola.
Nenhuma imagem gerada por IA; nenhum documento na tela (fonte no rodapé). Uso: python3 montar.py
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

# ---------- legendas ----------
blocos = []
for fid in range(1, 11):
    toks, ws = FALAS[fid]["texto"].split(), pw(fid)
    if len(toks) != len(ws):
        raise SystemExit(f"fala {fid}: roteiro {len(toks)} palavras, transcrição {len(ws)}: {[w['w'] for w in ws]}")
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
C = {"mapa": FI[3]["inicio"] - 0.30, "millet": FI[5]["inicio"] - 0.25, "barras": FI[6]["inicio"] - 0.18,
     "vendaval": FI[7]["inicio"] - 0.20, "queda": FI[8]["inicio"] - 0.15, "abre": FI[9]["inicio"] - 0.15, "cartela": FI[10]["inicio"] - 0.35}
C["mapa_fim"] = C["mapa"] + 9.6
C["millet"] = max(C["millet"], C["mapa_fim"] - 0.45)
M = {"cinco": ts(1, "cinco"), "n922": ts(2, "922"), "semestre": ts(2, "semestre"),
     "custos": ts(7, "custos"), "credito": ts(7, "crédito"), "endiv": ts(7, "endividamento"),
     "eu": ts(10, "Eu"), "advogado": ts(10, "advogado"), "recuperacao": ts(10, "Recuperação"), "segue": ts(10, "segue")}
XF = 0.45   # fusão entre clipes

def vid(i, src, a, b, ms=0.0, tr=0):
    return (f'<video id="{i}" class="clip artv" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-media-start="{ms:.2f}" '
            f'data-track-index="{tr}" muted playsinline src="assets/art/{src}.mp4"></video>')
VIDEOS = "\n".join([
    vid("v-temp", "rj_fazenda_tempestade", 0, C["mapa"] + XF, 0, 0),
    vid("v-mapa", "mapa", C["mapa"], C["mapa_fim"], 0, 1),
    vid("v-millet", "rj_millet", C["millet"], C["barras"] + XF, 0, 2),
    vid("v-barras", "barras", C["barras"], C["vendaval"] + XF, 0, 3),
    vid("v-vend", "mp_vendaval", C["vendaval"], C["queda"] + XF, 0, 4),
    vid("v-queda", "queda", C["queda"], C["abre"] + XF, 0, 5),
    vid("v-abre", "rj_fazenda_abre", C["abre"], C["cartela"] + XF + 0.2, 0, 6),
])
caps = "\n".join(f'<div class="cap" id="cap{i}"><span>{b["txt"]}</span></div>' for i, b in enumerate(leg))
SRC_SERASA = "FONTE: SERASA EXPERIAN, LEVANTAMENTOS DE 12/8 E 19/10/2026"
def ov(i, a, b, html, cls="", tr=10):
    return f'<div id="{i}" class="clip ov {cls}" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="{tr}">{html}</div>'
OVS = "\n".join([
    ov("o-5", M["cinco"] - 0.1, C["mapa"] + 0.2, '<div class="mao big">5 por dia</div>', "topo", 10),
    ov("o-922", M["n922"] - 0.2, C["mapa"] + 0.2, '<div class="mao num" id="n922">0</div><div class="mao sub">pedidos no 1º semestre de 2026</div>', "meio", 11),
    ov("o-src1", FI[2]["inicio"], C["mapa"] + 0.2, SRC_SERASA, "rod", 12),
    ov("o-cred1", 0.6, FI[2]["inicio"] - 0.05, 'PINTURA FEITA EM CÓDIGO, À MANEIRA DE VAN GOGH, “A COLHEITA” (1888)', "cred", 13),
    ov("o-src2", C["mapa"] + 0.8, C["mapa_fim"], 'FONTE: SERASA EXPERIAN, 19/10/2026 · 2º TRIMESTRE DE 2026 · MAPA: NATURAL EARTH', "rod", 14),
    ov("o-cred2", C["millet"] + 0.4, C["barras"], 'PINTURA FEITA EM CÓDIGO, À MANEIRA DE MILLET, “O SEMEADOR” (1850)', "cred", 15),
    ov("o-src3", C["barras"] + 0.4, C["vendaval"], 'FONTE: SERASA EXPERIAN, 19/10/2026 · “SEM PROPRIEDADES” PODE INCLUIR ARRENDATÁRIOS', "rod", 16),
    ov("o-mot", C["vendaval"], C["queda"],
       '<div class="mot" id="m1">custos elevados</div><div class="mot" id="m2">crédito mais seletivo</div><div class="mot" id="m3">endividamento</div>', "motivos", 17),
    ov("o-src4", C["vendaval"] + 0.4, C["queda"], SRC_SERASA + ' · PINTURA À MANEIRA DE VAN GOGH', "rod", 18),
    ov("o-src5", C["queda"] + 0.4, C["abre"], 'FONTE: SERASA EXPERIAN, 19/10/2026 (565 PEDIDOS NO 2º TRI DE 2025; 448 NO 2º TRI DE 2026)', "rod", 19),
    ov("o-cred3", C["abre"] + 0.4, C["cartela"], 'PINTURA FEITA EM CÓDIGO, À MANEIRA DE VAN GOGH', "cred", 20),
])
CART = """<div id="ct-luz"></div><div id="ct-nome">Dr. Pelicioni</div><div id="ct-fil"></div><div id="ct-prof">ADVOGADO</div>
<div id="ct-tese">antes da recuperação judicial, existe renegociação</div><div id="ct-direct">Dúvida sobre o seu contrato? Direct aberto.</div>
<div id="ct-fontes">Fontes: Serasa Experian (levantamentos de 12/8 e 19/10/2026) · mapa: Natural Earth · pinturas feitas em código, à maneira de Van Gogh e Millet · trilha original</div>"""
SFX = [("paper", C["mapa"] + 0.1, .45, .8), ("paper", C["barras"] + 0.05, .4, .8), ("whoosh", C["vendaval"] - 0.2, .25, 1.0),
       ("paper", C["queda"] + 0.05, .4, .8), ("boom", C["cartela"] + 0.1, .22, 1.5)]
sfx = "\n".join(f'<audio id="sx{n}" class="clip" data-start="{s:.3f}" data-duration="{d}" data-track-index="{40 + n}" data-volume="{v}" src="assets/audio/sfx/{f}.mp3"></audio>' for n, (f, s, v, d) in enumerate(SFX))

HTML = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Cinco por dia · recuperação judicial no agro</title>
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
.mao{{font-family:'Caveat';font-weight:700;color:#f6efd8;text-shadow:0 3px 14px rgba(10,14,30,.75),0 0 2px rgba(10,14,30,.9)}}
.topo .big{{position:absolute;left:0;right:0;top:90px;text-align:center;font-size:168px;line-height:1;transform:rotate(-3deg)}}
.meio .num{{position:absolute;left:0;right:0;top:300px;text-align:center;font-size:190px;line-height:1}}
.meio .sub{{position:absolute;left:0;right:0;top:500px;text-align:center;font-size:56px}}
.rod{{top:auto;bottom:0;height:auto;padding:14px 40px 18px;background:rgba(243,234,216,.92);color:#3a3026;font:500 21px/1.35 'IBM Plex Mono';letter-spacing:.03em}}
.cred{{top:auto;bottom:0;height:auto;padding:14px 40px 18px;background:linear-gradient(0deg,rgba(10,14,26,.75),rgba(10,14,26,0));color:#f6efd8;font:500 21px/1.35 'IBM Plex Mono';letter-spacing:.04em}}
.motivos .mot{{position:absolute;left:70px;font:900 64px/1 'Inter';color:#f6efd8;background:rgba(14,22,48,.78);padding:14px 24px;border-left:8px solid #8cc25e;opacity:0}}
#m1{{top:170px}} #m2{{top:300px}} #m3{{top:430px}}
#cartela{{background:#0b1424}}
#ct-luz{{position:absolute;inset:0;background:radial-gradient(ellipse 60% 45% at 50% 42%,#1a2a24 0%,#0b141c 60%,#070c12 100%)}}
#ct-nome{{position:absolute;left:0;right:0;top:250px;text-align:center;font:500 112px 'Newsreader';color:#eee8dc}}
#ct-fil{{position:absolute;left:380px;width:320px;top:400px;height:3px;background:#8cc25e}}
#ct-prof{{position:absolute;left:0;right:0;top:428px;text-align:center;font:500 30px 'IBM Plex Mono';letter-spacing:.32em;color:#c9ced6}}
#ct-tese{{position:absolute;left:60px;right:60px;top:520px;text-align:center;font:italic 600 40px 'Newsreader';color:#d8d4c8}}
#ct-direct{{position:absolute;left:0;right:0;top:610px;text-align:center;font:900 34px 'Inter';color:#f0c24b}}
#ct-fontes{{position:absolute;left:70px;right:70px;bottom:28px;text-align:center;font:500 22px/1.4 'IBM Plex Mono';color:#9aa3b3}}
#caps{{position:absolute;inset:0;z-index:30}}
.cap{{position:absolute;left:0;right:0;top:860px;display:flex;justify-content:center;opacity:0}}
.cap span{{display:inline-block;background:#f0c24b;color:#000;font:900 54px/1.12 'Inter';padding:6px 18px 8px;border-radius:6px;box-shadow:0 6px 18px rgba(0,0,0,.25)}}
.grain{{position:absolute;inset:0;width:1080px;height:1080px;mix-blend-mode:multiply;opacity:.10;pointer-events:none;z-index:25}}
</style></head><body>
<div id="root" data-composition-id="video" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1080">
{VIDEOS}
{OVS}
<div id="cartela" class="clip ov" data-start="{C['cartela']:.3f}" data-duration="{TOTAL - C['cartela']:.3f}" data-track-index="21">{CART}</div>
<div id="caps" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="22">{caps}</div>
<img id="grain" class="grain clip" data-start="0" data-duration="{TOTAL}" data-track-index="23" src="assets/img/paper-grain.png">
<audio id="voz" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="24" data-volume="1" src="assets/audio/narracao.wav"></audio>
<audio id="trilha" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="25" data-volume="0.16" data-fade-in="0.6" data-fade-out="2.0" src="assets/audio/modao.mp3"></audio>
{sfx}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
const C = {json.dumps(C)}, M = {json.dumps(M)}, LEG = {json.dumps(leg, ensure_ascii=False)}, XF = {XF};
const enter = 'power3.out';
// câmeras lentas e fusões
tl.fromTo('#v-temp', {{ scale: 1.0 }}, {{ scale: 1.10, duration: C.mapa + XF, ease: 'none' }}, 0);
[['#v-mapa', C.mapa], ['#v-millet', C.millet], ['#v-barras', C.barras], ['#v-vend', C.vendaval], ['#v-queda', C.queda], ['#v-abre', C.abre]].forEach(([id, t0]) =>
  tl.fromTo(id, {{ opacity: 0 }}, {{ opacity: 1, duration: XF, ease: 'none' }}, t0));
tl.fromTo('#v-millet', {{ scale: 1.0 }}, {{ scale: 1.06, duration: C.barras - C.millet + XF, ease: 'none' }}, C.millet);
tl.fromTo('#v-vend', {{ scale: 1.0 }}, {{ scale: 1.08, duration: C.queda - C.vendaval + XF, ease: 'none' }}, C.vendaval);
tl.fromTo('#v-abre', {{ scale: 1.12 }}, {{ scale: 1.0, duration: C.cartela - C.abre + XF, ease: 'none' }}, C.abre);
// 5 por dia + contador
tl.fromTo('#o-5 .big', {{ opacity: 0, scale: 1.25 }}, {{ opacity: 1, scale: 1, duration: .45, ease: 'back.out(2)' }}, M.cinco - .05);
tl.to('#o-5 .big', {{ opacity: .0, duration: .4 }}, M.n922 - .5);
const cnt = {{ v: 0 }}; tl.fromTo('#o-922', {{ opacity: 0 }}, {{ opacity: 1, duration: .3 }}, M.n922 - .2);
tl.to(cnt, {{ v: 922, duration: 1.3, ease: 'power2.out', onUpdate: () => document.getElementById('n922').textContent = Math.round(cnt.v) }}, M.n922 - .15);
tl.fromTo('#o-922 .sub', {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: .5, ease: enter }}, M.semestre - .1);
// rodapés e créditos
document.querySelectorAll('.rod, .cred').forEach(el => tl.fromTo(el, {{ opacity: 0 }}, {{ opacity: 1, duration: .5 }}, +el.dataset.start + .05));
// motivos
[['#m1', M.custos], ['#m2', M.credito], ['#m3', M.endiv]].forEach(([id, t0]) => tl.fromTo(id, {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: .4, ease: enter }}, t0 - .05));
// cartela
tl.fromTo('#cartela', {{ opacity: 0 }}, {{ opacity: 1, duration: .5 }}, C.cartela);
tl.fromTo('#ct-nome', {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: .6, ease: enter }}, M.eu);
tl.fromTo('#ct-fil', {{ scaleX: 0 }}, {{ scaleX: 1, duration: .6, ease: enter }}, M.eu + .3);
tl.fromTo('#ct-prof', {{ opacity: 0 }}, {{ opacity: 1, duration: .4 }}, M.advogado);
tl.fromTo('#ct-tese', {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: .5, ease: enter }}, M.recuperacao);
tl.fromTo('#ct-direct', {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: .5, ease: enter }}, M.segue);
tl.fromTo('#ct-fontes', {{ opacity: 0 }}, {{ opacity: 1, duration: .6 }}, C.cartela + .8);
// legendas: sobem para o topo nos gráficos (para não cobrir os rótulos de baixo)
[[C.barras, C.vendaval], [C.queda, C.abre]].forEach(([a, b]) => {{ tl.set('#caps', {{ y: -846 }}, a); tl.set('#caps', {{ y: 0 }}, b); }});
LEG.forEach((b, i) => {{ tl.fromTo('#cap' + i, {{ opacity: 0, scale: .92 }}, {{ opacity: 1, scale: 1, duration: .12, ease: 'power2.out' }}, b.ini); tl.set('#cap' + i, {{ opacity: 0 }}, b.fim); }});
tl.to({{}}, {{ duration: {TOTAL} }}, 0);
window.__timelines = window.__timelines || {{}}; window.__timelines['video'] = tl;
</script></body></html>"""
(P / "index.html").write_text(HTML, encoding="utf-8"); (P / "hyperframes.json").write_text('{ "name": "rj5-cinco-por-dia" }\n')
print("ok", TOTAL, len(leg), "blocos", {k: round(v, 2) for k, v in C.items()})
