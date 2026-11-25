"""Gera hf/index.html: vídeo "O banco leiloa a sua fazenda sem juiz?" (alienação fiduciária, Lei 9.514/1997), 1080x1080, ~58 s.
Imagens reais do TikTok (colheita em formação, @miqueiasdoagro; colheitadeira, @hohljd) em moldura de react, com crédito e
"imagem ilustrativa"; óleo com espátula (Lemo-Opuscar, MIT) na fazenda com silos, de manhã e no fim de tarde; pinturas em
código à maneira de Pieter de Hooch, Willem Claesz. Heda e Camille Corot (huashu-art-motion). Cartões com o texto literal
da Lei 9.514/1997 (art. 26, § 1º, e art. 27, § 5º-A). Nenhuma imagem gerada por IA.
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
for fid in range(1, 10):
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
C = {"chave": FI[2]["inicio"] - .25, "react": FI[3]["inicio"] - .25, "cartorio": FI[4]["inicio"] - .25, "leilao": FI[5]["inicio"] - .25,
     "pior": FI[6]["inicio"] - .25, "porteira": FI[7]["inicio"] - .25, "fim": FI[8]["inicio"] - .3, "cartela": FI[9]["inicio"] - .35}
M = {"cartorio3": ts(3, "cartório"), "diz": ts(4, "diz"), "q15": ts(4, "15"), "dois": ts(5, "dois"), "segundo": ts(5, "segundo"), "metade": ts(5, "metade"),
     "pior": ts(6, "pior"), "recomprar": ts(7, "recomprar"),
     "eu": ts(9, "Eu"), "advogado": ts(9, "advogado"), "antes": ts(9, "Na"), "segue": ts(9, "segue")}
XF = 0.45
ORD = [("real_abertura", 0), ("fazenda_chave", 0), ("real_colheita_b", 0), ("lf_hooch", 0), ("lf_heda", 0), ("real_colheitadeira", 0), ("lf_corot", 0), ("fazenda_fim", 0)]
INI = [0, C["chave"], C["react"], C["cartorio"], C["leilao"], C["pior"], C["porteira"], C["fim"], C["cartela"]]
def vid(i, src, ms, a, b, tr):
    b = min(b, a + dur(src) - ms)
    return (f'<video id="{i}" class="clip artv" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-media-start="{ms}" '
            f'data-track-index="{tr}" muted playsinline src="assets/art/{src}.mp4"></video>')
VIDEOS = "\n".join(vid(f"v{k}", s, ms, INI[k], INI[k + 1] + XF + (.2 if k == 7 else 0), k) for k, (s, ms) in enumerate(ORD))
def ov(i, a, b, html, cls="", tr=10):
    return f'<div id="{i}" class="clip ov {cls}" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="{tr}">{html}</div>'
SRC_L = 'Lei 9.514/1997, com a redação da Lei 14.711/2023 · texto compilado publicado pelo Senado Federal'
CARD1 = (f'<div class="card" id="card1"><div class="cardsrc">{SRC_L}</div><div class="cardtxt">“Art. 26. […] § 1º […] o devedor e, se for o caso, o terceiro '
         'fiduciante serão intimados, a requerimento do fiduciário, <mark>pelo oficial do registro de imóveis</mark> competente, a satisfazer, <mark>no prazo de 15 (quinze) dias</mark>, '
         'a prestação vencida […]”</div></div>')
CARD2 = (f'<div class="card" id="card2"><div class="cardsrc">{SRC_L}</div><div class="cardtxt">“Art. 27. […] § 5º-A Se o produto do leilão não for suficiente para o '
         'pagamento integral do montante da dívida, das despesas e dos encargos […], <mark>o devedor continuará obrigado pelo pagamento do saldo remanescente</mark> […]”</div></div>')
REAL = lambda perfil: f'IMAGEM ILUSTRATIVA · IMAGENS: {perfil} · TIKTOK'
OVS = [
    ov("o-capa", 0, 2.5, '<div class="capa" id="capa"><div class="capa-chip">FAZENDA EM GARANTIA</div><div class="capa-big">O BANCO<br>LEILOA<br>SEM JUIZ?</div><div class="capa-sub">e você ainda pode ficar devendo</div></div>', "", 9),
    ov("o-src0", 0, C["chave"], REAL('@MIQUEIASDOAGRO'), "rod", 10),
    ov("o-flash", 0, 1.2, '<div id="flash"></div>', "", 8),
    ov("o-cred1", C["chave"] + .4, C["react"], 'PINTURA A ÓLEO COM ESPÁTULA, FEITA EM CÓDIGO', "cred", 11),
    ov("o-dr1", C["react"] + .1, C["cartorio"], '<div class="drtag" id="dr1">DR. PELICIONI</div>', "", 12),
    ov("o-src2", C["react"] + .3, C["cartorio"], REAL('@MIQUEIASDOAGRO'), "rod", 13),
    ov("o-cart", M["cartorio3"] - .1, C["cartorio"] + .2, '<div class="carimbo" id="ccart">cartório, não juiz</div>', "", 14),
    ov("o-card1", M["diz"] - .1, C["leilao"] + .1, CARD1, "", 15),
    ov("o-src3", C["cartorio"] + .4, C["leilao"], 'LEI 9.514/1997, ART. 26 · PINTURA À MANEIRA DE PIETER DE HOOCH', "rod", 16),
    ov("o-cont", M["dois"] - .15, C["pior"] + .2, '<div class="cont"><div class="cnum" id="n1">1º leilão</div><div class="cnum c10" id="n2">2º leilão</div>'
       '<div class="cnum c5" id="n50">50%<small>da avaliação, se o banco aceitar</small></div></div>', "", 17),
    ov("o-src4", C["leilao"] + .4, C["pior"], 'LEI 9.514/1997, ART. 27, § 2º · PINTURA À MANEIRA DE WILLEM CLAESZ. HEDA', "rod", 18),
    ov("o-dr2", C["pior"] + .1, C["porteira"], '<div class="drtag" id="dr2">DR. PELICIONI</div>', "", 19),
    ov("o-card2", M["pior"] - .1, C["porteira"] + .1, CARD2, "", 20),
    ov("o-src5", C["pior"] + .3, C["porteira"], REAL('@HOHLJD'), "rod", 21),
    ov("o-pref", M["recomprar"] - .15, C["fim"] + .2, '<div class="tag" id="t1">preferência até o 2º leilão</div>', "", 22),
    ov("o-src6", C["porteira"] + .4, C["fim"], 'LEI 9.514/1997, ART. 27, § 2º-B · PINTURA À MANEIRA DE CAMILLE COROT', "rod", 23),
    ov("o-cred9", C["fim"] + .3, C["cartela"], 'PINTURA A ÓLEO COM ESPÁTULA, FEITA EM CÓDIGO', "cred", 24),
]
CART = """<div id="ct-luz"></div><div id="ct-nome">Dr. Pelicioni</div><div id="ct-fil"></div><div id="ct-prof">ADVOGADO</div>
<div id="ct-tese">na alienação fiduciária, o prazo corre no cartório</div><div id="ct-direct">Dúvida? Direct aberto.</div>
<div id="ct-fontes">Fontes: Lei 9.514/1997, arts. 22, 26 e 27, com a redação da Lei 14.711/2023 (texto compilado publicado pelo Senado Federal) · imagens reais ilustrativas: @miqueiasdoagro e @hohljd (TikTok) · pinturas feitas em código: óleo com espátula (motor Lemo-Opuscar, MIT) e à maneira de Pieter de Hooch, Willem Claesz. Heda e Camille Corot · trilha original</div>"""
SFX = [("boom", 0.38, .5, 1.5), ("paper", M["diz"] - .1, .4, .8), ("whoosh", C["cartorio"] - .2, .22, 1.0), ("paper", M["pior"] - .1, .4, .8), ("boom", C["cartela"] + .1, .22, 1.5)]
sfx = "\n".join(f'<audio id="sx{n}" class="clip" data-start="{s:.3f}" data-duration="{d}" data-track-index="{40 + n}" data-volume="{v}" src="assets/audio/sfx/{f}.mp3"></audio>' for n, (f, s, v, d) in enumerate(SFX))
HTML = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>O banco leiloa a sua fazenda sem juiz? · alienação fiduciária</title>
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
for (let k = 1; k < 8; k++) tl.fromTo('#v' + k, {{ opacity: 0 }}, {{ opacity: 1, duration: XF, ease: 'none' }}, INI[k]);
[3, 4, 6].forEach(k => tl.fromTo('#v' + k, {{ scale: 1.0 }}, {{ scale: 1.08, duration: INI[k + 1] - INI[k] + XF, ease: 'none' }}, INI[k]));
document.querySelectorAll('.rod, .cred').forEach(el => tl.fromTo(el, {{ opacity: 0 }}, {{ opacity: 1, duration: .5 }}, +el.dataset.start + .05));
// capa: visível desde o quadro 0 e sai antes do número de abertura
tl.set('#capa', {{ opacity: 1 }}, 0); tl.to('#capa', {{ opacity: 0, y: -20, duration: .35, ease: 'power2.in' }}, 2.0);
tl.fromTo('#v0', {{ scale: 1.0 }}, {{ scale: 1.18, duration: INI[1] + XF, ease: 'none' }}, 0);
tl.to('#v0', {{ x: 14, y: -10, duration: .05, yoyo: true, repeat: 5, ease: 'none' }}, 0.4); tl.set('#v0', {{ x: 0, y: 0 }}, 0.71);
tl.fromTo('#capa', {{ scale: 1.0 }}, {{ scale: 1.06, duration: .08, yoyo: true, repeat: 1 }}, 0.4);
tl.fromTo('#flash', {{ opacity: 0 }}, {{ opacity: .55, duration: .05 }}, 0.4); tl.to('#flash', {{ opacity: 0, duration: .35 }}, 0.45);
// reações do editor, prova, leilões, saldo e preferência
['#dr1', '#dr2'].forEach(s => tl.fromTo(s, {{ opacity: 0, y: -10 }}, {{ opacity: 1, y: 0, duration: .3, ease: enter }}, +document.querySelector(s).parentElement.dataset.start + .05));
tl.fromTo('#ccart', {{ opacity: 0, scale: 1.6 }}, {{ opacity: 1, scale: 1, duration: .22, ease: 'power4.in' }}, M.cartorio3 - .05);
tl.fromTo('#card1', {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: .4, ease: enter }}, M.diz - .1);
tl.fromTo('#n1', {{ opacity: 0, scale: .9 }}, {{ opacity: 1, scale: 1, duration: .3, ease: enter }}, M.dois - .1);
tl.to('#n1', {{ opacity: 0, duration: .2 }}, M.segundo - .15);
tl.fromTo('#n2', {{ opacity: 0, scale: .9 }}, {{ opacity: 1, scale: 1, duration: .3, ease: enter }}, M.segundo - .1);
tl.to('#n2', {{ opacity: 0, duration: .2 }}, M.metade - .15);
tl.fromTo('#n50', {{ opacity: 0, scale: .9 }}, {{ opacity: 1, scale: 1, duration: .3, ease: enter }}, M.metade - .1);
tl.fromTo('#card2', {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: .4, ease: enter }}, M.pior - .1);
tl.fromTo('#t1', {{ opacity: 0, x: -24 }}, {{ opacity: 1, x: 0, duration: .35, ease: enter }}, M.recomprar - .1);
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
(P / "index.html").write_text(HTML, encoding="utf-8"); (P / "hyperframes.json").write_text('{ "name": "fazenda-leilao-sem-juiz" }\n')
print("ok", TOTAL, len(leg), "blocos", {k: round(v, 2) for k, v in C.items()})
