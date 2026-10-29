"""Agenda, Livros da Bíblia, páginas institucionais, 404, RSS, sitemaps, robots.txt, llms.txt e índice da busca.

Equivalências com o Elite Boardgamers: Agenda ← calendário de lançamentos (/lancamentos/); Livros da Bíblia ← Consulta
Golden Geek (/consulta/); política editorial e institucionais ← build_politica() de build_home.py; sitemaps, robots e
llms.txt ← build_sitemap.py e build_llms.py; busca.json ← busca.py.
"""
import json
import re
from datetime import date, datetime, timedelta
from xml.sax.saxutils import escape as xesc

import portal
import seo
import imagens
from pagina import BRT, MESES, MES_CURTO, data_curta, data_longa, e, escrever, pagina, quando, capa_secao, hoje
from layout import cabecalho, formulario, rodape, trilha

# Cânon protestante: (sigla, nome, capítulos, grupo). Somas conferidas: 929 capítulos no AT e 260 no NT.
LIVROS = {
    "Antigo Testamento": [
        ("Gn", "Gênesis", 50, "Pentateuco"), ("Êx", "Êxodo", 40, "Pentateuco"), ("Lv", "Levítico", 27, "Pentateuco"),
        ("Nm", "Números", 36, "Pentateuco"), ("Dt", "Deuteronômio", 34, "Pentateuco"),
        ("Js", "Josué", 24, "Históricos"), ("Jz", "Juízes", 21, "Históricos"), ("Rt", "Rute", 4, "Históricos"),
        ("1Sm", "1 Samuel", 31, "Históricos"), ("2Sm", "2 Samuel", 24, "Históricos"), ("1Rs", "1 Reis", 22, "Históricos"),
        ("2Rs", "2 Reis", 25, "Históricos"), ("1Cr", "1 Crônicas", 29, "Históricos"), ("2Cr", "2 Crônicas", 36, "Históricos"),
        ("Ed", "Esdras", 10, "Históricos"), ("Ne", "Neemias", 13, "Históricos"), ("Et", "Ester", 10, "Históricos"),
        ("Jó", "Jó", 42, "Poéticos e sabedoria"), ("Sl", "Salmos", 150, "Poéticos e sabedoria"), ("Pv", "Provérbios", 31, "Poéticos e sabedoria"),
        ("Ec", "Eclesiastes", 12, "Poéticos e sabedoria"), ("Ct", "Cânticos", 8, "Poéticos e sabedoria"),
        ("Is", "Isaías", 66, "Profetas maiores"), ("Jr", "Jeremias", 52, "Profetas maiores"), ("Lm", "Lamentações", 5, "Profetas maiores"),
        ("Ez", "Ezequiel", 48, "Profetas maiores"), ("Dn", "Daniel", 12, "Profetas maiores"),
        ("Os", "Oseias", 14, "Profetas menores"), ("Jl", "Joel", 3, "Profetas menores"), ("Am", "Amós", 9, "Profetas menores"),
        ("Ob", "Obadias", 1, "Profetas menores"), ("Jn", "Jonas", 4, "Profetas menores"), ("Mq", "Miqueias", 7, "Profetas menores"),
        ("Na", "Naum", 3, "Profetas menores"), ("Hc", "Habacuque", 3, "Profetas menores"), ("Sf", "Sofonias", 3, "Profetas menores"),
        ("Ag", "Ageu", 2, "Profetas menores"), ("Zc", "Zacarias", 14, "Profetas menores"), ("Ml", "Malaquias", 4, "Profetas menores")],
    "Novo Testamento": [
        ("Mt", "Mateus", 28, "Evangelhos"), ("Mc", "Marcos", 16, "Evangelhos"), ("Lc", "Lucas", 24, "Evangelhos"), ("Jo", "João", 21, "Evangelhos"),
        ("At", "Atos", 28, "Histórico"),
        ("Rm", "Romanos", 16, "Cartas de Paulo"), ("1Co", "1 Coríntios", 16, "Cartas de Paulo"), ("2Co", "2 Coríntios", 13, "Cartas de Paulo"),
        ("Gl", "Gálatas", 6, "Cartas de Paulo"), ("Ef", "Efésios", 6, "Cartas de Paulo"), ("Fp", "Filipenses", 4, "Cartas de Paulo"),
        ("Cl", "Colossenses", 4, "Cartas de Paulo"), ("1Ts", "1 Tessalonicenses", 5, "Cartas de Paulo"), ("2Ts", "2 Tessalonicenses", 3, "Cartas de Paulo"),
        ("1Tm", "1 Timóteo", 6, "Cartas de Paulo"), ("2Tm", "2 Timóteo", 4, "Cartas de Paulo"), ("Tt", "Tito", 3, "Cartas de Paulo"),
        ("Fm", "Filemom", 1, "Cartas de Paulo"),
        ("Hb", "Hebreus", 13, "Cartas gerais"), ("Tg", "Tiago", 5, "Cartas gerais"), ("1Pe", "1 Pedro", 5, "Cartas gerais"),
        ("2Pe", "2 Pedro", 3, "Cartas gerais"), ("1Jo", "1 João", 5, "Cartas gerais"), ("2Jo", "2 João", 1, "Cartas gerais"),
        ("3Jo", "3 João", 1, "Cartas gerais"), ("Jd", "Judas", 1, "Cartas gerais"),
        ("Ap", "Apocalipse", 22, "Profético")],
}
assert sum(x[2] for x in LIVROS["Antigo Testamento"]) == 929 and sum(x[2] for x in LIVROS["Novo Testamento"]) == 260
assert len(LIVROS["Antigo Testamento"]) == 39 and len(LIVROS["Novo Testamento"]) == 27


