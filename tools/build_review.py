"""Gera a página de uma resenha a partir de um JSON de conteúdo.

Uso: python3 tools/build_review.py conteudo/<slug>.json
Saída: <slug>/index.html (o infografico.webp e a capa.jpg ficam na mesma pasta).
Com fotos oficiais aprovadas, a capa.jpg é refeita a partir da foto do topo.
"""
import hashlib
import html
import json
import re
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import faq  # noqa: E402
import seo  # noqa: E402
from imagens_resp import srcset  # noqa: E402
from layout import barra_leitura, convite_compartilhar, interacoes  # noqa: E402
from layout import CSS_BUSCA, CSS_TRILHA, ICONES, INSTAGRAM, WHATSAPP, cabecalho, icone, rodape, trilha  # noqa: E402,F401

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://meruvash.github.io/Arcvalion_gospel"
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
e = html.escape

def nome_br(c):
    """Nome do jogo como o leitor brasileiro conhece (o og_titulo usa o nome da edição nacional)."""
    return c["og_titulo"].split(" vale a pena")[0].split(" Resenha")[0]


def texto_cp(c):
    """Texto que acompanha o link quando alguém compartilha a resenha."""
    return f"{nome_br(c)}: {c['tagline']} Resenha da Portal Cristão"


def titulo_busca(c):
    """Título do Google e da prévia: titulo_busca (ângulo próprio da resenha) ou, nas antigas, o og_titulo."""
    t = c.get("titulo_busca") or c["og_titulo"].replace(" Resenha Portal Cristão", " Resenha")
    return t if len(t) > 42 else f"{t} | Portal Cristão"


def data_longa(iso):
    a, m, d = (int(x) for x in iso[:10].split("-"))
    return f"{d} de {MESES[m - 1]} de {a}"


def sev_class(s):
    s = s.lower()
    return "grave" if "grave" in s else ("leve" if "leve" in s else "moderada")


def campo(ficha, *nomes):
    for k, v in ficha:
        if k.lower() in nomes and "não confirmad" not in v.lower():
            return v
    return None


def numero(texto):
    m = re.search(r"\d+(?:,\d+)?", texto or "")
    return float(m.group().replace(",", ".")) if m else None


def faixa_nota(n):
    return "n9" if n >= 8 else ("n7" if n >= 7 else ("n6" if n >= 6 else "n5"))


def selo_class(selo):
    s = selo.lower()
    return "nao" if s.startswith("não") else ("publico" if "específico" in s or "ressalva" in s else "sim")


# perfil "Melhor para": rótulo curto (cartões) e frase completa (topo da resenha)
PERFIL_ROTULO = {"entrada": ("Primeiro jogo moderno", "Melhor para: primeiro jogo moderno"),
                 "dupla": ("Jogar a dois", "Melhor para: jogar a dois"),
                 "festa": ("Festa e grupos grandes", "Melhor para: festa e grupos grandes"),
                 "cooperativo": ("Cooperativo", "Melhor para: quem gosta de cooperar"),
                 "solo": ("Ótimo sozinho", "Melhor para: jogar sozinho"),
                 "proximo": ("O próximo passo", "Melhor para: dar o próximo passo"),
                 "estrategia": ("Estrategistas", "Melhor para: estrategistas"),
                 "campanha": ("Campanha com grupo fixo", "Melhor para: campanha com grupo fixo"),
                 "tema": ("Tema e história", "Melhor para: imersão e história")}


def perfil_rotulo(c, longo=False):
    """Rótulo do perfil "Melhor para"; resenhas sem perfil mostram o selo de recomendação."""
    r = PERFIL_ROTULO.get(c.get("melhor_para"))
    return r[1 if longo else 0] if r else c["selo"]


def nivel(c):
    """Nível de recomendação por extenso, com a ressalva quando houver."""
    return f'{c["selo"]}: {c["ressalva"]}' if c.get("ressalva") else c["selo"]


# perfil → página-guia em /jogos-de-tabuleiro/ (tools/build_guias.py)
GUIA_PERFIL = {"entrada": "para-iniciantes", "dupla": "para-dois-jogadores", "festa": "para-festa-e-grupos", "cooperativo": "cooperativos",
               "solo": "para-jogar-sozinho", "proximo": "peso-medio", "estrategia": "estrategia", "campanha": "campanha-e-legacy", "tema": "tematicos"}


def selo_perfil(c, prefixo=True, link=None):
    """Balão do perfil, com a cor do nível de recomendação; com link=prefixo, leva ao guia do perfil se ele existir."""
    rot = e(perfil_rotulo(c, longo=prefixo))
    guia = GUIA_PERFIL.get(c.get("melhor_para"))
    if link and guia and (ROOT / "jogos-de-tabuleiro" / guia / "index.html").exists():
        return f'<a class="selo {selo_class(c["selo"])} selo-link" href="{link}jogos-de-tabuleiro/{guia}/">{rot} <span aria-hidden="true">→</span></a>'
    return f'<span class="selo {selo_class(c["selo"])}">{rot}</span>'


NIVEIS = {3: "Ótimo", 2: "Bom", 1: "Fraco"}


def primeira_frase(t):
    m = re.match(r"(.+?[.!?])(\s|$)", t)
    return (m.group(1), t[m.end():].strip()) if m else (t, "")




def url_fonte(nome, url):
    """A Consulta Golden Geek morava na raiz do site e hoje fica em /consulta/: as fontes antigas ainda apontam para a raiz."""
    if url.rstrip("/") == SITE and "consulta" in nome.lower():
        return f"{SITE}/consulta/"
    return url


def versao(arq):
    """?v= com o hash do arquivo: quando a imagem muda, o endereço muda e navegador e WhatsApp buscam a nova."""
    return f"?v={hashlib.md5(arq.read_bytes()).hexdigest()[:8]}" if arq.exists() else ""


def capa_src(slug):
    return f"../{slug}/capa.jpg{versao(ROOT / slug / 'capa.jpg')}"


def mais_resenhas(c, n=6):
    """Outras resenhas publicadas (mais recentes primeiro) para o leitor continuar no site."""
    pauta = json.loads((ROOT / "pauta.json").read_text(encoding="utf-8"))
    ja = {c["slug"]} | {s for _, s, _ in c.get("comparacoes", []) if s}
    slugs = [p["url"].rstrip("/").split("/")[-1] for p in reversed(pauta["publicadas"])]
    total = len(slugs)
    cards = []
    for s in slugs:
        if s in ja or not (ROOT / "conteudo" / f"{s}.json").exists():
            continue
        o = json.loads((ROOT / "conteudo" / f"{s}.json").read_text(encoding="utf-8"))
        cards.append(
            f'<li><a href="../{s}/"><img src="{capa_src(s)}" srcset="{srcset(ROOT / s / "capa.jpg", "../", (400,))}" sizes="(min-width: 860px) 230px, 45vw" width="800" height="800" alt="" loading="lazy">'
            f'<b>{e(o["jogo"])}</b>{selo_perfil(o, prefixo=False)}</a></li>'
        )
        if len(cards) == n:
            break
    return (
        f'<section class="bloco claro mais-res" id="mais-resenhas"><h2>Continue lendo</h2>'
        f'<p class="sub">Outras resenhas de jogos premiados da Portal Cristão.</p><ul>{"".join(cards)}</ul>'
        f'<a class="ver-todas" href="../estudos/">Ver todas as {total} resenhas</a></section>'
    )


def noticias_do_jogo(c, n=5):
    """Notícias nossas que citam este jogo (campo jogos[].resenha das notas), mais recentes primeiro."""
    notas = []
    for p in (ROOT / "conteudo" / "noticias").glob("*.json"):
        nota = json.loads(p.read_text(encoding="utf-8"))
        if nota.get("status", "publicado") == "publicado" and any(j.get("resenha") == c["slug"] for j in nota.get("jogos", [])):
            notas.append(nota)
    if not notas:
        return ""
    notas.sort(key=lambda x: (x["data"], x.get("publicado_em", "")), reverse=True)
    itens = "".join(f'<li><time datetime="{x["data"]}">{data_longa(x["data"])}</time><a href="../noticias/{x["slug"]}/">{e(x["titulo"])}</a></li>'
                    for x in notas[:n])
    return f'<section class="bloco claro nj" id="noticias-do-jogo"><h2>Notícias sobre {e(c["jogo"])}</h2><ul>{itens}</ul></section>'


FOTO_DESC = {"mesa": "mesa montada vista de cima", "componentes": "cartas e componentes", "capa": "caixa do jogo", "jogabilidade": "partida em andamento"}


def fotos_do_jogo(slug):
    """Fotos oficiais aprovadas em <slug>/fotos/fontes.json, sem as que mostram pessoas, por tipo.

    Só valem quando o fontes.json tem "usar_na_pagina": true, para nenhuma página mudar antes da revisão das fotos."""
    p = ROOT / slug / "fotos" / "fontes.json"
    d = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    if not d.get("usar_na_pagina"):
        return {}
    fotos = {}
    for f in d["fotos"]:
        if f.get("aprovada") and not f.get("pessoas") and not f.get("fora"):
            # "jogar": true reserva a foto para Como é jogar, mesmo que já haja outra do mesmo tipo.
            fotos.setdefault("jogar" if f.get("jogar") else f["tipo"], f)
    return fotos


