"""Gera hf/index.html: vídeo "A porta e o porteiro" (acordo Mercosul–UE + EUDR), 1080x1080, ~72 s.
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
C = {"boudin": FI[2]["inicio"] - .25, "graf": FI[3]["inicio"] - .25, "delft": FI[4]["inicio"] - .25, "post": FI[5]["inicio"] - .25,
     "corte": FI[6]["inicio"] - .25, "klee": FI[7]["inicio"] - .25, "fim": FI[9]["inicio"] - .25, "cartela": FI[10]["inicio"] - .35}
M = {"n367": ts(1, "367"), "mercosul": ts(2, "Mercosul"), "n148": ts(2, "14,8"), "trinta": ts(4, "30"), "lei": ts(4, "lei"),
     "soja": ts(5, "soja"), "cafe": ts(5, "café"), "carne": ts(5, "carne"), "d31": ts(5, "31"), "autorizado": ts(6, "autorizado"), "fora": ts(6, "fora"),
     "rasoe": ts(7, "RAZOE"), "gov": ts(7, "gov"), "car": ts(8, "CAR"), "desm": ts(8, "desmatamento"), "emb": ts(8, "embargos"), "areas": ts(8, "áreas"),
     "eu": ts(10, "Eu"), "advogado": ts(10, "advogado"), "antes": ts(10, "Antes"), "segue": ts(10, "segue")}
XF = 0.45
ORD = ["colmeias", "eu_boudin", "grafico", "eu_delft", "eu_post", "eu_post_corte", "eu_klee", "colmeias_fim"]
INI = [0, C["boudin"], C["graf"], C["delft"], C["post"], C["corte"], C["klee"], C["fim"], C["cartela"]]
def vid(i, src, a, b, tr):
    return (f'<video id="{i}" class="clip artv" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-media-start="0" '
            f'data-track-index="{tr}" muted playsinline src="assets/art/{src}.mp4"></video>')
VIDEOS = "\n".join(vid(f"v{k}", s, INI[k], INI[k + 1] + XF + (.2 if k == 7 else 0), k) for k, s in enumerate(ORD))
def ov(i, a, b, html, cls="", tr=10):
    return f'<div id="{i}" class="clip ov {cls}" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="{tr}">{html}</div>'
CARD1 = ('<div class="card" id="card1"><div class="cardsrc">gov.br · Ministério da Agricultura e Pecuária · notícia de 1º/11/2026</div>'
         '<div class="cardtxt">“O Acordo de Parceria entre o Mercosul e a União Europeia completa, neste domingo (1º), seis meses de aplicação provisória. '
         'Nos primeiros cinco meses de vigência, as exportações do agronegócio brasileiro para o bloco europeu <mark>cresceram 14,8% em valor</mark>, '
         'na comparação com o mesmo período de 2025, e alcançaram US$ 12,21 bilhões […]”</div></div>')
CARD2 = ('<div class="card" id="card2"><div class="cardsrc">gov.br · Ministério da Agricultura e Pecuária · notícia de 10/11/2026</div>'
         '<div class="cardtxt">“[…] o produtor pode acessar <mark>gratuitamente</mark> a plataforma por meio de sua conta gov.br e solicitar uma análise socioambiental de sua propriedade. […] '
         'Os resultados são consolidados no <mark>Relatório de Análise Socioambiental para Operações de Exportação (RASOE)</mark>, documento oficial brasileiro previsto na '
         'Resolução CEC nº 17, de 8 de setembro de 2026 […]”</div></div>')
OVS = [
    ov("o-cred0", .6, C["boudin"], 'PINTURA A ÓLEO COM ESPÁTULA, FEITA EM CÓDIGO', "cred", 10),
    ov("o-367", M["n367"] - .15, C["boudin"] + .2, '<div class="mao big" id="b367">+367%</div><div class="mao sub" id="s367">mel e produtos de abelha · maio a setembro de 2026</div>', "", 11),
    ov("o-card1", M["mercosul"] - .1, M["mercosul"] + 3.2, CARD1, "", 12),
    ov("o-148", M["n148"] - .15, C["graf"] + .2, '<div class="mao big" id="b148">+14,8%</div>', "", 13),
    ov("o-src1", C["boudin"] + .4, C["graf"], 'FONTE: MAPA/AGROSTAT, 1º/11/2026 · PINTURA À MANEIRA DE BOUDIN', "rod", 14),
    ov("o-src2", C["graf"] + .4, C["delft"], 'FONTE: MAPA/AGROSTAT, 1º/11/2026 · MAIO A SETEMBRO DE 2026 × 2025, EM VALOR', "rod", 15),
    ov("o-30", M["trinta"] - .1, C["post"] + .2, '<div class="carimbo" id="c30">30 de dezembro</div><div class="mao sub2" id="s30">lei europeia contra o desmatamento (EUDR)</div>', "", 16),
    ov("o-src3", C["delft"] + .4, C["post"], 'COMISSÃO EUROPEIA: EUDR VALE PARA GRANDES E MÉDIAS EMPRESAS A PARTIR DE 30/12/2026 · À MANEIRA DE VERMEER', "rod", 17),
    ov("o-prod", M["soja"] - .1, C["corte"] + .2, '<div class="tag" id="t1">soja</div><div class="tag" id="t2">café</div><div class="tag" id="t3">carne</div><div class="mao big2" id="d31">31/12/2020</div>', "", 18),
    ov("o-src4", C["post"] + .4, C["corte"], 'COMISSÃO EUROPEIA: SEM DESMATAMENTO APÓS 31/12/2020 E PRODUÇÃO LEGAL NO PAÍS DE ORIGEM · À MANEIRA DE FRANS POST', "rod", 19),
    ov("o-aut", M["autorizado"] - .2, C["klee"] + .2, '<div class="mao lbl6" id="l6">desmate autorizado, depois de 31/12/2020</div><div class="carimbo fora" id="c6">fora</div>', "", 20),
    ov("o-src5", C["corte"] + .4, C["klee"], 'A REGRA EUROPEIA NÃO ABRE EXCEÇÃO PARA DESMATE AUTORIZADO APÓS A DATA DE CORTE · À MANEIRA DE FRANS POST', "rod", 21),
    ov("o-card2", M["rasoe"] - .4, M["rasoe"] + 3.0, CARD2, "", 22),
    ov("o-gov", M["gov"] - .2, C["fim"] + .2, '<div class="tag tag2" id="tg">gratuito · conta gov.br</div>', "", 23),
    ov("o-lay", M["car"] - .1, C["fim"] + .2, '<div class="lay" id="y1" style="left:200px;top:230px;color:#fff8e0">CAR</div><div class="lay" id="y2" style="left:330px;top:500px;color:#ffb08a">desmatamento</div>'
       '<div class="lay" id="y3" style="left:620px;top:300px;color:#ff8a7a">embargo</div><div class="lay" id="y4" style="left:740px;top:930px;color:#9ff0a8">área protegida</div>', "", 24),
    ov("o-src6", C["klee"] + .4, C["fim"], 'FONTE: MAPA, NOTÍCIA DE 10/11/2026 · RESOLUÇÃO CEC Nº 17/2026 · CAMADAS ILUSTRATIVAS · À MANEIRA DE PAUL KLEE', "rod", 25),
    ov("o-cred9", C["fim"] + .3, C["cartela"], 'PINTURA A ÓLEO COM ESPÁTULA, FEITA EM CÓDIGO', "cred", 26),
]
CART = """<div id="ct-luz"></div><div id="ct-nome">Dr. Pelicioni</div><div id="ct-fil"></div><div id="ct-prof">ADVOGADO</div>
<div id="ct-tese">antes de dezembro, confira o seu CAR</div><div id="ct-direct">Dúvida? Direct aberto.</div>
<div id="ct-fontes">Fontes: MAPA (notícias de 1º/11 e 10/11/2026; Agrostat) · Comissão Europeia, página do EUDR · Resolução CEC nº 17/2026 · pinturas feitas em código: óleo com espátula (motor Lemo-Opuscar, MIT) e à maneira de Boudin, Vermeer, Frans Post e Paul Klee · trilha original</div>"""
SFX = [("paper", M["mercosul"] - .1, .4, .8), ("whoosh", C["delft"] - .2, .22, 1.0), ("paper", M["rasoe"] - .4, .4, .8), ("boom", C["cartela"] + .1, .22, 1.5)]
sfx = "\n".join(f'<audio id="sx{n}" class="clip" data-start="{s:.3f}" data-duration="{d}" data-track-index="{40 + n}" data-volume="{v}" src="assets/audio/sfx/{f}.mp3"></audio>' for n, (f, s, v, d) in enumerate(SFX))
HTML = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>A porta e o porteiro · Mercosul–UE e EUDR</title>
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
.card{{position:absolute;left:70px;right:70px;top:90px;background:#fffdf6;padding:22px 26px 20px;box-shadow:0 18px 40px rgba(0,0,0,.45);transform:rotate(-1deg);opacity:0}}
.cardsrc{{font:500 17px/1.3 'IBM Plex Mono';color:#4a6a3a;letter-spacing:.02em;margin-bottom:12px;border-bottom:1px solid #d8d0bc;padding-bottom:10px}}
.cardtxt{{font:500 27px/1.5 'Newsreader';color:#1e1a16}} .cardtxt mark{{background:#ffd84a;padding:0 3px}}
.big{{position:absolute;left:0;right:0;top:110px;text-align:center;font-size:190px;line-height:1;transform:rotate(-3deg)}}
.big2{{position:absolute;left:0;right:0;top:330px;text-align:center;font-size:140px;line-height:1}}
.sub{{position:absolute;left:0;right:0;top:320px;text-align:center;font-size:46px}}
.sub2{{position:absolute;left:0;right:0;top:300px;text-align:center;font-size:48px}}
.carimbo{{position:absolute;left:300px;top:120px;padding:10px 26px;border:7px solid #c0281a;color:#c0281a;font:900 54px 'Inter';text-transform:uppercase;letter-spacing:.04em;transform:rotate(-7deg);background:rgba(255,248,236,.88);opacity:0}}
.carimbo.fora{{left:640px;top:420px;font-size:64px}}
.tag{{position:absolute;top:150px;font:900 54px/1 'Inter';color:#fff6dc;background:rgba(30,40,60,.82);padding:14px 22px;border-left:8px solid #8cc25e;opacity:0}}
#t1{{left:70px}} #t2{{left:330px}} #t3{{left:580px}}
.tag2{{left:70px;top:150px;border-left-color:#f0c24b}}
.lbl6{{position:absolute;left:330px;top:440px;font-size:44px;opacity:0}}
.lay{{position:absolute;font:900 38px 'Inter';text-shadow:0 2px 10px rgba(0,0,0,.85);opacity:0}}
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
for (let k = 1; k < 8; k++) tl.fromTo('#v' + k, {{ opacity: 0 }}, {{ opacity: 1, duration: XF, ease: 'none' }}, INI[k]);
[1, 3, 4, 5].forEach(k => tl.fromTo('#v' + k, {{ scale: 1.0 }}, {{ scale: 1.08, duration: INI[k + 1] - INI[k] + XF, ease: 'none' }}, INI[k]));
document.querySelectorAll('.rod, .cred').forEach(el => tl.fromTo(el, {{ opacity: 0 }}, {{ opacity: 1, duration: .5 }}, +el.dataset.start + .05));
// número de abertura e cartão 1
tl.fromTo('#b367', {{ opacity: 0, scale: 1.3 }}, {{ opacity: 1, scale: 1, duration: .45, ease: 'back.out(2)' }}, M.n367 - .1);
tl.fromTo('#s367', {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: .4 }}, M.n367 + .3);
tl.fromTo('#card1', {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: .4, ease: enter }}, M.mercosul - .1);
tl.to('#card1', {{ opacity: 0, duration: .35 }}, M.mercosul + 2.8);
tl.fromTo('#b148', {{ opacity: 0, scale: 1.3 }}, {{ opacity: 1, scale: 1, duration: .45, ease: 'back.out(2)' }}, M.n148 - .1);
// porteiro: carimbo da data
tl.fromTo('#c30', {{ opacity: 0, scale: 1.6 }}, {{ opacity: 1, scale: 1, duration: .22, ease: 'power4.in' }}, M.trinta - .05);
tl.fromTo('#s30', {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: .45, ease: enter }}, M.lei - .1);
// produtos e data de corte
[['#t1', M.soja], ['#t2', M.cafe], ['#t3', M.carne]].forEach(([id, t0]) => tl.fromTo(id, {{ opacity: 0, x: -24 }}, {{ opacity: 1, x: 0, duration: .35, ease: enter }}, t0 - .1));
tl.fromTo('#d31', {{ opacity: 0, scale: .9 }}, {{ opacity: 1, scale: 1, duration: .45, ease: enter }}, M.d31 - .1);
// corte autorizado
tl.fromTo('#l6', {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: .45, ease: enter }}, M.autorizado - .1);
tl.fromTo('#c6', {{ opacity: 0, scale: 1.6 }}, {{ opacity: 1, scale: 1, duration: .22, ease: 'power4.in' }}, M.fora - .05);
// RASOE e camadas
tl.fromTo('#card2', {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: .4, ease: enter }}, M.rasoe - .4);
tl.to('#card2', {{ opacity: 0, duration: .35 }}, M.rasoe + 2.6);
tl.fromTo('#tg', {{ opacity: 0, x: -24 }}, {{ opacity: 1, x: 0, duration: .35, ease: enter }}, M.gov - .1);
tl.to('#tg', {{ opacity: 0, duration: .3 }}, M.car - .3);
[['#y1', M.car], ['#y2', M.desm], ['#y3', M.emb], ['#y4', M.areas]].forEach(([id, t0]) => tl.fromTo(id, {{ opacity: 0, y: 8 }}, {{ opacity: 1, y: 0, duration: .35 }}, t0 + .1));
// cartela
tl.fromTo('#cartela', {{ opacity: 0 }}, {{ opacity: 1, duration: .5 }}, C.cartela);
tl.fromTo('#ct-nome', {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: .6, ease: enter }}, M.eu);
tl.fromTo('#ct-fil', {{ scaleX: 0 }}, {{ scaleX: 1, duration: .6, ease: enter }}, M.eu + .3);
tl.fromTo('#ct-prof', {{ opacity: 0 }}, {{ opacity: 1, duration: .4 }}, M.advogado);
tl.fromTo('#ct-tese', {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: .5, ease: enter }}, M.enquanto);
tl.fromTo('#ct-direct', {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: .5, ease: enter }}, M.segue);
tl.fromTo('#ct-fontes', {{ opacity: 0 }}, {{ opacity: 1, duration: .6 }}, C.cartela + .8);
// legendas: sobem para o topo no mapa (embaixo fica o Sul do mapa)

LEG.forEach((b, i) => {{ tl.fromTo('#cap' + i, {{ opacity: 0, scale: .92 }}, {{ opacity: 1, scale: 1, duration: .12, ease: 'power2.out' }}, b.ini); tl.set('#cap' + i, {{ opacity: 0 }}, b.fim); }});
tl.to({{}}, {{ duration: {TOTAL} }}, 0);
window.__timelines = window.__timelines || {{}}; window.__timelines['video'] = tl;
</script></body></html>"""
(P / "index.html").write_text(HTML, encoding="utf-8"); (P / "hyperframes.json").write_text('{ "name": "eudr-porta-porteiro" }\n')
print("ok", TOTAL, len(leg), "blocos", {k: round(v, 2) for k, v in C.items()})
