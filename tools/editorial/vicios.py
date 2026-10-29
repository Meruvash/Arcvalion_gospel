"""Vícios de texto e caça-clique. Portado de tools/vicios.py do Elite Boardgamers, com a lista do jornalismo cristão.

avisos(dados) -> avisos que não bloqueiam (texto com cara de série: troque por um fato concreto).
sensacionalismo(titulo) -> erros que bloqueiam a publicação (premissa 12: nada de manchete para gerar clique).
"""
import re

VICIOS = [
    (r"vale a pena", "diga para quem e por quê, com um fato"),
    (r"\bjornada\b", "palavra de efeito: diga o que aconteceu"),
    (r"mergulh", "palavra de efeito: diga o que a pessoa faz"),
    (r"envolvente|fascinante|cativante|incrível|experiência única|notável|impactante", "adjetivo vazio: troque por um fato"),
    (r"\bum[a]? verdadeir[oa]\b", "ênfase vazia: corte"),
    (r"\bpromete\b", "diga o que foi anunciado, por quem e onde"),
    (r"em resumo|em suma|vale (destacar|lembrar)|é importante (notar|destacar|lembrar)|sem dúvida", "muleta: corte"),
    (r"não é apenas|não é só um", "fórmula \"não é só X, é Y\": diga Y direto"),
    (r"se destaca", "diga em que e diante de quê"),
    (r"\bpolêmic", "rótulo: descreva o que foi dito ou feito e quem discorda"),
    (r"\bpolemiz|\bdetonou\b|\bdetona\b|\bdestruiu\b|\bhumilhou\b|\blacrou\b|\bmitou\b", "verbo de torcida: use o verbo neutro (criticou, rebateu, afirmou)"),
    (r"\bsegundo especialistas\b|\bespecialistas afirmam\b", "nomeie o especialista e a instituição"),
]

# Título de caça-clique bloqueia a publicação
CACA_CLIQUE = [
    (r"você não vai acreditar|não vai acreditar|veja o que aconteceu|o motivo vai|chocante|choca o brasil|inacreditável|bomba:|urgente:|"
     r"exclusivo!|surpreendente|deixou todos|ninguém esperava|veja o vídeo|assista antes que", "expressão de caça-clique"),
    (r"!", "ponto de exclamação no título"),
    (r"\?{2,}", "pontuação repetida"),
]
# palavras em caixa alta só valem para siglas curtas (STF, CNBB, PEC) ou da lista
SIGLAS_LONGAS = {"UNICEF", "UNESCO", "ANVISA", "BNDES", "FUNAI", "IBAMA", "SENAI", "SEBRAE", "PRONAMPE", "INSS", "ENEM", "FGTS", "OCDE", "MERCOSUL"}
PULAR = {"fontes", "url", "imagem", "slug", "credito", "revisao", "ia", "patrocinador", "afiliados", "tags", "referencias_biblicas"}


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


def sensacionalismo(titulo):
    erros = []
    for padrao, motivo in CACA_CLIQUE:
        if re.search(padrao, titulo, re.I):
            erros.append(f"título com {motivo}: {titulo!r}")
    gritos = [p for p in re.findall(r"\b[A-ZÀ-Ú]{5,}\b", titulo) if p not in SIGLAS_LONGAS]
    if gritos:
        erros.append(f"título com palavra em caixa alta ({', '.join(gritos)}): só siglas")
    return erros
