"""Cartões de prévia (og:image 1200×630) para WhatsApp e redes: um por notícia e um por estudo. Cópia do og.py do Elite.

Mesmo desenho do Elite (foto à esquerda com degradê, etiqueta colorida, título, trecho, selo e endereço), com o fundo
preto trocado por azul-marinho. Só texto que já está na página. Desenhado por tools/og_cartoes.js (Playwright), em
cache por conteúdo (.cache/og/); sem Node/Playwright, as páginas usam a própria foto.
"""
import hashlib
import html
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import portal

e = html.escape
CACHE = portal.ROOT / ".cache" / "og"
DESLIGADO = False
_FEITOS = {}
COR_SELO = {"Boa notícia": "#157a43", "Vale acompanhar": "#1f5fae", "Para refletir": "#6b4ea3", "Motivo de alerta": "#8a5200", "Informativo": "#5a6270",
            "Ótimo para começar": "#157a43", "Ideal para grupos": "#1f5fae", "Para aprofundar": "#6b4ea3"}

CSS = """@font-face{font-family:PS;src:url(%(fonte)s) format("woff2");font-weight:400 800}
*{box-sizing:border-box;margin:0}
body{width:1200px;height:630px;overflow:hidden;background:#0a1a33;color:#eceff3;font-family:PS,sans-serif;display:grid;grid-template-columns:560px 1fr}
.foto{position:relative;background:#0f2242 center/cover}.foto::after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(10,26,51,0) 68%%,#0a1a33)}
.foto.sem{display:grid;place-items:center;background:radial-gradient(circle at 40%% 40%%,color-mix(in srgb,var(--c) 45%%,#0a1a33),#0a1a33 75%%)}
.foto.sem img{width:300px;border-radius:24px}
.txt{padding:40px 52px 38px 28px;display:flex;flex-direction:column;gap:16px;border-top:8px solid var(--c);min-width:0}
.topo{display:flex;align-items:center;justify-content:space-between;gap:16px}.topo img{width:72px;border-radius:12px}
.tag{background:var(--c);color:#0a1a33;font-weight:800;font-size:21px;letter-spacing:.06em;text-transform:uppercase;padding:6px 14px;border-radius:5px}
h1{font-weight:800;letter-spacing:-.02em;line-height:1.06;display:-webkit-box;-webkit-line-clamp:5;-webkit-box-orient:vertical;overflow:hidden}
.sub{font-size:24px;line-height:1.3;color:#c9cfd8;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.pe{margin-top:auto;display:flex;align-items:center;gap:16px;flex-wrap:wrap}
.selo{font-weight:800;font-size:23px;color:#fff;border-radius:999px;padding:6px 18px}
.url{font-family:ui-monospace,Menlo,monospace;font-size:18px;letter-spacing:.06em;color:#a7afbb;text-transform:uppercase}"""


def tamanho_titulo(t):
    n = len(t)
    return 76 if n <= 14 else 58 if n <= 40 else 50 if n <= 70 else 44 if n <= 95 else 39


def trecho(t, limite=150):
    m = re.match(r"(.+?[.!?])(\s|$)", t)
    if m and len(m.group(1)) <= limite:
        return m.group(1)
    return t if len(t) <= limite else t[:limite].rsplit(" ", 1)[0].rstrip(",;:") + "…"


def uri(p):
    return Path(p).resolve().as_uri()


def pagina_cartao(cor, foto, tag, titulo, sub, selo):
    logo = uri(portal.ROOT / "assets" / "marca" / "logo-512.png")
    lado = (f'<div class="foto" style="background-image:url(\'{uri(foto)}\')"></div>' if foto and Path(foto).exists()
            else f'<div class="foto sem"><img src="{logo}" alt=""></div>')
    pe = (f'<span class="selo" style="background:{COR_SELO.get(selo, "#5a6270")}">{e(selo)}</span>'
          f'<span class="url">{e(portal.SITE.removeprefix("https://").split("/")[0])}</span>')
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS % {"fonte": uri(portal.ROOT / "assets" / "fontes" / "public-sans.woff2")}}</style></head>'
            f'<body style="--c:{cor}">{lado}<div class="txt"><div class="topo"><span class="tag">{e(tag)}</span><img src="{logo}" alt=""></div>'
            f'<h1 style="font-size:{tamanho_titulo(titulo)}px">{e(titulo)}</h1><p class="sub">{e(sub)}</p><div class="pe">{pe}</div></div></body></html>')


def cartoes(ns, estudos):
    out = []
    for n in ns:
        ed = portal.editoria(n["categoria"])
        foto = portal.CONTEUDO / "imagens" / n["imagem"]["arquivo"] if n.get("imagem") else None
        out.append((f"noticia-{n['slug']}", pagina_cartao(ed["viva"], foto, ed["nome"], n["titulo"], trecho(n["por_que_importa"]), n["selo"]), foto))
    for c in estudos:
        foto = portal.CONTEUDO / "imagens" / c["imagem"]["arquivo"] if c.get("imagem") else None
        out.append((f"estudo-{c['slug']}", pagina_cartao("#e3b23c", foto, "Estudo bíblico", c["titulo"], c["tagline"], c["selo"]), foto))
    return out


def gerar(ns, estudos):
    _FEITOS.clear()
    if DESLIGADO or not shutil.which("node"):
        return 0
    CACHE.mkdir(parents=True, exist_ok=True)
    tarefas, tmp = [], Path(tempfile.mkdtemp(prefix="og-"))
    try:
        for nome, pag, foto in cartoes(ns, estudos):
            extra = hashlib.md5(Path(foto).read_bytes()).hexdigest() if foto and Path(foto).exists() else "-"
            h = hashlib.sha256((pag.replace(str(portal.ROOT), "") + extra).encode()).hexdigest()[:16]
            _FEITOS[nome] = h
            if not (CACHE / f"{h}.jpg").exists():
                arq = tmp / f"{h}.html"
                arq.write_text(pag, encoding="utf-8")
                tarefas.append({"html": str(arq), "saida": str(CACHE / f"{h}.jpg")})
        if tarefas:
            lista = tmp / "t.json"
            lista.write_text(json.dumps(tarefas), encoding="utf-8")
            r = subprocess.run(["node", str(portal.ROOT / "tools" / "og_cartoes.js"), str(lista)], cwd=portal.ROOT, capture_output=True, text=True)
            if r.returncode:
                print("⚠️ cartões de prévia não gerados (Node/Playwright):", (r.stderr or r.stdout).strip()[-200:])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for nome, h in list(_FEITOS.items()):
        src = CACHE / f"{h}.jpg"
        if src.exists():
            dst = portal.SAIDA / "img" / "og" / f"{nome}.jpg"
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        else:
            del _FEITOS[nome]
    return len(tarefas)


def url_cartao(nome):
    h = _FEITOS.get(nome)
    return f"{portal.SITE}/img/og/{nome}.jpg?v={h[:8]}" if h else None
