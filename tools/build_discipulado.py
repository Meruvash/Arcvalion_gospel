"""Gera a seção Discipulado (lições para novos convertidos) a partir de conteudo/discipulado/<slug>/.

Uso: python3 tools/build_discipulado.py   (build_home.py chama)
Cada lição publicada vai para discipulado/<slug>/; em revisão, para previa/discipulado/<slug>/ (noindex, com aviso).
A página mostra o texto do aluno (aluno.md) e, recolhido, o guia do discipulador (discipulador.md). A lista
discipulado/index.html lista as lições publicadas, da mais recente para a mais antiga (sem numeração). O tema de cada lição sai do que as pessoas estão
perguntando (skill discipulado, "Escolher o tema"), não de uma lista fixa.
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
from discipulado.checar_licao import licoes, problemas  # noqa: E402
from layout import cabecalho, convite_compartilhar, icone, rodape, trilha  # noqa: E402

GRAVIDADE = {"Leve": "info", "Moderada": "ressalvas", "Grave": "fas"}

CAPA = f"{SITE}/estudos/capa.jpg"
CSS_DISC = """<style>
.nota .licao h2{margin-top:6px}.nota .licao .corpo{max-width:66ch}
.nota .licao blockquote{margin:0;padding:12px 16px;border-left:4px solid var(--gold);background:#f6f4ee;border-radius:0 8px 8px 0;display:grid;gap:8px}
.nota .licao blockquote p{color:var(--paper-ink)}
.nota .licao h3,.nota .licao h4{font-size:1.1rem;line-height:1.3;margin-top:10px}.nota .licao ul,.nota .licao ol{display:grid;gap:8px;padding-left:22px}
.nota .licao ul{list-style:disc}.nota .licao small,.nota .licao .credito-b{font-size:.82rem;color:var(--paper-muted)}
.nota .num-l{display:inline-block;font-size:.8rem;font-weight:800;letter-spacing:.04em;text-transform:uppercase;color:var(--paper-muted)}
.nota .meta-e{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:.88rem;color:var(--paper-muted);margin-top:6px}
.nota .ideia{font-size:1.05rem;color:#3a414c;margin-top:8px}
.nota details.guia>summary{cursor:pointer;font-weight:800;font-size:1.1rem;min-height:44px;display:flex;align-items:center}
.nota details.guia[open]>summary{margin-bottom:10px}
.nota .como{font-size:.9rem;color:#3a414c}
.lista-d{display:grid;gap:8px}.lista-d li{display:grid;gap:10px;align-items:baseline;padding:10px 0;border-top:1px solid var(--paper-line,#d5dae1)}
.lista-d li:first-child{border-top:0}
/* elementos visuais (30/10/2026): o melhor das notícias e das resenhas aplicado ao estudo */
.nota .r1{background:var(--panel2);color:var(--ink);border:1px solid #2e4d7a;border-left:4px solid var(--gold);display:grid;gap:12px}
.nota .r1 .kick{font-size:.75rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--gold)}
.nota .r1 .resp{font-size:1.12rem;font-weight:600;line-height:1.45;max-width:62ch}
.nota .r1 ul{display:grid;gap:8px}.nota .r1 li{display:flex;gap:8px;align-items:flex-start;color:#dfe4ea}
.nota .r1 li .ic{flex:none;width:20px;height:20px;color:#4cc38a;margin-top:2px}
.nota .r1 .pe{display:flex;flex-wrap:wrap;gap:6px 18px;font-size:.88rem;color:var(--muted)}.nota .r1 .pe b{color:var(--ink)}
.nota .vchave{border-left:4px solid var(--gold)}.nota .vchave blockquote{margin:0;font-size:1.2rem;font-weight:600;line-height:1.45}
.nota .vchave cite{display:block;margin-top:8px;font-style:normal;font-size:.85rem;color:var(--paper-muted)}
.nota .importa{border-left:4px solid var(--gold)}.nota .importa .corpo p{font-size:1.08rem;color:var(--paper-ink)}
.nota .nums{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}
.nota .nums li{background:#fff;border:1px solid var(--paper-line);border-radius:8px;padding:12px;display:grid;gap:2px}
.nota .nums small{font-size:.72rem;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:var(--paper-muted)}
.nota .nums b{font-size:1.08rem;line-height:1.25}.nota .nums span{font-size:.86rem;color:#3a414c}
.nota .callout{border-radius:8px;padding:14px 16px;display:grid;gap:6px;margin:4px 0}
.nota .callout .rot{font-size:.72rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase}
.nota .callout p{color:var(--paper-ink)}
.nota .callout.chave{background:#fbf3dc;border:1px solid #e6cf8a}.nota .callout.chave .rot{color:#8a5a00}.nota .callout.chave p{font-size:1.05rem;font-weight:600}
.nota .callout.termo{background:#eef3fb;border:1px solid #c9d7ee}.nota .callout.termo .rot{color:#1f5fae}
.nota .callout.atencao{background:#fbeeee;border:1px solid #efc6c6}.nota .callout.atencao .rot{color:#a3223a}
.nota .citacao{margin:6px 0;padding:6px 0 6px 18px;border-left:4px solid var(--gold)}
.nota .citacao p{font-size:1.2rem;font-weight:700;line-height:1.35;color:var(--paper-ink)}.nota .citacao cite{display:block;margin-top:6px;font-style:normal;font-size:.84rem;color:var(--paper-muted)}
.nota .equivocos{display:grid;gap:10px}.nota .equivocos li{display:grid;gap:4px;padding:12px 14px;border:1px solid var(--paper-line);border-left:4px solid #b3263e;border-radius:8px;background:#fff}
.nota .equivocos h3{font-size:1rem;display:flex;flex-wrap:wrap;gap:6px 10px;align-items:center}.nota .equivocos p{color:#3a414c}
.nota .licao ul.ok{list-style:none;padding-left:0}.nota .licao ul.ok li{position:relative;padding-left:30px}
.nota .licao ul.ok li::before{content:"";position:absolute;left:4px;top:.35em;width:14px;height:8px;border-left:3px solid #1b7a45;border-bottom:3px solid #1b7a45;transform:rotate(-45deg)}
.nota .licao ol.passos{list-style:none;padding-left:0;counter-reset:p;gap:12px}.nota .licao ol.passos li{counter-increment:p;position:relative;padding-left:44px;min-height:32px}
.nota .licao ol.passos li::before{content:counter(p);position:absolute;left:0;top:-2px;width:32px;height:32px;border-radius:50%;background:var(--gold);color:#0a1a33;font-weight:800;display:grid;place-items:center}
.nota .guardar{background:var(--panel2);color:var(--ink);border:1px solid var(--gold)}.nota .guardar h2{color:var(--gold)}
.nota .guardar ul{list-style:none;padding-left:0}.nota .guardar li{color:#eceff3;font-weight:600;padding-left:26px;position:relative}
.nota .guardar li::before{content:"";position:absolute;left:2px;top:.35em;width:13px;height:7px;border-left:3px solid var(--gold);border-bottom:3px solid var(--gold);transform:rotate(-45deg)}
/* Biblioteca e Trilhas (30/10/2026) */
.busca-d{display:grid;gap:6px;margin-top:14px;font-size:.9rem;font-weight:700}
.busca-d input{font:inherit;font-weight:400;font-size:1rem;min-height:46px;padding:10px 14px;border:1px solid var(--paper-line);border-radius:10px;background:#fff;color:var(--paper-ink)}
.continue{margin-top:12px;font-size:.95rem}.continue a{font-weight:800}
.cards-d{display:grid;gap:12px}@media (min-width:700px){.cards-d{grid-template-columns:1fr 1fr}}
.cards-d li[hidden],.biblio-cat[hidden]{display:none}
.cards-d a{display:grid;gap:6px;height:100%;padding:14px;border:1px solid var(--paper-line);border-radius:10px;background:#fff;text-decoration:none;color:inherit}
.cards-d a:hover{border-color:var(--gold)}.cards-d a:hover b{text-decoration:underline}
.cards-d img{width:100%;aspect-ratio:16/9;object-fit:cover;object-position:center 30%;border-radius:6px}
.cards-d b{font-size:1.06rem;line-height:1.25}.cards-d span{color:#3a414c;font-size:.93rem}.cards-d small{color:var(--paper-muted);font-size:.82rem}
.cards-d .ja,.passos-d .ja{display:none;font-style:normal;color:#1b7a45;font-weight:700}.lido .ja{display:inline}
.trilhas-d a{border-left:4px solid var(--gold)}
.passos-d{list-style:none;counter-reset:t;display:grid;gap:10px;padding-left:0}
.passos-d li{counter-increment:t;position:relative;padding-left:46px}
.passos-d li::before{content:counter(t);position:absolute;left:0;top:12px;width:32px;height:32px;border-radius:50%;background:var(--gold);color:#0a1a33;font-weight:800;display:grid;place-items:center}
.passos-d li.lido::before{content:"✓";background:#1b7a45;color:#fff}
.passos-d a,.passos-d .cx{display:grid;gap:4px;padding:12px 14px;border:1px solid var(--paper-line);border-radius:10px;background:#fff;text-decoration:none;color:inherit}
.passos-d .cx{background:transparent;border-style:dashed;color:var(--paper-muted)}.passos-d .cx b{font-weight:600}
.passos-d li.prep::before{background:#c9ced6}
.passos-d span{color:#3a414c;font-size:.93rem}.passos-d small{color:var(--paper-muted);font-size:.82rem}
.breve-d{display:grid;gap:6px;padding-left:20px;list-style:disc;color:var(--paper-muted)}
.voltar-d{margin:4px 0 0;font-weight:700}
.nas-trilhas ul{display:grid;gap:10px}.nas-trilhas li{display:grid;gap:4px;padding:12px 14px;border:1px solid var(--paper-line);border-left:4px solid var(--gold);border-radius:8px;background:#fff}
.nas-trilhas .tn{font-weight:800}.nas-trilhas .pos{font-size:.82rem;color:var(--paper-muted)}
.nas-trilhas .nav-t{display:flex;flex-wrap:wrap;justify-content:space-between;gap:6px 14px;font-size:.92rem}.nas-trilhas .nav-t:empty{display:none}.nas-trilhas .nav-t .prox{margin-left:auto;font-weight:700}
.lista-d a{font-weight:700}.lista-d small{display:block;color:var(--paper-muted);font-size:.85rem}.lista-d .breve{color:var(--paper-muted)}
</style>"""


def inline(t):
    """Ênfase e links do Markdown dentro de uma linha, depois de escapar o HTML."""
    t = e(t)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    t = re.sub(r"\[([^\]]+)\]\((\.\./[^)\s]*)\)", r'<a href="\2">\1</a>', t)  # link interno, ex.: ../quem-e-jesus/
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    return re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", t)


ROTULOS = {"chave": "Ideia-chave", "termo": "Palavra-chave", "atencao": "Cuidado com esta leitura"}


def callout(tipo, texto):
    """Destaques no meio do texto (> [!chave], [!termo], [!atencao], [!citacao] com a última linha "Fonte: ...")."""
    if tipo == "citacao":
        corpo, _, fonte = texto.rpartition("\nFonte:")
        corpo = corpo if fonte else texto
        return (f'<figure class="citacao"><p>{inline(" ".join(corpo.split()))}</p>'
                f'{f"<cite>{inline(fonte.strip())}</cite>" if fonte else ""}</figure>')
    return f'<aside class="callout {tipo}"><span class="rot">{ROTULOS.get(tipo, tipo)}</span>{markdown(texto)}</aside>'


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
            m2 = re.match(r"^\[!(\w+)\]\s*(.*)$", dentro, re.S)
            if m2:
                out.append(callout(m2.group(1), m2.group(2).strip()))
            else:
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
    return sorted((c for c, _ in carregar() if c.get("status") == "publicado"), key=lambda c: c["publicado_em"], reverse=True)


def catalogo():
    return json.loads((ROOT / "conteudo" / "discipulado" / "base" / "catalogo.json").read_text(encoding="utf-8"))


def categoria(slug):
    return next((x for x in catalogo()["categorias"] if x["slug"] == slug), None)


def itens_trilha(t, pub):
    """[(slug ou None, título)] de uma trilha; slug None para estudo em preparação ou ainda não publicado."""
    out = []
    for it in t["estudos"]:
        if isinstance(it, str):
            c = pub.get(it)
            out.append((it if c else None, c["titulo"] if c else it))
        else:
            out.append((None, it["titulo"]))
    return out


# guarda o estudo lido no navegador do visitante (só conveniência: sem login, vale naquele aparelho)
JS_LIDO = ("(()=>{try{const k='disc.lidos',a=JSON.parse(localStorage.getItem(k)||'[]').filter(x=>x.s!==D.s);"
           "a.unshift(D);localStorage.setItem(k,JSON.stringify(a.slice(0,30)))}catch(e){}})()")
JS_LISTA = ("(()=>{let a=[];try{a=JSON.parse(localStorage.getItem('disc.lidos')||'[]')}catch(e){}"
            "const lidos=new Set(a.map(x=>x.s));document.querySelectorAll('[data-s]').forEach(li=>{if(lidos.has(li.dataset.s))li.classList.add('lido')});"
            "const c=document.getElementById('continue');if(c&&a.length){c.hidden=false;c.querySelector('a').href=PRE+'discipulado/'+a[0].s+'/';"
            "c.querySelector('a').textContent=a[0].t}"
            "const b=document.getElementById('busca-d');if(b){const cards=[...document.querySelectorAll('.biblio li[data-busca]')],v=document.getElementById('vazio-d');"
            "const n=x=>x.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase();"
            "b.addEventListener('input',()=>{const q=n(b.value.trim());let k=0;cards.forEach(li=>{const ok=!q||n(li.dataset.busca).includes(q);li.hidden=!ok;k+=ok});"
            "document.querySelectorAll('.biblio-cat').forEach(sec=>{sec.hidden=q&&!sec.querySelector('li[data-busca]:not([hidden])')});v.hidden=k>0})}})()")


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
    def secao(t, x):
        html = markdown(x, 1)
        cls = "licao"
        if t == "Questão central":
            cls = "licao importa"
        elif t == "Aplicação prática":
            html = html.replace("<ul>", '<ul class="ok">')
        elif t == "Perguntas para reflexão":
            html = html.replace("<ol>", '<ol class="passos">')
        elif t == "Resumo":
            t, cls = "Para guardar", "licao guardar"
        sec = f'<section class="bloco {cls}"><h2>{inline(t)}</h2><div class="corpo">{html}</div></section>'
        # contexto rápido antes da fundamentação; leituras equivocadas depois do desenvolvimento
        if t == "Fundamentação bíblica" and c.get("contexto"):
            tiles = "".join(f"<li><small>{e(r)}</small><b>{e(v)}</b><span>{e(d)}</span></li>" for r, v, d in c["contexto"])
            sec = f'<section class="bloco"><h2>Em poucas linhas</h2><ul class="nums">{tiles}</ul></section>' + sec
        if t == "Desenvolvimento" and c.get("equivocos"):
            cards = "".join(f'<li><h3>{e(ti)} <span class="selo {GRAVIDADE.get(g, "info")}">{e(g)}</span></h3><p>{e(x)}</p></li>'
                            for g, ti, x in c["equivocos"])
            sec += f'<section class="bloco"><h2>Leituras equivocadas</h2><ul class="equivocos">{cards}</ul></section>'
        return sec
    blocos = "".join(secao(t, x) for t, x in secoes(aluno))
    rr = c.get("resumo_rapido") or {}
    resumo = (f'<section class="bloco r1" id="resumo"><span class="kick">Resumo em 1 minuto</span><p class="resp">{e(rr["resposta"])}</p>'
              f'<ul>{"".join(f"<li>{icone("ok")}<span>{e(i)}</span></li>" for i in rr.get("ideias", []))}</ul>'
              f'<p class="pe"><span><b>Texto central:</b> {e(rr.get("texto_central", ""))}</span><span><b>Leitura:</b> cerca de {c["tempo_min"]} min</span></p></section>') if rr else ""
    vk = c.get("versiculo_chave")
    vchave = (f'<section class="bloco vchave"><h2>Versículo-chave</h2><blockquote>{e(vk["texto"])}</blockquote>'
              f'<cite>{e(vk["referencia"])} · NTLH</cite></section>') if vk else ""
    rel = c.get("relevancia") or {}
    porque = "".join(f'<li><a href="{e(x["url"])}" target="_blank" rel="noopener">{e(x["fonte"])}</a>: {e(x["dado"])}{" (" + e(x["data"]) + ")" if x.get("data") else ""}</li>'
                     for x in rel.get("evidencias", []))
    cat = categoria(c.get("categoria", ""))
    pub = {x["slug"]: x for x in publicadas()}
    nas = ""
    for t in catalogo()["trilhas"]:
        its = itens_trilha(t, pub)
        pos = next((i for i, (sl, _) in enumerate(its) if sl == c["slug"] or (previa and isinstance(t["estudos"][i], str) and t["estudos"][i] == c["slug"])), None)
        if pos is None:
            continue
        ant = next(((sl, ti) for sl, ti in reversed(its[:pos]) if sl), None)
        prox = next(((sl, ti) for sl, ti in its[pos + 1:] if sl), None)
        nas += (f'<li><a class="tn" href="{pre}discipulado/trilha/{t["slug"]}/">{e(t["nome"])}</a><span class="pos">Passo {pos + 1} de {len(its)}</span>'
                f'<span class="nav-t">{f"<a href={pre}discipulado/{ant[0]}/>&larr; {e(ant[1])}</a>" if ant else ""}'
                f'{f"<a class=prox href={pre}discipulado/{prox[0]}/>{e(prox[1])} &rarr;</a>" if prox else ""}</span></li>')
    trilhas_box = f'<section class="bloco nas-trilhas"><h2>Este estudo está nas trilhas</h2><ul>{nas}</ul><p class="como">As trilhas são sugestões de percurso. Você pode ler qualquer estudo, em qualquer ordem.</p></section>' if nas else ""
    aud = c.get("auditoria") or {}
    aviso = ('<div style="background:#ffe3e3;color:#7a1f1f;padding:8px 16px;text-align:center;font-size:.9rem"><b>Prévia em revisão.</b> '
             'Esta lição ainda não foi publicada. Não compartilhe.</div>') if previa else ""
    fig = (f'<div class="bloco abre"><figure><img src="foto.jpg" alt="{e(im["alt"])}"><figcaption class="credito">{e(im["credito"])}</figcaption></figure></div>') if im else ""
    corpo = f"""{aviso}{cabecalho(pre, "Discipulado", sub=True)}
<main id="conteudo" class="in"><div class="nota">
 {trilha(("Início", pre), ("Discipulado", f"{pre}discipulado/"), *([(e(cat["nome"]), f"{pre}discipulado/tema/{cat['slug']}/")] if cat else []), (e(c["titulo"]), ""))}
 <article class="bloco">
  <span class="num-l">{e(cat["nome"]) if cat else "Discipulado"}</span>
  <h1>{e(c["titulo"])}</h1>
  <p class="meta-e"><span>Para quem está começando</span><span>Leitura de {c["tempo_min"]} min</span><span>Texto bíblico: NTLH</span></p>
  {"" if c.get("resumo_rapido") else f'<p class="ideia">{e(c["ideia_central"])}</p>'}
  {f'<p class="meta"><time datetime="{c["publicado_em"]}">{data_longa(c["publicado_em"][:10])}</time> · Redação O Paladino</p>' if not previa else ""}
 </article>
 {resumo}
 {fig}
 {vchave}
 {blocos}
 {trilhas_box}
 {convite_compartilhar(f'{c["titulo"]} (via O Paladino)', url, "Está discipulando alguém?", "Mande esta lição para quem você acompanha.")}
 {f'<section class="bloco como"><h2>Por que esta lição</h2><p class="como">A pergunta "{e(rel["pergunta"])}" aparece com frequência nas buscas e nas redes:</p><ul class="como">{porque}</ul></section>' if rel.get("pergunta") else ""}
 <section class="bloco"><details class="guia"><summary>Guia do discipulador</summary><div class="corpo licao">{markdown(guia, 1)}</div></details></section>
 <section class="bloco como"><h2>Como foi feito</h2><p class="como">{e((c.get("ia") or {}).get("uso", ""))}</p>
 {f'<p class="como">Auditoria independente: nota preliminar {aud["nota"]} de 100, em {aud["rodadas"]} rodada{"s" if aud["rodadas"] != 1 else ""}. A nota da auditoria não substitui a leitura por pessoas do público.</p>' if aud.get("nota") else ""}</section>
</div></main>
{"" if previa else f"<script>const D={json.dumps({'s': c['slug'], 't': c['titulo']}, ensure_ascii=False)};{JS_LIDO}</script>"}
{rodape(pre)}"""
    img = f"{SITE}/discipulado/{c['slug']}/foto.jpg" if im else CAPA
    trilha_ld = seo.trilha(("Início", f"{SITE}/"), ("Discipulado", f"{SITE}/discipulado/"),
                           *([(cat["nome"], f"{SITE}/discipulado/tema/{cat['slug']}/")] if cat else []), (c["titulo"], url))
    if previa:
        ld = seo.script(trilha_ld)
    else:
        modificado = lastmod_registrado(url, {k: v for k, v in c.items() if k != "publicado_em"})
        ld = seo.script(seo.artigo("Article", url, c["titulo"], c["descricao"], img, c["publicado_em"], modificado), trilha_ld)
    (pasta / "index.html").write_text(pagina(f'{c.get("titulo_seo") or c["titulo"]} | O Paladino', c["descricao"], "" if previa else url, img,
                                             pre, corpo, "article", CSS_DISC, ld), encoding="utf-8")
    return pasta / "index.html"


def cartao(c, pre):
    """Cartão de estudo na Biblioteca e nas páginas de categoria (com o texto de busca)."""
    busca = " ".join([c["titulo"], c.get("ideia_central", ""), *c.get("palavras_chave", [])])
    img = f'<img src="{pre}discipulado/{c["slug"]}/foto.jpg" alt="" loading="lazy">' if c.get("imagem") else ""
    return (f'<li data-s="{e(c["slug"])}" data-busca="{e(busca)}"><a href="{pre}discipulado/{c["slug"]}/">{img}'
            f'<b>{e(c["titulo"])}</b><span>{e(c["ideia_central"])}</span><small>Leitura de {c["tempo_min"]} min<i class="ja"> · já lido</i></small></a></li>')


def cartao_trilha(t, pub, pre):
    its = itens_trilha(t, pub)
    prontos = sum(1 for sl, _ in its if sl)
    primeiro = next((sl for sl, _ in its if sl), None)
    return (f'<li><a href="{pre}discipulado/trilha/{t["slug"]}/"><b>{e(t["nome"])}</b><span>{e(t["descricao"])}</span>'
            f'<small>{len(its)} estudos · {prontos} {"publicado" if prontos == 1 else "publicados"}</small></a></li>')


def pagina_lista():
    """discipulado/index.html: a Biblioteca (busca, continue, categorias, destaques) e as Trilhas."""
    pre = "../"
    cat_ = catalogo()
    pub = {c["slug"]: c for c in publicadas()}
    por_cat = {}
    for c in pub.values():
        por_cat.setdefault(c.get("categoria"), []).append(c)
    destaques = "".join(cartao(c, pre) for c in sorted(pub.values(), key=lambda c: c["publicado_em"]))
    cats = "".join(
        f'<li><a href="tema/{x["slug"]}/"><b>{e(x["nome"])}</b><span>{e(x["descricao"])}</span>'
        f'<small>{len(por_cat.get(x["slug"], []))} {"estudo" if len(por_cat.get(x["slug"], [])) == 1 else "estudos"} · {len(x.get("previstos", []))} em preparação</small></a></li>'
        for x in cat_["categorias"])
    trilhas_ = "".join(cartao_trilha(t, pub, pre) for t in cat_["trilhas"])
    corpo = f"""{cabecalho(pre, "Discipulado")}
<main id="conteudo" class="in"><div class="nota">
 {trilha(("Início", pre), ("Discipulado", ""))}
 <article class="bloco"><h1>Discipulado</h1><p class="ideia">Uma biblioteca para quem está começando a seguir Jesus. Escolha o assunto que você quer entender: cada estudo se explica sozinho, sem pré-requisito. Se preferir um caminho guiado, siga uma das trilhas.</p>
  <label class="busca-d"><span>Procurar um assunto</span><input id="busca-d" type="search" placeholder="Ex.: batismo, oração, Espírito Santo" autocomplete="off"></label>
  <p id="continue" class="continue" hidden>Continue de onde parou: <a href="#"></a></p></article>
 <section class="bloco biblio"><h2>Estudos publicados</h2><ul class="cards-d">{destaques}</ul><p id="vazio-d" class="como" hidden>Nenhum estudo publicado sobre isso ainda. Veja as categorias abaixo: o assunto pode estar em preparação.</p></section>
 <section class="bloco"><h2>Trilhas de discipulado</h2><p class="como">Percursos sugeridos para quem quer orientação, sozinho ou com um discipulador. São só sugestões: você pode sair e voltar à biblioteca quando quiser.</p><ul class="cards-d trilhas-d">{trilhas_}</ul></section>
 <section class="bloco"><h2>Categorias</h2><ul class="cards-d cats-d">{cats}</ul></section>
 <section class="bloco como"><h2>Como os estudos são feitos</h2><p class="como">Cada estudo responde a uma pergunta que as pessoas estão fazendo de verdade, nas buscas e nas redes, e parte de uma passagem bíblica, com texto na Nova Tradução na Linguagem de Hoje e fontes citadas no fim. A orientação é evangélica pentecostal, e o guia do discipulador registra onde outras tradições pensam diferente.</p></section>
</div></main>
<script>const PRE="{pre}";{JS_LISTA}</script>
{rodape(pre)}"""
    url = f"{SITE}/discipulado/"
    return pagina("Discipulado: estudos para novos convertidos | O Paladino",
                  "Biblioteca de discipulado para quem está começando na fé: estudos por tema, que se explicam sozinhos, e trilhas opcionais de formação.",
                  url, CAPA, pre, corpo, "website", CSS_DISC, seo.script(seo.trilha(("Início", f"{SITE}/"), ("Discipulado", url))))


def pagina_tema(x, pub):
    """discipulado/tema/<slug>/: os estudos de uma categoria e os temas em preparação."""
    pre = "../../../"
    cards = "".join(cartao(c, pre) for c in sorted((c for c in pub.values() if c.get("categoria") == x["slug"]), key=lambda c: c["publicado_em"]))
    previstos = "".join(f"<li>{e(t)}</li>" for t in x.get("previstos", []) if t not in {c["titulo"] for c in pub.values()})
    corpo = f"""{cabecalho(pre, "Discipulado", sub=True)}
<main id="conteudo" class="in"><div class="nota">
 {trilha(("Início", pre), ("Discipulado", f"{pre}discipulado/"), (e(x["nome"]), ""))}
 <article class="bloco"><span class="num-l">Categoria</span><h1>{e(x["nome"])}</h1><p class="ideia">{e(x["descricao"])}</p></article>
 <section class="bloco biblio"><h2>Estudos</h2>{f'<ul class="cards-d">{cards}</ul>' if cards else '<p class="como">Os primeiros estudos desta categoria estão em preparação.</p>'}</section>
 {f'<section class="bloco"><h2>Em preparação</h2><ul class="breve-d">{previstos}</ul></section>' if previstos else ""}
 <p class="voltar-d"><a href="{pre}discipulado/">&larr; Voltar à biblioteca</a></p>
</div></main>
<script>const PRE="{pre}";{JS_LISTA}</script>
{rodape(pre)}"""
    url = f"{SITE}/discipulado/tema/{x['slug']}/"
    return pagina(f'{x["nome"]}: estudos de discipulado | O Paladino', f'Estudos de discipulado sobre {x["nome"].lower()}: {x["descricao"]}',
                  url, CAPA, pre, corpo, "website", CSS_DISC,
                  seo.script(seo.trilha(("Início", f"{SITE}/"), ("Discipulado", f"{SITE}/discipulado/"), (x["nome"], url))))


def pagina_trilha(t, pub):
    """discipulado/trilha/<slug>/: a sequência sugerida, com acesso direto a qualquer estudo e marca do que já foi lido."""
    pre = "../../../"
    passos = "".join(
        (f'<li data-s="{e(sl)}"><a href="{pre}discipulado/{sl}/"><b>{e(ti)}</b><span>{e(pub[sl]["ideia_central"])}</span>'
         f'<small>Leitura de {pub[sl]["tempo_min"]} min<i class="ja"> · já lido</i></small></a></li>') if sl else
        f'<li class="prep"><div class="cx"><b>{e(ti)}</b><small>Em preparação</small></div></li>'
        for sl, ti in itens_trilha(t, pub))
    corpo = f"""{cabecalho(pre, "Discipulado", sub=True)}
<main id="conteudo" class="in"><div class="nota">
 {trilha(("Início", pre), ("Discipulado", f"{pre}discipulado/"), (e(t["nome"]), ""))}
 <article class="bloco"><span class="num-l">Trilha de discipulado</span><h1>{e(t["nome"])}</h1><p class="ideia">{e(t["descricao"])}</p>
  <p class="como">A ordem é uma sugestão. Cada estudo se explica sozinho: comece por onde quiser e volte à biblioteca a qualquer momento.</p></article>
 <section class="bloco"><h2>O percurso</h2><ol class="passos-d">{passos}</ol></section>
 <p class="voltar-d"><a href="{pre}discipulado/">&larr; Voltar à biblioteca</a></p>
</div></main>
<script>const PRE="{pre}";{JS_LISTA}</script>
{rodape(pre)}"""
    url = f"{SITE}/discipulado/trilha/{t['slug']}/"
    return pagina(f'Trilha {t["nome"]} | Discipulado | O Paladino', t["descricao"], url, CAPA, pre, corpo, "website", CSS_DISC,
                  seo.script(seo.trilha(("Início", f"{SITE}/"), ("Discipulado", f"{SITE}/discipulado/"), (t["nome"], url))))


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
    pub = {c["slug"]: c for c in publicadas()}
    cat_ = catalogo()
    for x in cat_["categorias"]:
        d = ROOT / "discipulado" / "tema" / x["slug"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(pagina_tema(x, pub), encoding="utf-8")
    for t in cat_["trilhas"]:
        d = ROOT / "discipulado" / "trilha" / t["slug"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(pagina_trilha(t, pub), encoding="utf-8")
    return feitos


if __name__ == "__main__":
    for f in todos():
        print("ok", f.relative_to(ROOT))
