"""Cartões de prévia (og:image 1200×630) para WhatsApp e redes, um por matéria. Portado de tools/og.py do original.

O cartão mostra só o que já está na página: título, editoria, tipo (Opinião, Patrocinado...) e a foto com crédito.
É desenhado por tools/og_cartoes.js (Playwright) e fica em cache (.cache/og/<hash>.jpg): só refaz quando o texto ou
a foto mudam. Sem Node/Playwright, a matéria usa a própria foto como og:image (url_cartao devolve None).
"""
import hashlib
import html
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import portal

e = html.escape
CACHE = portal.ROOT / ".cache" / "og"
DESLIGADO = False
_FEITOS = {}

CSS = """@font-face{font-family:PS;src:url(%(ps)s) format("woff2");font-weight:400 800}
@font-face{font-family:SS;src:url(%(ss)s) format("woff2");font-weight:700}
*{box-sizing:border-box;margin:0}
body{width:1200px;height:630px;overflow:hidden;background:#12294a;color:#fff;font-family:PS,sans-serif;display:grid;grid-template-columns:520px 1fr}
.foto{position:relative;background:#0c1d36 center/cover}.foto::after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(18,41,74,0) 70%%,#12294a)}
.foto.sem{display:grid;place-items:center}
.txt{padding:44px 54px 40px 30px;display:flex;flex-direction:column;gap:18px;border-top:10px solid %(cor)s;min-width:0}
.tags{display:flex;gap:10px;flex-wrap:wrap}.tag{background:%(fundo)s;color:%(cor)s;font-weight:800;font-size:22px;letter-spacing:.05em;text-transform:uppercase;padding:6px 14px;border-radius:6px}
.tag.t{background:#fff;color:#12294a}
h1{font-family:SS,Georgia,serif;font-weight:700;line-height:1.1;display:-webkit-box;-webkit-line-clamp:5;-webkit-box-orient:vertical;overflow:hidden}
.pe{margin-top:auto;display:flex;align-items:center;gap:14px}.pe b{font-family:SS,Georgia,serif;font-size:30px}.pe span{font-size:19px;color:#c8d2e1}
.cr{position:absolute;left:14px;bottom:10px;font-size:15px;color:#fff;text-shadow:0 1px 3px #000}"""


def tamanho(t):
    n = len(t)
    return 62 if n <= 40 else 54 if n <= 70 else 47 if n <= 95 else 41


def html_cartao(a):
    ed = portal.editoria(a["editoria"])
    uri = lambda p: Path(p).resolve().as_uri()  # noqa: E731
    css = CSS % {"ps": uri(portal.ROOT / "assets/fontes/public-sans.woff2"), "ss": uri(portal.ROOT / "assets/fontes/source-serif-4-700.woff2"),
                 "cor": ed["cor"], "fundo": ed["fundo"]}
    foto = portal.CONTEUDO / "imagens" / a["imagem"]["arquivo"] if a.get("imagem") else None
    lado = (f'<div class="foto" style="background-image:url(\'{uri(foto)}\')"><span class="cr">{e(a["imagem"]["credito"])}</span></div>' if foto and foto.is_file()
            else f'<div class="foto sem"><img src="{uri(portal.ROOT / "assets/marca/logo-512.png")}" width="260" alt=""></div>')
    tipo = "" if a["tipo"] == "noticia" else f'<span class="tag t">{e(portal.TIPOS[a["tipo"]][0])}</span>'
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{lado}<div class="txt">'
            f'<div class="tags"><span class="tag">{e(ed["nome"])}</span>{tipo}</div>'
            f'<h1 style="font-size:{tamanho(a["titulo"])}px">{e(a["titulo"])}</h1>'
            f'<div class="pe"><b>{e(portal.NOME)}</b><span>{e(portal.SITE.removeprefix("https://"))}</span></div></div></body></html>'), foto


def assinatura(a):
    pag, foto = html_cartao(a)
    extra = hashlib.md5(foto.read_bytes()).hexdigest() if foto and foto.is_file() else "-"
    return hashlib.sha256((pag.replace(str(portal.ROOT), "") + extra).encode()).hexdigest()[:16]


def gerar(artigos):
    """Desenha os cartões que faltam no cache e copia todos para publico/img/og/."""
    _FEITOS.clear()
    if DESLIGADO or portal.EXEMPLO and not shutil.which("node"):
        return 0
    CACHE.mkdir(parents=True, exist_ok=True)
    tarefas, tmp = [], Path(tempfile.mkdtemp(prefix="og-"))
    try:
        for a in artigos:
            h = assinatura(a)
            alvo = CACHE / f"{h}.jpg"
            _FEITOS[a["slug"]] = h
            if not alvo.exists():
                arq = tmp / f"{h}.html"
                arq.write_text(html_cartao(a)[0], encoding="utf-8")
                tarefas.append({"html": str(arq), "saida": str(alvo)})
        if tarefas:
            lista = tmp / "tarefas.json"
            lista.write_text(json.dumps(tarefas), encoding="utf-8")
            r = subprocess.run(["node", str(portal.ROOT / "tools" / "og_cartoes.js"), str(lista)], cwd=portal.ROOT, capture_output=True, text=True)
            if r.returncode:
                print("⚠️ cartões de prévia não gerados (Node/Playwright):", (r.stderr or r.stdout).strip()[-300:])
    except FileNotFoundError:
        print("⚠️ Node não encontrado: cartões de prévia não gerados")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for slug, h in list(_FEITOS.items()):
        src = CACHE / f"{h}.jpg"
        if src.exists():
            dst = portal.SAIDA / "img" / "og" / f"{slug}.jpg"
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        else:
            del _FEITOS[slug]
    return len(tarefas)


def url_cartao(a):
    h = _FEITOS.get(a["slug"]) if a else None
    return f"{portal.SITE}/img/og/{a['slug']}.jpg?v={h[:8]}" if h else None
