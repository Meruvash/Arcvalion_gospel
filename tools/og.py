"""Cartões de prévia (og:image 1200×630) para o WhatsApp e as redes: um por notícia e um por resenha.

Uso: python3 tools/og.py   (também roda no começo de build_home.py e de publicar.py)
O cartão repete o visual do site (fundo preto, fonte Public Sans, etiqueta colorida, logo) e mostra só texto
que já está na página: título, um trecho do "Por que importa" ou a frase de efeito da resenha, o selo de opinião,
a nota BGG e as vitórias em prêmios. Imagem larga = prévia grande no WhatsApp (quadrada vira miniatura).
Saída: img/og/<noticia|resenha>-<slug>.jpg. Só refaz o cartão cujo conteúdo (texto ou foto) mudou, registrado em
img/og/estado.json; o desenho é feito por tools/og_cartoes.js (Playwright). Sem Node/Playwright, as páginas
continuam com a imagem antiga (url_cartao devolve None).
"""
import hashlib
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://meruvash.github.io/Arcvalion_gospel"
PASTA = ROOT / "img" / "og"
ESTADO = PASTA / "estado.json"
e = html.escape

# cor da etiqueta e do filete por categoria (as mesmas das faixas do site)
COR_CAT = {"Notícias Gospel": "#6ea8ff", "Política e Sociedade": "#b493ff", "Família e Valores": "#3ddc84", "Fé e Bíblia": "#f0c24b",
           "Economia e Negócios": "#6ea8ff", "Música e Cultura Cristã": "#b493ff", "Eventos": "#f0c24b"}
COR_SELO_NOTA = {"Boa notícia": "#157a43", "Vale acompanhar": "#1f5fae", "Para refletir": "#6b4ea3", "Motivo de alerta": "#8a5200", "Informativo": "#5a6270"}
COR_SELO_RES = {"sim": "#157a43", "publico": "#8a5200", "nao": "#a3223a"}
COR_NOTA = {"n9": "#1d7d48", "n7": "#2366a8", "n6": "#6b4ea3", "n5": "#b23a48"}

CSS = """@font-face{font-family:PS;src:url(%(fonte)s) format("woff2");font-weight:400 800}
*{box-sizing:border-box;margin:0}
body{width:1200px;height:630px;overflow:hidden;background:#0a1a33;color:#eceff3;font-family:PS,sans-serif;display:grid;grid-template-columns:560px 1fr}
.foto{position:relative;background:#111 center/cover}.foto::after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(0,0,0,0) 68%%,#0a1a33)}
.foto.sem{display:grid;place-items:center;background:radial-gradient(circle at 40%% 40%%,color-mix(in srgb,var(--c) 45%%,#0a1a33),#0a1a33 75%%)}
.foto.sem img{width:300px;border-radius:24px}
.txt{padding:40px 52px 38px 28px;display:flex;flex-direction:column;gap:16px;border-top:8px solid var(--c);min-width:0}
.topo{display:flex;align-items:center;justify-content:space-between;gap:16px}.topo img{width:112px;border-radius:8px}
.tag{background:var(--c);color:#0a1a33;font-weight:800;font-size:21px;letter-spacing:.06em;text-transform:uppercase;padding:6px 14px;border-radius:5px}
h1{font-weight:800;letter-spacing:-.02em;line-height:1.06;display:-webkit-box;-webkit-line-clamp:5;-webkit-box-orient:vertical;overflow:hidden}
.sub{font-size:24px;line-height:1.3;color:#c9cfd8;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.pe{margin-top:auto;display:flex;align-items:center;gap:16px;flex-wrap:wrap}
.selo{font-weight:800;font-size:23px;color:#fff;border-radius:999px;padding:6px 18px}
.url{font-family:ui-monospace,Menlo,monospace;font-size:18px;letter-spacing:.06em;color:#a7afbb;text-transform:uppercase}
.nota{width:88px;height:100px;display:grid;place-items:center;clip-path:polygon(50%% 0,100%% 25%%,100%% 75%%,50%% 100%%,0 75%%,0 25%%);font-weight:800;font-size:32px}
.med{display:flex;align-items:center;gap:10px;font-size:23px;color:#f0c24b;font-weight:800}
.med i{width:24px;height:24px;border-radius:50%%;background:radial-gradient(circle at 35%% 30%%,#f7d77a,#e3b23c 60%%,#b9871d)}"""


def arquivo(p):
    return Path(p).resolve().as_uri()


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()[:10] if Path(p).exists() else "-"


def tamanho_titulo(t):
    n = len(t)
    return 76 if n <= 14 else 58 if n <= 40 else 50 if n <= 70 else 44 if n <= 95 else 39


def trecho(t, limite=150):
    """Primeira frase, ou o texto cortado numa palavra, para caber em três linhas."""
    m = re.match(r"(.+?[.!?])(\s|$)", t)
    if m and len(m.group(1)) <= limite:
        return m.group(1)
    return t if len(t) <= limite else t[:limite].rsplit(" ", 1)[0].rstrip(",;:") + "…"


