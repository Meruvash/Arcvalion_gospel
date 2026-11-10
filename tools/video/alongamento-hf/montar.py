"""Gera o projeto HyperFrames do vídeo "Você sabia" sobre alongamento de dívida rural (1080x1080, 30 fps).

Linguagem de documentário de TV: mapa de satélite real, fotos de arquivo com licença livre (crédito na tela),
documentos oficiais em perspectiva sobre a mesa com foco seletivo, rótulos de arquivo, linha do tempo, trilha
original por baixo da narração. Nenhuma imagem gerada por IA.
Uso: python3 montar.py   (escreve index.html e compositions/*.html a partir de assets/)
"""
import html
import json
from pathlib import Path

P = Path(__file__).resolve().parent
W = H = 1080
LEG = json.load(open(P / "assets/legendas.json", encoding="utf-8"))
DOCS = json.load(open(P / "assets/docs/docs.json"))
CRED = json.load(open(P / "assets/img/creditos.json", encoding="utf-8"))
TOTAL = 41.3

def t(fala, palavra, n=1):
    k = 0
    for w in LEG:
        if w["fala"] == fala and w["text"].strip('.,?:!"').lower() == palavra.lower():
            k += 1
            if k == n:
                return w["start"]
    raise KeyError((fala, palavra))

def fim(fala): return max(w["end"] for w in LEG if w["fala"] == fala)
def ini(fala): return min(w["start"] for w in LEG if w["fala"] == fala)

# ---------- plano de cortes (segundos absolutos) ----------
C = {}
C["mapa"] = 0.0
C["bcb"] = t(1, "virou") - 0.05
C["doc1"] = ini(2) - 0.08
C["voz1"] = ini(3) - 0.1
C["art11"] = ini(4) - 0.1
C["alin_b"] = ini(5) - 0.12
C["alin_a"] = t(5, "não") - 0.1
C["alin_c"] = t(5, "teve") - 0.1
C["stj"] = ini(6) - 0.12
C["linha"] = t(6, "porque") - 0.1
C["sumula"] = t(6, "alongar") - 0.3
C["lado"] = ini(7) - 0.1
C["contrato"] = ini(8) - 0.12
C["cartela"] = ini(9) - 0.3
ORDEM = ["mapa", "bcb", "doc1", "voz1", "art11", "alin_b", "alin_a", "alin_c", "stj", "linha", "sumula", "lado", "contrato", "cartela"]
def dur(k):
    i = ORDEM.index(k)
    return round((C[ORDEM[i + 1]] if i + 1 < len(ORDEM) else TOTAL) - C[k], 3)
def loc(abs_t, k): return round(abs_t - C[k], 3)

FONTES = """
@font-face { font-family: 'Source Serif'; src: url('assets/fonts/SourceSerif4-var.ttf') format('truetype'); font-weight: 200 900; }
"""
BASE_CSS = """
#{id} { position: absolute; inset: 0; overflow: hidden; background: #070c16; }
#{id} .lt { position: absolute; left: 44px; top: 44px; max-width: 940px; display: flex; align-items: flex-start; gap: 16px; line-height: 1.4;
  padding: 12px 18px 12px 14px; background: rgba(7,12,22,.72); border-radius: 4px;
  font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 26px; letter-spacing: 0.12em;
  text-transform: uppercase; color: #eee8da; text-shadow: 0 2px 10px rgba(0,0,0,.75); }
#{id} .lt .barra { flex: none; width: 5px; height: 30px; background: #f0c24b; }
#{id} .cred { position: absolute; right: 40px; bottom: 26px; font-family: 'Inter', sans-serif; font-weight: 400;
  font-size: 15px; color: rgba(235,232,224,.82); text-shadow: 0 1px 6px rgba(0,0,0,.9); }
"""

def rotulo_js(id_, d, entra=0.25, vazio=False):
    """Rótulo de arquivo: o filete cresce e o texto é revelado por máscara, da esquerda para a direita."""
    return f"""
  tl.fromTo('#{id_}-lt .barra', {{ scaleY: 0 }}, {{ scaleY: 1, duration: 0.25, ease: 'power3.out', transformOrigin: '50% 100%' }}, {entra});
  tl.fromTo('#{id_}-lt .txt', {{ clipPath: 'inset(0 100% 0 0)' }}, {{ clipPath: 'inset(0 0% 0 0)', duration: 0.55, ease: 'power3.out' }}, {entra + 0.12});
  tl.to('#{id_}-lt', {{ opacity: 0, duration: 0.15, ease: 'power2.in' }}, {max(entra + 0.9, d - 0.2)});"""

def cena(id_, d, corpo, css, js):
    return f"""<template>
  <style>{FONTES}{BASE_CSS.replace('{id}', id_)}{css}</style>
  <div id="{id_}" data-composition-id="{id_}" data-width="{W}" data-height="{H}">
{corpo}
  </div>
  <script>
  const tl = gsap.timeline({{ paused: true }});
{js}
  window.__timelines["{id_}"] = tl;
  </script>
</template>
"""

