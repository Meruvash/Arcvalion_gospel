"""Perguntas frequentes das resenhas e do guia: respostas curtas e diretas, do jeito que buscadores e assistentes de IA
citam. Pedido do usuário em 29/10/2026 (aparecer no ChatGPT, no Gemini e companhia).

Nada é escrito à mão aqui: toda resposta sai de campos já publicados na própria página (selo, veredito, ficha, preço com
data, edição nacional, prêmios, comparações). Pergunta sem dado para responder não aparece.
O FAQPage do JSON-LD repete exatamente o texto visível (o Google não mostra mais esse tipo como destaque para
sites comuns, mas ele organiza a página para quem a lê por máquina).
"""
import html
import re

e = html.escape

CSS = """.faq details{border-top:1px solid var(--paper-line,#ddd);padding:10px 0}.faq details:first-of-type{border-top:0}
.faq summary{cursor:pointer;list-style:none;display:flex;justify-content:space-between;gap:12px}
.faq summary::-webkit-details-marker{display:none}.faq summary::after{content:"+";font-weight:700;color:var(--link,#1d5fa8)}
.faq details[open] summary::after{content:"−"}.faq h3{font-size:1rem;margin:0;font-weight:700}
.faq details p{margin:8px 0 0;line-height:1.55}"""


VERBOS = ("quer ", "joga ", "gosta ", "tem ", "ama ", "busca ", "aceita ", "procura ", "prefere ", "reúne ", "está ", "curte ",
          "adora ", "gostou ", "aprecia ", "jogou ", "sente ", "precisa ", "não ")


def frases(t, n):
    partes = re.split(r"(?<=[.!?])\s+", (t or "").strip())
    return " ".join(partes[:n]).strip()


def _ficha(c, nome):
    return next((v for k, v in c.get("ficha", []) if k.lower() == nome.lower()), None)


def resenha(c, nome):
    """[(pergunta, resposta)] de uma resenha. `nome` é o nome em português do jogo."""
    p = []
    if c.get("selo") and c.get("veredito"):
        r = f"Nosso selo: {c['selo']}. {frases(c['veredito'], 2)}"
        if c.get("ressalva"):
            r += f" Ressalva: {c['ressalva']}."
        p.append((f"Vale a pena comprar {nome}?", r))
    jog, dur = _ficha(c, "Jogadores"), _ficha(c, "Duração anunciada")
    if jog:
        melhores = [j[0] for j in c.get("jogadores", []) if len(j) > 2 and j[2] == 3]
        r = f"{nome} é para {jog} jogadores" + (f", com duração anunciada de {dur}" if dur else "") + "."
        if melhores:
            r += f" Na nossa avaliação, funciona melhor com: {', '.join(m.lower() for m in melhores)}."
        p.append((f"Para quantos jogadores é {nome} e quanto tempo dura?", r))
    if c.get("edicao_nacional"):
        p.append((f"{nome} tem edição em português?", frases(c["edicao_nacional"], 1)))
    preco = c.get("preco_ref") or {}
    if preco.get("faixa") and preco.get("data"):
        p.append((f"Quanto custa {nome} no Brasil?",
                  f"Em {preco['data']}, {preco['faixa']}" + (f" ({preco['obs']})" if preco.get("obs") else "") + "."))
    # "Para quem gosta de…": só frases que começam por verbo que encaixa na construção
    quem = [q.strip().rstrip(".") for q in c.get("para_quem", []) if q.strip().lower().startswith(VERBOS)][:3]
    if quem:
        p.append((f"Para quem é {nome}?", "Para quem " + "; ".join(q[:1].lower() + q[1:] for q in quem) + "."))
    vit = [f"{a['premio']} {a['ano']}" + (f" ({a['categoria']})" if a.get("categoria") and a["categoria"] != a["premio"] else "")
           for a in c.get("premiacoes", []) if a.get("resultado") == "vencedor"]
    if vit:
        p.append((f"{nome} ganhou prêmios?", f"Sim: venceu {', '.join(vit)}."))
    comp = [x[0] for x in c.get("comparacoes", []) if x]
    if comp:
        lista = ", ".join(comp[:-1]) + " e " + comp[-1] if len(comp) > 1 else comp[0]
        primeira = c["comparacoes"][0]
        detalhe = f" {comp[0]}: {frases(primeira[2], 1)}" if len(primeira) > 2 and primeira[2] else ""
        p.append((f"Quais jogos são parecidos com {nome}?", f"Na resenha comparamos {nome} com {lista}.{detalhe}"))
    return p


def secao(perguntas, classe="bloco claro"):
    if not perguntas:
        return ""
    itens = "".join(f"<details><summary><h3>{e(q)}</h3></summary><p>{e(r)}</p></details>" for q, r in perguntas)
    return f'<section class="{classe} faq" id="perguntas"><h2>Perguntas frequentes</h2>{itens}</section>'


def ld(perguntas, url):
    return {"@type": "FAQPage", "@id": f"{url}#perguntas", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in perguntas]}


# Perguntas do guia de jogos de tabuleiro: cada uma aponta para o guia do perfil (build_guias.GUIAS)
PERGUNTAS_GUIA = {
    "melhores": "Quais são os melhores jogos de tabuleiro?",
    "entrada": "Qual o melhor jogo de tabuleiro para iniciantes?",
    "familia": "Qual o melhor jogo de tabuleiro para jogar em família?",
    "dupla": "Qual o melhor jogo de tabuleiro para jogar a dois?",
    "festa": "Qual o melhor jogo de tabuleiro para festa e grupos grandes?",
    "cooperativo": "Qual o melhor jogo de tabuleiro cooperativo?",
    "solo": "Qual o melhor jogo de tabuleiro para jogar sozinho?",
    "estrategia": "Qual o melhor jogo de tabuleiro de estratégia?",
    "proximo": "Que jogo de tabuleiro comprar depois do primeiro?",
    "campanha": "Qual o melhor jogo de tabuleiro de campanha ou legacy?",
    "tema": "Qual o melhor jogo de tabuleiro temático?",
}


def guia(perfil, nomes, criterio):
    """(pergunta, resposta) do guia: os três primeiros da lista e o critério, como estão na página do guia."""
    if perfil not in PERGUNTAS_GUIA or not nomes:
        return None
    lista = ", ".join(nomes[:2]) + " e " + nomes[2] if len(nomes) >= 3 else " e ".join(nomes)
    return (PERGUNTAS_GUIA[perfil], f"Entre os jogos premiados que resenhamos, os primeiros da nossa lista são {lista}. "
            f"Critério: {criterio}.")