def pagina(cor, foto, tag, titulo, sub, pe):
    fonte = arquivo(ROOT / "fontes" / "public-sans.woff2")
    logo = arquivo(ROOT / "marca" / "o-paladino.webp")
    lado = (f'<div class="foto" style="background-image:url(\'{arquivo(foto)}\')"></div>' if foto and Path(foto).exists()
            else f'<div class="foto sem"><img src="{logo}" alt=""></div>')
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS % {"fonte": fonte}}</style></head>'
            f'<body style="--c:{cor}">{lado}<div class="txt"><div class="topo"><span class="tag">{e(tag)}</span><img src="{logo}" alt=""></div>'
            f'<h1 style="font-size:{tamanho_titulo(titulo)}px">{e(titulo)}</h1><p class="sub">{e(sub)}</p><div class="pe">{pe}</div></div></body></html>')


def cartao_noticia(n):
    foto = ROOT / "noticias" / n["imagem"]["arquivo"] if n.get("imagem") else None
    pe = (f'<span class="selo" style="background:{COR_SELO_NOTA.get(n["selo"], "#5a6270")}">{e(n["selo"])}</span>'
          f'<span class="url">meruvash.github.io/Arcvalion_gospel · notícia</span>')
    return f"noticia-{n['slug']}", pagina(COR_CAT.get(n["categoria"], "#e3b23c"), foto, n["categoria"], n["titulo"], trecho(n["por_que_importa"]), pe), foto


def cartao_resenha(c):
    from build_review import campo, faixa_nota, nome_br, numero, selo_class
    nota = numero(campo(c["ficha"], "nota bgg"))
    vit = sum(1 for a in c["premiacoes"] if a["resultado"] == "vencedor")
    pe = ((f'<span class="nota" style="background:{COR_NOTA[faixa_nota(nota)]}">{f"{nota:.1f}".replace(".", ",")}</span>' if nota else "")
          + (f'<span class="med"><i></i>{vit} vitória{"s" if vit != 1 else ""} em prêmios</span>' if vit else "")
          + f'<span class="selo" style="background:{COR_SELO_RES[selo_class(c["selo"])]}">{e(c["selo"])}</span>')
    foto = ROOT / c["slug"] / "capa.jpg"
    return f"resenha-{c['slug']}", pagina("#e3b23c", foto, "Resenha", nome_br(c), c["tagline"], pe), foto


def todos():
    sys.path.insert(0, str(ROOT / "tools"))
    ns = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((ROOT / "conteudo" / "noticias").glob("*.json"))]
    # nota em revisão não ganha cartão público (a prévia usa a foto da própria nota)
    cartoes = [cartao_noticia(n) for n in ns if n.get("status", "publicado") == "publicado"]
    pauta = json.loads((ROOT / "pauta.json").read_text(encoding="utf-8"))
    for pub in pauta["publicadas"]:
        slug = pub["url"].rstrip("/").split("/")[-1]
        cartoes.append(cartao_resenha(json.loads((ROOT / "conteudo" / f"{slug}.json").read_text(encoding="utf-8"))))
    return cartoes


def gerar():
    """Refaz os cartões cujo texto ou foto mudou; apaga os de páginas que não existem mais. Devolve (refeitos, total)."""
    PASTA.mkdir(parents=True, exist_ok=True)
    estado = json.loads(ESTADO.read_text(encoding="utf-8")) if ESTADO.exists() else {}
    cartoes = todos()
    novos, tarefas = {}, []
    tmp = Path(tempfile.mkdtemp(prefix="og-"))
    try:
        for nome, pag, foto in cartoes:
            # a página guarda caminhos absolutos (mudam de máquina para máquina): o registro usa só o conteúdo
            assinatura = hashlib.sha256((pag.replace(str(ROOT), "") + md5(foto) if foto else pag.replace(str(ROOT), "")).encode()).hexdigest()[:16]
            novos[nome] = assinatura
            saida = PASTA / f"{nome}.jpg"
            if estado.get(nome) != assinatura or not saida.exists():
                h = tmp / f"{nome}.html"
                h.write_text(pag, encoding="utf-8")
                tarefas.append({"html": str(h), "saida": str(saida)})
        if tarefas:
            arq = tmp / "tarefas.json"
            arq.write_text(json.dumps(tarefas), encoding="utf-8")
            r = subprocess.run(["node", str(ROOT / "tools" / "og_cartoes.js"), str(arq)], cwd=ROOT, capture_output=True, text=True)
            if r.returncode:
                print("⚠️ cartões de prévia não gerados (Node/Playwright):", (r.stderr or r.stdout).strip()[-300:])
                novos = {k: v for k, v in novos.items() if estado.get(k) == v}
    except FileNotFoundError:
        print("⚠️ Node não encontrado: cartões de prévia não gerados")
        novos = {k: v for k, v in novos.items() if estado.get(k) == v}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for velho in PASTA.glob("*.jpg"):
        if velho.stem not in {n for n, _, _ in cartoes}:
            velho.unlink()
    ESTADO.write_text(json.dumps(dict(sorted(novos.items())), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return len(tarefas), len(cartoes)


def url_cartao(nome):
    """URL do cartão (com ?v= do conteúdo, para o WhatsApp buscar o novo quando mudar) ou None se ainda não existe."""
    arq = PASTA / f"{nome}.jpg"
    if not arq.exists():
        return None
    return f"{SITE}/img/og/{nome}.jpg?v={hashlib.md5(arq.read_bytes()).hexdigest()[:8]}"


if __name__ == "__main__":
    print("ok cartões de prévia: %d refeitos de %d" % gerar())