def rotulo_html(id_, txt, d):
    if not txt:
        return ""
    return f"""    <div id="{id_}-lt" class="lt clip" data-start="0" data-duration="{d}"><span class="barra"></span><span class="txt">{html.escape(txt)}</span></div>"""

# ---------- cena de foto (Ken Burns) ----------
def cena_foto(id_, foto, rot, z0=1.0, z1=1.08, x0=0, x1=0, y0=0, y1=0):
    d = dur(id_)
    c = CRED[foto]
    src = c["arquivo"].replace("../", "assets/") if c.get("video") else f"assets/img/{c['arquivo']}"
    midia = (f'<video id="{id_}-img" class="clip" data-start="0" data-duration="{d}" data-media-start="{c.get('inicio', 0)}" src="{src}" muted playsinline></video>' if c.get("video")
             else f'<img id="{id_}-img" class="clip" data-start="0" data-duration="{d}" src="{src}" alt="">')
    pino = f'\n    <div id="{id_}-pino" class="pino"></div>' if c.get("pino") else ""
    corpo = f"""    <div id="{id_}-kb" class="kb">{midia}</div>{pino}
{rotulo_html(id_, rot, d)}
    <div id="{id_}-cred" class="cred clip" data-layout-ignore data-start="0" data-duration="{d}">{html.escape(c['credito'])}</div>"""
    css = f"""
#{id_} .kb {{ position: absolute; inset: -4%; }}
#{id_} .pino {{ position: absolute; left: 480px; top: 480px; width: 120px; height: 120px; border-radius: 50%; border: 4px solid #f0c24b;
  box-shadow: 0 0 0 2px rgba(0,0,0,.35), inset 0 0 0 2px rgba(0,0,0,.25); opacity: 0; }}
#{id_} .kb img, #{id_} .kb video {{ width: 100%; height: 100%; object-fit: cover; object-position: {c.get('foco', '50% 50%')}; }}"""
    js = f"""  tl.fromTo('#{id_}-kb', {{ scale: {z0}, x: {x0}, y: {y0} }}, {{ scale: {z1}, x: {x1}, y: {y1}, duration: {d}, ease: 'power1.inOut' }}, 0);
{rotulo_js(id_, d) if rot else ""}"""
    if c.get("pino"):
        js += f"""
  tl.fromTo('#{id_}-pino', {{ scale: 1.8, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.35, ease: 'expo.out' }}, {min(0.5, d * 0.4):.2f});"""
    return cena(id_, d, corpo, css, js)

# ---------- cena do mapa ----------
def cena_mapa():
    id_ = "mapa"; d = dur(id_)
    corpo = f"""    <video id="mapa-video" class="clip" data-start="0" data-duration="{d}" src="assets/video/fazenda.mp4" muted playsinline></video>
{rotulo_html(id_, 'Propriedade rural · Sorriso (MT)', d)}
    <div id="mapa-cred" class="cred clip" data-layout-ignore data-start="0" data-duration="{d}">Imagem: Esri, Maxar, Earthstar Geographics</div>"""
    css = """
#mapa video { position: absolute; left: 0; top: 0; width: 1080px; height: 1080px; object-fit: cover; }"""
    js = rotulo_js(id_, d, entra=0.3)
    return cena(id_, d, corpo, css, js)

