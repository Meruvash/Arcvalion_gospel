"""Auditoria do vídeo renderizado: os 3 primeiros segundos e o ritmo da imagem (desde 19/11/2026).

Parte 3 da auditoria de padrão ouro (docs/video/AUDITORIA_PADRAO_OURO.md). Os testes vêm de duas skills públicas lidas
em 19/11/2026 e foram adaptados ao nosso formato:
- "virality" da Ootto (MIT): o quadro 0 já se move; não é cartão parado (o quadro de 0,5 s e o de 3 s não podem ser
  iguais); algo forte acontece antes de 3 s; a primeira palavra vem em até 0,5 s;
- "virality" da master-skills, de Jake Schincariol (MIT): nenhum plano parado por muito tempo; a imagem muda a cada fala.

Uso: python3 auditar_video.py video.mp4 [--tempos tempos.json] [--ref ouro1.mp4 ouro2.mp4]
- `--tempos`: o hf/assets/data/tempos.json do vídeo; com ele, a auditoria mede a primeira palavra e a mudança por fala.
- `--ref`: vídeos de padrão ouro para mostrar lado a lado.

A medida é a diferença média de brilho entre quadros (escala de cinza 96×96, 10 quadros por segundo). Os limites foram
calibrados nos vídeos do canal em 19/11/2026 e devem ser revistos quando houver mais resultados.
"""
import json, subprocess, sys
import numpy as np

FPS, S = 10, 96
LIM_MOVE = 1.2      # diferença mínima entre 0 e 0,5 s (o quadro 0 já se move)
LIM_CARTAO = 4.0    # diferença mínima entre 0,5 s e 3 s (não é cartão parado)
LIM_PICO = 8.0      # salto entre dois quadros seguidos que conta como "acontecimento" (carimbo, clarão, corte)
LIM_PARADO = 0.35   # abaixo disso, dois quadros seguidos são "a mesma imagem"
MAX_PARADO = 3.0    # segundos seguidos de imagem praticamente parada que ainda passam

def quadros(video):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-vf", f"fps={FPS},scale={S}:{S},format=gray", "-f", "rawvideo", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, S, S).astype(np.float32)

def medir(video, tempos=None):
    q = quadros(video); d = np.abs(np.diff(q, axis=0)).mean(axis=(1, 2))      # d[k]: diferença entre o quadro k e o k+1
    f = lambda t: q[min(int(round(t * FPS)), len(q) - 1)]
    R = {}
    R["V1 quadro 0 com imagem (não preto nem vazio)"] = (q[0].mean() > 30 and q[0].std() > 20, f"brilho {q[0].mean():.0f}, contraste {q[0].std():.0f}")
    mv = np.abs(f(0.5) - f(0)).mean()
    R["V2 o quadro 0 já se move (0 → 0,5 s)"] = (mv > LIM_MOVE, f"{mv:.1f}")
    ct = np.abs(f(3.0) - f(0.5)).mean()
    R["V3 não é cartão parado (0,5 s ≠ 3 s)"] = (ct > LIM_CARTAO, f"{ct:.1f}")
    pico = d[: 3 * FPS].max(); tp = (d[: 3 * FPS].argmax() + 1) / FPS
    R["V4 acontecimento forte antes de 3 s"] = (pico > LIM_PICO, f"salto {pico:.1f} aos {tp:.1f} s")
    parado, cur = 0, 0
    for x in d:
        cur = cur + 1 if x < LIM_PARADO else 0; parado = max(parado, cur)
    R["V5 nenhum trecho parado longo (até 3 s)"] = (parado / FPS <= MAX_PARADO, f"{parado / FPS:.1f} s")
    if tempos:
        T = json.load(open(tempos, encoding="utf-8")); fal = T["falas"]
        p0 = T["palavras"][0]["s"] if T.get("palavras") else fal[0]["inicio"]
        R["S1 primeira palavra em até 0,5 s"] = (p0 <= 0.5, f"{p0:.2f} s")
        sem = []
        for fa in fal:
            a, b = int(fa["inicio"] * FPS), max(int(fa["fim"] * FPS), int(fa["inicio"] * FPS) + 1)
            if d[a:b].max(initial=0) < LIM_PICO / 2: sem.append(fa["fala"])
        R["S2 a imagem muda em toda fala (corte, cartão, carimbo, letreiro)"] = (not sem, "todas" if not sem else f"sem mudança nas falas {sem}")
    return R

def main():
    a = sys.argv[1:]
    tempos = a[a.index("--tempos") + 1] if "--tempos" in a else None
    refs = a[a.index("--ref") + 1:] if "--ref" in a else []
    alvo = medir(a[0], tempos); ref = [(r, medir(r)) for r in refs]
    cab = "| Item | Este vídeo |" + "".join(f" {r.rsplit('/', 1)[-1]} |" for r, _ in ref)
    print(cab); print("|---" * (2 + len(ref)) + "|")
    for k, (ok, v) in alvo.items():
        linha = f"| {k} | {'✅' if ok else '❌'} {v} |"
        for _, R in ref: linha += (f" {'✅' if R[k][0] else '❌'} {R[k][1]} |" if k in R else " — |")
        print(linha)
    print(f"\n**Nota da abertura e do ritmo:** {sum(o for o, _ in alvo.values())}/{len(alvo)}")

if __name__ == "__main__":
    main()
