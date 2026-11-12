"""Gera hf/index.html: vídeo completo (v3, imagens à maneira de obras de arte, pintadas em código) "O prazo é quinta, a MP vence quarta" (1080x1080, 30 fps, ~61 s).
Linguagem "Arquivo Aberto": foto real em 2.5D, prints oficiais (BCB e Congresso) com realce no instante da fala,
tipografia cinética, legenda em caixa amarela. Sem TV da segunda voz (pedido do editor): a reação toca sobre o
próprio documento ou sobre o dado. Nenhuma imagem gerada por IA.  Uso: python3 montar2.py
"""
import json, re
from pathlib import Path
P = Path(__file__).resolve().parent / "hf"
T = json.load(open(P / "assets/data/tempos.json", encoding="utf-8"))
DOC = json.load(open(P / "assets/docs/res5330.json", encoding="utf-8"))
CN = json.load(open(P / "assets/docs/cn-andamento.json", encoding="utf-8"))
FALAS = {f["id"]: f for f in json.load(open(P.parent / "falas.json", encoding="utf-8"))}
TOTAL = T["total"]
FI = {f["fala"]: f for f in T["falas"]}

def pw(fala):
    return [w for w in T["palavras"] if w["fala"] == fala]

def ts(fala, k):
    return pw(fala)[k]["s"]

# ---------- legendas: texto do roteiro, tempos da transcrição ----------
blocos = []
for fid in range(1, 12):
    toks = FALAS[fid]["texto"].split()
    ws = pw(fid)
    if fid == 3:  # transcrição separou "Pera aí"; o roteiro diz "Peraí."
        ws = [ws[0], ws[2], ws[3]]
    assert len(toks) == len(ws), (fid, toks, [w["w"] for w in ws])
    atual = []
    for tok, w in zip(toks, ws):
        atual.append((tok, w))
        if len(atual) == 3 or re.search(r"[.,:?!…]$", tok):
            blocos.append(atual); atual = []
    if atual: blocos.append(atual)
leg = []
for i, b in enumerate(blocos):
    ini = b[0][1]["s"]
    prox = blocos[i + 1][0][1]["s"] if i + 1 < len(blocos) else TOTAL
    fim = min(prox, b[-1][1]["e"] + 0.45)
    leg.append({"txt": " ".join(t for t, _ in b), "ini": round(ini, 3), "fim": round(fim, 3)})

# ---------- cortes ----------
C = {}
C["doc1"] = FI[2]["inicio"] - 0.35          # folha do BCB sobe sobre a foto
C["cal"] = FI[4]["inicio"] - 0.12           # corte seco para o calendário
C["arte"] = FI[5]["inicio"] - 0.30          # pinturas: seca, enchente, granizo, geada, vendaval, preço
C["doc2"] = FI[6]["inicio"] - 0.30          # folha do BCB (§ 3º, laudo)
C["cn"] = FI[7]["inicio"] - 0.30            # andamento da MP no Congresso
C["doc3"] = FI[8]["inicio"] - 0.25          # juros (§ 4º, II)
C["datas"] = FI[9]["inicio"] - 0.12         # as duas datas
C["foto2"] = FI[10]["inicio"] - 0.15        # volta à propriedade
C["cartela"] = FI[11]["inicio"] - 0.30
M = {
    "quinta": ts(1, 10), "resolucao": ts(2, 2), "perdeu": ts(2, 7), "trinta": ts(2, 8), "duas": ts(2, 12),
    "ate3": ts(3, 2), "quinta3": ts(3, 3),
    "mas": ts(4, 2), "doze": ts(4, 5), "oito": ts(4, 8), "dois": ts(4, 12),
    "seca": ts(5, 2), "enchente": ts(5, 3), "granizo": ts(5, 4), "geada": ts(5, 5), "vendaval": ts(5, 6), "e5": ts(5, 7), "preco": ts(5, 12),
    "laudo": ts(6, 1), "habilitado": ts(6, 5),
    "medida": ts(7, 13), "perde": ts(7, 19), "amanha": ts(7, 25), "onze": ts(7, 26),
    "seis": ts(8, 4), "a8": ts(8, 5), "doze8": ts(8, 6),
    "entao": ts(9, 0), "camara": ts(10, 1), "hoje": ts(10, 4), "sera": ts(10, 5),
    "eu": ts(11, 0), "advogado": ts(11, 4), "aqui": ts(11, 5), "segue": ts(11, 16),
}
DR = DOC["rects"]
DW = DOC["largura"]

def hl(rs, cls):
    return "".join(f'<div class="hl {cls}" style="left:{r["x"]-6:.0f}px;top:{r["y"]-4:.0f}px;width:{r["w"]+12:.0f}px;height:{r["h"]+8:.0f}px"></div>' for r in rs)

