"""Vícios de texto: expressões genéricas que deixam notícia e resenha com cara de texto feito em série.

Uso: from vicios import avisos; avisos(dados_do_json) -> lista de avisos (não bloqueia a publicação).
Pedido do usuário em 29/10/2026: texto com cara de gente, sem fórmula. Quem escreve troca a expressão por um
detalhe concreto do jogo ou da notícia (o quê, quanto, para quem, por quê). Acrescente aqui os vícios novos.
"""
import re

# (expressão, o que fazer no lugar)
VICIOS = [
    (r"vale a pena", "diga para quem e por quê, com um detalhe do jogo"),
    (r"para quem gosta de", "nomeie o perfil ou um jogo parecido (\"quem jogou Azul\")"),
    (r"(ideal|perfeito) para", "diga o que no jogo atende esse público"),
    (r"\bquer um jogo\b", "varie a abertura dos itens de público"),
    (r"\bjornada\b", "palavra de efeito: diga o que acontece (campanha de 10 partidas, por exemplo)"),
    (r"mergulh", "palavra de efeito: diga o que o jogador faz"),
    (r"envolvente|fascinante|cativante|imersiv|incrível|experiência única|notável", "adjetivo vazio: troque por um fato"),
    (r"\bum[a]? verdadeir[oa]\b", "ênfase vazia: corte"),
    (r"\bpromete\b", "diga o que a editora anunciou, com a fonte"),
    (r"no mundo d[oa]s", "abertura genérica: comece pelo fato"),
    (r"em resumo|em suma|vale (destacar|lembrar)|é importante (notar|destacar|lembrar)|sem dúvida", "muleta: corte"),
    (r"não é apenas|não é só um", "fórmula \"não é só X, é Y\": diga Y direto"),
    (r"se destaca", "diga em que e diante de quê"),
]
PULAR = {"fontes", "url", "imagem", "verificacao_nacional", "ficha", "fonte", "slug", "credito", "pagina", "origem", "filtros_ajuste"}


def _textos(x, campo=""):
    if isinstance(x, str):
        yield campo, x
    elif isinstance(x, dict):
        for k, v in x.items():
            if k not in PULAR:
                yield from _textos(v, k)
    elif isinstance(x, list):
        for v in x:
            yield from _textos(v, campo)


def avisos(dados):
    achados = {}
    for campo, t in _textos(dados):
        for padrao, dica in VICIOS:
            for m in re.finditer(padrao, t, re.I):
                achados.setdefault((m.group(0).lower(), dica), []).append(campo)
    return [f"{exp!r} ({len(c)}x, em {', '.join(sorted(set(c)))}): {dica}" for (exp, dica), c in achados.items()]