def agenda_eventos():
    arq = portal.CONTEUDO / "agenda.json"
    evs = json.loads(arq.read_text(encoding="utf-8")).get("eventos", []) if arq.exists() else []
    for ev in evs:
        if not ev.get("nome") or not re.match(r"\d{4}-\d{2}-\d{2}", ev.get("inicio", "")) or not (ev.get("fonte") or {}).get("url"):
            raise SystemExit(f"agenda: {ev.get('nome')!r} precisa de nome, inicio (AAAA-MM-DD) e fonte com link")
    return sorted((ev for ev in evs if (ev.get("fim") or ev["inicio"])[:10] >= hoje().isoformat()), key=lambda ev: ev["inicio"])


def build_agenda(evs):
    """Agenda por mês, no molde do calendário de lançamentos do Elite (um bloco por mês, itens com data em destaque)."""
    pre = "../"
    por_mes = {}
    for ev in evs:
        por_mes.setdefault(ev["inicio"][:7], []).append(ev)
    blocos = ""
    for mes, lista in por_mes.items():
        a, m = int(mes[:4]), int(mes[5:7])
        itens = ""
        for ev in lista:
            d = date.fromisoformat(ev["inicio"][:10])
            onde = "On-line" if ev.get("online") else ", ".join(x for x in (ev.get("local"), f"{ev.get('cidade', '')}{' (' + ev['uf'] + ')' if ev.get('uf') else ''}") if x)
            alvo = f'{pre}noticias/{ev["materia"]}/' if ev.get("materia") else ev.get("url", "")
            nome = f'<a href="{e(alvo)}"{" target=_blank rel=noopener" if alvo.startswith("http") else ""}>{e(ev["nome"])}</a>' if alvo else e(ev["nome"])
            fim = f" a {data_curta(ev['fim'])}" if ev.get("fim") and ev["fim"][:10] != ev["inicio"][:10] else ""
            marcas = ("" if ev.get("confirmado", True) else " · <small>data a confirmar</small>") + (" · <small>divulgação paga</small>" if ev.get("patrocinado") else "")
            itens += (f'<li><span class="q">{d.day:02d} {MES_CURTO[d.month - 1]}{fim}</span><span><b>{nome}</b><br><span class="d">{e(onde)}'
                      f'{" · " + e(ev["organizador"]) if ev.get("organizador") else ""}{marcas} · fonte: <a href="{e(ev["fonte"]["url"])}" target="_blank" rel="noopener">{e(ev["fonte"]["nome"])}</a></span></span></li>')
        blocos += f'<section class="bloco agenda" id="{mes}"><h2>{MESES[m - 1].capitalize()} de {a}</h2><ul>{itens}</ul></section>'
    corpo = f"""{cabecalho(pre, "Agenda")}
<main id="conteudo" class="in arq">
 <div class="arq-topo"><h1>Agenda cristã</h1><p>Congressos, conferências, shows, encontros e feiras, com data, local e fonte. Evento só entra conferido; data não confirmada aparece como tal. <a href="{pre}contato/#evento" style="color:var(--gold)">Divulgue o seu evento</a>.</p></div>
 {blocos or '<section class="bloco"><p>Nenhum evento confirmado no momento.</p></section>'}
</main>
{rodape(pre)}"""
    eventos_ld = [seo.evento(ev) for ev in evs if ev.get("confirmado", True) and not ev.get("patrocinado")]
    escrever("agenda/index.html", pagina(f"Agenda cristã | {portal.NOME}", "Congressos, conferências, shows e encontros cristãos, com data, local e fonte.",
                                         f"{portal.SITE}/agenda/", capa_secao(), pre, corpo, indexavel=bool(evs),
                                         jsonld=seo.script(seo.trilha(("Início", f"{portal.SITE}/"), ("Agenda", f"{portal.SITE}/agenda/")), *eventos_ld)))