# ---------- cena de documento sobre a mesa ----------
def cena_doc(id_, doc, realces, alvo, z0, z1, rotulo, carimbos=(), entrada=True):
    """Folha impressa sobre a mesa escura, em perspectiva; a câmera vai até o alvo; o marcador passa no ritmo da fala.
    realces: [(nome_do_realce, t_ini_abs, t_fim_abs)]; carimbos: [(texto, t_abs, x, y, cor)]."""
    d = dur(id_)
    m = DOCS[doc]
    esc = 1000 / m["w"]                 # largura da folha na tela: 1000 px
    fw, fh = m["w"] * esc, m["h"] * esc
    rx = sum((DOCS["realces"][alvo][0][0], DOCS["realces"][alvo][0][2])) / 2 * esc
    ry = sum((DOCS["realces"][alvo][0][1], DOCS["realces"][alvo][0][3])) / 2 * esc
    marcas = []
    for k, (nome, a, b) in enumerate(realces):
        for j, r in enumerate(DOCS["realces"][nome]):
            x, y, x2, y2 = (v * esc for v in r)
            marcas.append((f"{id_}-m{k}{j}", x - 6, y - 4, x2 - x + 12, y2 - y + 8, a, b))
    marc_html = "\n".join(f'        <div id="{mid}" class="marca" style="left:{x:.0f}px;top:{y:.0f}px;width:{w:.0f}px;height:{h:.0f}px"></div>'
                          for mid, x, y, w, h, *_ in marcas)
    carimbo_html = "\n".join(f'        <div id="{id_}-c{k}" class="carimbo" data-layout-allow-occlusion style="left:{x}px;top:{y}px;color:{cor};border-color:{cor}">{html.escape(txt)}</div>'
                             for k, (txt, _, x, y, cor) in enumerate(carimbos))
    corpo = f"""    <div id="{id_}-mesa" class="mesa"></div>
    <div id="{id_}-cam" class="cam">
      <div id="{id_}-folha" class="folha" data-layout-allow-overflow style="width:{fw:.0f}px;height:{fh:.0f}px">
        <img id="{id_}-img" class="clip" data-start="0" data-duration="{d}" src="assets/docs/{doc}.png" alt="">
{marc_html}
{carimbo_html}
      </div>
    </div>
    <div id="{id_}-foco" class="foco" data-layout-ignore></div>
{rotulo_html(id_, rotulo, d)}"""
    css = f"""
#{id_} .mesa {{ position: absolute; inset: 0; background: radial-gradient(ellipse 70% 60% at 50% 42%, #2a3140 0%, #141a25 55%, #070c16 100%); }}
#{id_} .cam {{ position: absolute; inset: 0; perspective: 1500px; perspective-origin: 50% 40%; }}
#{id_} .folha {{ position: absolute; left: 0; top: 0; transform-origin: 0 0; background: #fbfaf6;
  box-shadow: 0 40px 80px rgba(0,0,0,.65), 0 8px 18px rgba(0,0,0,.45); }}
#{id_} .folha img {{ position: absolute; inset: 0; width: 100%; height: 100%; }}
#{id_} .marca {{ position: absolute; background: #ffd84a; mix-blend-mode: multiply; transform-origin: 0 50%; border-radius: 3px; }}
#{id_} .carimbo {{ position: absolute; font-family: 'Inter', sans-serif; font-weight: 900; font-size: 34px; letter-spacing: .04em;
  padding: 10px 22px; border: 5px solid; border-radius: 10px; mix-blend-mode: multiply; opacity: .88; white-space: nowrap; }}
#{id_} .foco {{ position: absolute; inset: 0; pointer-events: none;
  background: radial-gradient(ellipse 62% 30% at 50% 50%, rgba(7,12,22,0) 0%, rgba(7,12,22,0) 55%, rgba(7,12,22,.55) 85%, rgba(7,12,22,.85) 100%); }}"""
    # câmera: do enquadramento geral da folha até o alvo no centro da tela
    def pos(z, foco):
        cx = (fw / 2) * (1 - foco) + rx * foco
        cy = (fh / 2) * (1 - foco) + ry * foco
        return W / 2 - cx * z, H / 2 - cy * z
    xa, ya = pos(z0, 0.0); xb, yb = pos(z1, 1.0)
    js = []
    if entrada:
        js.append(f"  tl.fromTo('#{id_}-folha', {{ x: {xa + 700:.0f}, y: {ya + 120:.0f}, scale: {z0}, rotationX: 26, rotationZ: -7 }}, "
                  f"{{ x: {xa:.0f}, y: {ya:.0f}, scale: {z0}, rotationX: 22, rotationZ: -2, duration: 0.55, ease: 'expo.out' }}, 0);")
        js.append(f"  tl.to('#{id_}-folha', "
                  f"{{ x: {xb:.0f}, y: {yb:.0f}, scale: {z1}, rotationX: 14, rotationZ: -1, duration: {d - 0.55:.2f}, ease: 'power2.inOut' }}, 0.55);")
    else:
        js.append(f"  tl.fromTo('#{id_}-folha', {{ x: {xa:.0f}, y: {ya:.0f}, scale: {z0}, rotationX: 20, rotationZ: -1.5 }}, "
                  f"{{ x: {xb:.0f}, y: {yb:.0f}, scale: {z1}, rotationX: 14, rotationZ: -1, duration: {d:.2f}, ease: 'power2.inOut' }}, 0);")
    for mid, *_, a, b in marcas:
        js.append(f"  tl.fromTo('#{mid}', {{ scaleX: 0 }}, {{ scaleX: 1, duration: {max(0.2, b - a):.2f}, ease: 'none' }}, {loc(a, id_)});")
    for k, (_, ta, *_r) in enumerate(carimbos):
        js.append(f"  tl.fromTo('#{id_}-c{k}', {{ scale: 1.6, opacity: 0 }}, {{ scale: 1, opacity: .88, duration: 0.12, ease: 'power4.in' }}, {loc(ta, id_) - 0.12});")
        js.append(f"  tl.fromTo('#{id_}-cam', {{ x: 0, y: 0 }}, {{ keyframes: [{{ x: 6, y: -4, duration: 0.04 }}, {{ x: -5, y: 3, duration: 0.04 }}, {{ x: 0, y: 0, duration: 0.06 }}] }}, {loc(ta, id_)});")
    js.append(rotulo_js(id_, d))
    return cena(id_, d, corpo, css, "\n".join(js))

