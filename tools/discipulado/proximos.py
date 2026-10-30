"""Próximos temas do Discipulado, na ordem que completa as trilhas (pedido do editor, 30/10/2026).

Uso: python3 tools/discipulado/proximos.py [N]   (padrão 5)
Primeiro os temas que faltam nas trilhas (a trilha com menos temas faltando vem antes; empate pela ordem do catálogo),
cada tema uma vez só, na ordem da trilha; depois os previstos das categorias (a categoria com menos estudos antes).
Ao lado de cada tema, a categoria sugerida e as trilhas em que ele entra.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import portal  # noqa: E402
from discipulado.checar_licao import catalogo, licoes  # noqa: E402


def proximos(n=5):
    cat = catalogo()
    estudos = [json.loads(p.read_text(encoding="utf-8")) for p in licoes()]
    feitos = {c["titulo"] for c in estudos}
    por_cat = {x["slug"]: sum(1 for c in estudos if c.get("categoria") == x["slug"]) for x in cat["categorias"]}
    onde = {t: x["slug"] for x in cat["categorias"] for t in x.get("previstos", [])}
    faltam = lambda t: [i["titulo"] for i in t["estudos"] if isinstance(i, dict) and i["titulo"] not in feitos]
    fila = []
    for t in sorted(cat["trilhas"], key=lambda t: len(faltam(t))):
        for titulo in faltam(t):
            if titulo not in [f[0] for f in fila]:
                fila.append((titulo, onde.get(titulo, "?")))
    for x in sorted(cat["categorias"], key=lambda x: por_cat[x["slug"]]):
        for titulo in x.get("previstos", []):
            if titulo not in feitos and titulo not in [f[0] for f in fila]:
                fila.append((titulo, x["slug"]))
    trilhas = lambda titulo: [t["slug"] for t in cat["trilhas"] if any(isinstance(i, dict) and i["titulo"] == titulo for i in t["estudos"])]
    return [(titulo, c, trilhas(titulo)) for titulo, c in fila[:n]]


if __name__ == "__main__":
    portal.iniciar()
    for titulo, c, ts in proximos(int(sys.argv[1]) if len(sys.argv) > 1 else 5):
        print(f"{titulo}  | categoria: {c}" + (f" | trilhas: {', '.join(ts)}" if ts else ""))