JS_BIBLIA = """(()=>{const q=document.getElementById('bq'),g=document.querySelector('.cats'),lis=[...document.querySelectorAll('.livros li')];let t='';
const norm=s=>s.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase();
const ap=()=>{const v=norm(q.value.trim());let n=0;lis.forEach(li=>{const ok=(!t||li.dataset.t===t)&&(!v||norm(li.dataset.n).includes(v));li.hidden=!ok;n+=ok});
document.querySelectorAll('.livros section').forEach(s=>s.hidden=![...s.querySelectorAll('li')].some(li=>!li.hidden));document.getElementById('bq-n').textContent=n+' livro'+(n==1?'':'s')};
g.hidden=false;g.addEventListener('click',ev=>{const b=ev.target.closest('button');if(!b)return;t=b.dataset.c;g.querySelectorAll('button').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));ap()});
q.addEventListener('input',ap);ap()})()"""


def build_biblia(estudos):
    """Livros da Bíblia: a consulta do portal (no Elite, a Consulta Golden Geek). Busca por nome e filtro por testamento."""
    pre = "../"
    por_livro = {}
    for c in estudos:
        if c.get("status") == "publicado":
            por_livro.setdefault(c.get("livro", ""), []).append(c)
    secoes = ""
    for test, livros in LIVROS.items():
        grupos = {}
        for sig, nome, cap, grupo in livros:
            grupos.setdefault(grupo, []).append((sig, nome, cap))
        for grupo, itens in grupos.items():
            lis = "".join(
                f'<li data-t="{test[:1]}" data-n="{e(nome)} {e(sig)}"><b>{e(nome)}</b><span class="meta">{e(sig)} · {cap} capítulo{"s" if cap > 1 else ""}</span>'
                + "".join(f' <a href="{pre}estudos/{c["slug"]}/">Estudo: {e(c["titulo"])}</a>' for c in por_livro.get(nome, [])) + "</li>"
                for sig, nome, cap in itens)
            secoes += f'<section class="bloco"><h2>{e(grupo)} <span class="meta">{e(test)}</span></h2><ul class="lista-n livros-l">{lis}</ul></section>'
    corpo = f"""{cabecalho(pre, "Livros da Bíblia")}
<main id="conteudo" class="in arq">
 <div class="arq-topo"><h1>Livros da Bíblia</h1><p>Os 66 livros do cânon protestante, com a sigla, o número de capítulos e os nossos estudos de cada um: 39 do Antigo Testamento (929 capítulos) e 27 do Novo (260 capítulos).</p></div>
 <div class="cats" role="group" aria-label="Filtrar por testamento" hidden><button type="button" data-c="" aria-pressed="true">Todos<small>66</small></button><button type="button" data-c="A" aria-pressed="false">Antigo Testamento<small>39</small></button><button type="button" data-c="N" aria-pressed="false">Novo Testamento<small>27</small></button></div>
 <label class="busca-l"><span class="sr">Buscar livro</span><input id="bq" type="search" placeholder="Buscar livro pelo nome ou sigla" autocomplete="off"></label> <span id="bq-n" class="meta" aria-live="polite"></span>
 <div class="livros">{secoes}</div>
</main>
{rodape(pre)}
<script>{JS_BIBLIA}</script>"""
    css_extra = (".busca-l input{width:min(420px,100%);font:inherit;font-size:16px;padding:10px 14px;border-radius:10px;border:1px solid #2e4d7a;background:#0f2242;color:#eceff3}"
                 ".livros{display:grid;gap:16px}.livros-l li{display:flex;flex-wrap:wrap;gap:4px 12px;align-items:baseline;padding:10px 0}.livros-l a{color:var(--link);font-weight:700}"
                 ".livros section[hidden],.livros li[hidden]{display:none}.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%)}")
    import estilo_elite as est
    escrever("biblia/index.html", pagina(f"Livros da Bíblia | {portal.NOME}", "Os 66 livros da Bíblia com sigla, capítulos e estudos bíblicos de cada um.",
                                         f"{portal.SITE}/biblia/", capa_secao(), pre, corpo, css=est.CSS_HOME % {"pre": pre} + css_extra,
                                         jsonld=seo.script(seo.trilha(("Início", f"{portal.SITE}/"), ("Livros da Bíblia", f"{portal.SITE}/biblia/")))))


