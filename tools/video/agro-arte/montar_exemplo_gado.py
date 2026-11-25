"""Gera hf/index.html: vídeo "O gado do vizinho comeu a sua roça" (art. 936 e cerca divisória), 1080x1080, ~56 s.
Cenas: óleo com espátula (motor impasto do Lemo-Opuscar, MIT) na roça, de dia e no fim de tarde; mapa da divisa em aquarela
(p5.brush), usado em duas partes; pinturas em código à maneira de Paulus Potter, Théodore Rousseau e Jean-François Millet
(huashu-art-motion). Dois cartões com o texto literal do Código Civil (art. 936 e art. 1.297, § 3º). Nenhuma imagem gerada por IA.
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
C = {"potter": FI[3]["inicio"] - .25, "mapa1": FI[5]["inicio"] - .25, "rousseau": FI[6]["inicio"] - .25, "mapa2": FI[7]["inicio"] - .25,
     "millet": FI[8]["inicio"] - .25, "fim": FI[9]["inicio"] - .3, "cartela": FI[10]["inicio"] - .35}
M = {"dono": ts(3, "dono"), "codigo": ts(4, "Código"), "forca": ts(6, "força"), "tela": ts(8, "tela"),
     "eu": ts(10, "Eu"), "advogado": ts(10, "advogado"), "antes": ts(10, "Na"), "segue": ts(10, "segue")}
XF = 0.45
ORD = [("roca", 0), ("gd_potter", 0), ("mapa", 0), ("gd_rousseau", 0), ("mapa", 6.2), ("gd_millet", 0), ("roca_fim", 0)]
INI = [0, C["potter"], C["mapa1"], C["rousseau"], C["mapa2"], C["millet"], C["fim"], C["cartela"]]
def vid(i, src, ms, a, b, tr):
    b = min(b, a + dur(src) - ms)
    return (f'<video id="{i}" class="clip artv" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-media-start="{ms}" '
            f'data-track-index="{tr}" muted playsinline src="assets/art/{src}.mp4"></video>')
VIDEOS = "\n".join(vid(f"v{k}", s, ms, INI[k], INI[k + 1] + XF + (.2 if k == 6 else 0), k) for k, (s, ms) in enumerate(ORD))
def ov(i, a, b, html, cls="", tr=10):
    return f'<div id="{i}" class="clip ov {cls}" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="{tr}">{html}</div>'
SRC_CC = 'Código Civil (Lei 10.406/2002) · texto publicado pelo Senado Federal'
CARD1 = (f'<div class="card" id="card1"><div class="cardsrc">{SRC_CC}</div><div class="cardtxt">“Art. 936. O dono, ou detentor, do animal ressarcirá o dano por este '
         'causado, <mark>se não provar culpa da vítima ou força maior</mark>.”</div></div>')
CARD2 = (f'<div class="card" id="card2"><div class="cardsrc">{SRC_CC}</div><div class="cardtxt">“Art. 1.297. […] § 3º A construção de tapumes especiais para impedir a '
         'passagem de animais de pequeno porte, ou para outro fim, <mark>pode ser exigida de quem provocou a necessidade deles</mark>, pelo proprietário, que não está '
         'obrigado a concorrer para as despesas.”</div></div>')
OVS = [
    ov("o-capa", 0, 1.5, '<div class="capa" id="capa"><div class="capa-chip">VIZINHO E DIVISA</div><div class="capa-big">GADO INVADIU.<br>QUEM PAGA?</div><div class="capa-sub">e quando a conta é sua</div></div>', "", 9),
    ov("o-cred0", 1.6, C["potter"], 'PINTURA A ÓLEO COM ESPÁTULA, FEITA EM CÓDIGO', "cred", 10),
    ov("o-dono", M["dono"] - .15, M["codigo"] - .1, '<div class="tag" id="t1">o dono do animal paga</div>', "", 11),
    ov("o-card1", M["codigo"] - .1, C["mapa1"] + .1, CARD1, "", 12),
    ov("o-src1", C["potter"] + .4, C["mapa1"], 'CÓDIGO CIVIL, ART. 936 · PINTURA À MANEIRA DE PAULUS POTTER', "rod", 13),
    ov("o-src2", C["mapa1"] + .4, C["rousseau"], 'MAPA ILUSTRATIVO EM AQUARELA · EXEMPLOS HIPOTÉTICOS', "rod", 14),
    ov("o-forca", M["forca"] - .15, C["mapa2"] + .2, '<div class="carimbo" id="cforca">força maior</div>', "", 15),
    ov("o-src3", C["rousseau"] + .4, C["mapa2"], 'EXEMPLO HIPOTÉTICO · PINTURA À MANEIRA DE THÉODORE ROUSSEAU', "rod", 16),
    ov("o-src4", C["mapa2"] + .4, C["millet"], 'CÓDIGO CIVIL, ART. 1.297, § 1º: ATÉ PROVA EM CONTRÁRIO, CONFORME OS COSTUMES DA LOCALIDADE · MAPA ILUSTRATIVO', "rod", 17),
    ov("o-card2", M["tela"] - .1, C["fim"] + .1, CARD2, "", 18),
    ov("o-src5", C["millet"] + .4, C["fim"], 'CÓDIGO CIVIL, ART. 1.297, § 3º · PINTURA À MANEIRA DE JEAN-FRANÇOIS MILLET', "rod", 19),
    ov("o-cred9", C["fim"] + .3, C["cartela"], 'PINTURA A ÓLEO COM ESPÁTULA, FEITA EM CÓDIGO', "cred", 20),
]
CART = """<div id="ct-luz"></div><div id="ct-nome">Dr. Pelicioni</div><div id="ct-fil"></div><div id="ct-prof">ADVOGADO</div>
<div id="ct-tese">na divisa, cerca bem cuidada é prejuízo evitado</div><div id="ct-direct">Dúvida? Direct aberto.</div>
<div id="ct-fontes">Fontes: Código Civil (Lei 10.406/2002), arts. 936 e 1.297, texto publicado pelo Senado Federal · exemplos hipotéticos · pinturas feitas em código: óleo com espátula (motor Lemo-Opuscar, MIT) e à maneira de Paulus Potter, Théodore Rousseau e Jean-François Millet · mapa ilustrativo · trilha original</div>"""
SFX = [("paper", M["codigo"] - .1, .4, .8), ("whoosh", C["mapa1"] - .2, .22, 1.0), ("paper", M["tela"] - .1, .4, .8), ("boom", C["cartela"] + .1, .22, 1.5)]
sfx = "\n".join(f'<audio id="sx{n}" class="clip" data-start="{s:.3f}" data-duration="{d}" data-track-index="{40 + n}" data-volume="{v}" src="assets/audio/sfx/{f}.mp3"></audio>' for n, (f, s, v, d) in enumerate(SFX))
HTML = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>O gado do vizinho comeu a sua roça · divisa</title>
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
.capa-big{{font-size:112px !important;line-height:1.02 !important}}
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
#ct-fontes{{position:absolute;left:60px;right:60px;bottom:26px;text-align:center;font:500 19px/1.4 'IBM Plex Mono';color:#9aa3b3}}
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
for (let k = 1; k < 7; k++) tl.fromTo('#v' + k, {{ opacity: 0 }}, {{ opacity: 1, duration: XF, ease: 'none' }}, INI[k]);
[1, 3, 5].forEach(k => tl.fromTo('#v' + k, {{ scale: 1.0 }}, {{ scale: 1.08, duration: INI[k + 1] - INI[k] + XF, ease: 'none' }}, INI[k]));
document.querySelectorAll('.rod, .cred').forEach(el => tl.fromTo(el, {{ opacity: 0 }}, {{ opacity: 1, duration: .5 }}, +el.dataset.start + .05));
// capa: visível desde o quadro 0 e sai antes do número de abertura
tl.set('#capa', {{ opacity: 1 }}, 0); tl.to('#capa', {{ opacity: 0, y: -20, duration: .35, ease: 'power2.in' }}, 1.1);
// regra, prova, força maior e a tela
tl.fromTo('#t1', {{ opacity: 0, x: -24 }}, {{ opacity: 1, x: 0, duration: .35, ease: enter }}, M.dono - .1);
tl.fromTo('#card1', {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: .4, ease: enter }}, M.codigo - .1);
tl.fromTo('#cforca', {{ opacity: 0, scale: 1.6 }}, {{ opacity: 1, scale: 1, duration: .22, ease: 'power4.in' }}, M.forca - .05);
tl.fromTo('#card2', {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: .4, ease: enter }}, M.tela - .1);
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
(P / "index.html").write_text(HTML, encoding="utf-8"); (P / "hyperframes.json").write_text('{ "name": "gado-vizinho-roca" }\n')
print("ok", TOTAL, len(leg), "blocos", {k: round(v, 2) for k, v in C.items()})
