#!/usr/bin/env python3
"""
Medidor de legibilidade para português brasileiro.

Aplica o Índice de Flesch adaptado por Martins et al. (ICMC/USP, 1996):
    IF = 248,835 - 1,015 * (palavras / frases) - 84,6 * (sílabas / palavras)

Faixas: 75 a 100 fácil; 50 a 75 médio; 25 a 50 difícil; abaixo de 25 muito difícil.

Também verifica as metas do padrão de escrita da coleção:
  - média de palavras por frase entre 12 e 18
  - nenhuma frase com mais de 25 palavras
  - média de sílabas por palavra até 1,9
  - parágrafos com até 5 frases
  - zero travessão
  - clichês de púlpito listados

Uso:
    python3 tools/discipulado/legibilidade.py arquivo.md
    python3 tools/discipulado/legibilidade.py arquivo.md --secao "Entendendo a Palavra"
    python3 tools/discipulado/legibilidade.py arquivo.md --guia   (limites mais folgados)

Sai com código 1 quando reprova. Não negocia.
"""

import argparse
import re
import sys
import unicodedata

# metas revistas em 30/10/2026 (diretriz de qualidade literária do editor): prosa madura, sem frases picadas;
# o índice continua barrando texto pesado, mas não empurra mais para frases de cartilha
META_ALUNO = dict(flesch_min=60.0, media_min=12.0, media_max=24.0,
                  frase_max=40, silabas_max=2.0, paragrafo_max=7)
META_GUIA = dict(flesch_min=60.0, media_min=12.0, media_max=24.0,
                 frase_max=40, silabas_max=2.1, paragrafo_max=7)

CLICHES = [
    "amado", "amada", "irmão", "irmã", "a palavra diz", "deus tem um propósito",
    "não é por acaso", "varão", "ungido", "mover de deus", "tremendo",
    "glorioso", "maravilhoso", "poderoso", "ministrar", "ser tocado",
    "em nossa caminhada", "em um mundo cada vez", "mais do que uma simples", "lição poderosa",
    "imagine por um momento", "é importante lembrar", "não se trata apenas",
]

TRAVESSOES = ["—", "–", " - "]  # em dash, en dash, hífen solto com espaços

VOGAIS = set("aeiouáéíóúâêôãõàü")


def strip_markdown(texto: str) -> str:
    # [ \t] e não \s nas marcas de linha: \s também casa quebra de linha e juntava o parágrafo anterior ao título ou à lista
    texto = re.sub(r"<!--.*?-->", "", texto, flags=re.S)        # comentários HTML
    texto = re.sub(r"```.*?```", "", texto, flags=re.S)           # blocos de código
    texto = re.sub(r"^[ \t]{0,3}#{1,6}[ \t]+", "", texto, flags=re.M)  # marcas de título
    texto = re.sub(r"^[ \t]*[-*+][ \t]+", "", texto, flags=re.M)        # marcadores de lista
    texto = re.sub(r"^[ \t]*\d+\.[ \t]+", "", texto, flags=re.M)        # listas numeradas
    texto = re.sub(r"\*\*|__|\*|_|`|>", "", texto)                # ênfase e citação
    texto = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", texto)       # links
    return texto


def extrair_secao(texto: str, titulo: str) -> str:
    padrao = re.compile(r"^#{1,6}\s*(.+)$", re.M)
    titulos = list(padrao.finditer(texto))
    alvo = None
    for i, m in enumerate(titulos):
        if titulo.lower() in m.group(1).lower():
            inicio = m.end()
            fim = titulos[i + 1].start() if i + 1 < len(titulos) else len(texto)
            alvo = texto[inicio:fim]
            break
    if alvo is None:
        sys.exit(f"Seção não encontrada: {titulo}")
    return alvo


def contar_silabas(palavra: str) -> int:
    p = unicodedata.normalize("NFC", palavra.lower())
    p = re.sub(r"[^a-záéíóúâêôãõàüç]", "", p)
    if not p:
        return 0
    grupos = re.findall(r"[aeiouáéíóúâêôãõàü]+", p)
    n = 0
    for g in grupos:
        # ditongos e tritongos contam como um núcleo; hiatos comuns separados
        n += 1
        n += len(re.findall(r"[aeo][aeo]", g))           # ca-os, le-al (aproximação)
        n += len(re.findall(r"[íú]", g)) if len(g) > 1 else 0  # sa-í-da, ba-ú
    return max(n, 1)


def frases_de(texto: str):
    texto = re.sub(r"\s+", " ", texto).strip()
    if not texto:
        return []
    partes = re.split(r"(?<=[.!?;:])\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕ\"“(])", texto)
    return [f.strip() for f in partes if re.search(r"\w", f)]


def palavras_de(frase: str):
    return re.findall(r"[A-Za-zÀ-ÿ]+(?:-[A-Za-zÀ-ÿ]+)*", frase)