def preencher(texto, pre="../"):
    cfg = portal.CFG
    valores = {"nome": portal.NOME, "url": portal.SITE, "descricao": cfg.get("descricao", ""), "slogan": cfg.get("slogan", ""),
               "email_contato": cfg.get("email_contato", ""), "email_comercial": cfg.get("email_comercial") or cfg.get("email_contato", ""),
               "email_correcoes": cfg.get("email_correcoes") or cfg.get("email_contato", ""),
               "responsavel": (cfg.get("responsavel_editorial") or {}).get("nome", ""), "razao_social": cfg.get("razao_social") or portal.NOME,
               "cnpj": cfg.get("cnpj", ""), "fundacao": cfg.get("fundacao", "")}

    def troca(m):
        v = valores.get(m.group(1))
        if v is None:
            return m.group(0)
        if not v:
            return '<span class="pend">a definir</span>'
        return f'<a href="mailto:{e(v)}">{e(v)}</a>' if m.group(1).startswith("email") else e(v)
    s = re.sub(r"\{([a-z_]+)\}", troca, e(texto).replace("&#x27;", "'"))
    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: f'<a href="{pre + m.group(2)[1:] if m.group(2).startswith("/") else m.group(2)}">{m.group(1)}</a>', s)


def gerados(tipo, pre):
    if tipo == "equipe":
        resp = portal.CFG.get("responsavel_editorial") or {}
        itens = "".join(f'<li><b>{e(p["nome"])}</b>, {e(p.get("cargo", ""))}</li>' for p in portal.EQUIPE.values())
        r = (f'<p><b>{e(resp.get("cargo", "Responsável editorial"))}:</b> {e(resp["nome"])}</p>' if resp.get("nome")
             else '<p><span class="pend">Responsável editorial a definir</span></p>')
        return r + (f'<ul class="equipe">{itens}</ul>' if itens else '<p><span class="pend">Equipe a cadastrar</span></p>')
    if tipo == "editorias":
        com = {n["categoria"] for n in _NOTAS}
        return "<ul>" + "".join((f'<li><a href="{pre}noticias/categoria/{x["slug"]}/">{e(x["nome"])}</a>: ' if x["slug"] in com else f'<li><b>{e(x["nome"])}</b>: ')
                                + f'{e(x["descricao"])}</li>' for x in portal.visiveis()) + "</ul>"
    if tipo == "espacos":
        return "<ul>" + "".join(f'<li><b>{e(x["descricao"])}</b></li>' for x in portal.ANUNCIOS.get("espacos", []) if x.get("descricao")) + "</ul>"
    return ""


_NOTAS = []


