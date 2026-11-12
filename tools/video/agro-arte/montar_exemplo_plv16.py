"""Gera hf/index.html: vídeo "O relógio zerou" (PLV 16/2026, dívidas rurais), 1080x1080, ~65 s.
Cenas: pintura a óleo com espátula (motor impasto do Lemo-Opuscar, MIT) no relógio, na folhinha e no mapa;
pinturas em código à maneira de Monet, Chardin, Vermeer e Ruisdael (modelo antigo, huashu-art-motion) nas demais.
Duas inserções curtas de documento (autógrafo do PLV 16/2026). Legenda amarela. Nenhuma imagem gerada por IA.
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
C = {"cong": FI[2]["inicio"] - .25, "fol": FI[3]["inicio"] - .3, "medas": FI[4]["inicio"] - .25, "chardin": FI[5]["inicio"] - .25,
     "mapa": FI[6]["inicio"] - .3, "vermeer": FI[7]["inicio"] - .25, "ruis": FI[8]["inicio"] - .25, "fim": FI[9]["inicio"] - .3, "cartela": FI[10]["inicio"] - .35}
M = {"aprovou": ts(2, "aprovou"), "sancao": ts(2, "sanção"), "n120": ts(3, "120"), "regul": ts(3, "regulamentação"),
     "duas": ts(4, "duas"), "y2019": ts(4, "2019"), "y2025": ts(4, "2025"), "p30": ts(4, "30"),
     "clima": ts(5, "clima"), "queda": ts(5, "Queda"), "conta": ts(5, "conta"),
     "seis": ts(7, "6"), "dois": ts(7, "dois"),
     "paliativo": ts(8, "paliativo"), "nao": ts(8, "não"),
     "eu": ts(10, "Eu"), "advogado": ts(10, "advogado"), "enquanto": ts(10, "Enquanto"), "segue": ts(10, "segue")}
XF = 0.45
ORD = ["relogio", "plv_congresso", "folhinha", "plv_medas", "plv_chardin", "mapa", "plv_vermeer", "plv_ruisdael", "fim"]
INI = [0, C["cong"], C["fol"], C["medas"], C["chardin"], C["mapa"], C["vermeer"], C["ruis"], C["fim"], C["cartela"]]
def vid(i, src, a, b, tr):
    return (f'<video id="{i}" class="clip artv" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-media-start="0" '
            f'data-track-index="{tr}" muted playsinline src="assets/art/{src}.mp4"></video>')
VIDEOS = "\n".join(vid(f"v{k}", s, INI[k], INI[k + 1] + XF + (.2 if k == 8 else 0), k) for k, s in enumerate(ORD))

def ov(i, a, b, html, cls="", tr=10):
    return f'<div id="{i}" class="clip ov {cls}" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="{tr}">{html}</div>'
MEDAS_X = [520, 660, 800, 960, 1130, 1270, 1400]; MEDAS_Y = [600, 640, 690, 760, 690, 640, 600]
anos = "".join(f'<div class="ano" id="a{k}" style="left:{x - 420 - 60}px;top:{y + 18}px">{2019 + k}</div>' for k, (x, y) in enumerate(zip(MEDAS_X, MEDAS_Y)))
OVS = [
    ov("o-cred0", .6, C["cong"], 'PINTURA A ÓLEO COM ESPÁTULA, FEITA EM CÓDIGO', "cred", 10),
    ov("o-doc1", M["aprovou"] - .1, M["aprovou"] + 2.4, '<div class="card" id="card1"><img src="assets/img/doc1.png"><div class="cardleg">Texto aprovado · PLV 16/2026 · 11/11/2026</div></div>', "", 11),
    ov("o-src1", C["cong"] + .4, C["fol"], 'FONTE: AGÊNCIA SENADO, 11/11/2026 · PINTURA À MANEIRA DE MONET, SÉRIE “O PARLAMENTO” (1900–1904)', "rod", 12),
    ov("o-120", M["n120"] - .1, C["medas"], '<div class="mao n120" id="n120">120 dias</div><div class="carimbo" id="carimbo">depois da regulamentação</div>', "", 13),
    ov("o-src2", C["fol"] + .4, C["medas"], 'PLV 16/2026, ART. 1º, § 4º, IV · O TEXTO AINDA DEPENDE DE SANÇÃO', "rod", 14),
    ov("o-anos", M["y2019"] - .2, C["chardin"], anos + '<div class="mao safras" id="safras">2 safras ou mais</div><div class="mao menos30" id="menos30">−30% da renda esperada</div>', "", 15),
    ov("o-src3", C["medas"] + .4, C["chardin"], 'PLV 16/2026, ART. 1º, § 1º · PINTURA À MANEIRA DE MONET, SÉRIE “MEDAS” (1890–1891)', "rod", 16),
    ov("o-tags", M["clima"] - .1, C["mapa"], '<div class="tag" id="tg1">clima</div><div class="tag tag2" id="tg2">+ preço de venda</div>', "", 17),
    ov("o-doc2", M["queda"] - .05, M["queda"] + 2.5, '<div class="card card2" id="card2"><div class="docwrap"><img src="assets/img/doc2.png"><i class="hl" style="left:655px;top:227px;width:593px"></i><i class="hl" style="left:28px;top:284px;width:1200px"></i></div><div class="cardleg">PLV 16/2026, art. 1º, § 2º</div></div>', "", 18),
    ov("o-src4", C["chardin"] + .4, C["mapa"], 'PLV 16/2026, ART. 1º, § 2º · PINTURA À MANEIRA DE CHARDIN', "rod", 19),
    ov("o-maplbl", C["mapa"] + 2.6, C["vermeer"], '<div class="mao maplbl">perda mínima exigida</div>', "", 20),
    ov("o-src5", C["mapa"] + .4, C["vermeer"], 'ÁREAS DA SUDAM, SUDENE E SUDECO, APROXIMADAS POR ESTADO (A SUDENE INCLUI PARTE DE MG E ES) · ART. 1º, § 13 · MAPA: NATURAL EARTH', "rod", 21),
    ov("o-juros", M["seis"] - .2, C["ruis"], '<div class="mao juros" id="juros">6% a 12% ao ano</div><div class="mao carencia" id="carencia">2 anos pagando só juros</div>', "", 22),
    ov("o-src6", C["vermeer"] + .4, C["ruis"], 'PLV 16/2026, ART. 1º, § 4º · NA PERDA MAIS GRAVE, DE 5% A 11% · PINTURA À MANEIRA DE VERMEER', "rod", 23),
    ov("o-cit", M["paliativo"] - .5, C["fim"], '<div class="cit" id="c1">“é só um paliativo”<small>Jaime Bagattoli (PL-RO)</small></div><div class="cit" id="c2">“Não é a solução definitiva.”<small>Tereza Cristina (PP-MS)</small></div>', "", 24),
    ov("o-src7", C["ruis"] + .4, C["fim"], 'FONTE: AGÊNCIA SENADO, 11/11/2026 · PINTURA À MANEIRA DE RUISDAEL', "rod", 25),
    ov("o-cred9", C["fim"] + .4, C["cartela"], 'PINTURA A ÓLEO COM ESPÁTULA, FEITA EM CÓDIGO', "cred", 26),
]
CART = """<div id="ct-luz"></div><div id="ct-nome">Dr. Pelicioni</div><div id="ct-fil"></div><div id="ct-prof">ADVOGADO</div>
<div id="ct-tese">enquanto a lei não sai, guarde os laudos e os contratos</div><div id="ct-direct">Dúvida sobre o seu contrato? Direct aberto.</div>
<div id="ct-fontes">Fontes: PLV 16/2026 (texto aprovado em 11/11/2026; depende de sanção) e Agência Senado (11/11/2026) · pinturas feitas em código: óleo com espátula (motor Lemo-Opuscar, MIT) e à maneira de Monet, Chardin, Vermeer e Ruisdael · mapa: Natural Earth · trilha original</div>"""
SFX = [("paper", M["aprovou"] - .05, .4, .8), ("paper", M["queda"], .4, .8), ("whoosh", C["mapa"] - .2, .22, 1.0), ("boom", C["cartela"] + .1, .22, 1.5)]
sfx = "\n".join(f'<audio id="sx{n}" class="clip" data-start="{s:.3f}" data-duration="{d}" data-track-index="{40 + n}" data-volume="{v}" src="assets/audio/sfx/{f}.mp3"></audio>' for n, (f, s, v, d) in enumerate(SFX))

HTML = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>O relógio zerou · dívidas rurais</title>
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
.card{{position:absolute;left:600px;top:110px;width:420px;background:#fffdf6;padding:12px 12px 10px;box-shadow:0 18px 40px rgba(0,0,0,.45);transform:rotate(2deg);opacity:0}}
.card img{{display:block;width:100%}} .cardleg{{font:500 17px/1.3 'IBM Plex Mono';color:#4a4036;margin-top:8px}}
.card2{{left:60px;top:90px;width:960px;transform:rotate(-1.2deg)}}
.docwrap{{position:relative;width:1264px;transform:scale(.7405);transform-origin:0 0;height:336px;margin-bottom:-87px}}
.docwrap img{{width:1264px}} .hl{{position:absolute;height:38px;background:rgba(255,214,0,.5);mix-blend-mode:multiply;transform-origin:0 50%}}
.n120{{position:absolute;left:0;right:0;top:120px;text-align:center;font-size:150px;line-height:1;opacity:0}}
.carimbo{{position:absolute;left:250px;top:300px;padding:10px 26px;border:7px solid #c0281a;color:#c0281a;font:900 40px 'Inter';text-transform:uppercase;letter-spacing:.04em;transform:rotate(-7deg);background:rgba(255,248,236,.85);opacity:0}}
.ano{{position:absolute;width:120px;text-align:center;font:900 30px 'Inter';color:#fff6dc;text-shadow:0 2px 10px rgba(20,10,40,.9);opacity:0}}
.safras{{position:absolute;left:0;right:0;top:110px;text-align:center;font-size:96px;opacity:0}}
.menos30{{position:absolute;left:0;right:0;top:220px;text-align:center;font-size:84px;color:#ffe08a;opacity:0}}
.tag{{position:absolute;left:70px;top:150px;font:900 58px/1 'Inter';color:#fff6dc;background:rgba(30,40,60,.82);padding:14px 24px;border-left:8px solid #8cc25e;opacity:0}}
.tag2{{top:270px;border-left-color:#f0c24b}}
.maplbl{{position:absolute;left:700px;top:205px;font-size:44px;color:#2b211a;text-shadow:none;transform:rotate(-3deg)}}
.juros{{position:absolute;left:0;right:0;top:90px;text-align:center;font-size:120px;line-height:1;opacity:0}}
.carencia{{position:absolute;left:0;right:0;top:230px;text-align:center;font-size:80px;color:#ffe08a;opacity:0}}
.cit{{position:absolute;left:70px;right:70px;font:italic 600 62px/1.1 'Newsreader';color:#fff6dc;text-shadow:0 3px 16px rgba(0,0,0,.85);opacity:0}}
.cit small{{display:block;font:500 24px 'IBM Plex Mono';font-style:normal;letter-spacing:.04em;margin-top:10px;color:#e8e0cc}}
#c1{{top:120px}} #c2{{top:330px}}
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
<audio id="trilha" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="30" data-volume="0.15" data-fade-in="0.6" data-fade-out="2.0" src="assets/audio/trilha.mp3"></audio>
{sfx}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
const C = {json.dumps(C)}, M = {json.dumps(M)}, LEG = {json.dumps(leg, ensure_ascii=False)}, XF = {XF}, INI = {json.dumps(INI)};
const enter = 'power3.out';
// fusões e câmeras lentas (as pinturas do modelo antigo ganham zoom; as do Opuscar já têm câmera própria)
for (let k = 1; k < 9; k++) tl.fromTo('#v' + k, {{ opacity: 0 }}, {{ opacity: 1, duration: XF, ease: 'none' }}, INI[k]);
[1, 3, 4, 6, 7].forEach(k => tl.fromTo('#v' + k, {{ scale: 1.0 }}, {{ scale: 1.08, duration: INI[k + 1] - INI[k] + XF, ease: 'none' }}, INI[k]));
document.querySelectorAll('.rod, .cred').forEach(el => tl.fromTo(el, {{ opacity: 0 }}, {{ opacity: 1, duration: .5 }}, +el.dataset.start + .05));
// documento 1
tl.fromTo('#card1', {{ opacity: 0, y: 30, rotation: 6 }}, {{ opacity: 1, y: 0, rotation: 2, duration: .45, ease: enter }}, M.aprovou - .1);
tl.to('#card1', {{ opacity: 0, y: -20, duration: .35 }}, M.aprovou + 2.0);
// 120 dias + carimbo
tl.fromTo('#n120', {{ opacity: 0, scale: 1.2 }}, {{ opacity: 1, scale: 1, duration: .4, ease: 'back.out(2)' }}, M.n120 - .1);
tl.fromTo('#carimbo', {{ opacity: 0, scale: 1.6 }}, {{ opacity: 1, scale: 1, duration: .22, ease: 'power4.in' }}, M.regul - .05);
// anos das medas
for (let k = 0; k < 7; k++) tl.fromTo('#a' + k, {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: .3 }}, M.y2019 - .1 + k * (M.y2025 - M.y2019 + .2) / 7);
tl.fromTo('#safras', {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: .45, ease: enter }}, M.y2019 - .2);
tl.fromTo('#menos30', {{ opacity: 0, scale: .9 }}, {{ opacity: 1, scale: 1, duration: .4, ease: enter }}, M.p30 - .1);
// clima + preço; documento 2 com grifo
tl.fromTo('#tg1', {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: .35, ease: enter }}, M.clima - .1);
tl.fromTo('#tg2', {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: .35, ease: enter }}, M.queda);
tl.to('#o-tags', {{ opacity: 0, duration: .2 }}, M.queda + .2); tl.to('#o-tags', {{ opacity: 1, duration: .3 }}, M.queda + 2.6);
tl.fromTo('#card2', {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: .4, ease: enter }}, M.queda - .05);
tl.fromTo('.hl', {{ scaleX: 0 }}, {{ scaleX: 1, duration: .5, stagger: .4, ease: 'power2.out' }}, M.queda + .4);
tl.to('#card2', {{ opacity: 0, duration: .35 }}, M.queda + 2.15);
// juros
tl.fromTo('#juros', {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: .45, ease: enter }}, M.seis - .2);
tl.fromTo('#carencia', {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: .45, ease: enter }}, M.dois - .1);
// citações
tl.fromTo('#c1', {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: .5, ease: enter }}, M.paliativo - .5);
tl.fromTo('#c2', {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: .5, ease: enter }}, M.nao - .4);
// cartela
tl.fromTo('#cartela', {{ opacity: 0 }}, {{ opacity: 1, duration: .5 }}, C.cartela);
tl.fromTo('#ct-nome', {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: .6, ease: enter }}, M.eu);
tl.fromTo('#ct-fil', {{ scaleX: 0 }}, {{ scaleX: 1, duration: .6, ease: enter }}, M.eu + .3);
tl.fromTo('#ct-prof', {{ opacity: 0 }}, {{ opacity: 1, duration: .4 }}, M.advogado);
tl.fromTo('#ct-tese', {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: .5, ease: enter }}, M.enquanto);
tl.fromTo('#ct-direct', {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: .5, ease: enter }}, M.segue);
tl.fromTo('#ct-fontes', {{ opacity: 0 }}, {{ opacity: 1, duration: .6 }}, C.cartela + .8);
// legendas: sobem para o topo no mapa (embaixo fica o Sul do mapa)
tl.set('#caps', {{ y: -800 }}, C.mapa); tl.set('#caps', {{ y: 0 }}, C.vermeer);
LEG.forEach((b, i) => {{ tl.fromTo('#cap' + i, {{ opacity: 0, scale: .92 }}, {{ opacity: 1, scale: 1, duration: .12, ease: 'power2.out' }}, b.ini); tl.set('#cap' + i, {{ opacity: 0 }}, b.fim); }});
tl.to({{}}, {{ duration: {TOTAL} }}, 0);
window.__timelines = window.__timelines || {{}}; window.__timelines['video'] = tl;
</script></body></html>"""
(P / "index.html").write_text(HTML, encoding="utf-8"); (P / "hyperframes.json").write_text('{ "name": "plv16-relogio-zerado" }\n')
print("ok", TOTAL, len(leg), "blocos", {k: round(v, 2) for k, v in C.items()})
