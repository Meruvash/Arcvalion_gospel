"""Crivo de qualidade das fotos oficiais: decide se cada foto entra na página e em qual lugar.

Uso:
  python3 tools/imagens/crivo.py [slug ...]            relatório (sem argumentos, todos os jogos com fotos)
  python3 tools/imagens/crivo.py --aplicar slug ...    grava a escolha no fontes.json e libera a página

As regras estão em PADRAO_EDITORIAL.md ("Crivo de qualidade das fotos"). As medidas são automáticas;
o que exige olhar a foto fica em marcas no fontes.json, postas na revisão: "pessoas" (rosto de frente; mãos e rosto de perfil podem, pedido do usuário em 29/10/2026)
e "texto" (texto por cima da foto ou texto em outra língua que domina a imagem). "outra_edicao" não
reprova: a foto entra com o aviso no crédito.
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageFilter, ImageStat

ROOT = Path(__file__).resolve().parent.parent.parent

# Limites calibrados com as fotos já aprovadas (Terraforming Mars, Flip 7, Faraway, Wingspan, Arnak, Codenames, Nemesis...).
TOPO = {"lado": 800, "proporcao": 1.8, "branco": 0.35, "liso": 0.45}
JOGAR = {"lado": 600, "proporcao": 2.4}
CAIXA = {"lado": 400}
BRILHO = (40, 235)
NITIDEZ = 6
ORDEM_TOPO = ("mesa", "jogabilidade", "componentes")
ORDEM_JOGAR = ("componentes", "jogabilidade", "mesa")


def medir(arq):
    im = Image.open(arq).convert("RGB")
    w, h = im.size
    g = im.copy()
    g.thumbnail((400, 400))
    g = g.convert("L")
    px = list(g.getdata())
    W, H = g.size
    blocos = [ImageStat.Stat(g.crop((x, y, x + 10, y + 10))).stddev[0] for y in range(0, H - 10, 10) for x in range(0, W - 10, 10)]
    return {
        "lado": min(w, h),
        "proporcao": round(max(w, h) / min(w, h), 2),
        "brilho": round(ImageStat.Stat(g).mean[0]),
        # fundo de catálogo: muito branco recortado ou muitos trechos lisos (fundo de estúdio)
        "branco": round(sum(v > 235 for v in px) / len(px), 2),
        "liso": round(sum(s < 3 for s in blocos) / len(blocos), 2),
        "nitidez": round(ImageStat.Stat(g.filter(ImageFilter.FIND_EDGES)).mean[0], 1),
    }


def avaliar(f, m):
    """Motivos de reprovação geral e os lugares em que a foto pode entrar."""
    fora = []
    if f.get("pessoas"):
        fora.append("rosto de frente")
    if f.get("texto"):
        fora.append("texto por cima ou em outra língua")
    if not BRILHO[0] <= m["brilho"] <= BRILHO[1]:
        fora.append(f"brilho {m['brilho']}")
    if m["nitidez"] < NITIDEZ:
        fora.append(f"nitidez {m['nitidez']}")
    if fora:
        return fora, []
    lugares = []
    if f["tipo"] == "capa":
        if m["lado"] >= CAIXA["lado"]:
            lugares.append("preco")
        return (["caixa pequena demais"] if not lugares else []), lugares
    catalogo = m["branco"] >= TOPO["branco"] or m["liso"] >= TOPO["liso"]
    if m["lado"] >= TOPO["lado"] and m["proporcao"] <= TOPO["proporcao"] and not catalogo:
        lugares.append("topo")
    if m["lado"] >= JOGAR["lado"] and m["proporcao"] <= JOGAR["proporcao"]:
        lugares.append("jogar")
    return ([] if lugares else ["resolução ou proporção fora do limite"]), lugares


def escolher(fotos):
    """Topo: a melhor foto sem cara de catálogo; Como é jogar: outra foto, de preferência também sem fundo de catálogo."""
    pode = lambda lugar: [f for f in fotos if lugar in f["_lugares"]]
    topo = sorted(pode("topo"), key=lambda f: (ORDEM_TOPO.index(f["tipo"]), -f["_m"]["nitidez"]))
    topo = topo[0] if topo else None
    resto = [f for f in pode("jogar") if f is not topo]
    jogar = sorted(resto, key=lambda f: ("topo" not in f["_lugares"], ORDEM_JOGAR.index(f["tipo"])))
    caixa = pode("preco")
    return topo, (jogar[0] if jogar else None), (caixa[0] if caixa else None)


def crivo(slug, aplicar=False):
    p = ROOT / slug / "fotos" / "fontes.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    fotos = [f for f in d["fotos"] if f.get("aprovada")]
    for f in fotos:
        f["_m"] = medir(ROOT / slug / f["arquivo"])
        f["_fora"], f["_lugares"] = avaliar(f, f["_m"])
    topo, jogar, caixa = escolher(fotos)
    print(f"\n{slug}: {'PUBLICA' if topo else 'FICA COM O INFOGRÁFICO (nenhuma foto serve para o topo)'}")
    for f in fotos:
        uso = "topo" if f is topo else "como é jogar" if f is jogar else "preço" if f is caixa else "-"
        motivo = ", ".join(f["_fora"]) or ("pode: " + ", ".join(f["_lugares"]))
        print(f"  {f['arquivo']:28} {uso:13} {motivo}  {f['_m']}")
    if aplicar and topo:
        for f in d["fotos"]:
            for k in ("principal", "jogar", "fora", "_m", "_fora", "_lugares"):
                f.pop(k, None)
            if f is topo:
                f["principal"] = True
            elif f is jogar:
                f["jogar"] = True
            elif f is not caixa:
                f["fora"] = True
        d = {"slug": d["slug"], "usar_na_pagina": True, **{k: v for k, v in d.items() if k not in ("slug", "usar_na_pagina")}}
        p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print("  gravado no fontes.json")
    return bool(topo)


if __name__ == "__main__":
    args = sys.argv[1:]
    aplicar = "--aplicar" in args
    slugs = [a for a in args if not a.startswith("--")] or sorted(x.parent.parent.name for x in ROOT.glob("*/fotos/fontes.json"))
    for s in slugs:
        crivo(s, aplicar)
