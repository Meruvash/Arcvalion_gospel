"""Análise de conteúdo do roteiro de uma novela curta a partir da legenda (json3 do YouTube).

Uso: python3 tools/video/analisar_roteiro.py <legenda.json3> <codificacao.json> <saida.json> [--transcricao saida.txt]

Etapas (todas reprodutíveis, sem IA e sem rede):
 1. limpeza da legenda com regras explícitas (lixo, versões progressivas, duplicatas) e contagem do que foi removido;
 2. conferência da codificação manual: cada batida (tipo, segundo, citação) precisa ser achada na transcrição a até 20 s,
    com sobreposição de palavras >= 0,6; o que não for achado é listado como FALHA;
 3. tempos do ciclo (humilhação → chegada do protetor → revelação → punição) por ciclo e no agregado;
 4. contagem automática de léxico (status baixo, status alto, fórmulas verbais) e validação cruzada: a densidade de léxico
    de status baixo dentro das janelas codificadas como humilhação × fora delas, com teste de permutação;
 5. estatísticas de linguagem: palavras por fala, palavras por minuto, nomes, perguntas.
A transcrição completa (obra de terceiros) só é gravada se --transcricao for passado; não versionar.
"""
import argparse
import json
import random
import re
from collections import Counter

LIMIAR_SOBREPOSICAO = 0.6
JANELA_S = 20

STATUS_BAIXO = r"\b(poor|bumpkin|cleaner|janitor|maid|loser|losers|trash|scavenger|broke|cheap|nothing|beggar|country|pathetic|pitiful|fake|fraud|liar|clowns?|dog)\b"
STATUS_ALTO = r"\b(ceo|president|chairman|heir|billion|billions|million|millions|forbes|rolls|royce|vault|villa|manor|estate|yale|ivy|dior|emerald|ring|diamond|luxury|elite|elites)\b"
FORMULAS = {
    "how dare you": r"\bhow dare (you|he|she)\b",
    "do you know who": r"\b(do|don'?t) you know who\b",
    "(you) don't (even) deserve": r"\b(don'?t|doesn'?t) (even )?deserve\b",
    "impossible / can't be": r"\b(impossible|can'?t be|this can'?t be|how is that possible)\b",
    "spare me / I was wrong": r"\b(spare me|i was wrong|forgive me)\b",
    "you're dead": r"\byou'?re dead\b",
    "get out / get lost": r"\bget (out|lost)\b",
    "my wife": r"\bmy wife\b",
    "terminated / fired": r"\b(terminated|fire (you|her|him)|settle her salary)\b",
    "stop pretending": r"\bstop pretending\b",
    "security": r"\bsecurity\b",
    "what (isolado)": r"^\s*what\W*$",
}
NOMES = ["mia", "alexander", "kane", "sophie", "tom", "grandma", "tiffany", "chloe", "lila", "ethan", "daniel", "collins"]


def palavras(t):
    return re.findall(r"[a-z0-9']+", t.lower())


def carregar(json3):
    d = json.load(open(json3))
    falas = []
    for e in d.get("events", []):
        if "segs" not in e:
            continue
        t = "".join(s.get("utf8", "") for s in e["segs"]).replace("\n", " ").strip()
        if t:
            falas.append({"ini": e["tStartMs"] / 1000, "texto": t})
    return falas


def limpar(falas):
    norm = lambda t: re.sub(r"[^a-z0-9]", "", t.lower())
    saida, rem = [], Counter()
    for x in falas:
        t = x["texto"]
        if len(re.sub(r"[^A-Za-z]", "", t)) < 2 or (len(t) <= 3 and t.upper() == t and t.lower() not in ("i", "ok", "no")):
            rem["lixo"] += 1
            continue
        if saida and x["ini"] - saida[-1]["ini"] < 4.5:
            a, b = norm(saida[-1]["texto"]), norm(t)
            if a and a in b:
                rem["progressiva"] += 1
                saida[-1] = {"ini": saida[-1]["ini"], "texto": t}
                continue
            if b and b in a:
                rem["duplicada"] += 1
                continue
        saida.append(dict(x))
    return saida, dict(rem)


