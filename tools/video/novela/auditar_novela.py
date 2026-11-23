#!/usr/bin/env python3
"""Auditor de roteiro de novela curta (Reels 9:16), contra as fórmulas medidas no modelo de 1 hora.

Uso: python3 tools/video/novela/auditar_novela.py roteiro.json [--json]

As fórmulas, os números e o modo de medir estão em docs/video/novela/FORMULAS_NOVELA.md.

Duas camadas de regras:
1. Obrigatórias (O1 a O10; O8 e O9 só quando o roteiro tem "protagonista", O10 só na parte 2 em diante): nossas regras e o que o formato exige. Se uma falha, o roteiro reprova, qualquer que seja
   a nota.
Avisos (A1 a A4, não reprovam): docs/video/novela/REGRAS_ROTEIRO.md.
2. Fórmula do modelo (F1 a F10): cada item vale o peso medido nos 6 ciclos-pilar do modelo (a fração de pilares em
   que ele aparece). Aprovação com nota igual ou maior que 0,85.

Formato do roteiro.json:
{
  "titulo": "...", "duracao_s": 70, "aviso_dramatizacao": true,
  "batidas": [
    {"t": 0, "fim": 3, "tipo": "GANCHO", "quem": "Valdir", "modo": "texto|audio|video|tela|cartao|narracao",
     "fala": "...", "tela": "...", "marcas": ["dinheiro", "testemunhas", "objeto:papel"], "fonte": "url (só LEI)"}
  ]
}
Tipos: GANCHO, ATAQUE, HUMILHACAO, DESCRENCA, PROVA_DESPREZADA, REVELACAO, QUEDA, PROTECAO, RECOMPENSA, LEI,
GANCHO_FINAL, TRANSICAO.
"""
import json, re, sys

# Pesos = fração dos 6 ciclos-pilar do modelo em que o elemento aparece (medição de 22/11/2026, FORMULAS_NOVELA.md §2).
PESOS = {
    "F1_humilhacao_em_escada": 6 / 6,   # insulto antes da virada: 6 de 6 pilares (mediana 4)
    "F2_descrenca": 5 / 6,              # vítima chamada de mentirosa antes da virada: 5 de 6
    "F3_objeto_prova": 5 / 6,           # "fake/real/authentic": 5 de 6
    "F4_virada_no_ponto": 6 / 6,        # todo pilar tem virada; posição na faixa medida (F4)
    "F5_queda_do_vilao": 6 / 6,         # nos 6 o vilão perde (súplica em 3, punição nos outros)
    "F6_protecao_recompensa": 4 / 6,    # "my wife / who dares / I believe her": 4 de 6
    "F7_dinheiro_concreto": 3 / 6,      # número em dinheiro: 3 de 6 pilares (5 de 12 ciclos)
    "F8_testemunhas": 4 / 6,            # humilhação em público (escritório, restaurante, turma, banquete)
    "F9_ataque_cedo": 6 / 6,            # o conflito abre o ciclo: ataque até 10% do tempo
    "F10_identidade_ou_poder_escondido": 6 / 6,  # nos 6 o poder do humilhado já existia e só é revelado
}
VIRADA_MIN, VIRADA_MAX = 0.48, 0.81     # quartis 1 e 3 da posição da virada nos ciclos do modelo
PALAVRAS_POR_S_AUDIO = 2.9              # teto para a fala caber (narrador medido a ~2,7 palavras/s depois do atempo 1.08)
PALAVRAS_POR_S_LEITURA = 4.0            # teto para ler uma mensagem de texto na tela
BATIDA_MAX_S = 10                       # nenhum plano parado mais de 10 s


def palavras(s):
    return len(re.findall(r"[\wÀ-ÿ]+", s or ""))


