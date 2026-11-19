"""Auditoria de padrão ouro dos roteiros do agro (pedido do editor, 19/11/2026).

Compara as falas de um roteiro, batida a batida, com os dois vídeos de padrão ouro:
- "O caseiro e o vizinho" (falas_exemplo_usucapiao.json): 2.200 visualizações;
- "O irmão vendeu sem avisar" (falas_exemplo_heranca.json): 5.000 visualizações.

Uso: python3 auditar_roteiro.py falas.json [--md saida.md]
Entrada: a lista de falas no formato de sempre ({"id", "quem", "texto"}).
Saída: tabela item a item (o roteiro × caseiro × irmão), nota automática e lista do que falta.

A máquina só mede o que dá para medir no texto. Os itens de julgamento (busca real, terra em jogo, mito que não é
ditado, atemporal) ficam na parte manual de docs/video/AUDITORIA_PADRAO_OURO.md.
"""
import json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
OURO = {"caseiro": AQUI / "falas_exemplo_usucapiao.json", "irmão": AQUI / "falas_exemplo_heranca.json"}
PROXIMOS = r"\b(?:caseir[oa]|irm[aã]o|irm[aã]|pai|m[aã]e|filh[oa]|ti[oa]|prim[oa]|cunhad[oa]|sogr[oa]|genro|nora|esposa|marido|vizinh[oa]|s[oó]ci[oa]|herdeir[oa]|arrendat[aá]ri[oa]|meeir[oa]|pe[aã]o|empregad[oa]|parceir[oa])s?\b"
FORA = r"\b(?:estranh[oa]|desconhecid[oa]|de fora|terceir[oa])\b"
BEM = r"(sua|seu|da sua|do seu)\s+(fazenda|terra|s[ií]tio|ch[aá]cara|propriedade|heran[çc]a|gado|lavoura|ro[çc]a)|da heran[çc]a|da fazenda"
TEMPO = r"\b(anos?|dias?|meses|m[eê]s)\b"
NUM = r"\b\d+\b|\b(um|dois|duas|tr[eê]s|quatro|cinco|seis|sete|oito|nove|dez|onze|doze|quinze|vinte|trinta|cinquenta|cem|cento|mil)\b"
SIGLA = r"\b[A-Z]{2,}\b"
MORAL_TEMPO = r"tempo|prazo|calad|esper|perdid|demor|tarde|conta\b|correr|corre\b"

def n(s):
    return unicodedata.normalize("NFC", s)

def palavras(s):
    return re.findall(r"[\wÀ-ú]+", s)

def carregar(p):
    d = json.load(open(p, encoding="utf-8"))
    return {f["id"]: f for f in d}