# ---------- a segunda voz: forma de onda ----------
def cena_voz(id_, fundo_doc, alvo):
    d = dur(id_)
    n = 44
    barras = "\n".join(f'        <i id="{id_}-b{k}"></i>' for k in range(n))
    corpo = f"""    <div id="{id_}-fundo" class="fundo"><img id="{id_}-img" class="clip" data-start="0" data-duration="{d}" src="assets/docs/{fundo_doc}.png" alt=""></div>
    <div id="{id_}-tela" class="tela">
      <div class="onda">
{barras}
      </div>
    </div>
{rotulo_html(id_, 'A pergunta', d)}"""
    css = f"""
#{id_} .fundo {{ position: absolute; inset: -10%; opacity: .1; filter: blur(16px); }}
#{id_} .fundo img {{ width: 100%; height: 100%; object-fit: cover; }}
#{id_} .tela {{ position: absolute; left: 190px; top: 330px; width: 700px; height: 420px; border-radius: 56px;
  background: radial-gradient(ellipse at 50% 40%, #1b2638 0%, #0d1420 80%); border: 3px solid #4a5568;
  box-shadow: inset 0 0 60px rgba(0,0,0,.6), 0 30px 70px rgba(0,0,0,.6); }}
#{id_} .onda {{ position: absolute; left: 70px; right: 70px; top: 0; bottom: 0; display: flex; align-items: center; justify-content: space-between; }}
#{id_} .onda i {{ display: block; width: 7px; height: 240px; border-radius: 4px; background: #f0c24b; transform: scaleY(0.04); }}
#{id_} .lt {{ left: 190px; top: 260px; }}"""
    js = f"""  const ENV = window.__ENV30 || [];
  const T0 = {C[id_]};
  const barras = Array.from({{ length: {n} }}, (_, k) => document.getElementById('{id_}-b' + k));
  const proxy = {{ p: 0 }};
  tl.fromTo('#{id_}-tela', {{ scale: 0.92, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.3, ease: 'expo.out' }}, 0);
  tl.fromTo(proxy, {{ p: 0 }}, {{ p: 1, duration: {d}, ease: 'none', onUpdate: () => {{
    const f = Math.round((T0 + proxy.p * {d}) * 30);
    for (let k = 0; k < {n}; k++) {{
      const v = ENV[Math.min(ENV.length - 1, Math.max(0, f - {n // 2} + k))] || 0;
      const janela = Math.sin(Math.PI * (k + 0.5) / {n});
      barras[k].style.transform = 'scaleY(' + Math.max(0.04, v * janela).toFixed(3) + ')';
    }}
  }} }}, 0);
{rotulo_js(id_, d, 0.15)}"""
    return cena(id_, d, corpo, css, js)

# ---------- linha do tempo 2004 → 2021 → 2026 ----------
def cena_linha():
    id_ = "linha"; d = dur(id_)
    marcos = [("2004", "STJ · Súmula 298", "“direito do devedor”", 0.08),
              ("2021", "CMN · Res. 4.905", "banco “autorizado a prorrogar”", 0.5),
              ("2026", "CMN · Res. 5.314", "“por sua conveniência e decisão”", 0.92)]
    itens = []
    for k, (ano, quem, diz, pos) in enumerate(marcos):
        x = 60 + 960 * pos
        al = "left" if k == 0 else ("right" if k == 2 else "center")
        tx = {"left": -14, "center": -50, "right": -86}[al]
        itens.append(f"""      <div id="linha-k{k}" class="marco" style="left:{x:.0f}px"><span class="ponto{' quente' if k != 1 else ''}"></span>
        <div class="txt" style="text-align:{al};transform:translateX({tx}%)"><b>{ano}</b><em>{html.escape(quem)}</em><q>{html.escape(diz)}</q></div></div>""")
    corpo = f"""    <div id="linha-mesa" class="mesa"></div>
    <div id="linha-traco" class="traco"></div>
{chr(10).join(itens)}
{rotulo_html(id_, 'Linha do tempo · MCR 2-6-4 e Súmula 298', d)}"""
    css = """
#linha .mesa { position: absolute; inset: 0; background: radial-gradient(ellipse 80% 60% at 50% 45%, #1d2533 0%, #0b111c 70%, #070c16 100%); }
#linha .traco { position: absolute; left: 60px; width: 960px; top: 520px; height: 3px; background: #8a93a3; transform-origin: 0 50%; }
#linha .marco { position: absolute; top: 520px; width: 0; height: 0; }
#linha .ponto { position: absolute; left: -13px; top: -12px; width: 26px; height: 26px; border-radius: 50%; background: #c9ced6; }
#linha .ponto.quente { background: #f0c24b; box-shadow: 0 0 0 8px rgba(240,194,75,.18); }
#linha .txt { position: absolute; top: -190px; width: 330px; }
#linha .txt b { display: block; font-family: 'Source Serif', serif; font-weight: 700; font-size: 92px; line-height: 1; color: #eee8da; }
#linha .txt em { display: block; margin-top: 150px; font-style: normal; font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 19px; letter-spacing: .1em; text-transform: uppercase; color: #aab2bf; }
#linha .txt q { display: block; margin-top: 10px; font-family: 'Source Serif', serif; font-weight: 500; font-size: 27px; line-height: 1.2; color: #eee8da; quotes: none; }"""
    a = loc(t(6, "2004"), id_)
    js = [f"  tl.fromTo('#linha-traco', {{ scaleX: 0 }}, {{ scaleX: 1, duration: {d - 0.2:.2f}, ease: 'power2.inOut' }}, 0);"]
    for k in range(3):
        st = [0.05, 0.4, 0.75][k]
        js.append(f"  tl.fromTo('#linha-k{k} .ponto', {{ scale: 0 }}, {{ scale: 1, duration: 0.3, ease: 'back.out(2)' }}, {st:.2f});")
        js.append(f"  tl.fromTo('#linha-k{k} .txt', {{ opacity: 0, filter: 'blur(6px)' }}, {{ opacity: 1, filter: 'blur(0px)', duration: 0.3, ease: 'power3.out' }}, {st + 0.08:.2f});")
    js.append(rotulo_js(id_, d, 0.1))
    return cena(id_, d, corpo, css, "\n".join(js))

