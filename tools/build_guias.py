"""Páginas-guia "Melhores jogos de tabuleiro para…" e a página /jogos-de-tabuleiro/ que liga todas.

Uso: python3 tools/build_guias.py   (também roda no fim de build_home.py e de publicar.py)
Cada guia junta as resenhas publicadas que atendem a um critério verificável, a partir dos mesmos dados dos filtros
de /estudos/ (tools/filtros_resenha.py): primeiro os jogos cujo perfil principal ("melhor_para") é o do guia, depois
os que atendem ao critério pelos dados, por nota BGG. Guia com menos de MINIMO jogos não é publicado (página rala não
ajuda o leitor nem o Google); se já existia, sai do ar até ter jogos suficientes.
"""
import html
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import faq  # noqa: E402
import seo  # noqa: E402
from build_home import pagina  # noqa: E402
from build_review import ROOT, SITE, data_longa, nome_br, versao  # noqa: E402
from filtros_resenha import derivar  # noqa: E402
from imagens_resp import srcset  # noqa: E402
from layout import cabecalho, rodape, trilha  # noqa: E402

e = html.escape
MINIMO = 3
BASE = "jogos-de-tabuleiro"

# perfil: (slug, título da página, frase do cartão no guia geral, critério visível, introdução, regra pelos dados, filtro em /estudos/)
GUIAS = {
    "melhores": ("melhores", "Os melhores jogos de tabuleiro premiados",
                 "Os mais premiados entre todos os que resenhamos.",
                 "número de vitórias em prêmios (cada categoria conta) e, no empate, nota no BoardGameGeek",
                 "Uma lista para quem quer ir direto ao que a crítica e os jogadores mais premiaram: Spiel des Jahres, "
                 "Kennerspiel, As d'Or, Deutscher Spiele Preis e Golden Geek. Todos têm resenha completa no site, com "
                 "pontos fortes, pontos de atenção e para quem é cada um.",
                 lambda d: True, "ordem=nota"),
    "familia": ("para-familia", "Melhores jogos de tabuleiro para família",
                "Para jogar com crianças, pais e avós na mesma mesa.",
                "idade mínima de até 10 anos, peso no BoardGameGeek até 2,5, partidas de até 1 hora e espaço para 4 pessoas ou mais",
                "Jogo de família precisa caber na idade da criança, ser explicado rápido e acabar antes do cansaço, sem "
                "deixar os adultos entediados. Estes premiados atendem a tudo isso.",
                lambda d: d["idade"] is not None and d["idade"] <= 10 and d["peso"] is not None and d["peso"] <= 2.5
                and d["duracao"] and d["duracao"][1] <= 60 and d["jogadores"] and d["jogadores"][1] >= 4, "idade=10"),
    "entrada": ("para-iniciantes", "Melhores jogos de tabuleiro para iniciantes",
                "Regras curtas, partida rápida e diversão já na primeira mesa.",
                "peso no BoardGameGeek abaixo de 2 (numa escala de 1 a 5) e partidas de até 45 minutos",
                "Para começar nos jogos de tabuleiro modernos, o que mais pesa é explicar as regras em poucos minutos e "
                "terminar a partida antes de alguém perder o interesse. Estes jogos premiados cumprem as duas coisas e "
                "funcionam com quem nunca jogou nada além dos clássicos.",
                lambda d: d["peso"] is not None and d["peso"] < 2 and d["duracao"] and d["duracao"][1] <= 45, "peso=leve"),
    "dupla": ("para-dois-jogadores", "Melhores jogos de tabuleiro para dois jogadores",
              "Para casais e duplas: jogos que brilham com duas pessoas.",
              "2 jogadores é uma das melhores contagens, segundo a seção \"Com quantos jogar\" de cada resenha",
              "Muito jogo diz \"de 2 a 4 jogadores\", mas fica sem graça a dois. Aqui só entram os que a própria resenha "
              "aponta como ótimos com duas pessoas, seja por serem feitos para dupla, seja porque a disputa fica mais "
              "afiada assim.",
              lambda d: 2 in d["melhor"], "jogadores=2&melhor=on"),
    "festa": ("para-festa-e-grupos", "Melhores jogos de tabuleiro para festa e grupos grandes",
              "Muita gente na mesa, risada e partidas curtas.",
              "aceitam 6 pessoas ou mais e são melhores com 5 ou mais",
              "Para a reunião de família ou a noite com amigos, o jogo precisa receber todo mundo, ser explicado em "
              "minutos e render conversa. Estes são os premiados que fazem isso melhor.",
              lambda d: d["jogadores"] and d["jogadores"][1] >= 6 and any(m >= 5 for m in d["melhor"]), "jogadores=6"),
    "cooperativo": ("cooperativos", "Melhores jogos de tabuleiro cooperativos",
                    "Todos juntos contra o jogo: ganham ou perdem em equipe.",
                    "jogos cooperativos ou semicooperativos",
                    "Nos jogos cooperativos, a mesa inteira joga contra o próprio jogo: ninguém fica para trás e a vitória é "
                    "de todos. São ótimos para quem não gosta de disputa direta e para grupos com níveis diferentes de "
                    "experiência.",
                    lambda d: bool({"Cooperativo", "Semicooperativo"} & set(d["estilos"])), "estilo=Cooperativo"),
    "solo": ("para-jogar-sozinho", "Melhores jogos de tabuleiro para jogar sozinho",
             "Modo solo oficial que funciona de verdade.",
             "têm modo solo oficial e a resenha aponta 1 jogador como uma das melhores contagens",
             "Jogar sozinho virou um jeito comum de aproveitar a coleção. Mas nem todo modo solo é bom: aqui só entram "
             "jogos em que jogar sozinho aparece como uma das melhores formas de jogar, segundo a própria resenha.",
             lambda d: d["solo"] and 1 in d["melhor"], "jogadores=1&melhor=on"),
    "proximo": ("peso-medio", "Jogos de tabuleiro de peso médio: o próximo passo",
                "Para quem já passou dos jogos de entrada e quer mais decisões.",
                "peso no BoardGameGeek entre 2 e 3",
                "Depois dos primeiros jogos, muita gente quer partidas com mais escolhas, sem chegar aos jogos de três "
                "horas. Estes premiados ficam nesse meio: mais profundos que os de entrada e ainda fáceis de levar para "
                "a mesa.",
                lambda d: d["peso"] is not None and 2 <= d["peso"] <= 3, "peso=media"),
    "estrategia": ("estrategia", "Melhores jogos de tabuleiro de estratégia",
                   "Jogos pesados, com planejamento de longo prazo.",
                   "peso no BoardGameGeek a partir de 3,2",
                   "Para quem gosta de planejar várias rodadas à frente e não se importa com partidas longas. São os "
                   "jogos mais exigentes entre as nossas resenhas, e também os que mais recompensam quem joga de novo.",
                   lambda d: d["peso"] is not None and d["peso"] >= 3.2, "peso=pesada"),
    "campanha": ("campanha-e-legacy", "Jogos de tabuleiro de campanha e legacy",
                 "Uma história que continua de uma partida para a outra.",
                 "jogos de campanha ou legacy, em que as partidas se ligam",
                 "Nos jogos de campanha, cada partida continua a anterior; nos legacy, o próprio jogo muda para sempre. "
                 "Pedem um grupo fixo, mas entregam algo que nenhum outro estilo entrega: uma história construída pela mesa.",
                 lambda d: "Campanha" in d["estilos"], "estilo=Campanha"),
    "tema": ("tematicos", "Melhores jogos de tabuleiro temáticos",
             "Quando a história e a imersão são o centro da partida.",
             "o perfil principal da resenha é \"Tema e história\"",
             "Para quem joga pela experiência: investigar um crime, fugir de um alienígena ou atravessar a Terra-média. "
             "Nestes jogos, o tema não é enfeite; é o que move cada decisão.",
             lambda d: False, "perfil=tema"),
}

