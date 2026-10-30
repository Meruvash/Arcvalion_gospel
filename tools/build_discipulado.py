"""Gera a seção Discipulado (lições para novos convertidos) a partir de conteudo/discipulado/<NN-slug>/.

Uso: python3 tools/build_discipulado.py   (build_home.py chama)
Cada lição publicada vai para discipulado/<slug>/; em revisão, para previa/discipulado/<slug>/ (noindex, com aviso).
A página mostra o texto do aluno (aluno.md) e, recolhido, o guia do discipulador (discipulador.md). A lista
discipulado/index.html mostra as 12 lições da coleção por módulo (docs/discipulado/padrao-editorial.md, seção 5).
"""
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import portal  # noqa: E402
import seo  # noqa: E402
from build_sitemap import lastmod_registrado  # noqa: E402
from build_home import ROOT, SITE, data_longa, e, pagina  # noqa: E402
from discipulado.checar_licao import MODULOS, licoes, problemas  # noqa: E402
from layout import cabecalho, convite_compartilhar, rodape, trilha  # noqa: E402

# arquitetura fixa da coleção (padrao-editorial.md, seção 5): número -> (módulo, título)
COLECAO = {
    1: (1, "Quem é Jesus Cristo?"), 2: (1, "O que é o Evangelho e por que precisamos de salvação?"),
    3: (1, "O que significa nascer de novo?"), 4: (1, "Como ter certeza da minha fé?"),
    5: (2, "Como ler e entender a Bíblia?"), 6: (2, "Como conversar com Deus pela oração?"),
    7: (2, "Por que preciso fazer parte de uma igreja?"), 8: (2, "O que significam o batismo nas águas e a Ceia do Senhor?"),
    9: (3, "Quem é o Espírito Santo e como ele age?"), 10: (3, "O que é santificação e como vencer o pecado?"),
    11: (3, "Como lidar com dificuldades, dúvidas e tentações?"), 12: (3, "Como compartilhar minha fé e ajudar outras pessoas?"),
}
CAPA = f"{SITE}/estudos/capa.jpg"
CSS_DISC = """<style>
.nota .licao h2{margin-top:6px}.nota .licao .corpo{max-width:66ch}
.nota .licao blockquote{margin:0;padding:12px 16px;border-left:4px solid var(--gold);background:#f6f4ee;border-radius:0 8px 8px 0;display:grid;gap:8px}
.nota .licao blockquote p{color:var(--paper-ink)}
.nota .licao h3{font-size:1.05rem;margin-top:6px}.nota .licao ul,.nota .licao ol{display:grid;gap:8px;padding-left:22px}
.nota .licao ul{list-style:disc}.nota .licao small,.nota .licao .credito-b{font-size:.82rem;color:var(--paper-muted)}
.nota .num-l{display:inline-block;font-size:.8rem;font-weight:800;letter-spacing:.04em;text-transform:uppercase;color:var(--paper-muted)}
.nota .meta-e{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:.88rem;color:var(--paper-muted);margin-top:6px}
.nota .ideia{font-size:1.05rem;color:#3a414c;margin-top:8px}
.nota details.guia>summary{cursor:pointer;font-weight:800;font-size:1.1rem;min-height:44px;display:flex;align-items:center}
.nota details.guia[open]>summary{margin-bottom:10px}
.nota .como{font-size:.9rem;color:#3a414c}
.modulo{display:grid;gap:10px}.modulo h3{font-size:1rem;color:var(--paper-muted)}
.lista-d{display:grid;gap:8px}.lista-d li{display:grid;grid-template-columns:2.4em 1fr;gap:10px;align-items:baseline;padding:10px 0;border-top:1px solid var(--paper-line,#d5dae1)}
.lista-d li:first-child{border-top:0}.lista-d .n{font-weight:800;font-variant-numeric:tabular-nums;color:var(--gold)}
.lista-d a{font-weight:700}.lista-d small{display:block;color:var(--paper-muted);font-size:.85rem}.lista-d .breve{color:var(--paper-muted)}
</style>"""


def inline(t):
    """Ênfase e links do Markdown dentro de uma linha, depois de escapar o HTML."""
    t = e(t)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    return re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", t)