H_BCB = {
    "h30": "no mínimo, 30% (trinta por cento)", "hsaf": "perdas em duas ou mais safras",
    "hpraz": "prazo para contratação: até 12 de novembro de 2026",
    "hsec": "secas ou estiagens", "hinu": "inundações", "hgra": "chuvas de granizo", "hgea": "geadas",
    "hven": "vendaval", "hpre": "redução dos preços", "hlau": "laudo emitido por profissional habilitado",
    "h6": "6% a.a. (seis por cento ao ano)", "h9": "9% a.a. (nove por cento ao ano)", "h12": "12% a.a. (doze por cento ao ano)",
}

def folha_bcb(sid, chaves):
    return f'<div class="cam" id="{sid}-cam" style="width:{DW}px"><div class="sheet" style="width:{DW}px"><img src="assets/docs/res5330.png" style="width:{DW}px">' + \
        "".join(hl(DR[H_BCB[k]], f"{sid}-{k}") for k in chaves) + "</div></div>"

CNR = CN["rects"]["Data final após prorrogação: 11/11/2026"]
CNW = CN["largura"]

cal = ['<div class="dow">' + "".join(f"<span>{d}</span>" for d in "DSTQQSS") + "</div>", '<div class="grid">']
for d in range(1, 31):
    cal.append(f'<div class="day" id="d{d}"><span>{d}</span></div>')
cal.append("</div>")
CAL = "\n".join(cal)

leg_html = "\n".join(f'<div class="cap" id="cap{i}"><span>{b["txt"]}</span></div>' for i, b in enumerate(leg))
DUR = {"paper": 0.8, "stamp": 0.68, "whoosh": 1.0, "boom": 1.5}
SFX = [("whoosh", C["doc1"] - .2, .3), ("paper", C["doc1"] + .1, .5), ("stamp", M["resolucao"] + .05, .4),
       ("stamp", M["doze"] + .1, .5), ("boom", M["oito"] - .05, .2),
       ("whoosh", C["arte"] - .2, .3), ("paper", C["doc2"] + .1, .5),
       ("whoosh", C["cn"] - .2, .3), ("paper", C["cn"] + .1, .5), ("stamp", M["perde"] + .05, .4),
       ("paper", C["doc3"] + .05, .45), ("stamp", M["camara"] + .05, .4), ("boom", C["cartela"] + .1, .28)]
sfx_html = "\n".join(f'<audio id="sx{n}" class="clip" data-start="{s:.3f}" data-duration="{DUR[f]}" data-track-index="{20+n}" data-volume="{v}" src="assets/audio/sfx/{f}.mp3"></audio>'
                     for n, (f, s, v) in enumerate(SFX))

def scene(sid, a, b, track, inner, extra=""):
    return f'<div id="{sid}" class="scene clip" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="{track}" {extra}>{inner}</div>'

FOTO = """<div class="full grad-top"></div><div class="full grad-bot"></div>
  <div class="cred mono">PINTURA FEITA EM CÓDIGO, À MANEIRA DE<br>VAN GOGH, “A COLHEITA” (1888)</div>"""

A_HTML = FOTO.format(p="a") + """
  <div id="a-title">
    <div id="a-kick"><i></i><span>DÍVIDA RURAL · MP 1.376</span></div>
    <div class="mask"><div id="a-h">Até <em>quinta.</em></div></div>
    <div class="mask"><div id="a-date">12 DE NOVEMBRO DE 2026</div></div>
  </div>"""
B1 = folha_bcb("b1", ["h30", "hsaf", "hpraz"]) + """
  <div class="seal" id="b1-seal">BRASÍLIA · 23/7/2026</div>
  <div class="src mono" id="b1-src1">FONTE: RES. CMN 5.330/2026, ART. 1º, § 1º · BCB.GOV.BR</div>
  <div class="src mono" id="b1-src2">FONTE: RES. CMN 5.330/2026, ART. 1º, § 4º, IV · BCB.GOV.BR</div>"""
D_HTML = f"""<div id="d-in" class="full">
    <div id="d-head"><b>Novembro</b><span>2026</span></div>
    <div id="d-cal">{CAL}</div>
    <svg id="ring" width="1080" height="1080"><ellipse id="ring-e" fill="none" stroke="#C23B22" stroke-width="5"/><line id="ring-l" stroke="#C23B22" stroke-width="3"/></svg>
    <div id="d-tag">PRAZO NOS BANCOS</div>
    <div class="stat" id="st8" style="top:626px"><b id="n8">0</b><div>anos pra pagar<small>até oito anos de prazo de reembolso</small></div></div>
    <div class="stat" id="st2" style="top:796px"><b id="n2">0</b><div>anos sem pagar o principal<small>1ª parcela do principal 2 anos após a contratação</small></div></div>
  </div>
  <div id="d-src" class="mono">FONTE: RES. CMN 5.330/2026, ART. 1º, § 4º, III E IV</div>
  <img class="grain" src="assets/img/paper-grain.png" style="opacity:.10">"""
B2 = folha_bcb("b2", ["hlau"]) + """
  <div class="src mono" id="b2-src2">FONTE: RES. CMN 5.330/2026, ART. 1º, § 3º · BCB.GOV.BR</div>"""