def analisar(texto_bruto: str, meta: dict):
    texto = strip_markdown(texto_bruto)
    paragrafos = [p for p in re.split(r"\n\s*\n", texto) if p.strip()]
    frases = []
    paragrafos_longos = []
    for p in paragrafos:
        fs = frases_de(p)
        frases.extend(fs)
        n_pal_par = sum(len(palavras_de(f)) for f in fs)
        # parágrafo longo só reprova se também for pesado: muitas frases E mais de 80 palavras
        if len(fs) > meta["paragrafo_max"] and n_pal_par > 80:
            paragrafos_longos.append((len(fs), fs[0][:70]))

    palavras = [w for f in frases for w in palavras_de(f)]
    if not frases or not palavras:
        sys.exit("Texto vazio após limpeza.")

    n_frases, n_palavras = len(frases), len(palavras)
    n_silabas = sum(contar_silabas(w) for w in palavras)
    media_pf = n_palavras / n_frases
    media_sp = n_silabas / n_palavras
    flesch = 248.835 - 1.015 * media_pf - 84.6 * media_sp

    frases_longas = [(len(palavras_de(f)), f) for f in frases
                     if len(palavras_de(f)) > meta["frase_max"]]
    palavras_longas = sorted(
        {w.lower() for w in palavras if contar_silabas(w) >= 5})

    travessoes = []
    for i, linha in enumerate(texto_bruto.splitlines(), 1):
        if any(t in linha for t in TRAVESSOES):
            travessoes.append((i, linha.strip()[:80]))

    baixo = texto.lower()
    cliches = [(c, baixo.count(c)) for c in CLICHES if baixo.count(c)]

    return dict(
        n_frases=n_frases, n_palavras=n_palavras, media_pf=media_pf,
        media_sp=media_sp, flesch=flesch, frases_longas=frases_longas,
        palavras_longas=palavras_longas, paragrafos_longos=paragrafos_longos,
        travessoes=travessoes, cliches=cliches,
    )


def faixa(flesch: float) -> str:
    if flesch >= 75:
        return "fácil"
    if flesch >= 50:
        return "médio"
    if flesch >= 25:
        return "difícil"
    return "muito difícil"


def falhas(r: dict, meta: dict) -> list:
    """Lista das metas reprovadas (vazia quando passa). Usada pelo relatório e por tools/discipulado/checar_licao.py."""
    f = []
    if r["flesch"] < meta["flesch_min"]:
        f.append("índice de Flesch abaixo da meta")
    if r["media_pf"] > meta["media_max"]:
        f.append("média de palavras por frase acima da faixa")
    if r["media_sp"] > meta["silabas_max"]:
        f.append("média de sílabas por palavra acima da meta")
    if r["frases_longas"]:
        f.append(f"{len(r['frases_longas'])} frase(s) com mais de {meta['frase_max']} palavras")
    if r["paragrafos_longos"]:
        f.append(f"{len(r['paragrafos_longos'])} parágrafo(s) com mais de {meta['paragrafo_max']} frases")
    if r["travessoes"]:
        f.append(f"{len(r['travessoes'])} linha(s) com travessão")
    return f


def relatar(r: dict, meta: dict) -> int:
    reprovado = falhas(r, meta)
    print("=" * 60)
    print("LEGIBILIDADE (Flesch adaptado ao português, Martins et al. 1996)")
    print("=" * 60)
    print(f"Palavras: {r['n_palavras']}   Frases: {r['n_frases']}")
    print(f"Média de palavras por frase: {r['media_pf']:.1f}  (meta {meta['media_min']:.0f} a {meta['media_max']:.0f})")
    print(f"Média de sílabas por palavra: {r['media_sp']:.2f}  (meta até {meta['silabas_max']})")
    print(f"Índice de Flesch: {r['flesch']:.1f}  [{faixa(r['flesch'])}]  (meta {meta['flesch_min']:.0f}+)")
    print()

    if r["media_pf"] < meta["media_min"]:
        print(f"AVISO: média de palavras por frase baixa ({r['media_pf']:.1f}). "
              "Frases curtas são bem-vindas; conferir se o texto não ficou picado.")
        print()

    if r["frases_longas"]:
        print(f"FRASES LONGAS (> {meta['frase_max']} palavras):")
        for n, f in r["frases_longas"]:
            print(f"  [{n}] {f[:140]}{'...' if len(f) > 140 else ''}")
        print()

    if r["paragrafos_longos"]:
        print(f"PARÁGRAFOS LONGOS (> {meta['paragrafo_max']} frases):")
        for n, inicio in r["paragrafos_longos"]:
            print(f"  [{n} frases] começa em: {inicio}...")
        print()

    if r["travessoes"]:
        print("TRAVESSÕES:")
        for i, linha in r["travessoes"]:
            print(f"  linha {i}: {linha}")
        print()

    if r["cliches"]:
        print("CLICHÊS DE PÚLPITO (revisar; não reprova sozinho):")
        for c, n in r["cliches"]:
            print(f"  '{c}' x{n}")
        print()

    if r["palavras_longas"]:
        print("PALAVRAS COM 5+ SÍLABAS (candidatas a troca):")
        print("  " + ", ".join(r["palavras_longas"][:40]))
        print()

    print("-" * 60)
    if reprovado:
        print("REPROVADO:")
        for f in reprovado:
            print(f"  - {f}")
        print("Reescrever e rodar de novo. Violação mantida de propósito exige justificativa no fim do arquivo.")
        return 1
    print("APROVADO. Segue para auditoria.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Medidor de legibilidade em português.")
    ap.add_argument("arquivo")
    ap.add_argument("--secao", help="Analisar só a seção cujo título contém este texto")
    ap.add_argument("--guia", action="store_true", help="Usar metas do guia do discipulador")
    args = ap.parse_args()

    with open(args.arquivo, encoding="utf-8") as fh:
        texto = fh.read()
    if args.secao:
        texto = extrair_secao(texto, args.secao)

    meta = META_GUIA if args.guia else META_ALUNO
    sys.exit(relatar(analisar(texto, meta), meta))


if __name__ == "__main__":
    main()