def markdown(texto, nivel=0):
    """Markdown simples da coleção (títulos, parágrafos, listas, citação) para HTML. `nivel` desloca os títulos."""
    texto = re.sub(r"<!--.*?-->", "", texto, flags=re.S).strip()
    out = []
    for bloco in re.split(r"\n\s*\n", texto):
        linhas = [x.rstrip() for x in bloco.strip().splitlines()]
        if not linhas:
            continue
        m = re.match(r"^(#{1,6})\s+(.+)$", linhas[0])
        if m and len(linhas) == 1:
            n = min(len(m.group(1)) + nivel, 6)
            out.append(f"<h{n}>{inline(m.group(2))}</h{n}>")
        elif all(x.startswith(">") for x in linhas):
            dentro = "\n".join(re.sub(r"^>\s?", "", x) for x in linhas)
            out.append(f"<blockquote>{markdown(dentro, nivel)}</blockquote>")
        elif all(re.match(r"^[-*]\s+", x) for x in linhas):
            out.append("<ul>" + "".join("<li>" + inline(re.sub(r"^[-*]\s+", "", x)) + "</li>" for x in linhas) + "</ul>")
        elif all(re.match(r"^\d+\.\s+", x) for x in linhas):
            out.append("<ol>" + "".join("<li>" + inline(re.sub(r"^\d+\.\s+", "", x)) + "</li>" for x in linhas) + "</ol>")
        elif m:  # título seguido de texto no mesmo bloco
            n = min(len(m.group(1)) + nivel, 6)
            out.append(f"<h{n}>{inline(m.group(2))}</h{n}>" + markdown("\n".join(linhas[1:]), nivel))
        else:
            out.append(f"<p>{inline(' '.join(linhas))}</p>")
    # itens de lista separados por linha em branco (um parágrafo por item, para o medidor) viram uma lista só
    return re.sub(r"</(ul|ol)><\1>", "", "".join(out))


def secoes(texto):
    """Divide o aluno.md em [(título da seção, markdown)], sem o título '# ' da lição."""
    texto = re.sub(r"<!--.*?-->", "", texto, flags=re.S)
    texto = re.sub(r"^# .+$", "", texto, count=1, flags=re.M)
    partes = re.split(r"^## (.+)$", texto, flags=re.M)
    return [(partes[i].strip(), partes[i + 1]) for i in range(1, len(partes), 2)]


def carregar():
    """[(licao.json, pasta)] das lições em revisão ou publicadas."""
    out = []
    for a in licoes():
        c = json.loads(a.read_text(encoding="utf-8"))
        if c.get("status") in ("publicado", "revisao"):
            out.append((c, a.parent))
    return out


def publicadas():
    return sorted((c for c, _ in carregar() if c.get("status") == "publicado"), key=lambda c: c["numero"])


def build(c, pasta_src):
    previa = c.get("status") != "publicado"
    pre = "../../../" if previa else "../../"
    pasta = ROOT / ("previa" if previa else "") / "discipulado" / c["slug"]
    pasta.mkdir(parents=True, exist_ok=True)
    url = f"{SITE}/discipulado/{c['slug']}/"
    im = c.get("imagem")
    if im:
        shutil.copyfile(ROOT / "conteudo" / "imagens" / im["arquivo"], pasta / "foto.jpg")
    aluno = (pasta_src / "aluno.md").read_text(encoding="utf-8")
    guia = (pasta_src / "discipulador.md").read_text(encoding="utf-8")
    guia = re.sub(r"^# .+$", "", guia, count=1, flags=re.M)
    blocos = "".join(f'<section class="bloco licao"><h2>{inline(t)}</h2><div class="corpo">{markdown(x, 1)}</div></section>'
                     for t, x in secoes(aluno))
    aud = c.get("auditoria") or {}
    aviso = ('<div style="background:#ffe3e3;color:#7a1f1f;padding:8px 16px;text-align:center;font-size:.9rem"><b>Prévia em revisão.</b> '
             'Esta lição ainda não foi publicada. Não compartilhe.</div>') if previa else ""
    fig = (f'<div class="bloco abre"><figure><img src="foto.jpg" alt="{e(im["alt"])}"><figcaption class="credito">{e(im["credito"])}</figcaption></figure>'
           f'<p class="lide">{e(c["descricao"])}</p></div>') if im else ""
    corpo = f"""{aviso}{cabecalho(pre, "Discipulado", sub=True)}
<main id="conteudo" class="in"><div class="nota">
 {trilha(("Início", pre), ("Discipulado", f"{pre}discipulado/"), (e(c["titulo"]), ""))}
 <article class="bloco">
  <span class="num-l">Lição {c["numero"]} · Módulo {c["modulo"]}: {e(MODULOS[c["modulo"]])}</span>
  <h1>{e(c["titulo"])}</h1>
  <p class="meta-e"><span>Para quem está começando</span><span>Encontro de {c["tempo_min"]} min</span><span>Texto bíblico: NTLH</span></p>
  <p class="ideia">{e(c["ideia_central"])}</p>
  {f'<p class="meta"><time datetime="{c["publicado_em"]}">{data_longa(c["publicado_em"][:10])}</time> · Redação O Paladino</p>' if not previa else ""}
 </article>
 {fig}
 {blocos}
 {convite_compartilhar(f'{c["titulo"]} (via O Paladino)', url, "Está discipulando alguém?", "Mande esta lição para quem você acompanha.")}
 <section class="bloco"><details class="guia"><summary>Guia do discipulador</summary><div class="corpo licao">{markdown(guia, 1)}</div></details></section>
 <section class="bloco como"><h2>Como foi feito</h2><p class="como">{e((c.get("ia") or {}).get("uso", ""))}</p>
 {f'<p class="como">Auditoria independente: nota preliminar {aud["nota"]} de 100, em {aud["rodadas"]} rodada{"s" if aud["rodadas"] != 1 else ""}. A nota da auditoria não substitui a leitura por pessoas do público.</p>' if aud.get("nota") else ""}</section>
</div></main>
{rodape(pre)}"""
    img = f"{SITE}/discipulado/{c['slug']}/foto.jpg" if im else CAPA
    trilha_ld = seo.trilha(("Início", f"{SITE}/"), ("Discipulado", f"{SITE}/discipulado/"), (c["titulo"], url))
    if previa:
        ld = seo.script(trilha_ld)
    else:
        modificado = lastmod_registrado(url, {k: v for k, v in c.items() if k != "publicado_em"})
        ld = seo.script(seo.artigo("Article", url, c["titulo"], c["descricao"], img, c["publicado_em"], modificado), trilha_ld)
    (pasta / "index.html").write_text(pagina(f'{c["titulo"]} | Discipulado | O Paladino', c["descricao"], "" if previa else url, img,
                                             pre, corpo, "article", CSS_DISC, ld), encoding="utf-8")
    return pasta / "index.html"