def checar(F):
    """Itens automáticos. Cada um devolve (ok, valor mostrado)."""
    t = {i: n(F[i]["texto"]) for i in F}
    f1, f2 = t.get(1, ""), t.get(2, "")
    ult = max(F)
    meio = " ".join(t.get(i, "") for i in range(5, ult - 1))
    pers = re.findall(PROXIMOS, f1, re.I)
    chave = f2.split(":", 1)[1] if ":" in f2 else ""
    nums = re.findall(NUM, " ".join(t.get(i, "") for i in range(1, ult)), re.I)
    total = sum(len(palavras(x)) for x in t.values())
    editor_meio = [i for i in F if F[i]["quem"] != "narrador" and i != ult]
    R = {}
    R["A1 fala 1 abre com 'Você sabia que'"] = (f1.startswith("Você sabia que"), f1[:22] + "…")
    R["A2 personagem próximo na fala 1"] = (bool(pers), ", ".join(sorted(set(p.lower() for p in pers))) or "nenhum")
    R["A3 alguém de fora em contraste (estranho)"] = (bool(re.search(FORA, f1, re.I)), (re.search(FORA, f1, re.I) or [None])[0] if re.search(FORA, f1, re.I) else "não")
    R["A4 bem de quem assiste (sua terra, sua fazenda, a herança)"] = (bool(re.search(BEM, f1, re.I)), (re.search(BEM, f1, re.I).group(0) if re.search(BEM, f1, re.I) else "não"))
    R["A5 virada de poder ('pode' / 'não pode')"] = (bool(re.search(r"\bpode\b", f1, re.I)), "sim" if re.search(r"\bpode\b", f1, re.I) else "não")
    R["A6 fala 1 com até 30 palavras"] = (len(palavras(f1)) <= 30, f"{len(palavras(f1))} palavras")
    p8 = " ".join(palavras(f1)[:8])
    R["A8 o personagem aparece nas 8 primeiras palavras"] = (bool(re.search(PROXIMOS, p8, re.I)), p8 + "…")
    R["A7 fala 1 sem sigla nem número"] = (not re.search(SIGLA, f1) and not re.search(r"\d", f1), "limpa" if not re.search(SIGLA, f1) and not re.search(r"\d", f1) else "tem")
    R["B1 fala 2 no molde 'A explicação está em/numa … palavra(s): X'"] = (bool(re.match(r"A explicação está (numa|em \w+) palavras?:", f2)), f2)
    R["B2 chave curta (até 3 palavras depois dos dois-pontos)"] = (0 < len(palavras(chave)) <= 3, chave.strip() or "sem dois-pontos")
    R["C1 o personagem volta na fala 3"] = (bool(pers) and bool(re.search(PROXIMOS, t.get(3, ""), re.I)), "sim" if re.search(PROXIMOS, t.get(3, ""), re.I) else "não")
    R["D1 fala 4 cita a lei ('O Código Civil diz' / 'A lei diz')"] = (bool(re.search(r"\bdiz\b", t.get(4, ""), re.I)), t.get(4, "")[:40] + "…")
    vir = [i for i in range(5, ult) if t.get(i, "").startswith("Agora")]
    R["E1 virada marcada com 'Agora,' (falas 5 a 8)"] = (bool(vir), f"fala {vir[0]}" if vir else "não")
    R["F1 número de prazo (anos, dias, meses) no meio"] = (bool(re.search(TEMPO, meio, re.I)), ", ".join(sorted(set(m.lower() for m in re.findall(TEMPO, meio, re.I)))) or "não")
    R["F2 até 8 números ditos (escada curta, não lista)"] = (len(nums) <= 8, f"{len(nums)}")
    f9 = t.get(ult - 1, "")
    R["G1 penúltima fala é pergunta"] = (f9.rstrip().endswith("?"), f9)
    R["G2 a pergunta é sobre uma pessoa ('alguém')"] = (bool(re.search(r"\balgu[eé]m\b", f9, re.I)), "sim" if re.search(r"\balgu[eé]m\b", f9, re.I) else "não")
    R["G3 a pergunta fala da vida de quem assiste (sua/seu)"] = (bool(re.search(r"\b(sua|seu)\b", f9, re.I)), "sim" if re.search(r"\b(sua|seu)\b", f9, re.I) else "não")
    f10 = t.get(ult, "")
    R["H1 fecho no molde 'Eu sou o Dr. Pelicioni, advogado. Na/Em X, … Me segue pra …'"] = (bool(re.match(r"Eu sou o Dr\. Pelicioni, advogado\. (Na|No|Em) .+ Me segue pra", f10)), "sim" if re.match(r"Eu sou o Dr\. Pelicioni, advogado\. (Na|No|Em) .+ Me segue pra", f10) else "não")
    moral = f10.split("advogado.", 1)[-1].split("Me segue")[0]
    R["H2 moral do fecho é sobre tempo ou omissão"] = (bool(re.search(MORAL_TEMPO, moral, re.I)), moral.strip())
    R["I1 editor só no fecho (uma voz até a pergunta)"] = (not editor_meio, "sim" if not editor_meio else f"editor nas falas {editor_meio}")
    R["I2 10 falas"] = (len(F) == 10, f"{len(F)}")
    R["I3 de 160 a 195 palavras (o ouro tem 183 e 193; 55 a 57 s)"] = (160 <= total <= 195, f"{total}")
    return R

def main():
    arq = sys.argv[1]
    md = sys.argv[sys.argv.index("--md") + 1] if "--md" in sys.argv else None
    alvo = checar(carregar(arq)); ref = {k: checar(carregar(v)) for k, v in OURO.items()}
    linhas = ["| Item | Este roteiro | Caseiro | Irmão |", "|---|---|---|---|"]
    falta = []
    for k, (ok, val) in alvo.items():
        c, i = ref["caseiro"][k], ref["irmão"][k]
        cel = lambda o, v: ("✅ " if o else "❌ ") + str(v).replace("|", "/")[:70]
        linhas.append(f"| {k} | {cel(ok, val)} | {cel(*c)} | {cel(*i)} |")
        if not ok and (c[0] or i[0]): falta.append(k)
    nota = sum(ok for ok, _ in alvo.values()); tot = len(alvo)
    nc = sum(o for o, _ in ref["caseiro"].values()); ni = sum(o for o, _ in ref["irmão"].values())
    out = "\n".join(linhas) + f"\n\n**Nota automática:** {nota}/{tot} (caseiro {nc}/{tot}, irmão {ni}/{tot}).\n"
    out += ("\n**Desvios do padrão ouro** (itens que os dois vídeos de ouro, ou um deles, cumprem e este não):\n" + "\n".join(f"- {k}" for k in falta) + "\n") if falta else "\n**Nenhum desvio automático.**\n"
    print(out)
    if md: Path(md).write_text(out, encoding="utf-8")

if __name__ == "__main__":
    main()