CN_HTML = f"""<div class="cam" id="cn-cam" style="width:{CNW}px"><div class="sheet" style="width:{CNW}px"><img src="assets/docs/cn-andamento.png" style="width:{CNW}px">{hl(CNR, "cn-h")}</div></div>
  <div class="seal" id="cn-seal">CONGRESSO NACIONAL · 8/9/2026</div>
  <div class="src mono">FONTE: CONGRESSO NACIONAL, MPV 1.376/2026, TRAMITAÇÃO</div>"""
B3 = folha_bcb("b3", ["h6", "h9", "h12"]) + """
  <div class="src mono">FONTE: RES. CMN 5.330/2026, ART. 1º, § 4º, II · BCB.GOV.BR</div>"""
DATAS = """<div class="col" id="col1"><div class="dd">11/11</div><div class="wd">QUARTA</div><div class="lb">a MP perde a validade</div></div>
  <div class="vbar" id="vbar"></div>
  <div class="col" id="col2"><div class="dd red">12/11</div><div class="wd">QUINTA</div><div class="lb">fim do prazo nos bancos</div></div>
  <div class="src2 mono">FONTES: CONGRESSO NACIONAL (MPV 1.376/2026) · RES. CMN 5.330/2026, § 4º, IV</div>
  <img class="grain" src="assets/img/paper-grain.png" style="opacity:.10">"""
F2 = FOTO.format(p="f") + """
  <div class="seal" id="f-seal">CÂMARA DOS DEPUTADOS · 10/11/2026</div>
  <div class="srcf mono">FONTE: CÂMARA DOS DEPUTADOS, MPV 1376/2026, TRAMITAÇÃO</div>"""
CART = """<div class="full" id="ct-luz"></div>
  <div id="ct-nome">Dr. Pelicioni</div><div id="ct-fil"></div><div id="ct-prof">ADVOGADO</div>
  <div id="ct-tese">o que muda no crédito rural, explicado com a fonte</div>
  <div id="ct-direct">Dúvida sobre o seu contrato? Direct aberto.</div>
  <div id="ct-fontes">Fontes: Res. CMN 5.330/2026 (bcb.gov.br) · MPV 1.376/2026 (Congresso Nacional e Câmara dos Deputados) · pinturas feitas em código, à maneira de Van Gogh, Sisley, Monet e Pissarro</div>"""

ARTV = [("seca", "mp_seca", "arte", "enchente", "SECA", "À MANEIRA DE VAN GOGH"),
        ("enchente", "47_sisley", "enchente", "granizo", "ENCHENTE", "À MANEIRA DE SISLEY"),
        ("granizo", "mp_granizo", "granizo", "geada", "GRANIZO", "À MANEIRA DOS IMPRESSIONISTAS"),
        ("geada", "mp_geada", "geada", "vendaval", "GEADA", "À MANEIRA DE MONET"),
        ("vendaval", "mp_vendaval", "vendaval", "e5", "VENDAVAL", "À MANEIRA DE VAN GOGH"),
        ("preco", "46_pissarro", "e5", "doc2", "QUEDA DE PREÇO", "À MANEIRA DE PISSARRO")]
TT = {**M, **C}
def vid(i, src, a, b, ms=0.0, track=30):
    return (f'<video id="{i}" class="clip artv" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-media-start="{ms:.2f}" '
            f'data-track-index="{track}" muted playsinline src="assets/art/{src}.mp4"></video>')
VIDEOS = "\n".join([vid("v-alm1", "mp_fazenda", 0, C["doc1"] + 0.9, 0.0, 30), vid("v-alm2", "mp_fazenda", C["foto2"], C["cartela"] + 0.6, 2.2, 31)] +
                   [vid(f"v-{k}", src, TT[a] - (0.30 if k == "seca" else 0.04), TT[b] + (0.8 if b == "doc2" else -0.04), 0.2, 32 + n)
                    for n, (k, src, a, b, _, _) in enumerate(ARTV)])
ARTE = "".join(f'<div class="atag" id="tag-{k}"><b>{w}</b><span>{st}</span></div>' for k, _, _, _, w, st in ARTV) + \
    '<div class="src mono" id="arte-src">RES. CMN 5.330/2026, ART. 1º, § 2º · PINTURAS FEITAS EM CÓDIGO</div>'