def build_institucionais(ns=()):
    _NOTAS[:] = [n for n in ns if n.get("status", "publicado") == "publicado"]
    """Páginas de conteudo/paginas/*.json no estilo da política editorial do Elite (blocos claros sobre a moldura)."""
    feitas = []
    api = (portal.CFG.get("interacoes") or {}).get("api")
    for arq in sorted((portal.ROOT / "conteudo" / "paginas").glob("*.json")):
        p = json.loads(arq.read_text(encoding="utf-8"))
        pre = "../"
        url = f"{portal.SITE}/{p['slug']}/"
        secoes = ""
        for s in p.get("secoes", []):
            if s.get("so_com_api") and not api:
                continue
            pars = "".join(f"<p>{preencher(x, pre)}</p>" for x in s.get("paragrafos", []))
            lista = "".join(f"<li>{preencher(x, pre)}</li>" for x in s.get("lista", []))
            form = formulario(s["formulario"], pre, p["slug"]) if s.get("formulario") else ""
            ger = gerados(s["gerado"], pre) if s.get("gerado") else ""
            secoes += (f'<section class="bloco"{f" id=\"{s["id"]}\"" if s.get("id") else ""}><h2>{e(s["titulo"])}</h2><div class="corpo">{pars}'
                       f'{f"<ul>{lista}</ul>" if lista else ""}{ger}{form}</div></section>')
        corpo = f"""{cabecalho(pre, "")}
<main id="conteudo" class="in"><div class="nota">
 <article class="bloco">
  <h1>{e(p["titulo"])}</h1>
  <p class="lide">{preencher(p["lide"], pre)}</p>
 </article>
{secoes}
</div></main>
{rodape(pre)}"""
        ld = seo.script({"@type": p.get("schema", "WebPage"), "@id": url, "url": url, "name": p["titulo"], "inLanguage": "pt-BR", "publisher": {"@id": seo.org_id()}},
                        seo.trilha(("Início", f"{portal.SITE}/"), (p["titulo"], url)))
        escrever(f"{p['slug']}/index.html", pagina(f"{p['titulo']} | {portal.NOME}", re.sub(r"\{[a-z_]+\}", portal.NOME, p["descricao"]), url, capa_secao(), pre, corpo, jsonld=ld))
        feitas.append((p["slug"], p.get("atualizado_em")))
    return feitas


def build_404():
    pre = portal.BASE + "/"
    corpo = f"""{cabecalho(pre, "")}
<main id="conteudo" class="in"><div class="nota"><section class="bloco">
 <h1>Página não encontrada</h1>
 <p class="lide">O endereço pode ter mudado ou sido digitado errado. Veja o que há de novo:</p>
 <div class="jogos"><a href="{pre}">Notícias de hoje</a><a href="{pre}estudos/">Estudos bíblicos</a><a href="{pre}agenda/">Agenda</a><a href="{pre}biblia/">Livros da Bíblia</a></div>
</section></div></main>
{rodape(pre, "")}"""
    escrever("404.html", pagina(f"Página não encontrada | {portal.NOME}", "Página não encontrada.", "", capa_secao(), pre, corpo, indexavel=False))