# ---------- os dois documentos lado a lado ----------
def cena_lado():
    id_ = "lado"; d = dur(id_)
    def pedaco(k, doc, nome, rot, x, y, tilt):
        r = DOCS["realces"][nome][0]
        cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
        jw, jh = 760, 300
        esc = 0.62
        ox, oy = cx - jw / 2, cy - jh / 2
        return f"""    <div id="lado-p{k}" class="peca" style="left:{x}px;top:{y}px;width:{jw*esc:.0f}px;height:{jh*esc:.0f}px">
      <div class="janela" style="transform:rotate({tilt}deg)">
        <img id="lado-img{k}" class="clip" data-layout-allow-overflow data-start="0" data-duration="{d}" src="assets/docs/{doc}.png" alt=""
             style="left:{-ox*esc:.0f}px;top:{-oy*esc:.0f}px;width:{DOCS[doc]['w']*esc:.0f}px;height:{DOCS[doc]['h']*esc:.0f}px">
        <div class="marca" style="left:{(r[0]-ox)*esc-4:.0f}px;top:{(r[1]-oy)*esc-3:.0f}px;width:{(r[2]-r[0])*esc+8:.0f}px;height:{(r[3]-r[1])*esc+6:.0f}px"></div>
      </div>
      <div class="rot">{html.escape(rot)}</div>
    </div>"""
    corpo = f"""    <div id="lado-mesa" class="mesa"></div>
{pedaco(0, 'bcb-item4', 'conveniencia', 'MCR 2-6-4 · 2026', 50, 300, -2)}
{pedaco(1, 'stj-sumula', 'devedor', 'Súmula 298 · 2004', 560, 470, 2)}
    <div id="lado-vs" class="vs">×</div>
{rotulo_html(id_, 'A pergunta', d)}"""
    css = """
#lado .mesa { position: absolute; inset: 0; background: radial-gradient(ellipse 80% 60% at 50% 45%, #1d2533 0%, #0b111c 70%, #070c16 100%); }
#lado .peca { position: absolute; }
#lado .janela { position: absolute; inset: 0; overflow: hidden; background: #fbfaf6; box-shadow: 0 30px 60px rgba(0,0,0,.6); }
#lado .janela img { position: absolute; max-width: none; }
#lado .marca { position: absolute; background: #ffd84a; mix-blend-mode: multiply; border-radius: 3px; }
#lado .rot { position: absolute; left: 0; top: -44px; font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 19px; letter-spacing: .12em; text-transform: uppercase; color: #eee8da; }
#lado .vs { position: absolute; left: 0; right: 0; top: 650px; text-align: center; font-family: 'Source Serif', serif; font-weight: 300; font-size: 96px; line-height: 1; color: #f0c24b; }"""
    js = f"""  tl.fromTo('#lado-p0', {{ x: -500, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.5, ease: 'expo.out' }}, 0.05);
  tl.fromTo('#lado-p1', {{ x: 500, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.5, ease: 'expo.out' }}, 0.2);
  tl.fromTo('#lado-vs', {{ opacity: 0, scale: 1.4 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: 'power3.out' }}, {loc(t(7, 'Então'), 'lado') - 0.1:.2f});
  tl.fromTo('#lado-p0, #lado-p1', {{ scale: 1 }}, {{ scale: 1.04, duration: {d - 0.6:.2f}, ease: 'none' }}, 0.6);
{rotulo_js(id_, d, 0.1)}"""
    return cena(id_, d, corpo, css, js)