# como cada guia ordena a lista (o padrão vale para os guias que correspondem a um perfil "Melhor para")
ORDEM_TXT = {"melhores": "", "familia": ", em ordem de nota no BoardGameGeek"}

CSS_GUIA = """<style>
.guia .lide{max-width:68ch}
.criterio{font-size:.92rem;color:var(--paper-muted);margin-top:10px}
.jogos-g{display:grid;gap:12px}
.jogos-g>li>a{display:grid;grid-template-columns:96px 1fr;gap:14px;align-items:start;text-decoration:none;color:var(--paper-ink);padding:12px;border:1px solid var(--paper-line);border-radius:12px;background:#fff;transition:border-color .15s ease}
.jogos-g>li>a:hover{border-color:var(--gold)}
.jogos-g img{width:96px;height:96px;object-fit:cover;border-radius:8px}
.jogos-g h3{font-size:1.1rem;line-height:1.25;font-weight:800}
.jogos-g .tg{font-weight:600;margin-top:2px}
.fx{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
.fx li{font-size:.8rem;font-weight:700;padding:3px 9px;border-radius:999px;background:var(--paper-line)}
.pq{font-size:.9rem;color:var(--paper-muted);margin-top:8px}.pq-r{font-weight:800;color:var(--paper-ink)}
.ress-g{font-size:.82rem;font-weight:700;color:#8a5200;margin-top:4px}
.perfis{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px}
.perfis a{display:grid;gap:4px;height:100%;padding:14px 16px;border:1px solid var(--paper-line);border-radius:12px;background:#fff;color:var(--paper-ink);text-decoration:none;transition:border-color .15s ease}
.perfis a:hover{border-color:var(--gold)}.perfis b{font-size:1.02rem}.perfis span{font-size:.88rem;color:var(--paper-muted)}.perfis small{font-weight:800;color:var(--link)}
.perguntas{display:grid;gap:10px}.perguntas li{padding-left:14px;border-left:3px solid var(--gold)}
.mais-g{font-weight:700;color:var(--link)}
.ranking{counter-reset:pos}.ranking>li{counter-increment:pos;position:relative}
.ranking>li>a{padding-left:52px}.ranking>li::before{content:counter(pos) "º";position:absolute;left:12px;top:14px;font-weight:800;font-size:1.05rem;color:var(--premios);font-variant-numeric:tabular-nums}
@media (max-width:480px){.jogos-g>li>a{grid-template-columns:72px 1fr;gap:12px}.jogos-g img{width:72px;height:72px}}
</style>"""