def auditar(r):
    b = sorted(r["batidas"], key=lambda x: x["t"])
    dur = float(r["duracao_s"])
    tipos = [x["tipo"] for x in b]
    res = []

    def item(cod, ok, nota, peso=None):
        res.append({"item": cod, "ok": bool(ok), "nota": nota, "peso": peso})

    # Obrigatórias
    item("O1_aviso_dramatizacao", r.get("aviso_dramatizacao") is True, "aviso fixo na tela")
    g = b[0]
    item("O2_gancho_ate_3s", g["tipo"] == "GANCHO" and g["t"] == 0 and g["fim"] <= 3,
         f"1ª batida {g['tipo']} {g['t']}–{g['fim']} s")
    leis = [x for x in b if x["tipo"] == "LEI"]
    item("O3_lei_com_fonte", bool(leis) and all(re.match(r"https?://", x.get("fonte", "")) for x in leis),
         f"{len(leis)} batida(s) LEI, todas com link")
    longas = [f"{x['t']}–{x['fim']}" for x in b if x["fim"] - x["t"] > BATIDA_MAX_S]
    item("O4_ritmo", not longas, f"batidas com mais de {BATIDA_MAX_S} s: {longas or 'nenhuma'}")
    apertos = []
    for x in b:
        w, d = palavras(x.get("fala")), max(0.1, x["fim"] - x["t"])
        teto = PALAVRAS_POR_S_AUDIO if x["modo"] in ("audio", "narracao", "video") else PALAVRAS_POR_S_LEITURA
        if w / d > teto:
            apertos.append(f"{x['t']}s ({w} palavras em {d:.0f} s)")
    item("O5_falas_cabem", not apertos, f"apertadas: {apertos or 'nenhuma'}")
    item("O6_gancho_final", tipos[-1] == "GANCHO_FINAL", f"última batida: {tipos[-1]}")
    buracos = [f"{b[i]['fim']}→{b[i+1]['t']}" for i in range(len(b) - 1) if abs(b[i + 1]["t"] - b[i]["fim"]) > 0.01]
    item("O7_linha_do_tempo", not buracos and abs(b[-1]["fim"] - dur) < 0.01,
         f"buracos ou sobreposições: {buracos or 'nenhum'}; fim {b[-1]['fim']} de {dur}")

    # Protagonista (docs/video/novela/PERSONAGEM_DR_PELICIONI.md)
    prot = r.get("protagonista")
    if prot:
        rev0 = next((x for x in b if x["tipo"] == "REVELACAO"), None)
        dele = [x for x in b if prot.lower() in x["quem"].lower()]
        antes_dele = [x for x in dele if rev0 and x["t"] < rev0["t"]]
        leis_dele = [x for x in dele if x["tipo"] == "LEI"]
        prev = [x for x in dele if "previsao" in x.get("marcas", [])]
        cumpre = [x for x in b if "previsao_cumprida" in x.get("marcas", [])]
        item("O8_protagonista_resolve",
             bool(rev0) and prot.lower() in rev0["quem"].lower() and not antes_dele and leis_dele and prev
             and cumpre and cumpre[0]["t"] > prev[0]["t"],
             f"{prot}: entra na virada={bool(rev0) and prot.lower() in rev0['quem'].lower()}, aparece antes={len(antes_dele)}, "
             f"falas de lei={len(leis_dele)}, previsão={len(prev)} cumprida={len(cumpre)}")
        proib = r"garant|vai ganhar|com certeza|me contrat|contrat[ea] |consulta gr[aá]tis|honor[aá]ri|!"
        ruins = [x["fala"] for x in dele if re.search(proib, x.get("fala", ""), re.I)]
        item("O9_sem_promessa_nem_captacao", not ruins, f"falas vetadas: {ruins or 'nenhuma'}")

    # Fórmula do modelo
    rev = [x for x in b if x["tipo"] == "REVELACAO"]
    tv = rev[0]["t"] if rev else None
    antes = [x for x in b if tv is not None and x["t"] < tv]
    depois = [x for x in b if tv is not None and x["t"] >= tv]
    hum = [x for x in antes if x["tipo"] in ("HUMILHACAO", "ATAQUE")]
    item("F1_humilhacao_em_escada", len(hum) >= 2, f"{len(hum)} ataque(s)/humilhação(ões) antes da virada (mín. 2)",
         PESOS["F1_humilhacao_em_escada"])
    item("F2_descrenca", any(x["tipo"] == "DESCRENCA" for x in antes), "vítima desacreditada antes da virada",
         PESOS["F2_descrenca"])
    objs_desp = {m for x in antes if x["tipo"] == "PROVA_DESPREZADA" for m in x.get("marcas", []) if m.startswith("objeto:")}
    objs_rev = {m for x in depois for m in x.get("marcas", []) if m.startswith("objeto:")}
    item("F3_objeto_prova", bool(objs_desp & objs_rev),
         f"desprezado antes {sorted(objs_desp)} · decisivo depois {sorted(objs_rev)}", PESOS["F3_objeto_prova"])
    pos = (tv / dur) if tv is not None else None
    item("F4_virada_no_ponto", pos is not None and VIRADA_MIN <= pos <= VIRADA_MAX,
         f"virada em {pos:.0%} (faixa medida {VIRADA_MIN:.0%}–{VIRADA_MAX:.0%})" if pos is not None else "sem REVELACAO",
         PESOS["F4_virada_no_ponto"])
    item("F5_queda_do_vilao", any(x["tipo"] == "QUEDA" for x in depois), "vilão perde depois da virada",
         PESOS["F5_queda_do_vilao"])
    item("F6_protecao_recompensa", any(x["tipo"] in ("PROTECAO", "RECOMPENSA") for x in depois),
         "proteção ou recompensa depois da virada", PESOS["F6_protecao_recompensa"])
    din = [x for x in b if "dinheiro" in x.get("marcas", [])
           and re.search(r"\d|\bmil\b|milh|reais|R\$", (x.get("fala") or "") + " " + (x.get("tela") or ""))]
    item("F7_dinheiro_concreto", bool(din), f"número em dinheiro dito ou escrito em {len(din)} batida(s)",
         PESOS["F7_dinheiro_concreto"])
    item("F8_testemunhas", any("testemunhas" in x.get("marcas", []) for x in antes), "humilhação diante de outros",
         PESOS["F8_testemunhas"])
    at = [x for x in b if x["tipo"] in ("ATAQUE", "HUMILHACAO")]
    cedo = (bool(at) and at[0]["t"] <= 0.10 * dur) or "ataque" in g.get("marcas", [])
    item("F9_ataque_cedo", cedo,
         f"1º ataque em {at[0]['t'] if at else '—'} s (até {0.10 * dur:.0f} s, ou no próprio gancho)",
         PESOS["F9_ataque_cedo"])
    item("F10_identidade_ou_poder_escondido", any("poder_escondido" in x.get("marcas", []) for x in b),
         "o poder do humilhado existia antes e só é revelado", PESOS["F10_identidade_ou_poder_escondido"])

    # Série (REGRAS_ROTEIRO.md §5): a parte 2 em diante retoma o estado de passagem e repete a última batida anterior.
    if int(r.get("parte", 1)) > 1:
        item("O10_continuidade_da_serie", bool(r.get("handoff_anterior")) and b[0].get("reprise") is True,
             "parte > 1: precisa de 'handoff_anterior' e da 1ª batida com 'reprise': true")

    # Avisos (heurísticos, não reprovam): REGRAS_ROTEIRO.md
    avisos = []
    tensao = [x["t"] for x in b if x["tipo"] in ("GANCHO", "ATAQUE", "HUMILHACAO", "PROVA_DESPREZADA", "DESCRENCA",
                                                  "REVELACAO", "LEI", "QUEDA", "GANCHO_FINAL")]
    gaps = [round(tensao[i + 1] - tensao[i], 1) for i in range(len(tensao) - 1)]
    if gaps and max(gaps) > 15:
        avisos.append(f"A1 escada: {max(gaps)} s sem ponto de tensão (máx. 15 s)")
    sem_porque = [x["t"] for x in b[1:] if not x.get("porque")]
    if sem_porque:
        avisos.append(f"A2 'então/mas': {len(sem_porque)} batida(s) sem o campo 'porque' ({sem_porque[:5]}…)")
    fim = (b[-1].get("fala") or "").strip()
    if re.search(r"(\.\.\.|…|—|-)$", fim) and "consequencia" not in b[-1].get("marcas", []):
        avisos.append("A3 gancho final cortado no meio da frase sem marca 'consequencia'")
    fisicas = [x for x in antes if x["tipo"] in ("HUMILHACAO", "ATAQUE") and not x.get("modo") in ("texto", "tela")]
    if len(hum) >= 2 and not fisicas:
        avisos.append("A4 escada só de palavras: nenhuma humilhação encenada antes da virada")

    obrig_ok = all(x["ok"] for x in res if x["item"].startswith("O"))
    tot = sum(x["peso"] for x in res if x["peso"])
    got = sum(x["peso"] for x in res if x["peso"] and x["ok"])
    nota = got / tot
    return {"titulo": r.get("titulo"), "itens": res, "obrigatorias_ok": obrig_ok, "nota_formula": round(nota, 3),
            "aprovado": obrig_ok and nota >= 0.85, "avisos": avisos}


def main():
    r = json.load(open(sys.argv[1], encoding="utf-8"))
    a = auditar(r)
    if "--json" in sys.argv:
        print(json.dumps(a, ensure_ascii=False, indent=1))
    else:
        print(f"# {a['titulo']}")
        for x in a["itens"]:
            p = f" (peso {x['peso']:.2f})" if x["peso"] else ""
            print(f"{'✅' if x['ok'] else '❌'} {x['item']}{p}: {x['nota']}")
        for av in a.get("avisos", []):
            print(f"⚠️ {av}")
        print(f"\nObrigatórias: {'ok' if a['obrigatorias_ok'] else 'FALHOU'} · nota da fórmula: {a['nota_formula']:.2f} "
              f"(mín. 0,85) · {'APROVADO' if a['aprovado'] else 'REPROVADO'}")
    sys.exit(0 if a["aprovado"] else 1)


if __name__ == "__main__":
    main()