def build_feed(ns):
    itens = []
    for n in [x for x in ns if x.get("status", "publicado") == "publicado"][:30]:
        d = quando(n["publicado_em"])
        u = f"{portal.SITE}/noticias/{n['slug']}/"
        itens.append(f"<item><title>{xesc(n['titulo'])}</title><link>{xesc(u)}</link><guid isPermaLink=\"true\">{xesc(u)}</guid>"
                     f"<pubDate>{d.strftime('%a, %d %b %Y %H:%M:%S %z')}</pubDate><category>{xesc(portal.editoria(n['categoria'])['nome'])}</category>"
                     f"<description>{xesc(n['lide'])}</description></item>")
    escrever("feed.xml", f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>
<title>{xesc(portal.NOME)}</title><link>{xesc(portal.SITE)}/</link><description>{xesc(portal.CFG.get('descricao', ''))}</description><language>pt-br</language>
<atom:link href="{xesc(portal.SITE)}/feed.xml" rel="self" type="application/rss+xml"/>
{chr(10).join(itens)}
</channel></rss>
""")


def build_sitemaps(ns, estudos, evs, institucionais):
    pub = [n for n in ns if n.get("status", "publicado") == "publicado"]
    est = [c for c in estudos if c.get("status") == "publicado"]
    lm = lambda x: x.get("atualizado_em") or x.get("publicado_em")  # noqa: E731
    maior = lambda lista: max((lm(x) for x in lista if lm(x)), key=lambda d: quando(d), default=None)  # noqa: E731
    ent = [(f"{portal.SITE}/", maior(pub + est)), (f"{portal.SITE}/noticias/", maior(pub)), (f"{portal.SITE}/biblia/", None)]
    if est:
        ent.append((f"{portal.SITE}/estudos/", maior(est)))
    if evs:
        ent.append((f"{portal.SITE}/agenda/", None))
    for x in portal.visiveis():
        lista = [n for n in pub if n["categoria"] == x["slug"]]
        if lista:
            ent.append((f"{portal.SITE}/noticias/categoria/{x['slug']}/", maior(lista)))
    ent += [(f"{portal.SITE}/noticias/{n['slug']}/", lm(n)) for n in pub]
    ent += [(f"{portal.SITE}/estudos/{c['slug']}/", lm(c)) for c in est]
    ent += [(f"{portal.SITE}/{s}/", d) for s, d in institucionais]
    linhas = "\n".join(f"  <url><loc>{xesc(u)}</loc>{f'<lastmod>{d}</lastmod>' if d else ''}</url>" for u, d in ent)
    escrever("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{linhas}\n</urlset>\n')
    limite = datetime.now(BRT) - timedelta(hours=48)
    recentes = [n for n in pub if quando(n["publicado_em"]) >= limite]
    news = "".join(f"""  <url><loc>{xesc(portal.SITE)}/noticias/{n['slug']}/</loc><news:news><news:publication><news:name>{xesc(portal.NOME)}</news:name><news:language>pt</news:language></news:publication>"""
                   f"""<news:publication_date>{n['publicado_em']}</news:publication_date><news:title>{xesc(n['titulo'])}</news:title></news:news></url>\n""" for n in recentes)
    escrever("sitemap-noticias.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
             f'xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">\n{news}</urlset>\n')
    return len(ent), len(recentes)


TREINO_IA = ["GPTBot", "Google-Extended", "CCBot", "ClaudeBot", "anthropic-ai", "Applebot-Extended", "Bytespider", "meta-externalagent"]


def build_robots():
    if portal.EXEMPLO:
        escrever("robots.txt", "User-agent: *\nDisallow: /\n")
        return
    bloq = ""
    if (portal.CFG.get("robots") or {}).get("bloquear_treino_ia"):
        bloq = "\n" + "".join(f"User-agent: {b}\n" for b in TREINO_IA) + "Disallow: /\n"
    escrever("robots.txt", f"""# {portal.NOME}: todos os robôs de busca e de IA são bem-vindos.
User-agent: *
Allow: /
Disallow: {portal.BASE}/previa/
{bloq}
Sitemap: {portal.SITE}/sitemap.xml
Sitemap: {portal.SITE}/sitemap-noticias.xml
""")


def build_llms(ns, estudos):
    pub = [n for n in ns if n.get("status", "publicado") == "publicado"]
    linhas = [f"# {portal.NOME}", "", f"> {portal.CFG.get('descricao', '')} Portal cristão de notícias e estudos bíblicos, em português do Brasil.", "",
              "Toda notícia lista as fontes consultadas, com data, separa fato de opinião e passa por revisão humana antes de publicar.", "",
              "## Estudos bíblicos", ""]
    linhas += [f"- [{c['titulo']}]({portal.SITE}/estudos/{c['slug']}/): {c['tagline']}" for c in estudos if c.get("status") == "publicado"]
    linhas += ["", "## Notícias recentes", ""] + [f"- [{n['titulo']}]({portal.SITE}/noticias/{n['slug']}/) ({n['data']})" for n in pub[:20]]
    linhas += ["", "## Referências", "", f"- [Livros da Bíblia]({portal.SITE}/biblia/)", f"- [Agenda cristã]({portal.SITE}/agenda/)",
               f"- [Política editorial]({portal.SITE}/politica-editorial/)", ""]
    escrever("llms.txt", "\n".join(linhas))


def build_busca(ns, estudos):
    regs = [{"t": "n", "n": n["titulo"], "s": f"{portal.editoria(n['categoria'])['nome']} · {data_curta(n['data'])}", "u": f"noticias/{n['slug']}/"}
            for n in ns if n.get("status", "publicado") == "publicado"]
    regs += [{"t": "r", "n": c["titulo"], "s": c["passagem"], "u": f"estudos/{c['slug']}/"} for c in estudos if c.get("status") == "publicado"]
    regs += [{"t": "l", "n": nome, "s": f"{test} · {cap} capítulos", "u": "biblia/", "a": sig} for test, ls in LIVROS.items() for sig, nome, cap, _ in ls]
    escrever("busca.json", json.dumps(regs, ensure_ascii=False, separators=(",", ":")))
    return len(regs)