# ---------- o contrato já assinado: antes ou depois de 1º/7/2026 ----------
def cena_contrato():
    id_ = "contrato"; d = dur(id_)
    a = loc(t(8, "contrato"), id_); b = loc(t(8, "assinou"), id_)
    corpo = f"""    <div id="contrato-mesa" class="mesa"></div>
    <div id="contrato-regua" class="regua"></div>
    <div id="contrato-marco" class="marco"><span></span><b>1º/7/2026</b><em>Res. CMN 5.314 entra em vigor</em></div>
    <div id="contrato-antes" class="lado esq">ANTES</div>
    <div id="contrato-depois" class="lado dir">DEPOIS</div>
    <div id="contrato-cartao" class="cartao"><i>CÉDULA DE CRÉDITO RURAL</i><b>seu contrato</b><u></u><u></u><u></u></div>
    <div id="contrato-q" class="q">?</div>
{rotulo_html(id_, 'Em disputa · a regra alcança contratos anteriores?', d)}"""
    css = """
#contrato .mesa { position: absolute; inset: 0; background: radial-gradient(ellipse 80% 60% at 50% 45%, #1d2533 0%, #0b111c 70%, #070c16 100%); }
#contrato .regua { position: absolute; left: 60px; right: 60px; top: 640px; height: 3px; background: #8a93a3; transform-origin: 50% 50%; }
#contrato .marco { position: absolute; left: 540px; top: 640px; }
#contrato .marco span { position: absolute; left: -2px; top: -70px; width: 4px; height: 140px; background: #f0c24b; }
#contrato .marco b { position: absolute; left: -200px; width: 400px; top: 90px; text-align: center; font-family: 'Source Serif', serif; font-weight: 700; font-size: 54px; color: #eee8da; }
#contrato .marco em { position: absolute; left: -250px; width: 500px; top: 160px; text-align: center; font-style: normal; font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 19px; letter-spacing: .1em; text-transform: uppercase; color: #aab2bf; }
#contrato .lado { position: absolute; top: 595px; font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 24px; letter-spacing: .3em; color: #8a93a3; }
#contrato .esq { left: 110px; } #contrato .dir { right: 110px; }
#contrato .cartao { position: absolute; left: 150px; top: 250px; width: 300px; height: 210px; background: #fbfaf6; border-radius: 4px; padding: 26px 28px;
  box-shadow: 0 30px 60px rgba(0,0,0,.6); }
#contrato .cartao i { display: block; font-style: normal; font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 14px; letter-spacing: .12em; color: #555; }
#contrato .cartao b { display: block; margin-top: 12px; font-family: 'Source Serif', serif; font-weight: 700; font-size: 40px; color: #1b1b1b; }
#contrato .cartao u { display: block; margin-top: 14px; height: 8px; background: #d8d4c8; border-radius: 4px; text-decoration: none; }
#contrato .q { position: absolute; left: 470px; top: 210px; font-family: 'Source Serif', serif; font-weight: 900; font-size: 150px; color: #f0c24b; }"""
    js = f"""  tl.fromTo('#contrato-regua', {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.6, ease: 'power3.inOut' }}, 0);
  tl.fromTo('#contrato-marco', {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: 'expo.out' }}, 0.35);
  tl.fromTo('#contrato-antes, #contrato-depois', {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4, ease: 'power2.out' }}, 0.6);
  tl.fromTo('#contrato-cartao', {{ x: 700, y: -40, rotation: 8, opacity: 0 }}, {{ x: 0, y: 0, rotation: -3, opacity: 1, duration: 0.7, ease: 'expo.out' }}, {max(0.7, a - 0.2):.2f});
  tl.fromTo('#contrato-q', {{ opacity: 0, scale: 1.5 }}, {{ opacity: 1, scale: 1, duration: 0.25, ease: 'power4.out' }}, {b:.2f});
{rotulo_js(id_, d, 0.15)}"""
    return cena(id_, d, corpo, css, js)

# ---------- cartela final ----------
def cena_cartela():
    id_ = "cartela"; d = dur(id_)
    a2 = loc(t(9, "Aqui"), id_); a3 = loc(t(9, "Me"), id_)
    corpo = f"""    <div id="cartela-luz" class="luz"></div>
    <h1 id="cartela-nome" class="nome clip" data-start="0" data-duration="{d}">Dr. Pelicioni</h1>
    <div id="cartela-filete" class="filete clip" data-start="0" data-duration="{d}"></div>
    <div id="cartela-prof" class="prof clip" data-start="0" data-duration="{d}">ADVOGADO</div>
    <p id="cartela-tese" class="tese clip" data-start="0" data-duration="{d}">o que muda no crédito rural, explicado com a fonte</p>
    <p id="cartela-direct" class="direct clip" data-start="0" data-duration="{d}">Dúvida sobre o seu contrato? Direct aberto.</p>
    <p id="cartela-fontes" class="fontes clip" data-layout-ignore data-start="0" data-duration="{d}">Fontes: Res. CMN 5.314/2026 e 4.905/2021 (bcb.gov.br) · Súmula 298 (scon.stj.jus.br) · imagens de arquivo: Coverr e Mixkit (licenças livres)</p>"""
    css = """
#cartela .luz { position: absolute; inset: 0; background: radial-gradient(ellipse 60% 45% at 50% 42%, #1a2232 0%, #0b111c 60%, #070c16 100%); }
#cartela .nome { position: absolute; left: 0; right: 0; top: 330px; text-align: center; font-family: 'Source Serif', serif; font-weight: 700; font-size: 104px; color: #eee8da; letter-spacing: -0.01em; }
#cartela .filete { position: absolute; left: 380px; width: 320px; top: 480px; height: 3px; background: #f0c24b; transform-origin: 50% 50%; }
#cartela .prof { position: absolute; left: 0; right: 0; top: 505px; text-align: center; font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 28px; letter-spacing: .32em; color: #c9ced6; }
#cartela .tese { position: absolute; left: 0; right: 0; top: 610px; text-align: center; font-family: 'Source Serif', serif; font-style: italic; font-weight: 400; font-size: 34px; color: #d8d4c8; }
#cartela .direct { position: absolute; left: 0; right: 0; top: 700px; text-align: center; font-family: 'Inter', sans-serif; font-weight: 700; font-size: 30px; color: #f0c24b; }
#cartela .fontes { position: absolute; left: 60px; right: 60px; bottom: 40px; text-align: center; font-family: 'Inter', sans-serif; font-weight: 400; font-size: 16px; line-height: 1.4; color: #8a93a3; }"""
    js = f"""  tl.fromTo('#cartela-nome', {{ opacity: 0, filter: 'blur(8px)' }}, {{ opacity: 1, filter: 'blur(0px)', duration: 0.5, ease: 'power3.out' }}, 0.15);
  tl.fromTo('#cartela-filete', {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.6, ease: 'expo.out' }}, 0.45);
  tl.fromTo('#cartela-prof', {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4, ease: 'power2.out' }}, 0.7);
  tl.fromTo('#cartela-tese', {{ opacity: 0, filter: 'blur(6px)' }}, {{ opacity: 1, filter: 'blur(0px)', duration: 0.4, ease: 'power3.out' }}, {a2:.2f});
  tl.fromTo('#cartela-direct', {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: 'power3.out' }}, {a3:.2f});
  tl.fromTo('#cartela-fontes', {{ opacity: 0 }}, {{ opacity: 1, duration: 0.6, ease: 'power2.out' }}, 0.8);"""
    return cena(id_, d, corpo, css, js)

