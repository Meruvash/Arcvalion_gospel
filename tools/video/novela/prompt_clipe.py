#!/usr/bin/env python3
"""Monta e confere o prompt de um clipe da novela para o Seedance (Higgsfield), a partir de um JSON de clipe.

Uso: python3 tools/video/novela/prompt_clipe.py clipe.json [--saida prompt.txt]
Sai com código 1 se alguma regra mecânica falhar (o prompt não deve ser enviado).

A ordem dos blocos e as regras vêm do que foi medido nos nossos testes de 23/11/2026 (docs/video/novela/FORMATO_CENA.md) e
de ideias adaptadas de três coleções públicas lidas em 23/11/2026 (drama-skills, MIT; screenwriting-skills, MIT;
micro-drama-skills): ver docs/video/novela/REGRAS_ROTEIRO.md.

Formato do clipe.json:
{
 "id": "k4", "duracao": 6, "modelo": "seedance_2_0_mini",
 "cenario": "terreiro",                       # chave de CENARIOS
 "personagens": ["Dr. Pelicioni", "Valdir"],   # na ordem das folhas anexadas (@Image1, @Image2…)
 "voz": "Dr. Pelicioni",                       # o único falante do clipe (ou null); a amostra vai como @Audio1
 "planos": [ {"de": 0, "ate": 2.5, "quadro": "close-up", "camera": "static, eye level",
              "quem": "Valdir", "acao": "his smile fades", "expressao": "suspicious", "fala": false} , ...],  # "fala": true no plano de quem fala
 "fala": {"texto": "…", "emocao": "calm, low, slow", "inicio": 1.0}   # opcional
}
"""
import json, re, sys

# Trava visual de cada personagem: frase fixa, igual em todos os clipes (ELENCO_FIXO.md e as folhas aprovadas).
TRAVAS = {
    "Dr. Pelicioni": "the man of his reference sheet, short dark hair, trimmed beard, dark-rimmed glasses with clear "
                     "transparent lenses, navy blue blazer with a blue polka-dot pocket square, light-blue open-collar shirt, grey trousers",
    "Rosa": "the woman of her reference sheet, mid-fifties, grey-streaked hair tied back, floral cotton blouse in soft pink and green",
    "Valdir": "the heavy-set man of his reference sheet, grey mustache, white cowboy hat, red plaid shirt, gold chain",
    "Cleide": "the woman of her reference sheet, bleached blonde blow-dried hair, long red nails, leopard-print blouse, big gold earrings",
    "Tavares": "the man of his reference sheet, slicked-back hair, tight shiny grey suit without tie, mirrored sunglasses",
    "Bruna": "the young woman of her reference sheet, loose curly hair, freckles, plain t-shirt and denim jacket",
    "Antônio": "the old man of his reference sheet, sparse white beard, worn button shirt, straw hat",
    "Zuleide": "the woman of her reference sheet, short grey hair, cardigan, reading glasses on a chain",
}
CENARIOS = {
    "terreiro": "the dirt farmyard in front of a simple white farmhouse with a wooden gate, late-afternoon golden light",
    "cozinha": "a simple rural farmhouse kitchen with a wooden table, enamel coffee pot, morning light from a window",
    "porteira": "a wooden farm gate on a red dirt road, pasture behind, golden hour",
    "escritorio": "a sober law office with dark wood and books, soft side light",
}
LOOK = ("Live-action cinematic Brazilian telenovela, vertical 9:16, realistic skin and fabric, shallow depth of field, "
        "subtle handheld camera.")
EXCLUSOES = ("Every shot is one full frame: no split screen, no panels, no subtitles, no on-screen text, no speech bubbles, "
             "no watermark. The reference images never appear inside the frame.")
SEM_MUSICA = "No background music."
PALAVRAS_POR_S = 2.9
FOLGA_FINAL = 1.0   # ~1 s depois da fala, para a última palavra não ser cortada (FORMATO_CENA.md)


def palavras(s):
    return len(re.findall(r"[\wÀ-ÿ]+", s or ""))


