"""Nota de aderência de um vídeo ao padrão "Reel Novela Visual padrão" (docs/video/REEL_NOVELA_VISUAL_PADRAO.md).

Uso:
  python3 tools/video/analisar_visual.py meu_reel.mp4 /tmp/m.json
  python3 tools/video/checar_reel_novela.py /tmp/m.json [--padrao docs/video/REEL_NOVELA_VISUAL_PADRAO.json] [--json]

Fórmula (por medida k com faixa [min_k, max_k], largura L_k = max_k - min_k, ou 1 se a faixa for um ponto):
  s_k = 1                                   se min_k <= x_k <= max_k
  s_k = max(0, 1 - d_k / L_k)               caso contrário, d_k = distância de x_k até a faixa
  A   = Σ w_k s_k / Σ w_k                   (aderência, 0 a 1); aprovado se A >= 0,80
Medida ausente no JSON conta s_k = 0. Sai com código 0 se aprovado, 1 se reprovado.
"""
import argparse
import json
import sys
from pathlib import Path

PADRAO = Path(__file__).resolve().parents[2] / "docs/video/REEL_NOVELA_VISUAL_PADRAO.json"


def pegar(d, chave):
    for parte in chave.split("."):
        if not isinstance(d, dict) or parte not in d or d[parte] is None:
            return None
        d = d[parte]
    return d


def nota(x, lo, hi):
    if x is None:
        return 0.0
    if lo <= x <= hi:
        return 1.0
    largura = (hi - lo) or 1.0
    d = lo - x if x < lo else x - hi
    return max(0.0, 1.0 - d / largura)


def avaliar(metricas, padrao):
    linhas, soma, pesos = [], 0.0, 0.0
    for m in padrao["medidas"]:
        x = pegar(metricas, m["chave"])
        s = nota(x, m["min"], m["max"])
        soma += m["peso"] * s
        pesos += m["peso"]
        linhas.append({"medida": m["rotulo"], "valor": x, "alvo": m["alvo"], "faixa": [m["min"], m["max"]], "nota": round(s, 3)})
    a = soma / pesos if pesos else 0.0
    return {"aderencia": round(a, 3), "aprovado": a >= padrao["aprovacao"], "medidas": linhas}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("metricas")
    ap.add_argument("--padrao", default=str(PADRAO))
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    r = avaliar(json.load(open(a.metricas)), json.load(open(a.padrao)))
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        for l in r["medidas"]:
            v = "—" if l["valor"] is None else (round(l["valor"], 3) if isinstance(l["valor"], float) else l["valor"])
            marca = "ok " if l["nota"] == 1 else ("~  " if l["nota"] > 0 else "X  ")
            print(f"{marca}{l['medida']:<44} {str(v):>9}  alvo {l['alvo']:<6} faixa {l['faixa']}")
        print(f"\naderência A = {r['aderencia']:.3f} → {'APROVADO' if r['aprovado'] else 'REPROVADO'} (corte 0,80)")
    sys.exit(0 if r["aprovado"] else 1)


if __name__ == "__main__":
    main()