# ---------- título da abertura (sobre a foto do Banco Central) ----------
def titulo_bcb():
    return f"""
    <div id="bcb-tit" class="tit">
      <div id="bcb-t1" class="l1">Decisão do</div>
      <div id="bcb-t2" class="l2">banco?</div>
    </div>""", """
#bcb .tit { position: absolute; left: 0; right: 0; top: 150px; text-align: center; font-family: 'Source Serif', serif; color: #eee8da;
  text-shadow: 0 6px 30px rgba(0,0,0,.75); }
#bcb .l1 { font-weight: 600; font-size: 104px; line-height: 1.02; }
#bcb .l2 { font-weight: 900; font-size: 132px; line-height: 1.0; color: #f0c24b; }""", f"""
  tl.fromTo('#bcb-t1', {{ opacity: 0, filter: 'blur(8px)' }}, {{ opacity: 1, filter: 'blur(0px)', duration: 0.18, ease: 'power3.out' }}, {loc(t(1, 'decisão'), 'bcb') - 0.05:.2f});
  tl.fromTo('#bcb-t2', {{ opacity: 0, filter: 'blur(8px)' }}, {{ opacity: 1, filter: 'blur(0px)', duration: 0.18, ease: 'power3.out' }}, {loc(t(1, 'banco'), 'bcb') - 0.05:.2f});"""

# ---------- legendas (referência 1: preto sobre caixa amarela) ----------
def legendas():
    grupos, cur = [], []
    for w in LEG:
        if cur and (len(cur) == 3 or w["fala"] != cur[-1]["fala"] or w["start"] - cur[-1]["end"] > 0.15):
            grupos.append(cur); cur = []
        cur.append(w)
        if w["text"][-1] in ",.?:":
            grupos.append(cur); cur = []
    if cur:
        grupos.append(cur)
    corpo, js = [], []
    for i, g in enumerate(grupos):
        a = max(0.1, g[0]["start"] - 0.03)
        b = grupos[i + 1][0]["start"] - 0.03 if i + 1 < len(grupos) and grupos[i + 1][0]["start"] - g[-1]["end"] < 0.6 else g[-1]["end"] + 0.25
        if g[0]["fala"] == 9:
            continue  # a conclusão é a cartela: o texto já está na tela
        txt = " ".join(w["text"] for w in g)
        corpo.append(f'    <div id="cap-g{i}" class="grupo"><span>{html.escape(txt)}</span></div>')
        js.append(f"  tl.set('#cap-g{i}', {{ opacity: 1, visibility: 'visible' }}, {a:.3f});")
        js.append(f"  tl.fromTo('#cap-g{i} span', {{ scale: 0.94 }}, {{ scale: 1, duration: 0.1, ease: 'power2.out' }}, {a:.3f});")
        js.append(f"  tl.set('#cap-g{i}', {{ opacity: 0, visibility: 'hidden' }}, {b:.3f});")
    css = """
#legendas { position: absolute; inset: 0; pointer-events: none; }
#legendas .grupo { position: absolute; left: 0; right: 0; top: 840px; text-align: center; opacity: 0; visibility: hidden; }
#legendas .grupo span { display: inline-block; background: #f0c24b; color: #121212; font-family: 'Inter', sans-serif; font-weight: 900;
  font-size: 46px; line-height: 1; padding: 14px 22px 16px; border-radius: 8px; box-shadow: 0 10px 30px rgba(0,0,0,.45); }"""
    return f"""<template>
  <style>{css}</style>
  <div id="legendas" data-composition-id="legendas" data-width="{W}" data-height="{H}">
{chr(10).join(corpo)}
  </div>
  <script>
  const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
  window.__timelines["legendas"] = tl;
  </script>
</template>
"""