def faixa(a, b, un=""):
    return f"{a}{un}" if a == b else f"{a} a {b}{un}"


def fatos(d, c):
    """Fichinhas do cartão, só com dados que a resenha publica."""
    out = []
    if d["jogadores"]:
        j = faixa(*d["jogadores"]) + " jogadores"
        if d["melhor"]:
            m = d["melhor"]
            j += " · melhor com " + (str(m[0]) if len(m) == 1 else f"{m[0]} a {m[-1]}" if m == list(range(m[0], m[-1] + 1)) else ", ".join(map(str, m)))
        out.append(j)
    if d["duracao"]:
        out.append(faixa(*d["duracao"], " min"))
    if d["peso"] is not None:
        out.append(f"peso {d['peso']:.1f}".replace(".", ",") + " / 5")
    vit = [a for a in c["premiacoes"] if a.get("resultado") == "vencedor"]
    if vit:
        out.append(f"{vit[0]['premio']} {vit[0]['ano']}")
    return "".join(f"<li>{e(x)}</li>" for x in out)


def resenhas():
    pauta = json.loads((ROOT / "pauta.json").read_text(encoding="utf-8"))
    out = []
    for p in pauta["publicadas"]:
        slug = p["url"].rstrip("/").split("/")[-1]
        c = json.loads((ROOT / "conteudo" / f"{slug}.json").read_text(encoding="utf-8"))
        out.append((c, derivar(c), p.get("data")))
    return out


def vitorias(c):
    return sum(1 for a in c["premiacoes"] if a.get("resultado") == "vencedor")


def selecao(perfil, todas):
    _, _, _, _, _, regra, _ = GUIAS[perfil]
    escolhidos = [(c, d) for c, d, _ in todas if d["melhor_para"] == perfil or regra(d)]
    if perfil == "melhores":
        return sorted(escolhidos, key=lambda x: (-vitorias(x[0]), -(x[1]["nota"] or 0)))
    return sorted(escolhidos, key=lambda x: (x[1]["melhor_para"] != perfil, -(x[1]["nota"] or 0)))


VERBOS = ("quer ", "joga ", "gosta ", "tem ", "ama ", "busca ", "aceita ", "procura ", "prefere ", "reúne ", "está ", "curte ", "adora ")


def para_quem(c):
    """"Para quem joga sempre em dupla": só quando a frase da resenha começa por verbo que encaixa na construção."""
    f = (c.get("para_quem") or [""])[0].strip().rstrip(".")
    f = f[:1].lower() + f[1:]
    return f'<p class="pq"><span class="pq-r">Para quem</span> {e(f)}.</p>' if f.startswith(VERBOS) else ""


def cartao(c, d, pre):
    capa = ROOT / c["slug"] / "capa.jpg"
    return (f'<li><a href="{pre}{c["slug"]}/"><img src="{pre}{c["slug"]}/capa.jpg{versao(capa)}" srcset="{srcset(capa, pre, (400,))}" '
            f'sizes="96px" width="800" height="800" alt="" loading="lazy">'
            f'<div><h3>{e(nome_br(c))}</h3><p class="tg">{e(c["tagline"])}</p><ul class="fx">{fatos(d, c)}</ul>'
            + para_quem(c)
            + (f'<p class="ress-g">Com ressalva: {e(c["ressalva"])}</p>' if c.get("ressalva") else "")
            + "</div></a></li>")


