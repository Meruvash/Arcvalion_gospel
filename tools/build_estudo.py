"""Gera a página de cada estudo bíblico a partir de conteudo/estudos/<slug>.json (esqueleto da resenha do Elite).

Uso: python3 tools/build_estudo.py [conteudo/estudos/<slug>.json ...]   (sem argumentos, todos; build_home.py chama)
Publicado vai para estudos/<slug>/; em revisão, para previa/estudos/<slug>/ (noindex, com aviso no topo).
O centro da página é "O que dizem os teólogos" (`questao`, `posicoes`, `convergencias`; docs/PADRAO_EDITORIAL.md).
"""
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import portal  # noqa: E402
import seo  # noqa: E402
from build_sitemap import lastmod_registrado  # noqa: E402
from build_home import ROOT, SITE, data_longa, e, pagina  # noqa: E402
from estudos.checar_estudo import NIVEIS, problemas  # noqa: E402
from layout import cabecalho, convite_compartilhar, rodape, trilha  # noqa: E402

SELO = {"Ótimo para começar": "compra", "Ideal para grupos": "acompanhar", "Para aprofundar": "fas"}
GRAVIDADE = {"Leve": "info", "Moderada": "ressalvas", "Grave": "fas"}
CSS_ESTUDO = """<style>
.nota .meta-e{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:.88rem;color:var(--paper-muted);margin-top:6px}
.nota .tagline{font-size:1.05rem;color:#3a414c;margin-top:8px}
.nota .chave{border-left:4px solid var(--gold)}.nota .chave blockquote{margin:0;font-size:1.15rem;font-weight:600;line-height:1.45}
.nota .chave cite{display:block;margin-top:8px;font-style:normal;font-size:.85rem;color:var(--paper-muted)}
.nota ol.partes{display:grid;gap:10px;padding-left:20px}.nota ol.partes b{display:block}
.nota .questao{font-size:1.12rem;font-weight:700;margin-bottom:14px}
.nota .lados{display:grid;gap:14px}@media (min-width:700px){.nota .lados{grid-template-columns:1fr 1fr}}
.nota .lado{border:1px solid var(--paper-line,#d5dae1);border-top:4px solid var(--acc,var(--gold));border-radius:8px;padding:14px;display:grid;gap:12px;align-content:start}
.nota .lado h3{font-size:1.05rem;line-height:1.25}.nota .lado>p{color:#3a414c;font-size:.95rem}
.nota .teo{border-top:1px solid var(--paper-line,#d5dae1);padding-top:10px;display:grid;gap:6px}
.nota .teo b{font-size:.98rem}.nota .teo .quem{font-size:.8rem;color:var(--paper-muted)}
.nota .teo p{font-size:.93rem;color:#3a414c}.nota .teo q{display:block;font-style:italic;color:var(--paper-ink)}
.nota .teo a{font-size:.82rem;color:var(--link)}
.nota ul.marcas{display:grid;gap:10px}.nota ul.marcas li{padding-left:16px;position:relative}
.nota ul.marcas li:before{content:"";position:absolute;left:0;top:.6em;width:7px;height:7px;border-radius:50%%;background:var(--gold)}
.nota .itens{display:grid;gap:12px}.nota .itens h3{font-size:1rem;margin-bottom:2px}.nota .itens p{color:#3a414c}
.nota dl.ficha{display:grid;grid-template-columns:auto 1fr;gap:6px 14px;font-size:.92rem}.nota dl.ficha dt{font-weight:700}
.nota .como{font-size:.85rem;color:var(--paper-muted)}
.nota .posicao{border-left:4px solid var(--gold)}.nota .posicao .corpo p{color:var(--paper-ink)}.nota .posicao .assina{font-size:.78rem;color:var(--paper-muted);margin-top:10px}
</style>""".replace("%%", "%")


def lista(itens):
    return "".join(f"<li>{e(x)}</li>" for x in itens)