CSS = f"""
@font-face{{font-family:'Inter';src:url(assets/fonts/inter-latin-900-normal.woff2) format('woff2');font-weight:900}}
@font-face{{font-family:'Newsreader';src:url(assets/fonts/newsreader-latin-500-normal.woff2) format('woff2');font-weight:500}}
@font-face{{font-family:'Newsreader';src:url(assets/fonts/newsreader-latin-600-italic.woff2) format('woff2');font-weight:600;font-style:italic}}
@font-face{{font-family:'IBM Plex Mono';src:url(assets/fonts/ibm-plex-mono-latin-500-normal.woff2) format('woff2');font-weight:500}}
@font-face{{font-family:'IBM Plex Sans Condensed';src:url(assets/fonts/ibm-plex-sans-condensed-latin-600-normal.woff2) format('woff2');font-weight:600}}
:root{{--paper:#EEE8DC;--ink:#13233F;--inkSoft:#3E4A5C;--accent:#C23B22;--yellow:#f0c24b;--desk:#16233a;--navy:#0b1424}}
*{{box-sizing:border-box;margin:0}}
html,body{{width:1080px;height:1080px;overflow:hidden;background:#000}}
#root{{position:relative;width:1080px;height:1080px;overflow:hidden;background:#000}}
.scene{{position:absolute;inset:0;overflow:hidden}}
.full{{position:absolute;inset:0}}
.mono{{font:500 24px 'IBM Plex Mono';letter-spacing:.06em}}
.mask{{overflow:hidden}}
.layer{{position:absolute;inset:0;transform-origin:50% 55%}}
.layer img{{position:absolute;left:0;top:0}}
.grad-top{{background:linear-gradient(180deg,rgba(8,14,26,.78) 0%,rgba(8,14,26,0) 46%)}}
.grad-bot{{background:linear-gradient(0deg,rgba(8,14,26,.65) 0%,rgba(8,14,26,0) 32%)}}
.cred{{position:absolute;left:72px;right:60px;bottom:40px;color:var(--paper);line-height:1.35}}
#a-title{{position:absolute;left:72px;top:70px;color:var(--paper)}}
#a-kick{{font:500 24px 'IBM Plex Mono';letter-spacing:.16em;display:flex;align-items:center;gap:16px}}
#a-kick i{{display:block;width:48px;height:3px;background:var(--accent);transform-origin:0 50%}}
#a-h{{font:500 128px/1.0 'Newsreader';letter-spacing:-.02em;margin-top:14px}}
#a-h em{{font-style:italic;font-weight:600;color:var(--yellow)}}
#a-date{{font:500 30px 'IBM Plex Mono';letter-spacing:.1em;margin-top:12px}}
.docscene{{background:var(--desk)}}
.cam{{position:absolute;left:0;top:0;transform-origin:0 0}}
.sheet{{position:relative;background:#fff;box-shadow:0 30px 80px rgba(0,0,0,.55)}}
.sheet img{{display:block}}
.hl{{position:absolute;background:var(--yellow);mix-blend-mode:multiply;transform-origin:0 50%;border-radius:4px;opacity:0}}
.seal{{position:absolute;right:56px;top:64px;border:3px solid var(--accent);color:var(--accent);background:rgba(238,232,220,.95);
  font:500 26px 'IBM Plex Mono';letter-spacing:.12em;padding:10px 18px;transform:rotate(-4deg);opacity:0}}
.src{{position:absolute;left:0;right:0;bottom:0;height:86px;background:rgba(10,18,32,.92);color:var(--paper);display:flex;align-items:center;padding:0 48px}}
.srcf{{position:absolute;left:72px;right:60px;bottom:118px;color:var(--paper);opacity:0}}
#d{{background:var(--paper)}}
#d-in{{transform-origin:50% 40%}}
#d-head{{position:absolute;left:72px;top:58px;display:flex;align-items:baseline;gap:22px}}
#d-head b{{font:500 64px 'Newsreader';color:var(--ink)}}
#d-head span{{font:500 24px 'IBM Plex Mono';letter-spacing:.14em;color:var(--inkSoft)}}
#d-cal{{position:absolute;left:72px;top:150px;width:936px}}
.dow{{display:grid;grid-template-columns:repeat(7,1fr);font:500 26px 'IBM Plex Mono';color:var(--inkSoft);padding-bottom:8px;border-bottom:1.5px solid rgba(19,35,63,.35)}}
.dow span{{padding-left:10px}}
.grid{{display:grid;grid-template-columns:repeat(7,1fr);grid-auto-rows:62px}}
.day{{position:relative;border-bottom:1px solid rgba(19,35,63,.12);font:500 30px 'Newsreader';color:var(--ink);padding:10px 0 0 10px}}
.day .fill{{position:absolute;inset:4px;background:var(--yellow);opacity:0;border-radius:6px;z-index:0}}
.day span{{position:relative;z-index:1}}
#ring{{position:absolute;left:0;top:0;pointer-events:none}}
#d-tag{{position:absolute;font:500 26px 'IBM Plex Mono';letter-spacing:.12em;color:var(--accent);opacity:0}}
.stat{{position:absolute;left:72px;display:flex;align-items:baseline;gap:26px;color:var(--ink);opacity:0}}
.stat b{{font:500 170px/1 'Newsreader';letter-spacing:-.03em;font-variant-numeric:tabular-nums lining-nums;width:150px;text-align:right}}
.stat div{{font:italic 600 52px/1.1 'Newsreader';color:var(--accent)}}
.stat small{{display:block;font:600 30px 'IBM Plex Sans Condensed';color:var(--inkSoft);font-style:normal;margin-top:4px}}
#d-src{{position:absolute;left:72px;bottom:44px;color:var(--inkSoft)}}
#datas{{background:var(--paper)}}
.col{{position:absolute;top:150px;width:420px;text-align:center;color:var(--ink)}}
#col1{{left:90px}} #col2{{left:570px}}
.dd{{font:500 170px/1 'Newsreader';letter-spacing:-.03em;font-variant-numeric:lining-nums}}
.dd.red{{color:var(--accent)}}
.wd{{font:500 28px 'IBM Plex Mono';letter-spacing:.2em;color:var(--inkSoft);margin-top:10px}}
.lb{{font:italic 600 40px/1.15 'Newsreader';margin-top:18px}}
.vbar{{position:absolute;left:539px;top:160px;width:2px;height:330px;background:var(--ink);opacity:.35;transform-origin:50% 0}}
.src2{{position:absolute;left:72px;right:60px;bottom:44px;color:var(--inkSoft);font-size:22px;line-height:1.35}}
#cartela{{background:var(--navy)}}
#ct-luz{{background:radial-gradient(ellipse 60% 45% at 50% 42%,#1a2232 0%,#0b111c 60%,#070c16 100%)}}
#ct-nome{{position:absolute;left:0;right:0;top:250px;text-align:center;font:500 112px 'Newsreader';color:var(--paper);letter-spacing:-.01em}}
#ct-fil{{position:absolute;left:380px;width:320px;top:400px;height:3px;background:var(--yellow)}}
#ct-prof{{position:absolute;left:0;right:0;top:428px;text-align:center;font:500 30px 'IBM Plex Mono';letter-spacing:.32em;color:#c9ced6}}
#ct-tese{{position:absolute;left:0;right:0;top:520px;text-align:center;font:italic 600 38px 'Newsreader';color:#d8d4c8}}
#ct-direct{{position:absolute;left:0;right:0;top:600px;text-align:center;font:900 34px 'Inter';color:var(--yellow)}}
#ct-fontes{{position:absolute;left:70px;right:70px;bottom:40px;text-align:center;font:500 22px/1.4 'IBM Plex Mono';color:#9aa3b3}}
#caps{{z-index:20}}
.cap{{position:absolute;left:0;right:0;top:528px;display:flex;justify-content:center;opacity:0}}
.cap span{{display:inline-block;background:var(--yellow);color:#000;font:900 54px/1.12 'Inter';padding:6px 18px 8px;border-radius:6px;letter-spacing:-.01em;box-shadow:0 6px 18px rgba(0,0,0,.25)}}
.artv{{position:absolute;left:0;top:0;width:1080px;height:1080px;object-fit:cover;transform-origin:50% 55%}}
#arte{{background:transparent}}
.atag{{position:absolute;left:56px;top:56px;opacity:0;background:rgba(10,18,32,.82);padding:14px 22px 12px;border-left:6px solid var(--yellow)}}
.atag b{{display:block;font:900 44px/1 'Inter';color:var(--paper);letter-spacing:.02em}}
.atag span{{display:block;font:500 24px 'IBM Plex Mono';color:#c9ced6;letter-spacing:.1em;margin-top:8px}}
.grain{{position:absolute;inset:0;width:1080px;height:1080px;mix-blend-mode:multiply;pointer-events:none;object-fit:cover}}
"""