def build_guia(perfil, todas):
    slug, titulo, _, criterio, intro, _, filtro = GUIAS[perfil]
    jogos = selecao(perfil, todas)
    destino = ROOT / BASE / slug
    if len(jogos) < MINIMO:
        if destino.exists():
            shutil.rmtree(destino)
        return None
    pre = "../../"
    url = f"{SITE}/{BASE}/{slug}/"
    lista = "".join(cartao(c, d, pre) for c, d in jogos)
    ol = '<ol class="jogos-g ranking">' if perfil == "melhores" else '<ol class="jogos-g">'
    corpo = f"""{cabecalho(pre, "Resenhas", sub=True)}
<main id="conteudo" class="in"><div class="nota guia">
 {trilha(("Início", pre), ("Jogos de tabuleiro", f"{pre}{BASE}/"), (titulo, ""))}
 <article class="bloco">
  <h1>{e(titulo)}</h1>
  <p class="lide">{e(intro)}</p>
  <p class="criterio"><span class="pq-r">Como escolhemos:</span> {e(criterio)}. Só entram jogos premiados com resenha completa no site{ORDEM_TXT.get(perfil, "; primeiro os que têm este perfil como principal, depois por nota no BoardGameGeek")}.</p>
 </article>
 <section class="bloco"><h2>Os {len(jogos)} jogos escolhidos</h2>{ol}{lista}</ol>
  <p class="criterio"><a class="mais-g" href="{pre}estudos/?{filtro}">Refinar na busca de resenhas →</a></p></section>
 <section class="bloco"><h2>Outros guias</h2><ul class="perfis">{perfis_html(todas, pre, exceto=perfil)}</ul></section>
</div></main>
{rodape(pre)}"""
    ld = seo.script({"@type": "ItemList", "@id": f"{url}#lista", "name": titulo, "numberOfItems": len(jogos),
                     "itemListElement": [{"@type": "ListItem", "position": i, "url": f"{SITE}/{c['slug']}/", "name": nome_br(c)}
                                         for i, (c, _) in enumerate(jogos, 1)]},
                    seo.trilha(("Início", f"{SITE}/"), ("Jogos de tabuleiro", f"{SITE}/{BASE}/"), (titulo, url)))
    descr = f"{titulo}: {len(jogos)} jogos premiados com resenha completa, escolhidos por critério: {criterio}."
    destino.mkdir(parents=True, exist_ok=True)
    (destino / "index.html").write_text(pagina(f"{titulo} | Portal Cristão" if len(titulo) <= 42 else titulo, descr, url,
                                               f"{SITE}/{jogos[0][0]['slug']}/capa.jpg", pre, corpo, head_extra="\n" + CSS_GUIA, jsonld=ld),
                                        encoding="utf-8")
    return url


def perfis_html(todas, pre, exceto=None):
    itens = []
    for perfil, (slug, titulo, frase, *_rest) in GUIAS.items():
        n = len(selecao(perfil, todas))
        if perfil == exceto or n < MINIMO:
            continue
        itens.append(f'<li><a href="{pre}{BASE}/{slug}/"><b>{e(titulo)}</b><span>{e(frase)}</span><small>{n} jogos</small></a></li>')
    return "".join(itens)