def teologo(t):
    cit = f'<q>{e(t["citacao"])}</q>' if t.get("citacao") else ""
    return (f'<div class="teo"><b>{e(t["autor"])}</b><span class="quem">{e(t["quem"])}</span><p>{e(t["texto"])}</p>{cit}'
            f'<a href="{e(t.get("citacao_url") or t["url"])}" target="_blank" rel="noopener">{e(t["obra"])} ({e(t["data"])})</a></div>')


def build(c):
    previa = c.get("status") != "publicado"
    pre = "../../../" if previa else "../../"
    pasta = ROOT / ("previa" if previa else "") / "estudos" / c["slug"]
    pasta.mkdir(parents=True, exist_ok=True)
    url = f"{SITE}/estudos/{c['slug']}/"
    im = c["imagem"]
    shutil.copyfile(ROOT / "conteudo" / "imagens" / im["arquivo"], pasta / "foto.jpg")
    sc = SELO.get(c["selo"], "info")
    v = c["versiculo_chave"]
    passagem = c.get("tipo") == "passagem"
    vozes = f'<div class="lados">{"".join(f"<div class=lado>{teologo(t)}</div>" for t in c.get("vozes", []))}</div>' if passagem else ""
    lados = "".join(f'<div class="lado"><h3>{e(p["lado"])}</h3><p>{e(p["resumo"])}</p>{"".join(teologo(t) for t in p["teologos"])}</div>'
                    for p in c.get("posicoes", []))
    partes = "".join(f"<li><b>{e(t)}</b>{e(x)}</li>" for t, x in c["estrutura"])
    destaques = "".join(f"<div><h3>{e(t)}</h3><p>{e(x)}</p></div>" for t, x in c["destaques"])
    atencao = "".join(f'<div><h3>{e(t)} <span class="selo {GRAVIDADE.get(g, "info")}">{e(g)}</span></h3><p>{e(x)}</p></div>'
                      for g, t, x in c["atencao"])
    formatos = "".join(f"<li><b>{e(f)}:</b> {e(x)}</li>" for f, x, *_ in c.get("formatos", []))
    versiculos = "".join(f"<li><b>{e(r)}</b> {e(x)}</li>" for r, x in c.get("versiculos", []))
    ficha = "".join(f"<dt>{e(k)}</dt><dd>{e(x)}</dd>" for k, x in c.get("ficha", []))
    fontes = "".join(f'<li><a href="{e(u)}" target="_blank" rel="noopener">{e(n)}</a> <span>{e(uso)}</span></li>' for n, u, uso in c["fontes"])
    aviso = ('<div style="background:#ffe3e3;color:#7a1f1f;padding:8px 16px;text-align:center;font-size:.9rem"><b>Prévia em revisão.</b> '
             'Este estudo ainda não foi publicado: espera a revisão. Não compartilhe.</div>') if previa else ""
    corpo = f"""{aviso}{cabecalho(pre, "Estudos", sub=True)}
<main id="conteudo" class="in"><div class="nota">
 {trilha(("Início", pre), ("Estudos bíblicos", f"{pre}estudos/"), (e(c["titulo"]), ""))}
 <article class="bloco">
  <span class="selo {sc}">{e(c["selo"])}</span>
  <h1>{e(c["titulo"])}</h1>
  <p class="meta-e"><span>{e(c["passagem"])}</span><span>{e(c["genero"])} · {e(c["testamento"])}</span><span>Nível {NIVEIS[c["nivel"]].lower()}</span><span>{c["tempo_min"]} min de estudo</span></p>
  <p class="tagline">{e(c["tagline"])}</p>
  {f'<p class="meta"><time datetime="{c["publicado_em"]}">{data_longa(c["publicado_em"][:10])}</time> · Redação O Paladino</p>' if not previa else ""}
 </article>
 <div class="bloco abre"><figure><img src="foto.jpg" alt="{e(im["alt"])}"><figcaption class="credito">{e(im["credito"])}</figcaption></figure><p class="lide">{e(c["lede"])}</p></div>
 <section class="bloco chave"><h2>Versículo-chave</h2><blockquote>{e(v["texto"])}</blockquote><cite>{e(v["referencia"])} · {e(v["traducao"])}</cite></section>
 <section class="bloco"><h2>Contexto</h2><div class="corpo">{"".join(f"<p>{e(p)}</p>" for p in c["contexto"])}</div></section>
 <section class="bloco"><h2>Estrutura do texto</h2>{f'<p class="corpo">{e(c["estrutura_resumo"])}</p>' if c.get("estrutura_resumo") else ""}<ol class="partes">{partes}</ol></section>
 <section class="bloco" id="teologos"><h2>O que dizem os teólogos</h2>{f'<p class="questao">{e(c["questao"])}</p>' if c.get("questao") else ""}{vozes if passagem else f'<div class="lados">{lados}</div>'}</section>
 {f'<section class="bloco"><h2>Em que os dois lados concordam</h2><ul class="marcas">{lista(c["convergencias"])}</ul></section>' if c.get("convergencias") else ""}
 {f'<section class="bloco posicao"><h2>{"O olhar pentecostal" if passagem else "Nossa posição"}</h2><div class="corpo">{"".join(f"<p>{e(x)}</p>" for x in c["nossa_posicao"])}</div><p class="assina">Posição O Paladino · linha editorial pentecostal</p></section>' if c.get("nossa_posicao") else ""}
 <section class="bloco"><h2>O que o texto ensina</h2><div class="itens">{destaques}</div></section>
 <section class="bloco"><h2>Leituras equivocadas</h2><div class="itens">{atencao}</div></section>
 <section class="bloco"><h2>Para a vida</h2><div class="corpo">{"".join(f"<p>{e(p)}</p>" for p in c["aplicacao"])}</div></section>
 <section class="bloco quem"><div><h2>É para você se…</h2><ul class="ok">{lista(c["para_quem"])}</ul></div>{f'<div><h2>Pense duas vezes se…</h2><ul class="no">{lista(c["nao_e_para"])}</ul></div>' if c.get("nao_e_para") else ""}</section>
 {f'<section class="bloco"><h2>Como estudar</h2><ul class="marcas">{formatos}</ul>{f"<p class=corpo><b>Dica:</b> {e(c['dica'])}</p>" if c.get("dica") else ""}</section>' if formatos else ""}
 {f'<section class="bloco"><h2>Versículos para ler junto</h2><ul class="marcas">{versiculos}</ul>{f"<p class=corpo>{e(c['relacionadas'])}</p>" if c.get("relacionadas") else ""}</section>' if versiculos else ""}
 {f'<section class="bloco"><h2>Traduções</h2><p class="corpo">{e(c["traducoes"])}</p></section>' if c.get("traducoes") else ""}
 <section class="bloco veredito {sc}"><h2>Para guardar</h2><span class="selo {sc}">{e(c["selo"])}</span><p>{e(c["veredito"])}</p></section>
 {convite_compartilhar(f'{c["titulo"]} (via O Paladino)', url, "Conhece alguém que vai gostar?", "Mande este estudo para o seu grupo.")}
 {f'<section class="bloco"><h2>Ficha</h2><dl class="ficha">{ficha}</dl></section>' if ficha else ""}
 <section class="bloco fontes"><h2>Fontes</h2><ul>{fontes}</ul><p class="como">Consulta às fontes em {e(c["consulta"])}.</p></section>
 <section class="bloco como"><h2>Como foi feito</h2><p>{e((c.get("ia") or {}).get("uso", ""))}</p></section>
</div></main>
{rodape(pre)}"""
    img = f"{SITE}/estudos/{c['slug']}/foto.jpg"
    trilha_ld = seo.trilha(("Início", f"{SITE}/"), ("Estudos bíblicos", f"{SITE}/estudos/"), (c["titulo"], url))
    if previa:
        ld = seo.script(trilha_ld)
    else:
        modificado = lastmod_registrado(url, {k: v for k, v in c.items() if k != "publicado_em"})
        ld = seo.script(seo.artigo("Article", url, c["titulo"], c["descricao"], img, c["publicado_em"], modificado), trilha_ld)
    html = pagina(f'{c["titulo"]} | O Paladino', c["descricao"], "" if previa else url, img,
                  pre, corpo, "article", CSS_ESTUDO, ld)
    (pasta / "index.html").write_text(html, encoding="utf-8")
    return pasta / "index.html"