def achar(falas, seg, citacao):
    alvo = set(palavras(citacao))
    melhor = (0.0, None)
    for i, f in enumerate(falas):
        if abs(f["ini"] - seg) > JANELA_S:
            continue
        # junta a fala com a seguinte (a legenda quebra frases)
        texto = f["texto"] + " " + (falas[i + 1]["texto"] if i + 1 < len(falas) else "")
        ws = set(palavras(texto))
        # tolera palavras grudadas pela leitura da legenda ("rememberme")
        colado = re.sub(r"[^a-z0-9]", "", texto.lower())
        ok = sum(1 for w in alvo if w in ws or (len(w) > 3 and w in colado))
        s = ok / max(len(alvo), 1)
        if s > melhor[0]:
            melhor = (s, f["ini"])
    return melhor


def resumo(xs):
    xs = sorted(xs)
    if not xs:
        return None
    n = len(xs)
    med = xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2
    return {"n": n, "min": round(xs[0], 1), "mediana": round(med, 1), "media": round(sum(xs) / n, 1), "max": round(xs[-1], 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("legenda"); ap.add_argument("codificacao"); ap.add_argument("saida")
    ap.add_argument("--transcricao")
    a = ap.parse_args()

    brutas = carregar(a.legenda)
    falas, removidas = limpar(brutas)
    dur = falas[-1]["ini"] + 3
    if a.transcricao:
        with open(a.transcricao, "w") as fh:
            for f in falas:
                fh.write(f"{int(f['ini'] // 60):02d}:{int(f['ini'] % 60):02d} {f['texto']}\n")

    cod = json.load(open(a.codificacao))
    conferencia, falhas = [], []
    for c in cod["ciclos"]:
        for tipo, seg, cit in c["batidas"]:
            s, t = achar(falas, seg, cit)
            item = {"ciclo": c["id"], "tipo": tipo, "anotado_s": seg, "achado_s": t, "sobreposicao": round(s, 2), "citacao": cit}
            conferencia.append(item)
            if s < LIMIAR_SOBREPOSICAO:
                falhas.append(item)
            else:
                # passa a usar o tempo achado na transcrição
                pass

    tempo = {(x["ciclo"], x["tipo"], x["citacao"]): (x["achado_s"] if x["sobreposicao"] >= LIMIAR_SOBREPOSICAO else x["anotado_s"]) for x in conferencia}

    # tempos de ciclo (só ciclos do tipo "tapa")
    t_hc, t_cr, t_hp, t_ciclo, punicoes = [], [], [], [], []
    for c in cod["ciclos"]:
        bt = sorted(((tempo[(c["id"], tp, ct)], tp) for tp, _, ct in c["batidas"]))
        primeiro = lambda tipo, depois=0: next((t for t, tp in bt if tp == tipo and t >= depois), None)
        if c["tipo"] != "tapa":
            continue
        h = primeiro("HUMILHACAO")
        ch = primeiro("CHEGADA", h or 0)
        r = primeiro("REVELACAO", ch or 0)
        p = primeiro("PUNICAO", h or 0)
        if h is not None and ch is not None:
            t_hc.append(ch - h)
        if ch is not None and r is not None:
            t_cr.append(r - ch)
        if h is not None and p is not None:
            t_hp.append(p - h)
            punicoes.append(p)
        t_ciclo.append(bt[-1][0] - bt[0][0])
    punicoes.sort()
    intervalo_punicoes = [b - a_ for a_, b in zip(punicoes, punicoes[1:])]

    contagem_tipos = Counter(x["tipo"] for x in conferencia)

    # léxico e validação cruzada
    por_fala = []
    for f in falas:
        tl = f["texto"].lower()
        por_fala.append({"ini": f["ini"], "baixo": len(re.findall(STATUS_BAIXO, tl)), "alto": len(re.findall(STATUS_ALTO, tl)),
                         "n": len(palavras(tl))})
    janelas_h = []
    for c in cod["ciclos"]:
        hs = [tempo[(c["id"], tp, ct)] for tp, _, ct in c["batidas"] if tp in ("HUMILHACAO", "ESCALADA")]
        if hs:
            janelas_h.append((min(hs) - 5, max(hs) + 30))
    dentro = lambda t: any(lo <= t <= hi for lo, hi in janelas_h)

    def densidade(sel):
        b = sum(x["baixo"] for x, s in zip(por_fala, sel) if s)
        n = sum(x["n"] for x, s in zip(por_fala, sel) if s)
        return 1000 * b / max(n, 1)

    sel = [dentro(x["ini"]) for x in por_fala]
    d_in, d_out = densidade(sel), densidade([not s for s in sel])
    obs = d_in - d_out
    rng = random.Random(42)
    # permutação por blocos de 60 s (preserva a dependência local)
    blocos = sorted({int(x["ini"] // 60) for x in por_fala})
    marca_bloco = {b: any(dentro(t) for t in range(b * 60, b * 60 + 60, 5)) for b in blocos}
    maior = 0
    for _ in range(2000):
        emb = list(marca_bloco.values())
        rng.shuffle(emb)
        mapa = dict(zip(marca_bloco.keys(), emb))
        s2 = [mapa[int(x["ini"] // 60)] for x in por_fala]
        if densidade(s2) - densidade([not s for s in s2]) >= obs:
            maior += 1

    formulas = {k: sum(1 for f in falas if re.search(rx, f["texto"].lower())) for k, rx in FORMULAS.items()}
    exemplos = {k: [f"{int(f['ini'] // 60):02d}:{int(f['ini'] % 60):02d}" for f in falas if re.search(rx, f["texto"].lower())][:6]
                for k, rx in FORMULAS.items()}
    tokens = [w for f in falas for w in palavras(f["texto"])]
    nomes = {n: tokens.count(n) for n in NOMES}
    pf = [len(palavras(f["texto"])) for f in falas]
    com_pontuacao = [f for f in falas if f["ini"] > 3270]  # a partir de ~54:30 a legenda traz pontuação
    perguntas = sum(1 for f in com_pontuacao if f["texto"].strip().endswith("?"))
    exclam = sum(1 for f in com_pontuacao if f["texto"].strip().endswith("!"))

    res = {
        "corpus": {"falas_brutas": len(brutas), "falas_limpas": len(falas), "removidas": removidas, "palavras": len(tokens),
                   "duracao_s": round(dur), "palavras_por_minuto": round(len(tokens) / (dur / 60), 1),
                   "palavras_por_fala": resumo(pf), "vocabulario_distinto": len(set(tokens))},
        "conferencia_codificacao": {"batidas": len(conferencia), "achadas": len(conferencia) - len(falhas),
                                    "taxa": round((len(conferencia) - len(falhas)) / len(conferencia), 3), "falhas": falhas},
        "batidas_por_tipo": dict(contagem_tipos),
        "ciclos": {"total": len(cod["ciclos"]), "tapa_na_cara": sum(1 for c in cod["ciclos"] if c["tipo"] == "tapa"),
                   "humilhacao_ate_chegada_s": resumo(t_hc), "chegada_ate_revelacao_s": resumo(t_cr),
                   "humilhacao_ate_punicao_s": resumo(t_hp), "duracao_ciclo_s": resumo(t_ciclo),
                   "intervalo_entre_punicoes_s": resumo(intervalo_punicoes)},
        "plantio_pagamento": [
            {"plantio": "não lembra do protetor (00:35)", "pagamento": "menino de 8 anos (83:15)", "distancia_s": 4995 - 35},
            {"plantio": "abóboras para a velha pobre (12:12)", "pagamento": "a avó cita as abóboras ao pedir a mão (74:02)", "distancia_s": 4442 - 732},
            {"plantio": "anel 'barato' escolhido (16:24)", "pagamento": "é o anel do poder (26:09 / 28:05)", "distancia_s": 1569 - 984},
            {"plantio": "convite da câmara (52:46)", "pagamento": "a diretora da câmara é a avó (56:37)", "distancia_s": 3397 - 3166}],
        "lexico": {
            "status_baixo_por_mil_palavras": {"dentro_humilhacao": round(d_in, 2), "fora": round(d_out, 2), "razao": round(d_in / max(d_out, 1e-9), 2),
                                              "p_permutacao_blocos_60s": round((maior + 1) / 2001, 4)},
            "status_alto_total": sum(x["alto"] for x in por_fala), "status_baixo_total": sum(x["baixo"] for x in por_fala)},
        "formulas_verbais_falas": formulas, "formulas_verbais_exemplos_mmss": exemplos,
        "nomes_mencoes": nomes,
        "pontuacao_trecho_final": {"falas": len(com_pontuacao), "perguntas": perguntas, "exclamacoes": exclam,
                                   "frac_perguntas": round(perguntas / max(len(com_pontuacao), 1), 3)},
    }
    json.dump(res, open(a.saida, "w"), ensure_ascii=False, indent=2)
    print(json.dumps({k: res[k] for k in ("corpus", "conferencia_codificacao", "ciclos", "lexico")}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