def foto_principal(fotos):
    """Tira de `fotos` a foto do topo: a marcada com "principal": true, senão mesa, componentes, jogabilidade, caixa."""
    escolhida = next((t for t, f in fotos.items() if f.get("principal")), None)
    return next((fotos.pop(t) for t in (escolhida, "mesa", "componentes", "jogabilidade", "capa") if t in fotos), None)


def capa_da_foto(slug, f):
    """capa.jpg (lista de resenhas e prévia do WhatsApp) passa a ser a foto do topo, recortada no centro em 800×800."""
    im = Image.open(ROOT / slug / f["arquivo"]).convert("RGB")
    w, h = im.size
    lado = min(w, h)
    im = im.crop(((w - lado) // 2, (h - lado) // 2, (w + lado) // 2, (h + lado) // 2)).resize((800, 800), Image.LANCZOS)
    for q in range(85, 55, -5):
        im.save(ROOT / slug / "capa.jpg", quality=q, optimize=True, progressive=True)
        if (ROOT / slug / "capa.jpg").stat().st_size <= 250_000:
            break


def foto_html(c, f, classe="foto", lazy=True):
    # variantes menores em todas as fotos: a do topo é a imagem LCP; as de baixo pesam no plano de dados do celular
    tam = "(min-width: 860px) 420px, calc(100vw - 32px)" if not lazy else "(min-width: 860px) 700px, calc(100vw - 32px)"
    resp = f' srcset="{srcset(ROOT / c["slug"] / f["arquivo"], "../")}" sizes="{tam}"'
    # foto menor que o ideal (último recurso da triagem) aparece no tamanho real, sem esticar e borrar
    if f["largura"] < 800:
        resp += f' style="max-width:min(100%,{f["largura"]}px);margin-inline:auto;display:block"'
    return (f'<figure class="{classe}"><img src="{e(f["arquivo"])}"{resp} width="{f["largura"]}" height="{f["altura"]}" '
            f'alt="{e(c["jogo"])}: {FOTO_DESC.get(f["tipo"], f["tipo"])}"{" loading=\"lazy\"" if lazy else " fetchpriority=\"high\""}>'
            f'<figcaption>{e(f["credito"])}</figcaption></figure>')


def layout_v2(c, premios_bloco, ficha_html, fontes, fotos=None, info_meio=""):
    """Página do padrão editorial v2: resumo no topo, formatos visuais por seção e 'Ler mais' para o que é longo."""
    fotos = fotos or {}
    r = c.get("roteiro", {})
    pf = lambda t: f'<li>{icone("ok", "ic ok")}<span>{e(t)}</span></li>'
    pn = lambda t: f'<li>{icone("nao", "ic no")}<span>{e(t)}</span></li>'
    peso = numero(campo(c["ficha"], "peso bgg"))
    preco = c.get("preco_ref") or {}
    medidor = (
        f'<div class="medidor"><span class="m-k">Peso BGG</span><span class="m-bar" role="img" aria-label="Peso {peso:.1f} de 5">'
        f'<i style="width:{peso / 5 * 100:.0f}%"></i></span><b>{f"{peso:.1f}".replace(".", ",")}/5</b></div>' if peso else ""
    )
    vit = [a for a in c["premiacoes"] if a["resultado"] == "vencedor"]
    premio_txt = (
        f'<p class="r30-premio"><span class="med" aria-hidden="true"></span><span><b>{len(vit)} vitória{"s" if len(vit) != 1 else ""} em prêmios</b>, '
        f'incluindo {e(vit[0]["premio"])} {vit[0]["ano"]} · {e(vit[0]["categoria"])}</span></p>' if vit else ""
    )
    resumo = f"""<section class="bloco r30" id="resumo">
   <h2 class="kick">Resumo em 30 segundos</h2>
   <div class="r30-grid">
    <div><h3>Destaques</h3><ul class="mini">{"".join(pf(t) for t, _ in c["funciona"][:3])}</ul></div>
    <div><h3>Atenção</h3><ul class="mini">{"".join(pn(t) for _, t, _ in c["atencao"][:3])}</ul></div>
   </div>
   <div class="r30-pe">{medidor}{f'<div class="r30-preco">{icone("preco")}<span><b>{e(preco["faixa"])}</b> · consulta em {e(preco["data"])}</span></div>' if preco else ""}</div>
   {premio_txt}
   <p class="r30-quem"><b>Para quem:</b> {e("; ".join(x[0].lower() + x[1:] for x in c["para_quem"][:2]))}.</p>
  </section>"""
    passos = "".join(
        f'<li><span class="n">{i}</span><div><h3>{e(t.capitalize())}</h3><p>{e(x)}</p></div></li>'
        for i, (t, x) in enumerate(c.get("passos") or r.get("passos", []), 1)
    )
    como = f"""<section class="bloco claro" id="como-funciona"><h2>Como funciona {e(c["jogo"])}</h2>
   {f'<p class="sub">{e(c.get("como_resumo") or r["como_resumo"])}</p>' if c.get("como_resumo") or r.get("como_resumo") else ""}
   <ol class="passos">{passos}</ol>
   <details class="mais"><summary>Ler as regras completas</summary><div class="leitura">{"".join(f"<p>{e(x)}</p>" for x in c["como_funciona"])}</div></details>
  </section>"""
    cit = c.get("citacao")
    jogar = f"""<section class="bloco faixa" id="como-e-jogar"><h2>Como é jogar {e(c["jogo"])}</h2>
   {f'<blockquote class="cit"><p>“{e(cit["texto"])}”</p><cite>{e(cit["fonte"])}</cite></blockquote>' if cit else ""}
   {next((foto_html(c, fotos[t]) for t in ("jogar", "componentes", "jogabilidade", "mesa") if t in fotos), "")}
   <div class="leitura"><p>{e(c["experiencia"][0])}</p></div>
   {f'<details class="mais"><summary>Continuar lendo</summary><div class="leitura">{"".join(f"<p>{e(x)}</p>" for x in c["experiencia"][1:])}</div></details>' if len(c["experiencia"]) > 1 else ""}
  </section>"""

    def cartao(classe, ic, titulo, texto, sev=""):
        # Acordeão: o título já diz o ponto; o porquê abre com um toque.
        return (f'<li class="pcc {classe}">{icone(ic, "ic " + classe)}<details><summary><h3>{e(titulo)}{sev}</h3><span class="lm">Por quê?</span></summary>'
                f"<p>{e(texto)}</p></details></li>")
    pros = "".join(cartao("ok", "ok", t, x) for t, x in c["funciona"])
    contras = "".join(cartao("no", "nao", t, x, f' <span class="sev {sev_class(sv)}">{e(sv)}</span>') for sv, t, x in c["atencao"])
    pc = f"""<section class="bloco claro pc2" id="pros-contras">
   <div><h2>O que funciona muito bem</h2><ul>{pros}</ul></div>
   <div><h2>Pontos de atenção</h2><ul>{contras}</ul></div>
  </section>"""
    barras = "".join(
        f'<li><span>{e(k)}</span><span class="bar" role="img" aria-label="{n} de 5"><i style="width:{n * 20}%"></i></span><b>{n}</b></li>'
        for k, n in c.get("perfil") or r.get("perfil", [])
    )
    tiles = "".join(
        f'<li><span class="tn">{e(nj)}</span><span class="pontos" role="img" aria-label="{NIVEIS[nv]}">'
        + "".join(f'<i class="{"on" if k < nv else ""}"></i>' for k in range(3))
        + f'</span><b class="nv">{NIVEIS[nv]}</b><p>{e(x)}</p></li>'
        for nj, x, nv in c.get("jogadores", [])
    )
    quem = f"""<section class="bloco claro" id="para-quem"><h2>Para quem é</h2>
   {f'<h3 class="h3s">Perfil do jogo</h3><ul class="barras">{barras}</ul>' if barras else ""}
   {f'<h3 class="h3s">Com quantos jogar</h3><ul class="tiles" aria-hidden="true">{tiles}</ul><ul class="tiles-txt">{"".join(f"<li><b>{e(nj)}<span class=sr> ({NIVEIS[nv]})</span>:</b> {e(x)}</li>" for nj, x, nv in c.get("jogadores", []))}</ul>' if tiles else ""}
   <div class="quem quem2">
    <div><h3 class="h3s">É para você se…</h3><ul>{"".join(f"<li>{e(x)}</li>" for x in c["para_quem"])}</ul></div>
    <div class="nao"><h3 class="h3s">Pense duas vezes se…</h3><ul>{"".join(f"<li>{e(x)}</li>" for x in c["nao_e_para"])}</ul></div>
   </div>
   {f'<details class="dica"><summary>{icone("dica")}<b>Dica para a primeira partida</b></summary><p>{e(c["primeira_partida"])}</p></details>' if c.get("primeira_partida") else ""}
  </section>"""
    edicao = f"""<section class="bloco claro duo" id="edicao">
   <div class="preco-card"><h2>Edição nacional e preço</h2>
    {f'<p class="faixa-preco">{e(preco["faixa"])}</p><p class="preco-meta">Lojas consultadas em {e(preco["data"])}{" · " + e(preco["obs"]) if preco.get("obs") else ""}</p>' if preco else ""}
    {foto_html(c, fotos["capa"], "foto caixa") if "capa" in fotos else ""}<p>{e(c.get("edicao_nacional", ""))}</p></div>
   <details class="mais dobra" open><summary><h2>Expansões e versões</h2></summary><p>{e(c.get("versoes", ""))}</p></details>
  </section>"""
    cards = "".join(
        f'<li><a class="cc" href="../{sl}/"><img src="{capa_src(sl)}" srcset="{srcset(ROOT / sl / "capa.jpg", "../", (400,))}" sizes="(min-width: 860px) 230px, 45vw" width="800" height="800" alt="" loading="lazy"><span><b>{e(j)}</b><span>{e(x)}</span><span class="vr">Ler a resenha →</span></span></a></li>'
        if sl else f'<li><div class="cc"><span class="cc-ph" aria-hidden="true">{e(j[0])}</span><span><b>{e(j)}</b><span>{e(x)}</span></span></div></li>'
        for j, sl, x in c.get("comparacoes", [])
    )
    compara = f'<section class="bloco claro" id="compare"><h2>Se você gosta de {e(c["jogo"])}…</h2><ul class="cards">{cards}</ul></section>' if cards else ""
    veredito = f"""<section class="bloco fecho" id="veredito">
   <h2>Veredito: {e(nome_br(c))} vale a pena?</h2>
   <span class="selo {selo_class(c["selo"])}">{e(nivel(c))}</span>
   <p>{e(c["veredito"])}</p>
   <p class="tagline">{e(c["tagline"])}</p>
  </section>
  {convite_compartilhar(texto_cp(c), f"{SITE}/{c['slug']}/", f"Conhece alguém que joga {e(nome_br(c))}?", "Mande esta resenha para a turma.", "bloco claro")}
  {interacoes("../", f"/{c['slug']}/", "bloco claro")}"""
    mais = noticias_do_jogo(c) + mais_resenhas(c)
    comunidade = f"""<section class="bloco comunidade"><h2>Gostou da resenha?</h2><p>A Portal Cristão publica resenhas de jogos premiados todos os dias. Entre no grupo para conversar sobre jogos e siga no Instagram.</p><div class="acoes"><a class="zap" href="{WHATSAPP}" target="_blank" rel="noopener">{icone("zap", "ic zi")}<span><b>Entrar no grupo do WhatsApp</b></span></a><a class="ig-btn" href="{INSTAGRAM}" target="_blank" rel="noopener">{icone("insta")}<span>Seguir @portalcristao</span></a></div></section>"""
    fontes_bloco = f'<section class="bloco claro fontes" id="fontes"><details class="mais"><summary><h2>Fontes ({len(c["fontes"])})</h2></summary><ul>{fontes}</ul><p class="note">Consulta às fontes em {e(c["consulta"])}.</p></details></section>'
    abas = "".join(
        f'<li><a href="#{i}">{t}</a></li>'
        for i, t in (("resumo", "Resumo"), ("como-funciona", "Como funciona"), ("como-e-jogar", "Como é jogar"), ("pros-contras", "Prós e contras"),
                     *((("infografico", "Infográfico"),) if 'id="infografico"' in info_meio else ()), ("para-quem", "Para quem é"), ("edicao", "Preço"), ("veredito", "Veredito"), ("mais-resenhas", "Mais resenhas"), ("ficha", "Ficha"))
    )
    premios_bloco = re.sub(r'<h2>Prêmios</h2><p class="resumo">(.*?)</p>', r'<details class="mais dobra" open><summary><h2>Prêmios</h2> <span class="resumo">\1</span></summary>', premios_bloco).replace("</ul></section>", "</ul></details></section>")
    main = f"""<main id="conteudo" class="v2" style="--acc:{e(c.get("cor", "#e3b23c"))}">
 <div class="col">
  {resumo}
  {como}
  {jogar}
  {pc}
  <a class="zap zap-meio" href="{WHATSAPP}" target="_blank" rel="noopener">{icone("zap", "ic zi")}<span><b>Entre no grupo do WhatsApp</b><small>Converse sobre {e(c["jogo"])} e receba as próximas resenhas</small></span></a>
  {info_meio}
  {quem}
  {edicao}
  {compara}
  {veredito}
  {mais}
  {comunidade}
  {faq.secao(faq.resenha(c, nome_br(c)))}
  {fontes_bloco}
 </div>
 <aside>
  {premios_bloco}
  <section class="bloco claro" id="ficha"><details class="mais dobra" open><summary><h2>Ficha técnica</h2></summary><dl>{ficha_html}</dl><p class="note">{e(c["nota_ficha"])}</p></details></section>
 </aside>
</main>
<div class="progresso" aria-hidden="true"><i></i></div>
<a class="voltar-topo" href="#topo" aria-label="Voltar ao topo">{icone("topo")}</a>"""
    return abas, main


def build(c):
    slug = c["slug"]
    ficha = c["ficha"]
    ano = campo(ficha, "ano") or ""
    autor = campo(ficha, "designer", "designers") or ""
    nota = numero(campo(ficha, "nota bgg"))
    peso = campo(ficha, "peso bgg")
    regua = [
        ("jogadores", (lambda d: d and re.sub(r"^(\d+) a (\d+)", r"\1–\2", d))(campo(ficha, "jogadores")), "Jogadores"),
        ("duracao", (lambda d: d and re.sub(r" a ", "–", d).replace(" minutos", " min"))(campo(ficha, "duração anunciada", "duração")), "Duração"),
        ("idade", campo(ficha, "idade"), "Idade"),
        ("peso", f"{numero(peso):.1f}".replace(".", ",") + " / 5" if numero(peso) else None, "Peso BGG"),
    ]
    regua_html = "".join(
        f'<li>{icone(n)}<span class="r-v">{e(re.split(r" [(;]", v)[0])}</span><span class="r-k">{k}</span></li>'
        for n, v, k in regua if v
    )
    nota_html = (
        f'<div class="nota {faixa_nota(nota)}" role="img" aria-label="Nota BGG {nota:.1f} de 10">'
        f'<span>{f"{nota:.1f}".replace(".", ",")}</span></div><p class="nota-k">Nota BGG</p>'
        if nota else ""
    )
    premios = "".join(
        f'<li class="pr{" win" if a["resultado"] == "vencedor" else ""}">'
        f'<span class="pr-m" aria-hidden="true">{"" if a["resultado"] == "vencedor" else (str(a["colocacao"]) + "º" if a.get("colocacao") else "")}</span>'
        f'<span class="pr-t"><b>{e(a["premio"])} {a["ano"]}</b><span>{e(a["categoria"])} · {e(a["rotulo"])}</span></span></li>'
        for a in c["premiacoes"]
    )
    vitorias = sum(1 for a in c["premiacoes"] if a["resultado"] == "vencedor")
    premios_bloco = (
        f'<section class="bloco claro" id="premios"><h2>Prêmios</h2><p class="resumo">{vitorias} vitória{"s" if vitorias != 1 else ""} em {len(c["premiacoes"])} premiações da pauta</p><ul>{premios}</ul></section>'
        if c["premiacoes"] else ""
    )
    ficha_html = "".join(
        f'<div><dt>{e(k)}</dt><dd{" class=na" if "não confirmad" in v.lower() else ""}>{e(v)}</dd></div>'
        for k, v in ficha
    )
    como = "".join(f"<p>{e(p)}</p>" for p in c["como_funciona"])
    funciona = "".join(f'<li>{icone("ok", "ic ok")}<div><h3>{e(t)}</h3><p>{e(x)}</p></div></li>' for t, x in c["funciona"])
    atencao = "".join(
        f'<li>{icone("nao", "ic no")}<div><h3>{e(t)} <span class="sev {sev_class(s)}">{e(s)}</span></h3><p>{e(x)}</p></div></li>'
        for s, t, x in c["atencao"]
    )
    sim = "".join(f"<li>{e(x)}</li>" for x in c["para_quem"])
    nao = "".join(f"<li>{e(x)}</li>" for x in c["nao_e_para"])
    fontes = "".join(
        f'<li><a href="{e(url_fonte(n, u))}" target="_blank" rel="noopener">{e(n)}</a> <span>{e(uso)}</span></li>' for n, u, uso in c["fontes"]
    )
    serie = f'<p class="note">{e(c["serie"])}</p>' if c.get("serie") else ""
    # Seções do padrão editorial v2; resenhas antigas sem esses campos continuam iguais.
    experiencia = (
        f'<section class="bloco claro" id="como-e-jogar"><h2>Como é jogar {e(c["jogo"])}</h2><div class="leitura">'
        + "".join(f"<p>{e(x)}</p>" for x in c["experiencia"]) + "</div></section>"
        if c.get("experiencia") else ""
    )
    jogadores = "".join(f"<li><b>{e(n)}</b> {e(x)}</li>" for n, x, *_ in c.get("jogadores", []))
    partida_bloco = (
        '<section class="bloco claro duo" id="jogadores">'
        + (f'<div><h2>Com quantos jogar</h2><ul class="lista">{jogadores}</ul></div>' if jogadores else "")
        + (f'<div><h2>Primeira partida</h2><p>{e(c["primeira_partida"])}</p></div>' if c.get("primeira_partida") else "")
        + "</section>"
        if jogadores or c.get("primeira_partida") else ""
    )
    edicao_bloco = (
        '<section class="bloco claro duo" id="edicao">'
        + (f'<div><h2>Edição nacional e preço</h2><p>{e(c["edicao_nacional"])}</p></div>' if c.get("edicao_nacional") else "")
        + (f'<div><h2>Expansões e versões</h2><p>{e(c["versoes"])}</p></div>' if c.get("versoes") else "")
        + "</section>"
        if c.get("edicao_nacional") or c.get("versoes") else ""
    )
    comparacoes = "".join(
        f'<li><h3>{f"<a href=\"../{s}/\">{e(j)}</a>" if s else e(j)}</h3><p>{e(x)}</p></li>'
        for j, s, x in c.get("comparacoes", [])
    )
    comparacoes_bloco = (
        f'<section class="bloco claro" id="compare"><h2>Se você gosta de {e(c["jogo"])}…</h2><ul class="compara">{comparacoes}</ul></section>'
        if comparacoes else ""
    )
    abas_extra = "".join(
        f'<li><a href="#{i}">{t}</a></li>'
        for i, t, ok in (("como-e-jogar", "Como é jogar", experiencia), ("edicao", "Edição e preço", edicao_bloco))
        if ok
    )
    linha = " · ".join(x for x in (ano, autor) if x)
    info = ROOT / slug / "infografico.webp"
    larg, alt = Image.open(info).size if info.exists() else (1600, 1600)
    leg = c.get("legenda", "")
    legenda_btn = f'<button type="button" class="post-btn" id="b-legenda" aria-expanded="false" aria-controls="legenda">{icone("copiar")}Legenda</button>' if leg else ""
    legenda_box = (
        f'<div class="legenda" id="legenda" hidden><p class="leg-st" role="status"></p>'
        f'<div class="leg-txt" id="leg-txt" tabindex="0" aria-label="Legenda para o Instagram">{e(leg)}</div>'
        f'<div class="leg-acoes"><button type="button" class="post-btn" id="b-copiar">{icone("copiar")}Copiar de novo</button>'
        f'<button type="button" class="post-btn" id="b-compartilhar" hidden>{icone("compartilhar")}Compartilhar legenda</button></div>'
        f'<p class="leg-dica">Não colou? Toque em “Compartilhar legenda” e escolha “Copiar”, ou segure o dedo no texto acima.</p></div>'
        if leg else ""
    )
    abas_antigas = f""" <li><a href="#como-funciona">Como funciona</a></li>{abas_extra}<li><a href="#pros-contras">Prós e contras</a></li><li><a href="#para-quem">Para quem é</a></li><li><a href="#veredito">Veredito</a></li><li><a href="#ficha">Ficha</a></li>{'<li><a href="#premios">Prêmios</a></li>' if c["premiacoes"] else ""}<li><a href="#fontes">Fontes</a></li>"""
    main_antigo = f"""<main id="conteudo">
 <div class="col">
  <section class="bloco claro" id="como-funciona"><h2>Como funciona {e(c["jogo"])}</h2><div class="leitura">{como}{serie}</div></section>
  {experiencia}
  <section class="bloco claro pc" id="pros-contras">
   <div><h2>O que funciona muito bem</h2><ul>{funciona}</ul></div>
   <div><h2>Pontos de atenção</h2><ul>{atencao}</ul></div>
  </section>
  {partida_bloco}
  <section class="bloco claro quem" id="para-quem">
   <div><h2>É para você se…</h2><ul>{sim}</ul></div>
   <div class="nao"><h2>Pense duas vezes se…</h2><ul>{nao}</ul></div>
  </section>
  {edicao_bloco}
  {comparacoes_bloco}
  <section class="bloco fecho" id="veredito">
   <h2>Veredito: {e(nome_br(c))} vale a pena?</h2>
   <span class="selo {selo_class(c["selo"])}">{e(nivel(c))}</span>
   <p>{e(c["veredito"])}</p>
   <p class="tagline">{e(c["tagline"])}</p>
  </section>
  <section class="bloco comunidade"><h2>Gostou da resenha?</h2><p>A Portal Cristão publica resenhas de jogos premiados todos os dias. Entre no grupo para conversar sobre jogos e siga no Instagram.</p><div class="acoes"><a class="zap" href="{WHATSAPP}" target="_blank" rel="noopener">{icone("zap", "ic zi")}<span><b>Entrar no grupo do WhatsApp</b></span></a><a class="ig-btn" href="{INSTAGRAM}" target="_blank" rel="noopener">{icone("insta")}<span>Seguir @portalcristao</span></a></div></section>
  <section class="bloco claro fontes" id="fontes"><h2>Fontes</h2><ul>{fontes}</ul><p class="note">Consulta às fontes em {e(c["consulta"])}.</p></section>
 </div>
 <aside>
  {premios_bloco}
  <section class="bloco claro" id="ficha"><h2>Ficha técnica</h2><dl>{ficha_html}</dl><p class="note">{e(c["nota_ficha"])}</p></section>
 </aside>
</main>"""
    info_arq = ROOT / c["slug"] / "infografico.webp"
    info_ss = f' srcset="{srcset(info_arq, "../")}" sizes="(min-width: 860px) 520px, calc(100vw - 32px)"' if info_arq.exists() else ""
    info_fig = f"""<figure class="capa" id="info">
  <a href="infografico.webp" target="_blank" rel="noopener"><img src="infografico.webp"{info_ss} width="{larg}" height="{alt}" alt="{e(c["alt"])}"{{carga}}></a>
  <figcaption>Toque para ver o infográfico em tamanho cheio.</figcaption>
  <div class="post"><button type="button" class="post-btn" id="b-salvar">{icone("salvar")}Salvar na galeria</button>{legenda_btn}</div>
  <p class="post-st" id="salvar-st" role="status"></p>
  {legenda_box}
 </figure>"""
    # Com foto oficial, ela vira a capa da página e o infográfico desce para o meio da resenha.
    fotos = fotos_do_jogo(slug) if c.get("experiencia") else {}
    # Só a caixa não basta para o topo: sem foto de mesa, componentes ou jogabilidade, fica o infográfico.
    principal = foto_principal(fotos) if set(fotos) - {"capa"} else None
    if principal:
        try:
            capa_da_foto(slug, principal)
        except Exception as ex:  # foto com problema: fica a capa.jpg que já existe e a resenha sai igual
            print(f"  aviso: capa de {slug} não refeita ({ex.__class__.__name__})")
    versao_capa = versao(ROOT / slug / "capa.jpg")
    # data de publicação: a que publicar.py gravou em pauta.json (resenha ainda não publicada fica sem data)
    pauta = json.loads((ROOT / "pauta.json").read_text(encoding="utf-8"))
    publicada = next((p["data"] for p in pauta["publicadas"] if p["url"].rstrip("/").endswith("/" + slug)), None)
    url = f"{SITE}/{slug}/"
    pub_html = ""
    ld = seo.script(seo.trilha(("Início", f"{SITE}/"), ("Resenhas", f"{SITE}/estudos/"), (c["jogo"], url)))
    if publicada:
        pub_html = (f'<p class="pub">Resenha publicada em <time datetime="{publicada}">{data_longa(publicada)}</time>'
                    f' · Redação Portal Cristão · com base em <a href="#fontes">{len(c["fontes"])} fontes</a></p>')
        from build_sitemap import lastmod_registrado
        ld = seo.script(seo.artigo("Article", url, f'{c["jogo"]}: resenha', c["descricao"], f"{SITE}/{slug}/capa.jpg{versao_capa}",
                                   publicada, lastmod_registrado(url, c), {"@type": "Game", "name": c["jogo"]}),
                        *([faq.ld(faq.resenha(c, nome_br(c)), url)] if faq.resenha(c, nome_br(c)) and c.get("experiencia") else []),
                        seo.trilha(("Início", f"{SITE}/"), ("Resenhas", f"{SITE}/estudos/"), (c["jogo"], url)))
    if principal and not info.exists():
        # Resenha só com fotos (sem infográfico): a foto fica no topo e a legenda do Instagram ganha bloco próprio.
        topo_fig = foto_html(c, principal, "capa foto-capa", lazy=False)
        info_meio = (f'<section class="bloco info-meio" id="legenda-ig"><h2>Legenda para o Instagram</h2>'
                     f'<div class="post">{legenda_btn}</div>{legenda_box}</section>' if leg else "")
    elif not info.exists():
        sys.exit(f"{slug}: sem infografico.webp e sem foto liberada para o topo; não há o que pôr no topo da página.")
    elif principal:
        topo_fig = foto_html(c, principal, "capa foto-capa", lazy=False)
        info_meio = (f'<section class="bloco info-meio" id="infografico"><h2>Infográfico para o Instagram</h2>'
                     f'<p class="sub">A resenha inteira em uma imagem: salve na galeria ou copie a legenda pronta.</p>'
                     f'{info_fig.replace("{carga}", " loading=\"lazy\"")}</section>')
    else:
        topo_fig, info_meio = info_fig.replace("{carga}", ' fetchpriority="high"'), ""
    # prévia do WhatsApp: o cartão largo de tools/og.py (prévia grande); sem ele, a capa quadrada
    from og import url_cartao
    cartao = url_cartao(f"resenha-{slug}")
    og_imagem = (f'<meta property="og:image" content="{cartao}">\n<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">'
                 if cartao else f'<meta property="og:image" content="{SITE}/{slug}/capa.jpg{versao_capa}">\n<meta property="og:image:width" content="800">\n<meta property="og:image:height" content="800">')
    if c.get("experiencia"):
        abas_html, main_html = layout_v2(c, premios_bloco, ficha_html, fontes, fotos, info_meio)
    else:
        abas_html, main_html = abas_antigas, main_antigo
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">
<title>{e(titulo_busca(c))}</title>
<meta name="description" content="{e(c["descricao"])}">
<link rel="canonical" href="{SITE}/{slug}/">
<meta name="robots" content="max-image-preview:large">
<meta property="og:site_name" content="Portal Cristão">
<meta property="og:locale" content="pt_BR">
<meta property="og:title" content="{e(titulo_busca(c))}">
<meta property="og:description" content="{e(c["descricao"])}">
<meta property="og:type" content="article">
<meta property="og:url" content="{SITE}/{slug}/">
{og_imagem}
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0a1a33">
<link rel="icon" href="../favicon.svg" type="image/svg+xml">
<link rel="preload" href="../fontes/public-sans.woff2" as="font" type="font/woff2" crossorigin>
{ld}
<style>
@font-face{{font-family:"Public Sans";src:url(../fontes/public-sans.woff2) format("woff2");font-weight:400 800;font-style:normal;font-display:swap}}
@font-face{{font-family:"Public Sans";src:url(../fontes/public-sans-italic.woff2) format("woff2");font-weight:400;font-style:italic;font-display:swap}}
:root{{color-scheme:dark;--bar:#0a1a33;--bar-ink:#e9ecf1;--gold:#e3b23c;--ground:#0a1a33;--panel:#0f2242;--panel2:#142b52;--ink:#eceff3;--muted:#a1a9b5;--line:#1e3a64;--link:#8cb8ff;--ok:#157a43;--ok-ink:#5fd18f;--no:#c43a52;--no-ink:#ff8094;--warn:#8a5200;--warn-ink:#ffb547;--n9:#1d7d48;--n7:#2366a8;--n6:#6b4ea3;--n5:#b23a48}}
*{{box-sizing:border-box}}
html{{-webkit-text-size-adjust:100%;scroll-padding-top:calc(var(--nav-h,49px) + 64px)}}
body{{margin:0;background:var(--ground);color:var(--ink);font:16px/1.6 "Public Sans",system-ui,sans-serif}}
h1,h2,h3,p,ul,dl,dd,figure{{margin:0}}
ul{{padding:0;list-style:none}}
img{{display:block;max-width:100%;height:auto}}
a{{color:var(--link);text-underline-offset:.18em}}
::selection{{background:#e3b23c;color:#0a1a33}}
:focus-visible{{outline:3px solid var(--gold);outline-offset:2px;border-radius:3px}}
.sr{{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}}
.skip{{position:absolute;left:-999px}}.skip:focus{{left:12px;top:8px;z-index:9;background:var(--gold);color:#0a1a33;padding:6px 10px}}
.bar{{background:var(--bar);color:var(--bar-ink);border-bottom:1px solid var(--line)}}
.bar .in{{max-width:1120px;margin:0 auto;padding:8px 16px;display:flex;align-items:center;gap:12px}}
.bar a{{color:var(--bar-ink);text-decoration:none;font-weight:600;font-size:.95rem}}
.marca{{display:flex;align-items:center;gap:10px}}.marca img{{width:84px;height:auto;border-radius:6px}}
.bar .todas{{margin-left:auto;border:1px solid #2e4d7a;border-radius:6px;padding:6px 12px}}
.bar .todas:hover{{background:#17325a;border-color:var(--gold)}}
.nav{{background:var(--panel);border-bottom:1px solid var(--line)}}
.nav ul{{max-width:1120px;margin:0 auto;padding:0 8px;display:flex;gap:2px;overflow-x:auto;scrollbar-width:none}}
.nav a{{display:block;padding:11px 10px;white-space:nowrap;color:var(--ink);text-decoration:none;font-weight:700;font-size:.92rem;border-bottom:3px solid transparent}}
.nav a:hover{{border-bottom-color:var(--gold)}}.nav a[aria-current]{{color:var(--gold);border-bottom-color:var(--gold)}}
.jogo{{background:var(--panel);border-bottom:1px solid var(--line)}}
.jogo .in{{max-width:1120px;margin:0 auto;padding:20px 16px 0;display:grid;gap:20px}}
{CSS_TRILHA}{CSS_BUSCA}
.jogo .trilha{{grid-column:1/-1;margin-bottom:-8px}}
.capa a{{display:block;border-radius:8px;overflow:hidden;box-shadow:0 8px 28px rgba(0,0,0,.6)}}
.capa figcaption{{font-size:.82rem;color:var(--muted);margin-top:6px}}
.foto-capa img{{border-radius:8px;box-shadow:0 8px 28px rgba(0,0,0,.6)}}
.foto{{margin:0 0 16px}}.foto img{{width:100%;border-radius:8px}}.foto figcaption{{font-size:.78rem;color:var(--muted);margin-top:6px}}
.claro .foto figcaption{{color:#5a6270}}
.foto.caixa{{float:right;width:112px;margin:4px 0 8px 14px}}.foto.caixa figcaption{{font-size:.7rem;line-height:1.3}}.foto.caixa img{{background:#fff}}.preco-card::after{{content:"";display:block;clear:both}}
.info-meio .capa{{max-width:520px}}.info-meio .sub{{color:var(--muted)}}
.topo{{display:grid;grid-template-columns:1fr auto;gap:4px 16px;align-items:start}}
h1{{font-size:clamp(2rem,7vw,3.1rem);line-height:1.05;font-weight:800;letter-spacing:-.02em}}
.linha{{grid-column:1;color:var(--muted);font-size:.95rem}}
.nota-box{{grid-column:2;grid-row:1/span 2;display:grid;justify-items:center}}
.nota{{width:64px;height:72px;display:grid;place-items:center;clip-path:polygon(50% 0,100% 25%,100% 75%,50% 100%,0 75%,0 25%);color:#fff;font-weight:800;font-size:1.45rem;font-variant-numeric:tabular-nums}}
.n9{{background:var(--n9)}}.n7{{background:var(--n7)}}.n6{{background:var(--n6)}}.n5{{background:var(--n5)}}
.nota-k{{font-size:.72rem;color:var(--muted);margin-top:2px}}
.veredito{{display:flex;flex-wrap:wrap;align-items:center;gap:8px 12px;margin-top:14px;padding:12px 14px;border-radius:8px;background:var(--panel2)}}
.selo{{font-weight:800;font-size:.9rem;border-radius:999px;padding:3px 12px;color:#fff;background:var(--ok)}}
.selo.publico{{background:var(--warn)}}.selo.nao{{background:var(--no)}}
.veredito p{{font-weight:600}}
.selo-link{{text-decoration:none}}.selo-link:hover{{filter:brightness(1.12);text-decoration:underline;text-underline-offset:3px}}
.nivel{{flex-basis:100%;font-size:.86rem;font-weight:700;color:var(--ok-ink)}}.nivel.publico{{color:var(--warn-ink)}}.nivel.nao{{color:var(--no-ink)}}
.nivel::before{{content:"✓ "}}.nivel.publico::before{{content:"! "}}.nivel.nao::before{{content:"✕ "}}
.r30 .nivel{{color:#157a43;margin-top:6px}}.r30 .nivel.publico{{color:#8a5200}}.r30 .nivel.nao{{color:#a3223a}}
.lede{{margin-top:14px;color:#c9cfd8;max-width:66ch}}
.pub{{margin-top:10px;color:var(--muted);font-size:.85rem}}.pub a{{color:var(--link)}}
.regua{{display:grid;grid-template-columns:repeat(2,1fr);gap:1px;margin-top:16px;border:1px solid var(--line);border-radius:8px;background:var(--line);overflow:hidden}}
.regua li{{display:grid;grid-template-columns:auto 1fr;column-gap:8px;padding:10px 12px;align-items:center;background:var(--panel)}}
.ic{{width:22px;height:22px;fill:none;stroke:currentColor;stroke-width:1.75;stroke-linecap:round;stroke-linejoin:round}}
.regua .ic{{grid-row:span 2;color:var(--muted)}}
.r-v{{font-weight:700;font-variant-numeric:tabular-nums;line-height:1.25}}.r-k{{font-size:.78rem;color:var(--muted)}}
.abas{{position:sticky;top:0;z-index:5;background:var(--panel);border-bottom:1px solid var(--line)}}
.abas ul{{max-width:1120px;margin:0 auto;padding:0 8px;display:flex;overflow-x:auto;scrollbar-width:none}}
.abas a{{display:block;padding:12px 10px;white-space:nowrap;color:var(--ink);text-decoration:none;font-weight:600;font-size:.92rem;border-bottom:3px solid transparent}}
.abas a:hover{{border-bottom-color:var(--gold)}}
.abas a.ativo{{border-bottom-color:var(--gold);color:var(--gold)}}
.abas .li-volta{{position:sticky;left:0;z-index:1;background:var(--panel)}}
.abas .volta{{display:flex;align-items:center;gap:2px;color:var(--gold);padding-left:4px;padding-right:12px;margin-right:4px;border-right:1px solid var(--line)}}
.abas .volta .ic{{width:18px;height:18px}}
main{{max-width:1120px;margin:0 auto;padding:20px 16px 48px;display:grid;gap:20px}}
.bloco{{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:20px}}
h2{{font-size:1.3rem;font-weight:800;letter-spacing:-.01em;margin-bottom:12px}}
.bloco p+p{{margin-top:10px}}.leitura{{max-width:70ch}}
.pc{{display:grid;gap:20px}}
.pc li{{display:grid;grid-template-columns:auto 1fr;gap:10px;padding:14px 0;border-top:1px solid var(--line)}}
.pc li:first-child{{border-top:0;padding-top:0}}
.pc h3{{font-size:1rem;font-weight:700}}.pc p{{color:#c3c9d2;font-size:.95rem}}
.ic.ok{{color:var(--ok-ink);margin-top:2px}}.ic.no{{color:var(--no-ink);margin-top:2px}}
.sev{{font-size:.72rem;font-weight:700;border-radius:4px;padding:1px 6px;vertical-align:2px;margin-left:4px;background:var(--panel2);color:var(--muted)}}
.sev.moderada{{background:#2a1f0c;color:var(--warn-ink)}}.sev.grave{{background:#2b1117;color:var(--no-ink)}}
.quem,.duo{{display:grid;gap:20px}}
.lista li{{margin:8px 0}}.lista b{{display:block}}
.compara li{{padding:12px 0;border-top:1px solid #dde1e7}}.compara li:first-child{{border-top:0;padding-top:0}}.compara h3{{font-size:1rem;font-weight:700}}.quem li{{margin:6px 0;padding-left:16px;position:relative}}.quem li::before{{content:"";position:absolute;left:0;top:.65em;width:7px;height:7px;border-radius:50%;background:var(--ok)}}
.quem .nao li::before{{background:var(--no)}}
.fecho{{background:var(--panel2);color:var(--bar-ink);border:1px solid var(--gold)}}
.fecho .selo{{margin-bottom:10px;display:inline-block}}.fecho p{{max-width:70ch}}
.tagline{{font-size:1.25rem;font-weight:800;margin-top:12px;color:#fff}}
.col,aside{{display:grid;gap:20px;align-content:start}}
dl div{{display:grid;grid-template-columns:42% 1fr;gap:10px;padding:10px 0;border-top:1px solid var(--line);font-size:.93rem}}
dl div:first-child{{border-top:0}}dt{{color:var(--muted)}}dd.na{{color:var(--muted);font-style:italic}}
.note{{font-size:.82rem;color:var(--muted);margin-top:10px}}
.pr{{display:grid;grid-template-columns:auto 1fr;gap:10px;align-items:center;padding:11px 0;border-top:1px solid var(--line)}}
.pr:first-child{{border-top:0}}
.pr-m{{width:30px;height:30px;border-radius:50%;display:grid;place-items:center;border:2px solid var(--muted);color:var(--muted);font-size:.78rem;font-weight:800}}
.pr.win .pr-m{{border:0;background:radial-gradient(circle at 35% 30%,#f7d77a,var(--gold) 60%,#b9871d)}}
.pr-t b{{display:block;font-size:.93rem}}.pr-t span{{font-size:.82rem;color:var(--muted)}}
.resumo{{font-size:.88rem;color:var(--muted);margin:-6px 0 8px}}
.fontes li{{margin:6px 0;font-size:.93rem}}.fontes span{{color:var(--muted);font-size:.85rem}}
/* blocos de leitura claros sobre a moldura preta */
.bloco.claro{{background:#f4f5f7;color:#14171c;border-color:#f4f5f7}}
.claro p,.claro .pc p{{color:#3a414c}}
.claro dt,.claro .resumo,.claro .note,.claro .pr-t span,.claro.fontes span{{color:#5a6270}}
.claro dl div,.claro .pr,.claro li{{border-color:#dde1e7}}
.claro a{{color:#1f5fae}}
.claro .ic.ok{{color:#1b7a45}}.claro .ic.no{{color:#b3263e}}
.claro .sev{{background:#e6e9ee;color:#5a6270}}.claro .sev.moderada{{background:#fdf1dc;color:#8a5200}}.claro .sev.grave{{background:#fbe4e8;color:#a3223a}}
.claro .pr-m{{border-color:#8a929e;color:#5a6270}}
.claro.quem li::before,.claro .quem li::before{{background:#1b7a45}}.claro .nao li::before{{background:#b3263e}}
footer{{background:var(--bar);color:var(--bar-ink);font-size:.88rem;border-top:1px solid var(--line)}}
.bar .ig,.bar .zap-mini{{display:flex;align-items:center;gap:6px;padding:6px 10px;border-radius:6px}}
.bar .ig{{margin-left:auto}}.bar .ig:hover{{color:var(--gold)}}
.bar .zap-mini{{background:#157a43;color:#fff}}.bar .zap-mini:hover{{background:#11683a}}
.bar .todas{{margin-left:0}}
@media (max-width:700px){{.bar .ig span,.bar .zap-mini span{{display:none}}.bar .todas{{padding:6px 10px}}}}
@media (max-width:599px){{.bar .todas{{display:none}}.bar .ig{{margin-left:auto}}.marca img{{width:68px}}footer .in{{align-items:center}}footer a{{display:inline-block;padding:6px 0}}}}
.zap{{display:flex;align-items:center;gap:12px;margin-top:16px;padding:14px 18px;border-radius:10px;background:#157a43;color:#fff;text-decoration:none;transition:background-color .2s ease,transform .2s ease}}
.zap-meio{{margin-top:0}}.zap:hover{{background:#11683a}}.zap:active{{transform:scale(.98)}}
.zap .zi{{width:30px;height:30px;flex:none}}.zap b{{display:block;font-size:1.05rem}}.zap small{{display:block;font-size:.85rem;opacity:.9}}
.comunidade p{{max-width:62ch;color:#c9cfd8}}.comunidade .acoes{{display:flex;flex-wrap:wrap;gap:12px;align-items:center}}
.ig-btn{{display:flex;align-items:center;gap:8px;margin-top:16px;padding:14px 18px;border-radius:10px;border:1px solid #2e4d7a;color:var(--ink);text-decoration:none;font-weight:700}}
.ig-btn:hover{{border-color:var(--gold);color:var(--gold)}}
.post{{display:flex;flex-wrap:wrap;gap:10px;margin-top:12px}}
.post-btn{{flex:1 1 auto;white-space:nowrap;display:flex;align-items:center;justify-content:center;gap:7px;min-height:46px;padding:10px 12px;border-radius:10px;border:1px solid #2e4d7a;background:var(--panel2);color:var(--ink);font:inherit;font-weight:700;cursor:pointer;touch-action:manipulation;transition:border-color .2s ease,transform .15s ease}}
.post-btn:hover{{border-color:var(--gold)}}.post-btn:active{{transform:scale(.97)}}
.post-st:empty,.leg-st:empty{{display:none}}.post-st,.leg-st{{font-size:.88rem;color:var(--ok-ink);margin-top:8px}}
.legenda{{margin-top:12px;padding:12px;border-radius:10px;background:#f4f5f7;color:#14171c}}
.legenda .leg-st{{color:#1b7a45;font-weight:700;margin:0 0 8px}}
.leg-txt{{white-space:pre-wrap;max-height:15em;overflow:auto;border:1px solid #dde1e7;border-radius:8px;padding:10px;font-size:.92rem;line-height:1.5;color:#14171c;background:#fff;-webkit-user-select:all;user-select:all}}
.leg-acoes{{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}}
.legenda .post-btn{{background:#0a1a33;color:#fff;border-color:#14171c}}
.leg-dica{{font-size:.8rem;color:#5a6270;margin-top:8px}}
/* layout v2 */
.v2>.col,.v2 .bloco{{min-width:0}}
.v2 .kick{{margin:0;font-size:.75rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--gold)}}
/* paleta de seções (referência: The Verge, como em notícias): filete na cor do jogo sobre o título de cada seção
   e a linha de publicação em monoespaçada */
.v2 .bloco.claro>h2,.v2 .faixa>h2,.v2 .pc2>div>h2,.v2 .preco-card>h2{{border-top:3px solid var(--acc);padding-top:10px}}

.pub{{font-family:ui-monospace,"SF Mono",SFMono-Regular,Menlo,Consolas,monospace;font-size:.72rem;text-transform:uppercase;letter-spacing:.05em}}
.r30{{background:#0e2142;border:1px solid #2e4d7a;border-left:4px solid var(--acc);display:grid;gap:14px}}
.r30-grid{{display:grid;gap:14px}}.r30 h3{{font-size:.8rem;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);margin-bottom:6px}}
.mini li{{display:flex;gap:8px;align-items:flex-start;margin:5px 0;font-weight:600;font-size:.95rem}}.mini .ic{{width:18px;height:18px;flex:none;margin-top:3px}}
.r30-pe{{display:flex;flex-wrap:wrap;gap:10px 22px;align-items:center}}
.medidor{{display:flex;align-items:center;gap:8px}}.m-k{{font-size:.8rem;color:var(--muted)}}
.m-bar,.barras .bar{{display:block;border:0;height:8px;border-radius:99px;background:#1c355e;overflow:hidden}}.m-bar{{width:110px}}
.m-bar i,.barras .bar i{{display:block;height:100%;border-radius:inherit;background:var(--acc)}}
.r30-preco{{display:flex;align-items:center;gap:8px;font-size:.92rem}}.r30-preco .ic{{color:var(--gold)}}
.r30-quem{{font-size:.92rem;color:#c9cfd8}}
.r30-premio{{display:flex;gap:8px;align-items:flex-start;font-size:.92rem;color:#c9cfd8}}.r30-premio b{{color:#fff}}
.med{{flex:none;width:16px;height:16px;margin-top:3px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#f7d77a,var(--gold) 60%,#b9871d)}}
.sub{{color:#3a414c;font-weight:600;margin:-4px 0 14px}}
.passos{{list-style:none;padding:0;margin:0;display:grid;gap:0;counter-reset:p}}
.passos li{{display:grid;grid-template-columns:40px 1fr;gap:12px;position:relative;padding-bottom:16px}}
.passos li:not(:last-child)::before{{content:"";position:absolute;left:19px;top:40px;bottom:0;width:2px;background:#dde1e7}}
.passos .n{{width:40px;height:40px;border-radius:50%;display:grid;place-items:center;background:var(--acc);color:#fff;font-weight:800;font-size:1.1rem}}
.passos h3{{font-size:1rem;font-weight:800;margin-top:8px}}.passos p{{font-size:.95rem}}
details.mais{{margin-top:6px;border-top:1px solid #dde1e7;padding-top:10px}}
details.mais summary{{cursor:pointer;font-weight:700;color:#1f5fae;list-style:none}}details.mais summary::-webkit-details-marker{{display:none}}
details.mais summary::after{{content:" ▾";content:" ▾" / ""}}details.mais[open] summary::after{{content:" ▴";content:" ▴" / ""}}details.mais[open] .leitura{{margin-top:10px}}
.fontes details.mais{{border:0;margin:0;padding:0}}.fontes summary h2{{display:inline;margin:0}}
.faixa{{background:#0c1e3c;border:1px solid #1e3a64;border-left:4px solid var(--acc)}}.faixa details.mais{{border-top-color:#1e3a64}}.faixa details.mais summary{{color:var(--link)}}.faixa .leitura p{{color:#c9cfd8}}
.cit{{margin:0 0 16px;padding:0}}.cit p{{font-size:clamp(1.4rem,4.5vw,1.9rem);line-height:1.2;font-weight:800;color:#fff;letter-spacing:-.01em}}
.cit cite{{display:block;margin-top:6px;font-style:normal;font-size:.85rem;color:var(--gold)}}
.pc2{{display:grid;gap:20px}}.pc2 ul{{display:grid;gap:10px}}
.pcc{{display:grid;grid-template-columns:auto 1fr;gap:10px;padding:12px;border-radius:8px;background:#fff;border-left:4px solid #1b7a45;box-shadow:0 1px 2px rgba(0,0,0,.06)}}
.pcc.no{{border-left-color:#b3263e}}.pcc h3{{font-size:1rem;font-weight:700}}.pcc p{{font-size:.93rem;color:#3a414c;margin-top:2px}}
.pcc summary{{cursor:pointer;list-style:none}}.pcc summary::-webkit-details-marker{{display:none}}
.pcc summary{{display:grid;grid-template-columns:1fr auto;align-items:start;gap:10px}}
.pcc .lm{{font-size:.82rem;font-weight:700;color:#1f5fae;white-space:nowrap;margin-top:2px}}.pcc .lm::after{{content:" ▾";content:" ▾" / ""}}.pcc details[open] .lm::after{{content:" ▴";content:" ▴" / ""}}.pcc details p{{margin-top:6px}}
.h3s{{font-size:.8rem;text-transform:uppercase;letter-spacing:.06em;color:#5a6270;margin:18px 0 10px}}#para-quem h2+.h3s{{margin-top:0}}
.barras li{{display:grid;grid-template-columns:minmax(120px,40%) 1fr 22px;gap:10px;align-items:center;margin:7px 0;font-size:.93rem}}
.barras .bar{{background:#e3e6eb}}.barras b{{text-align:right;font-variant-numeric:tabular-nums}}
.tiles{{display:grid;gap:10px}}.tiles li{{background:#fff;border:1px solid #dde1e7;border-radius:8px;padding:12px}}
.tn{{font-weight:800;font-size:1.05rem}}.pontos{{display:inline-flex;gap:4px;margin-left:8px;vertical-align:1px}}
.pontos i{{width:10px;height:10px;border-radius:50%;background:#dde1e7}}.pontos i.on{{background:var(--acc)}}
.nv{{margin-left:6px;font-size:.82rem;color:#5a6270}}.tiles p{{font-size:.9rem;color:#3a414c;margin-top:4px}}
.quem2{{margin-top:4px}}
.dica{{margin-top:18px;padding:12px 14px;border-radius:8px;background:#fff8e6;border-left:4px solid var(--gold)}}
.dica summary{{display:flex;align-items:center;gap:10px;cursor:pointer;list-style:none}}.dica summary::-webkit-details-marker{{display:none}}
.dica summary::after{{content:"▾";content:"▾" / "";margin-left:auto;color:#8a5200}}.dica[open] summary::after{{content:"▴";content:"▴" / ""}}
.dica .ic{{color:#8a5200;flex:none}}.dica p{{font-size:.93rem;color:#3a414c;margin-top:8px}}
details.dobra{{border:0;margin:0;padding:0}}details.dobra summary{{color:inherit}}details.dobra summary::after{{color:#5a6270}}.dobra summary h2{{display:inline;margin:0}}.dobra summary .resumo{{display:block;margin:4px 0 0}}.dobra[open] summary{{margin-bottom:12px}}
.preco-card .faixa-preco{{font-size:1.6rem;font-weight:800;letter-spacing:-.01em;color:#14171c;font-variant-numeric:tabular-nums}}
.preco-meta{{font-size:.82rem;color:#5a6270;margin:0 0 8px}}
.cards{{display:flex;gap:12px;overflow-x:auto;scroll-snap-type:x mandatory;padding-bottom:6px;margin:0 -4px}}.cards li{{flex:0 0 84%;scroll-snap-align:start;padding:0 4px}}.cards .cc{{height:100%}}.cc{{display:grid;grid-template-columns:72px 1fr;gap:12px;align-items:start;text-decoration:none;color:inherit;padding:10px;border-radius:8px;background:#fff;border:1px solid #dde1e7}}
a.cc:hover{{border-color:var(--acc)}}.cc img,.cc-ph{{width:72px;height:72px;border-radius:6px;object-fit:cover}}
.cc-ph{{display:grid;place-items:center;background:#0a1a33;color:var(--gold);font-weight:800;font-size:1.6rem}}
.cc b{{display:block}}.cc span span{{display:block;font-size:.9rem;color:#3a414c}}.cc .vr{{color:#1f5fae;font-weight:700;margin-top:4px}}
.nj li{{display:grid;gap:2px;padding:10px 0;border-top:1px solid #dde1e7}}.nj li:first-child{{border-top:0}}.nj time{{font-size:.8rem;color:#5a6270}}.nj a{{color:#1f5fae;font-weight:700;text-decoration:none}}.nj a:hover{{text-decoration:underline}}
.mais-res ul{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}
.mais-res a{{display:grid;gap:6px;text-decoration:none;color:#14171c}}
.mais-res img{{width:100%;aspect-ratio:1;object-fit:cover;border-radius:8px}}
.mais-res b{{font-size:.95rem;line-height:1.25}}.mais-res .selo{{justify-self:start;font-size:.72rem;padding:2px 8px}}
.mais-res a:hover b{{text-decoration:underline}}
.mais-res .ver-todas{{color:#fff;display:block;margin-top:16px;padding:14px;border-radius:10px;background:#0a1a33;color:#fff;text-align:center;font-weight:800;text-decoration:none}}
.mais-res .ver-todas:hover{{background:#0a1a33;color:#fff}}
@media (min-width:860px){{.mais-res ul{{grid-template-columns:repeat(3,1fr)}}}}
.v2 .fecho{{border-color:var(--acc);box-shadow:inset 4px 0 0 var(--acc)}}
.progresso{{position:fixed;top:0;left:0;right:0;height:3px;z-index:20;pointer-events:none}}.progresso i{{display:block;height:100%;width:0;background:var(--gold)}}
.voltar-topo{{position:fixed;right:14px;bottom:14px;width:44px;height:44px;border-radius:50%;display:grid;place-items:center;background:#0a1a33;color:#fff;border:1px solid #2e4d7a;opacity:0;pointer-events:none;transition:opacity .2s ease;z-index:20}}
.voltar-topo.on{{opacity:1;pointer-events:auto}}
.tiles{{grid-template-columns:repeat(3,minmax(0,1fr))}}.tiles li{{padding:10px 8px;text-align:center}}.tiles .pontos{{display:flex;justify-content:center;margin:6px 0 2px}}.tiles .nv{{display:block;margin:0}}.tiles p{{display:none}}
.tiles-txt{{margin-top:10px}}.tiles-txt li{{font-size:.9rem;color:#3a414c;margin:6px 0}}
@media (min-width:860px){{.r30-grid,.pc2{{grid-template-columns:1fr 1fr}}.cards{{display:grid;overflow:visible}}.cards li{{padding:0}}}}
@media (max-width:859px){{.v2 #premios{{order:0}}}}
@media (max-width:359px){{.tiles{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}
@media (prefers-reduced-motion:reduce){{.voltar-topo{{transition:none}}}}
footer .in{{max-width:1120px;margin:0 auto;padding:18px 16px;display:flex;flex-wrap:wrap;gap:10px 20px}}
footer a{{color:var(--bar-ink)}}
@media (min-width:860px){{
 .jogo .in{{grid-template-columns:minmax(0,420px) 1fr;gap:32px;padding-top:28px;padding-bottom:4px}}
 main{{grid-template-columns:minmax(0,1fr) 340px;align-items:start}}
 .pc,.quem,.duo{{grid-template-columns:1fr 1fr}}
 .regua{{grid-template-columns:repeat(auto-fit,minmax(120px,1fr))}}
 aside{{position:sticky;top:calc(var(--nav-h,49px) + 64px)}}
}}
@media (max-width:859px){{aside{{display:contents}}#premios{{order:-1}}}}
@media (prefers-reduced-motion:reduce){{html{{scroll-behavior:auto}}}}
{faq.CSS}
</style>
</head>
<body>
<a class="skip" href="#conteudo">Pular para o conteúdo</a>
{cabecalho("../", "Resenhas", sub=True)}

<section class="jogo"><div class="in">
 {trilha(("Início", "../"), ("Resenhas", "../estudos/"), (e(c["jogo"]), ""))}
 {topo_fig}
 <div>
  <div class="topo">
   <h1>{e(c["jogo"])}</h1>
   <div class="nota-box">{nota_html}</div>
   <p class="linha">{e(linha)}</p>
  </div>
  <div class="veredito">{selo_perfil(c, link="../")}<p>{e(c["tagline"])}</p><p class="nivel {selo_class(c["selo"])}">{e(nivel(c))}</p></div>
  <ul class="regua">{regua_html}</ul>
  <p class="lede">{e(c["lede"])}</p>
  {pub_html}
 </div>
</div>
</section>
<nav class="abas" aria-label="Seções da resenha"><ul>
<li class="li-volta"><a class="volta" href="../estudos/">{icone("voltar")}Resenhas</a></li>
{abas_html}
</ul></nav>

{main_html}

{rodape("../", barra_leitura(texto_cp(c), f"{SITE}/{slug}/"))}
<script>
(() => {{
  // Menu de seções: marca a seção que está na tela e rola o menu até ela.
  const links = [...document.querySelectorAll(".abas a[href^='#']")];
  const alvo = new Map(links.map(a => [a.getAttribute("href").slice(1), a]));
  if ("IntersectionObserver" in window && links.length) {{
    const obs = new IntersectionObserver(ents => {{
      ents.forEach(en => {{
        if (!en.isIntersecting) return;
        links.forEach(l => l.classList.remove("ativo"));
        const l = alvo.get(en.target.id);
        if (l) {{ l.classList.add("ativo"); const ul = l.closest("ul"); ul.scrollTo({{ left: l.parentElement.offsetLeft - ul.clientWidth / 2 + l.parentElement.clientWidth / 2 }}); }}
      }});
    }}, {{ rootMargin: "-45% 0px -50% 0px" }});
    alvo.forEach((_, id) => {{ const s = document.getElementById(id); if (s) obs.observe(s); }});
  }}
  // No celular, ficha, prêmios e versões começam fechados; no computador ficam abertos.
  if (innerWidth < 860) document.querySelectorAll("details.dobra").forEach(d => d.removeAttribute("open"));
  const barra = document.querySelector(".progresso i"), topo = document.querySelector(".voltar-topo");
  if (barra) {{
    const atualiza = () => {{
      const h = document.documentElement.scrollHeight - innerHeight;
      barra.style.width = (h > 0 ? scrollY / h * 100 : 0) + "%";
      topo.classList.toggle("on", scrollY > innerHeight * 1.5);
    }};
    addEventListener("scroll", atualiza, {{ passive: true }}); atualiza();
  }}
}})();
(() => {{
  const img = document.querySelector("#info img"), st = document.getElementById("salvar-st"), nome = "{slug}-portal-cristao.jpg";
  let arquivo = null;
  // Prepara o JPEG antes do toque: o compartilhamento precisa acontecer logo no clique.
  const preparar = () => {{
    if (arquivo || !img.naturalWidth) return;
    const cv = document.createElement("canvas");
    cv.width = img.naturalWidth; cv.height = img.naturalHeight;
    cv.getContext("2d").drawImage(img, 0, 0);
    cv.toBlob(b => {{ if (b) arquivo = new File([b], nome, {{ type: "image/jpeg" }}); }}, "image/jpeg", 0.92);
  }};
  if (img) img.complete ? preparar() : img.addEventListener("load", preparar);
  if (img) document.getElementById("b-salvar").addEventListener("click", async () => {{
    preparar();
    if (!arquivo) {{ st.textContent = "A imagem ainda está carregando. Tente de novo em um instante."; return; }}
    if (navigator.canShare && navigator.canShare({{ files: [arquivo] }})) {{
      try {{ await navigator.share({{ files: [arquivo] }}); st.textContent = "No menu, escolha “Salvar imagem” para mandar para a galeria."; }}
      catch (e) {{ if (e.name !== "AbortError") st.textContent = "Não deu para abrir o menu. Toque e segure na imagem e escolha “Salvar imagem”."; }}
    }} else {{
      const a = document.createElement("a");
      a.href = URL.createObjectURL(arquivo); a.download = nome; a.click();
      setTimeout(() => URL.revokeObjectURL(a.href), 4000);
      st.textContent = "Imagem salva.";
    }}
  }});
  const caixa = document.getElementById("legenda");
  if (!caixa) return;
  const txt = document.getElementById("leg-txt"), lst = caixa.querySelector(".leg-st"), btn = document.getElementById("b-legenda");
  const texto = txt.textContent;
  // Seleciona o texto e copia na hora do toque (o Brave bloqueia a API assíncrona); a API moderna entra como reforço.
  const copiar = async () => {{
    const r = document.createRange(); r.selectNodeContents(txt);
    const sel = getSelection(); sel.removeAllRanges(); sel.addRange(r);
    let ok = false;
    try {{ ok = document.execCommand("copy"); }} catch {{}}
    try {{ await navigator.clipboard.writeText(texto); ok = true; }} catch {{}}
    lst.textContent = ok ? "Legenda copiada! É só colar no Instagram." : "Não deu para copiar automático: use “Compartilhar legenda” ou segure o dedo no texto.";
  }};
  btn.addEventListener("click", () => {{ caixa.hidden = false; btn.setAttribute("aria-expanded", "true"); copiar(); }});
  document.getElementById("b-copiar").addEventListener("click", copiar);
  const comp = document.getElementById("b-compartilhar");
  if (navigator.share) {{
    comp.hidden = false;
    comp.addEventListener("click", () => navigator.share({{ text: texto }}).catch(() => {{}}));
  }}
}})();
</script>
{seo.ANALYTICS}
</body>
</html>
"""


if __name__ == "__main__":
    import og
    print("ok cartões de prévia: %d refeitos de %d" % og.gerar())
    for arg in sys.argv[1:]:
        c = json.loads(Path(arg).read_text(encoding="utf-8"))
        out = ROOT / c["slug"] / "index.html"
        out.parent.mkdir(exist_ok=True)
        out.write_text(build(c), encoding="utf-8")
        print("ok", out.relative_to(ROOT))
    import build_sitemap
    print("ok sitemap.xml (%d URLs), sitemap-noticias.xml (%d), robots.txt" % build_sitemap.atualizar()[:2])