# ---------- monta tudo ----------
def escreve(nome, txt):
    (P / "compositions" / f"{nome}.html").write_text(txt, encoding="utf-8")

escreve("mapa", cena_foto("mapa", "abertura", "", 1.0, 1.08))
fb = cena_foto("bcb", "predio", "", 1.04, 1.12)
t_html, t_css, t_js = titulo_bcb()
fb = fb.replace('    <div id="bcb-cred"', t_html + '\n    <div id="bcb-cred"', 1).replace("</style>", t_css + "</style>", 1).replace(
    '  window.__timelines["bcb"]', t_js + '\n  window.__timelines["bcb"]', 1)
escreve("bcb", fb)
escreve("doc1", cena_doc("doc1", "bcb-item4", [("conveniencia", t(2, "por"), t(2, "decisão") + 0.45)], "conveniencia", 0.95, 1.75,
                         "Documento · Resolução CMN nº 5.314 · Banco Central",
                         carimbos=[("BRASÍLIA · 25/6/2026", t(2, "manual"), 560, 40, "#b3262d")]))
escreve("voz1", cena_voz("voz1", "bcb-item4", "conveniencia"))
escreve("art11", cena_doc("art11", "bcb-art11", [("vigor", t(4, "Mas"), t(4, "é") + 0.3)], "vigor", 1.15, 1.45, "Art. 11 · vigência",
                          carimbos=[("EM VIGOR · 1º/7/2026", t(4, "erro"), 600, 470, "#b3262d")], entrada=False))
escreve("alin_b", cena_foto("alin_b", "seca", "MCR 2-6-4 · b) frustração de safras, por fatores adversos", 1.0, 1.1))
escreve("alin_a", cena_foto("alin_a", "estrada", "MCR 2-6-4 · a) dificuldade de comercialização dos produtos", 1.08, 1.0, -20, 20))
escreve("alin_c", cena_foto("alin_c", "tornado", "MCR 2-6-4 · c) eventuais ocorrências prejudiciais ao desenvolvimento das explorações", 1.0, 1.1))
escreve("stj", cena_foto("stj", "binoculo", "", 1.0, 1.06))
escreve("linha", cena_linha())
escreve("sumula", cena_doc("sumula", "stj-sumula", [("devedor", t(6, "direito"), t(6, "devedor") + 0.35)], "devedor", 1.0, 1.6,
                           "Súmula 298 · STJ · DJ 22/11/2004", entrada=True))
escreve("lado", cena_lado())
escreve("contrato", cena_foto("contrato", "contrato", "Em disputa · a regra alcança contratos assinados antes de 1º/7/2026?", 1.0, 1.1))
escreve("cartela", cena_cartela())
escreve("legendas", legendas())

hosts = "\n".join(f"""      <div id="{k}" data-composition-id="{k}" data-composition-src="compositions/{k}.html" data-start="{C[k]:.3f}" data-duration="{dur(k)}"
           data-track-index="1" data-track-kind="graphics" data-width="{W}" data-height="{H}" style="z-index:{i + 1}"></div>"""
                  for i, k in enumerate(ORDEM))
SFX = [("sfx-papel1", "paper", C["doc1"] + 0.05, 0.5), ("sfx-carimbo1", "stamp", t(2, "manual") - 0.02, 0.55),
       ("sfx-carimbo2", "stamp", t(4, "erro") - 0.02, 0.55), ("sfx-virada", "whoosh", C["stj"] - 0.15, 0.35),
       ("sfx-papel2", "paper", C["sumula"] + 0.05, 0.45), ("sfx-impacto", "boom", C["cartela"], 0.3)]
sfx = "\n".join(f'      <audio id="{i}" class="clip" data-start="{s:.3f}" data-duration="1" data-track-index="{5 + n}" data-volume="{v}" src="assets/audio/sfx/{f}.mp3"></audio>'
                for n, (i, f, s, v) in enumerate(SFX))
env = (P / "assets/audio/envelope30.json").read_text()
index = f"""<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: #070c16; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="{W}" data-height="{H}">
{hosts}
      <div id="legendas" data-composition-id="legendas" data-composition-src="compositions/legendas.html" data-start="0" data-duration="{TOTAL}"
           data-track-index="2" data-track-kind="captions" data-width="{W}" data-height="{H}" style="z-index:50"></div>
      <audio id="narracao" class="clip" data-start="0" data-track-index="3" data-volume="0.78" src="assets/audio/narracao.wav"></audio>
      <audio id="trilha" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="4" data-volume="0.16" data-fade-in="0.4" data-fade-out="1.8" src="assets/audio/trilha.mp3"></audio>
{sfx}
    </div>
    <script>
      window.__ENV30 = {env};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""
(P / "index.html").write_text(index, encoding="utf-8")
print(json.dumps({k: [round(C[k], 2), dur(k)] for k in ORDEM}))