def publicados():
    """Estudos no ar, do mais recente para o mais antigo (home, lista de estudos e sitemap)."""
    cs = [json.loads(a.read_text(encoding="utf-8")) for a in sorted((ROOT / "conteudo" / "estudos").glob("*.json"))]
    return sorted((c for c in cs if c.get("status") == "publicado"), key=lambda c: c["publicado_em"], reverse=True)


def pagina_lista():
    """estudos/index.html: os estudos publicados em cartões, com a obra de arte de cada um."""
    pre = "../"
    cards = "".join(
        f'<li><a href="{c["slug"]}/"><img src="{c["slug"]}/foto.jpg" alt="" loading="lazy">'
        f'<span class="selo {SELO.get(c["selo"], "info")}">{e(c["selo"])}</span><b>{e(c["titulo"])}</b>'
        f'<small>{e(c["passagem"])} · {c["tempo_min"]} min</small><span>{e(c["tagline"])}</span></a></li>' for c in publicados())
    css = CSS_ESTUDO + """<style>
.lista-e{display:grid;gap:14px}@media (min-width:700px){.lista-e{grid-template-columns:1fr 1fr}}
.lista-e a{display:grid;gap:6px;text-decoration:none;color:inherit}.lista-e img{width:100%;aspect-ratio:4/3;object-fit:cover;object-position:top;border-radius:8px}
.lista-e .selo{justify-self:start}.lista-e b{font-size:1.05rem;line-height:1.25}.lista-e a:hover b{text-decoration:underline}
.lista-e small{color:var(--paper-muted)}.lista-e span:last-child{color:#3a414c;font-size:.93rem}
</style>"""
    corpo = f"""{cabecalho(pre, "Estudos")}
<main id="conteudo" class="in"><div class="nota">
 {trilha(("Início", pre), ("Estudos bíblicos", ""))}
 <article class="bloco"><h1>Estudos bíblicos</h1><p class="tagline">Cada estudo parte de uma passagem e mostra o que teólogos brasileiros de referência dizem sobre ela, lado a lado, com as fontes.</p></article>
 <section class="bloco"><h2>Todos os estudos</h2>{f'<ul class="lista-e">{cards}</ul>' if cards else '<p>Os primeiros estudos estão em preparação.</p>'}</section>
</div></main>
{rodape(pre)}"""
    url = f"{SITE}/estudos/"
    return pagina("Estudos bíblicos | O Paladino", "Estudos bíblicos com fontes: a passagem, o contexto e o que dizem os teólogos brasileiros de cada lado.",
                  url, f"{SITE}/estudos/capa.jpg", pre, corpo, "website", css,
                  seo.script(seo.trilha(("Início", f"{SITE}/"), ("Estudos bíblicos", url))))


def todos(arqs=None):
    portal.iniciar()
    feitos = []
    for a in arqs or sorted((ROOT / "conteudo" / "estudos").glob("*.json")):
        c = json.loads(Path(a).read_text(encoding="utf-8"))
        if c.get("status") not in ("publicado", "revisao"):
            continue
        if problemas(c):
            sys.exit(f"Estudo fora do padrão (rode tools/estudos/checar_estudo.py): {c.get('slug')}")
        feitos.append(build(c))
    return feitos


if __name__ == "__main__":
    for f in todos(sys.argv[1:]):
        print("ok", f.relative_to(ROOT))