def pagina_lista():
    """discipulado/index.html: as 12 lições da coleção por módulo; as publicadas com link."""
    pre = "../"
    pub = {c["numero"]: c for c in publicadas()}
    mods = ""
    for m, nome in MODULOS.items():
        itens = ""
        for n, (mod, titulo) in COLECAO.items():
            if mod != m:
                continue
            c = pub.get(n)
            itens += (f'<li><span class="n">{n:02d}</span><span><a href="{c["slug"]}/">{e(c["titulo"])}</a><small>{e(c["ideia_central"])}</small></span></li>' if c
                      else f'<li><span class="n">{n:02d}</span><span>{e(titulo)}<small class="breve">Em preparação</small></span></li>')
        mods += f'<div class="modulo"><h3>Módulo {m}: {e(nome)}</h3><ol class="lista-d">{itens}</ol></div>'
    corpo = f"""{cabecalho(pre, "Discipulado")}
<main id="conteudo" class="in"><div class="nota">
 {trilha(("Início", pre), ("Discipulado", ""))}
 <article class="bloco"><h1>Discipulado</h1><p class="ideia">Doze lições para quem está começando a seguir Jesus. Cada uma tem o texto para o aluno, em linguagem simples, e um guia para quem conduz o encontro.</p></article>
 <section class="bloco"><h2>As lições</h2><div class="corpo" style="max-width:none">{mods}</div></section>
 <section class="bloco como"><h2>Como as lições são feitas</h2><p class="como">Cada lição parte de uma passagem bíblica, com pesquisa em comentários e obras de referência, texto bíblico na Nova Tradução na Linguagem de Hoje e medição de legibilidade. As citações bíblicas e das fontes são conferidas na página onde foram lidas. A orientação é evangélica pentecostal, e o guia do discipulador registra onde outras tradições pensam diferente.</p></section>
</div></main>
{rodape(pre)}"""
    url = f"{SITE}/discipulado/"
    return pagina("Discipulado para novos convertidos | O Paladino",
                  "Lições de discipulado para quem está começando na fé: texto simples para o aluno, guia para o discipulador e fontes conferidas.",
                  url, CAPA, pre, corpo, "website", CSS_DISC, seo.script(seo.trilha(("Início", f"{SITE}/"), ("Discipulado", url))))


def todos():
    portal.iniciar()
    feitos = []
    for c, pasta in carregar():
        erros = problemas(c, pasta=pasta)
        if erros:
            sys.exit(f"Lição fora do padrão (rode tools/discipulado/checar_licao.py): {pasta.name}\n - " + "\n - ".join(erros))
        feitos.append(build(c, pasta))
    (ROOT / "discipulado").mkdir(exist_ok=True)
    (ROOT / "discipulado" / "index.html").write_text(pagina_lista(), encoding="utf-8")
    return feitos


if __name__ == "__main__":
    for f in todos():
        print("ok", f.relative_to(ROOT))