HTML = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><title>MP 1.376 · o prazo é quinta</title>
<script src="assets/lib/gsap.min.js"></script>
<script src="assets/lib/CustomEase.min.js"></script>
<style>{CSS}</style></head><body>
<div id="root" data-composition-id="video" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1080">
{VIDEOS}
{scene("a", 0, C["doc1"] + 0.9, 0, A_HTML)}
{scene("b1", C["doc1"], C["cal"], 1, B1,)}
{scene("d", C["cal"], C["arte"] + 0.05, 2, D_HTML)}
{scene("arte", C["arte"], C["doc2"] + 0.8, 13, ARTE)}
{scene("b2", C["doc2"], C["cn"] + 0.9, 3, B2)}
{scene("cn", C["cn"], C["doc3"] + 0.6, 4, CN_HTML)}
{scene("b3", C["doc3"], C["datas"], 5, B3)}
{scene("datas", C["datas"], C["foto2"], 6, DATAS)}
{scene("f", C["foto2"], C["cartela"] + 0.6, 7, F2)}
{scene("cartela", C["cartela"], TOTAL, 8, CART)}
<div id="caps" class="scene clip" data-start="0" data-duration="{TOTAL}" data-track-index="9">
{leg_html}
</div>
<img id="grain" class="grain clip" data-start="0" data-duration="{TOTAL}" data-track-index="10" src="assets/img/paper-grain.png" style="opacity:.12;z-index:30">
<audio id="voz" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="11" data-volume="1" src="assets/audio/narracao.wav"></audio>
<audio id="trilha" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="12" data-volume="0.12" data-fade-out="1.5" src="assets/audio/trilha-longa.mp3"></audio>
{sfx_html}
</div>
<script>
document.fonts.ready.then(() => {{
  gsap.registerPlugin(CustomEase);
  const enter = CustomEase.create('enter', 'M0,0 C0.22,1 0.36,1 1,1');
  const cam = CustomEase.create('cam', 'M0,0 C0.65,0 0.35,1 1,1');
  const M = {json.dumps(M)}, C = {json.dumps(C)};
  const LEG = {json.dumps(leg, ensure_ascii=False)};
  const R = {json.dumps({k: DR[v] for k, v in H_BCB.items()})};
  R.tit = {json.dumps(DR["RESOLUÇÃO CMN Nº 5.330, DE 23 DE JULHO DE 2026"][0])};
  const CNR = {json.dumps(CNR)};
  const tl = gsap.timeline({{ paused: true }});
  const $ = s => document.querySelector(s);
  ['b1', 'b2', 'cn', 'b3'].forEach(id => $('#' + id).style.background = '#16233a');
  const view = (x, y, z, cy = 470) => ({{ x: 540 - x * z, y: cy - y * z, scale: z }});
  const DW = {DW}, CNW = {CNW};
  const mid = r => r[0].y + r[0].h / 2;
  const showHL = (sel, t, d = .45) => document.querySelectorAll(sel).forEach((h, i) => tl.fromTo(h, {{ scaleX: 0, opacity: .55 }}, {{ scaleX: 1, opacity: .55, duration: d, ease: enter }}, t + i * .25));
  const sheetIn = (id, t) => tl.fromTo('#' + id, {{ yPercent: 100 }}, {{ yPercent: 0, duration: .8, ease: cam }}, t);
  const sheetPush = (id, t) => tl.fromTo('#' + id, {{ xPercent: 100, rotation: -2.5, transformOrigin: '0% 100%' }}, {{ xPercent: 0, rotation: 0, duration: .8, ease: cam }}, t);

  // ---------- fotos 2.5D ----------
  tl.fromTo('#v-alm1', {{ scale: 1.0 }}, {{ scale: 1.12, duration: C.doc1 + .9, ease: 'none' }}, 0);
  tl.fromTo('#v-alm2', {{ scale: 1.16 }}, {{ scale: 1.0, duration: C.cartela + .6 - C.foto2, ease: 'none' }}, C.foto2);
  const ART = {json.dumps([k for k, *_ in ARTV])};
  const at = k => M[k === 'preco' ? 'e5' : k];
  ART.forEach((k, i) => {{
    tl.fromTo('#v-' + k, {{ scale: 1.04 }}, {{ scale: 1.12, duration: 1.6, ease: 'none' }}, at(k) - .05);
    tl.fromTo('#tag-' + k, {{ opacity: 0, x: -14 }}, {{ opacity: 1, x: 0, duration: .25, ease: enter }}, at(k) - .02);
    if (i < ART.length - 1) tl.set('#tag-' + k, {{ opacity: 0 }}, at(ART[i + 1]) - .04);
  }});
  tl.fromTo('#arte-src', {{ yPercent: 100 }}, {{ yPercent: 0, duration: .5, ease: enter }}, C.arte + .4);
  const W0 = 1170, H0 = 700, s0 = 1080 * 1.12 / H0;
  document.querySelectorAll('.layer img').forEach(im => {{ im.style.width = W0 * s0 + 'px'; im.style.height = H0 * s0 + 'px'; }});
  const ox = -(W0 * s0 - 1080) * 0.36, oy = -(H0 * s0 - 1080) / 2, F = [0.90, 0.96, 1.0];
  function foto(p, t0, t1, zA, zB, dxB) {{
    const c = {{ p: 0 }};
    const draw = () => {{ const z = zA + (zB - zA) * c.p, dx = dxB * c.p; F.forEach((f, i) => gsap.set(`#${{p}}-ly${{i}}`, {{ scale: 1 + (z - 1) * f, x: ox + dx * f, y: oy }})); }};
    tl.to(c, {{ p: 1, duration: t1 - t0, ease: 'none', onUpdate: draw }}, t0); draw();
  }}

  // ---------- A ----------
  tl.fromTo('#a .grad-top', {{ opacity: 0 }}, {{ opacity: 1, duration: .6, ease: enter }}, 0);
  tl.fromTo('#a-kick i', {{ scaleX: 0 }}, {{ scaleX: 1, duration: .6, ease: enter }}, .25);
  tl.fromTo('#a-kick span', {{ opacity: 0, x: -10 }}, {{ opacity: 1, x: 0, duration: .6, ease: enter }}, .3);
  tl.fromTo('#a-h', {{ yPercent: 105 }}, {{ yPercent: 0, duration: .85, ease: enter }}, M.quinta - .05);
  tl.fromTo('#a-date', {{ yPercent: 110 }}, {{ yPercent: 0, duration: .8, ease: enter }}, M.quinta + .2);
  tl.fromTo('#a .cred', {{ opacity: 0 }}, {{ opacity: 1, duration: .6 }}, .6);
  sheetIn('b1', C.doc1);

  // ---------- B1: § 1º, depois § 4º, IV (durante a reação "Peraí. Até quinta-feira?") ----------
  tl.set('#b1-cam', view(DW / 2, R.tit.y + 470 / .72 - 40, .72), C.doc1);
  tl.to('#b1-cam', {{ ...view(DW / 2, R.tit.y + 470 / .72 - 70, .72), duration: M.perdeu - C.doc1 - .4, ease: 'none' }}, C.doc1 + .8);
  tl.to('#b1-cam', {{ ...view(DW / 2, mid(R.hsaf), .72, 330), duration: 1.0, ease: cam }}, M.perdeu - .4);
  tl.to('#b1-cam', {{ ...view(DW / 2, mid(R.hsaf) + 6, .745, 330), duration: M.ate3 - M.perdeu - 1.2, ease: 'none' }}, M.perdeu + .6);
  tl.to('#b1-cam', {{ ...view(DW / 2, mid(R.hpraz), .74, 330), duration: .9, ease: cam }}, M.ate3 - .6);
  tl.fromTo('#b1-seal', {{ opacity: 0, scale: 1.4 }}, {{ opacity: 1, scale: 1, duration: .35, ease: 'power3.in' }}, M.resolucao);
  tl.fromTo('#b1-src1', {{ yPercent: 100 }}, {{ yPercent: 0, duration: .6, ease: enter }}, M.resolucao + .3);
  tl.to('#b1-src1', {{ yPercent: 100, duration: .3, ease: 'power2.in' }}, M.ate3 - .6);
  tl.fromTo('#b1-src2', {{ yPercent: 100 }}, {{ yPercent: 0, duration: .5, ease: enter }}, M.ate3 - .3);
  showHL('.b1-h30', M.trinta); showHL('.b1-hsaf', M.duas); showHL('.b1-hpraz', M.quinta3 - .15, .6);

  // ---------- D: calendário ----------
  tl.fromTo('#d-in', {{ scale: 1.04 }}, {{ scale: 1, duration: C.doc2 - C.cal, ease: 'none' }}, C.cal);
  tl.fromTo('#d-head', {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: .5, ease: enter }}, C.cal);
  tl.fromTo('#d-cal', {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: .6, ease: enter }}, C.cal + .1);
  ['#d10', '#d11', '#d12'].forEach((id, i) => {{
    const f = document.createElement('div'); f.className = 'fill'; $(id).prepend(f);
    tl.fromTo(f, {{ opacity: 0 }}, {{ opacity: i < 2 ? .35 : .85, duration: .3 }}, [C.cal + .42, M.mas, M.doze - .1][i]);
  }});
  const r12 = $('#d12').getBoundingClientRect(), rr = $('#root').getBoundingClientRect();
  const cx = r12.left - rr.left + 27, cy = r12.top - rr.top + 26;
  const el = $('#ring-e'); el.setAttribute('cx', cx); el.setAttribute('cy', cy); el.setAttribute('rx', 46); el.setAttribute('ry', 27);
  const L = 2 * Math.PI * Math.sqrt((46 * 46 + 27 * 27) / 2); el.setAttribute('stroke-dasharray', L);
  tl.fromTo(el, {{ attr: {{ 'stroke-dashoffset': L }} }}, {{ attr: {{ 'stroke-dashoffset': 0 }}, duration: .6, ease: enter }}, M.doze);
  const r29 = $('#d29').getBoundingClientRect(), yTag = r29.top - rr.top + 16, xl = cx + 44;
  const ln = $('#ring-l'); ln.setAttribute('x1', xl); ln.setAttribute('x2', xl); ln.setAttribute('y1', cy + 18); ln.setAttribute('y2', yTag + 4);
  const LL = yTag + 4 - (cy + 18); ln.setAttribute('stroke-dasharray', LL);
  tl.fromTo(ln, {{ attr: {{ 'stroke-dashoffset': LL }} }}, {{ attr: {{ 'stroke-dashoffset': 0 }}, duration: .35, ease: enter }}, M.doze + .35);
  gsap.set('#d-tag', {{ left: xl + 14, top: yTag - 4 }});
  tl.fromTo('#d-tag', {{ opacity: 0, y: -8 }}, {{ opacity: 1, y: 0, duration: .45, ease: enter }}, M.doze + .55);
  const n8 = {{ v: 0 }}, n2 = {{ v: 0 }};
  tl.fromTo('#st8', {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: .6, ease: enter }}, M.oito);
  tl.to(n8, {{ v: 8, duration: .9, ease: enter, onUpdate: () => $('#n8').textContent = Math.round(n8.v) }}, M.oito);
  tl.fromTo('#st2', {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: .6, ease: enter }}, M.dois);
  tl.to(n2, {{ v: 2, duration: .7, ease: enter, onUpdate: () => $('#n2').textContent = Math.round(n2.v) }}, M.dois);
  tl.fromTo('#d-src', {{ opacity: 0 }}, {{ opacity: 1, duration: .5 }}, M.oito + .3);

  // ---------- B2: § 3º (laudo) ----------
  sheetIn('b2', C.doc2);
  tl.set('#b2-cam', view(DW / 2, mid(R.hlau), .735, 330), C.doc2);
  tl.to('#b2-cam', {{ ...view(DW / 2, mid(R.hlau) + 4, .76, 330), duration: C.cn - C.doc2 + .6, ease: 'none' }}, C.doc2 + .6);
  tl.fromTo('#b2-src2', {{ yPercent: 100 }}, {{ yPercent: 0, duration: .5, ease: enter }}, C.doc2 + .5);
  showHL('.b2-hlau', M.laudo, .5);

  // ---------- CN: andamento da MP no Congresso ----------
  sheetPush('cn', C.cn);
  const yc = mid(CNR);
  tl.set('#cn-cam', view(CNW / 2, yc - 160, .56, 470), C.cn);
  tl.to('#cn-cam', {{ ...view(CNW / 2, yc - 60, .58, 400), duration: M.medida - C.cn - .3, ease: 'none' }}, C.cn + .8);
  tl.to('#cn-cam', {{ ...view(1139, yc, .76, 330), duration: 1.0, ease: cam }}, M.medida - .3);
  tl.to('#cn-cam', {{ ...view(1139, yc + 4, .77, 330), duration: C.doc3 - M.medida, ease: 'none' }}, M.medida + .7);
  tl.fromTo('#cn-seal', {{ opacity: 0, scale: 1.4 }}, {{ opacity: 1, scale: 1, duration: .35, ease: 'power3.in' }}, M.perde);
  showHL('.cn-h', M.perde - .05, .5);

  // ---------- B3: juros (§ 4º, II) ----------
  sheetIn('b3', C.doc3);
  tl.set('#b3-cam', view(DW / 2, mid(R.h9), .735, 330), C.doc3);
  tl.to('#b3-cam', {{ ...view(DW / 2, mid(R.h9), .76, 330), duration: C.datas - C.doc3, ease: 'none' }}, C.doc3 + .6);
  showHL('.b3-h6', M.seis - .05); showHL('.b3-h9', M.a8); showHL('.b3-h12', M.doze8);

  // ---------- as duas datas (reação "Então como fica quem ainda não assinou?") ----------
  tl.fromTo('#col1', {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: .5, ease: enter }}, C.datas + .05);
  tl.fromTo('#vbar', {{ scaleY: 0 }}, {{ scaleY: 1, duration: .5, ease: enter }}, C.datas + .2);
  tl.fromTo('#col2', {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: .5, ease: enter }}, C.datas + .35);
  tl.fromTo('#datas .src2', {{ opacity: 0 }}, {{ opacity: 1, duration: .5 }}, C.datas + .4);

  // ---------- volta à propriedade: "A Câmara recebeu a medida hoje. Será que ela vota a tempo?" ----------
  tl.fromTo('#f .grad-top', {{ opacity: 0 }}, {{ opacity: .8, duration: .4 }}, C.foto2);
  tl.fromTo('#f .cred', {{ opacity: 0 }}, {{ opacity: 1, duration: .4 }}, C.foto2 + .2);
  tl.fromTo('#f-seal', {{ opacity: 0, scale: 1.4 }}, {{ opacity: 1, scale: 1, duration: .35, ease: 'power3.in' }}, M.camara);
  tl.fromTo('#f .srcf', {{ opacity: 0 }}, {{ opacity: 1, duration: .5 }}, M.camara + .3);

  // ---------- cartela ----------
  tl.fromTo('#cartela', {{ opacity: 0 }}, {{ opacity: 1, duration: .5, ease: enter }}, C.cartela);
  tl.fromTo('#ct-nome', {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: .6, ease: enter }}, M.eu);
  tl.fromTo('#ct-fil', {{ scaleX: 0 }}, {{ scaleX: 1, duration: .6, ease: enter }}, M.eu + .3);
  tl.fromTo('#ct-prof', {{ opacity: 0 }}, {{ opacity: 1, duration: .4 }}, M.advogado);
  tl.fromTo('#ct-tese', {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: .5, ease: enter }}, M.aqui);
  tl.fromTo('#ct-direct', {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: .5, ease: enter }}, M.segue);
  tl.fromTo('#ct-fontes', {{ opacity: 0 }}, {{ opacity: 1, duration: .6 }}, C.cartela + .8);
  tl.to('#caps', {{ y: 300, duration: .01 }}, C.cartela);

  // ---------- legendas ----------
  LEG.forEach((b, i) => {{
    tl.fromTo('#cap' + i, {{ opacity: 0, scale: .92 }}, {{ opacity: 1, scale: 1, duration: .12, ease: 'power2.out' }}, b.ini);
    tl.set('#cap' + i, {{ opacity: 0 }}, b.fim);
  }});
  tl.to({{}}, {{ duration: {TOTAL} }}, 0);
  window.__timelines = window.__timelines || {{}};
  window.__timelines['video'] = tl;
}});
</script>
</body></html>
"""
(P / "index.html").write_text(HTML, encoding="utf-8")
(P / "hyperframes.json").write_text('{ "name": "mp1376-video" }\n')
print("ok", TOTAL, len(leg), "blocos de legenda", {k: round(v, 2) for k, v in C.items()})