def build_hub(todas):
    pre = "../"
    url = f"{SITE}/{BASE}/"
    titulo = "Jogos de tabuleiro: guia para escolher o seu"
    recentes = sorted(todas, key=lambda x: x[2] or "", reverse=True)[:6]
    # perguntas frequentes: respostas tiradas dos próprios guias (os três primeiros e o critério)
    pergs = []
    for perfil, (slug_g, _, _, criterio, _, _, _) in GUIAS.items():
        sel = selecao(perfil, todas)
        qa = faq.guia(perfil, [nome_br(c) for c, _ in sel[:3]], criterio) if len(sel) >= MINIMO else None
        if qa:
            pergs.append((*qa, f"{pre}{BASE}/{slug_g}/"))
    faq_html = ('<section class="bloco faq" id="perguntas"><h2>Perguntas frequentes</h2>' + "".join(
        f'<details><summary><h3>{e(q)}</h3></summary><p>{e(r)} <a href="{u}">Ver o guia completo →</a></p></details>'
        for q, r, u in pergs) + "</section>") if pergs else ""
    corpo = f"""{cabecalho(pre, "Resenhas", sub=True)}
<main id="conteudo" class="in"><div class="nota guia">
 {trilha(("Início", pre), ("Jogos de tabuleiro", ""))}
 <article class="bloco">
  <h1>{e(titulo)}</h1>
  <p class="lide">Os jogos de tabuleiro modernos, os board games, vão muito além de Banco Imobiliário e War: há jogos
  para dois, para festas, para jogar sozinho, cooperativos e de estratégia pesada. Este guia ajuda a achar o seu entre
  os premiados que já resenhamos, com critérios claros e links para a resenha completa de cada um.</p>
 </article>
 <section class="bloco"><h2>Escolha pelo jeito que você joga</h2><ul class="perfis">{perfis_html(todas, pre)}</ul></section>
 <section class="bloco"><h2>Quatro perguntas antes de comprar</h2><ul class="perguntas corpo">
  <li><b>Com quantas pessoas você vai jogar?</b> Veja a "melhor contagem", não só o mínimo e o máximo da caixa. <a href="{pre}estudos/?jogadores=2&amp;melhor=on">Jogos ótimos a dois</a> · <a href="{pre}estudos/?jogadores=6">para 6 ou mais</a>.</li>
  <li><b>Quanto tempo vocês têm?</b> De partidas de 15 minutos a sessões de 3 horas. <a href="{pre}estudos/?duracao=30">Até 30 minutos</a> · <a href="{pre}estudos/?duracao=999">mais de 2 horas</a>.</li>
  <li><b>Quão complexo pode ser?</b> O "peso" do BoardGameGeek vai de 1 (leve) a 5 (pesado); abaixo de 2 é jogo de entrada. <a href="{pre}estudos/?peso=leve">Leves</a> · <a href="{pre}estudos/?peso=media">médios</a> · <a href="{pre}estudos/?peso=pesada">pesados</a>.</li>
  <li><b>Competir ou cooperar?</b> Nos cooperativos todos ganham ou perdem juntos. <a href="{pre}estudos/?estilo=Cooperativo">Ver cooperativos</a>.</li>
 </ul></section>
 <section class="bloco"><h2>Prêmios que ajudam a escolher</h2><div class="corpo">
  <p>Todos os jogos resenhados aqui venceram ou foram finalistas de prêmios importantes: o Spiel des Jahres (Alemanha,
  jogos de família) e o Kennerspiel des Jahres (para quem já joga), o As d'Or (França), o Deutscher Spiele Preis
  (votado pelo público) e o Golden Geek (votado pela comunidade do BoardGameGeek). Para ver todos os premiados do
  Golden Geek desde 2015, use a <a href="{pre}consulta/">Consulta Golden Geek</a>; para os vencedores de cada prêmio
  que já resenhamos, veja a <a href="{pre}premios/">página de prêmios</a>.</p>
 </div></section>
 {faq_html}
 <section class="bloco"><h2>Resenhas mais recentes</h2><ol class="jogos-g">{"".join(cartao(c, d, pre) for c, d, _ in recentes)}</ol>
  <p class="criterio"><a class="mais-g" href="{pre}estudos/">Ver todas as {len(todas)} resenhas →</a></p></section>
</div></main>
{rodape(pre)}"""
    guias = [(GUIAS[p][1], f"{SITE}/{BASE}/{GUIAS[p][0]}/") for p in GUIAS if len(selecao(p, todas)) >= MINIMO]
    ld = seo.script({"@type": "CollectionPage", "@id": url, "url": url, "name": titulo, "inLanguage": "pt-BR",
                     "hasPart": [{"@type": "WebPage", "url": u, "name": n} for n, u in guias]},
                    *([faq.ld([(q, r) for q, r, _ in pergs], url)] if pergs else []),
                    seo.trilha(("Início", f"{SITE}/"), ("Jogos de tabuleiro", url)))
    descr = ("Guia de jogos de tabuleiro (board games): como escolher pelo número de jogadores, duração e complexidade, "
             "e os melhores premiados para iniciantes, para dois, para festa, cooperativos e de estratégia.")
    (ROOT / BASE).mkdir(exist_ok=True)
    (ROOT / BASE / "index.html").write_text(pagina(titulo, descr, url, f"{SITE}/estudos/capa.jpg", pre, corpo,
                                                   head_extra="\n" + CSS_GUIA + "\n<style>" + faq.CSS + "</style>", jsonld=ld), encoding="utf-8")
    return url


def build():
    todas = resenhas()
    urls = [u for u in (build_guia(p, todas) for p in GUIAS) if u]
    return [build_hub(todas)] + urls


if __name__ == "__main__":
    for u in build():
        print("ok", u)
