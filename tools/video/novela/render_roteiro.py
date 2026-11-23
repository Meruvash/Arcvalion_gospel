#!/usr/bin/env python3
"""Gera a versão de leitura (Markdown) de roteiros de novela em JSON, com a tabela do verificador.
Uso: python3 tools/video/novela/render_roteiro.py saida.md roteiro1.json [roteiro2.json ...]"""
import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from auditar_novela import auditar
NOMES = {"GANCHO": "Gancho", "ATAQUE": "Ataque", "HUMILHACAO": "Humilhação", "DESCRENCA": "Descrença",
         "PROVA_DESPREZADA": "Prova desprezada", "REVELACAO": "**VIRADA**", "QUEDA": "Queda do vilão",
         "PROTECAO": "Proteção", "RECOMPENSA": "Recompensa", "LEI": "Lei (fonte)", "GANCHO_FINAL": "Gancho final",
         "TRANSICAO": "Respiro"}
out = ["# Roteiros de novela (versão de leitura, gerada dos JSON por `tools/video/novela/render_roteiro.py`)", ""]
for p in sys.argv[2:]:
    r = json.load(open(p, encoding="utf-8")); a = auditar(r)
    out += [f"## {r['titulo']}", "", f"Arquivo: `{os.path.basename(p)}` · {r['duracao_s']} s · 9:16 · aviso «DRAMATIZAÇÃO» fixo",
            "", "| Tempo | Batida | Quem (modo) | Fala | Tela |", "|---|---|---|---|---|"]
    for b in r["batidas"]:
        fala = b["fala"].replace("|", "/")
        out.append(f"| {b['t']}–{b['fim']} s | {NOMES[b['tipo']]} | {b['quem']} ({b['modo']}) | {fala} | {b['tela']} |")
    ok = sum(1 for x in a["itens"] if x["ok"])
    out += ["", f"**Verificador:** {ok}/{len(a['itens'])} itens · nota da fórmula {a['nota_formula']:.2f} · "
            f"{'APROVADO' if a['aprovado'] else 'REPROVADO'}", ""]
open(sys.argv[1], "w", encoding="utf-8").write("\n".join(out))
