"""Monta o prompt do infográfico quadrado 1:1 a partir do roteiro em conteudo/<slug>.json (padrão editorial v2).

Uso: python3 tools/prompt_infografico.py conteudo/<slug>.json [...]
"""
import json
import sys

TAMANHO = "2048x2048"


def prompt(c):
    r = c["roteiro"]
    q = lambda s: f'"{s}"'
    lista = lambda xs: " · ".join(q(x) for x in xs)
    passos = "\n".join(f"Step {i} title {q(t)} — text {q(d)}" for i, (t, d) in enumerate(r["passos"], 1))
    numeros = "\n".join(f"Stat box {i}: label {q(k)}, big value {q(v)}, small line {q(x)}" for i, (k, v, x) in enumerate(r["numeros"], 1))
    return f"""Use the reference images as the style and layout template for an "ELITE BOARDGAMERS" board game review infographic. The FIRST reference (Código Secreto) is the main template: copy its density, hierarchy and panel structure. Same dark navy background, glowing neon-bordered panels, gold "ELITE BOARDGAMERS" crown logo top-left, huge bold 3D title, parchment note boxes.
FORMAT: SQUARE 1:1 Instagram post (2048x2048), NOT a tall poster. Compress the template's full structure into the square: same blocks, tighter panels, smaller but crisp and legible text. Fill the whole canvas edge to edge with information; no empty decorative areas, no empty strip at the bottom.

LAYOUT, top to bottom:
1. Top band (short): logo top-left; huge title; tagline banner under the title; a tilted parchment note box top-right with the highlight text; themed artwork behind.
2. Middle band: left sidebar of 10 icon + text rows; a large stylized game box in the center-left; on the right, a row of 4 stat boxes (label, big value, small context line), and below them the game components laid out on a wooden table.
3. "COMO FUNCIONA?" header with the summary line beside it, then a row of 5 numbered step cards (blue, green, orange, purple, red), each with a small illustration on top and the full step text below.
4. Three panels side by side: green "PONTOS FORTES" with check marks, red "PONTOS DE ATENÇÃO" with X marks, blue "FICHA TÉCNICA" with small icons per line.
5. Bottom band: "PRÊMIOS" panel with gold laurel medals; the extra panel; a gold "VEREDITO ELITE BOARDGAMERS" box with a crown and the verdict phrase; next to it a parchment box with the verdict paragraph. Give the bottom band enough height that every paragraph fits at the same text size as the rest; never shrink or squeeze text into a corner.

Theme for this game, {c["jogo"]}: {r["tema"]}. Top artwork: {r["cena"]}. Box art and table: stylized illustration of {r["mesa"]}. Do not reuse imagery from the reference games. Render the game box and every component (cards, boards, tokens, dice, miniatures) as a premium, high-detail product shot: crisp sharp edges, realistic materials and printing, soft studio lighting, accurate perspective. No blurry, warped, melted or low-resolution components. Stylized illustrations only; no real publisher logos. Use a Brazilian flag icon ONLY on the sidebar row that names the Brazilian publisher, if there is one; no other flags.

Render EXACTLY this Portuguese text, spelled exactly as written with correct accents, and no other text:
Logo: "ELITE BOARDGAMERS"
Title: {q(r["titulo"])}
Tagline banner: {q(r["chamada"])}
Parchment note top-right: {q(r["destaque"])}
Sidebar rows: {lista(r["lateral"])}
{numeros}
"COMO FUNCIONA?" — summary line: {q(r["como_resumo"])}
{passos}
Green panel "PONTOS FORTES": {lista(r["fortes"])}
Red panel "PONTOS DE ATENÇÃO": {lista(r["atencao"])}
Blue panel "FICHA TÉCNICA": {lista(r["ficha"])}
Panel "PRÊMIOS": gold medals: {lista(r["premios"])}
Panel {q(r["extra"]["titulo"])}: {q(r["extra"]["texto"])}
Verdict box: "VEREDITO ELITE BOARDGAMERS" — {q(r["veredito"])}
Verdict paragraph: {q(r["veredito_texto"])}"""


if __name__ == "__main__":
    out = {}
    for a in sys.argv[1:]:
        c = json.load(open(a, encoding="utf-8"))
        out[c["slug"]] = prompt(c)
    print(json.dumps(out, ensure_ascii=False))