def montar(c):
    erros = []
    pers = c.get("personagens", [])
    tag = {p: f"@Image{i + 1}" for i, p in enumerate(pers)}
    for p in pers:
        if p not in TRAVAS:
            erros.append(f"personagem sem trava: {p}")
    if c.get("cenario") not in CENARIOS:
        erros.append(f"cenário desconhecido: {c.get('cenario')}")
    # Planos: contíguos de 0 até a duração, sem sobreposição (passar corta a fala; sobrar faz câmera lenta)
    pl = sorted(c["planos"], key=lambda x: x["de"])
    t = 0.0
    for x in pl:
        if abs(x["de"] - t) > 0.01:
            erros.append(f"plano começa em {x['de']} s, esperado {t} s (buraco ou sobreposição)")
        if x["ate"] - x["de"] < 1.5:
            erros.append(f"plano {x['de']}–{x['ate']} s com menos de 1,5 s")
        t = x["ate"]
    if abs(t - c["duracao"]) > 0.01:
        erros.append(f"planos somam {t} s, o clipe tem {c['duracao']} s")
    # Um falante só
    falantes = {x["quem"] for x in pl if x.get("fala")}
    if len(falantes) > 1:
        erros.append(f"mais de um falante no clipe: {sorted(falantes)}")
    f = c.get("fala")
    if f:
        if not c.get("voz"):
            erros.append("há fala mas não há voz (amostra) definida")
        cabe = (c["duracao"] - f.get("inicio", 0.5) - FOLGA_FINAL) * PALAVRAS_POR_S
        if palavras(f["texto"]) > cabe:
            erros.append(f"fala com {palavras(f['texto'])} palavras não cabe ({cabe:.0f} no máximo neste clipe)")
    # Texto
    linhas = [LOOK, ""]
    quem = [f"{tag[p]} is {p}: {TRAVAS.get(p, '')}." for p in pers]
    linhas.append(" ".join(quem))
    if c.get("voz"):
        linhas.append(f"@Audio1 is the voice of {tag.get(c['voz'], '@Image1')}, {c['voz']}: every line {c['voz']} speaks is in this voice.")
    linhas += ["", f"Setting: {CENARIOS.get(c.get('cenario'), '')}.", EXCLUSOES, ""]
    for x in pl:
        q = x["quem"]
        ref = f"{tag[q]} {q}" if q in tag else q
        linhas.append(f"{x['de']:g}-{x['ate']:g} s: {x['quadro']}, {x.get('camera', 'static')}. {ref} {x['acao']}"
                      + (f", {x['expressao']}" if x.get("expressao") else "") + ".")
    if f:
        linhas += ["", f"{tag.get(c['voz'], '')} {c['voz']} says in Brazilian Portuguese ({f.get('emocao', 'natural')}): \"{f['texto']}\"",
                   "The line starts directly on its first word, with no breath or noise before it, and is spoken once, complete.",
                   "Every spoken line is in Brazilian Portuguese, exactly the words in quotes; nobody speaks any other language."]
        depois = [x for x in pl if x["de"] >= (f.get("inicio", 0) + 0.1) and not x.get("fala")]
        if depois:
            linhas.append("Every shot after the line is in silence.")
    else:
        linhas += ["", "Nobody speaks in this clip."]
    linhas += [SEM_MUSICA + " Only natural ambient sound of the place.",
               "Every character keeps the face, hair and clothes of their reference sheet in close-up and in motion; "
               "the place and the light stay photographic and realistic."]
    txt = "\n".join(linhas)
    if "silence" in txt.lower() and "total silence" in txt.lower():
        erros.append("o prompt pede silêncio total, o que apaga a fala")
    return txt, erros


def main():
    c = json.load(open(sys.argv[1], encoding="utf-8"))
    txt, erros = montar(c)
    if "--saida" in sys.argv:
        open(sys.argv[sys.argv.index("--saida") + 1], "w", encoding="utf-8").write(txt + "\n")
    print(txt)
    print("\n" + ("✅ prompt conferido" if not erros else "❌ " + "\n❌ ".join(erros)))
    sys.exit(1 if erros else 0)


if __name__ == "__main__":
    main()
