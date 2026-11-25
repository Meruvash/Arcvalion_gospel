"""Crivo de qualidade da imagem antes de entregar (pedido do editor, 21/11/2026, depois de gente deformada no vídeo do CCIR).

Nenhum vídeo, prévia ou capa vai ao editor sem passar por aqui E pela revisão visual dos quadros que este script gera.

Uso:
  python3 crivo_qualidade.py video.mp4 [--saida pasta] [--passo 1.0]
  python3 crivo_qualidade.py imagem.jpg [--saida pasta]      (prévia ou fonte de IA, antes de entrar no vídeo)

O que faz:
1. Tira um quadro a cada `--passo` segundos, em tamanho cheio, e monta folhas de 4 quadros (2×2, 1080 px) para revisão.
   Imagem solta: faz recortes ampliados 2× em grade (3×3), para ver rosto e mão de perto.
2. Mede a nitidez de cada quadro (variância do laplaciano, 512 px, escala de cinza) e marca os que caem para menos de
   45% da mediana do vídeo: borrão de IA ampliada, quadro derretido ou fusão mal feita.
3. Escreve `crivo.md` com a lista de verificação. Quem revisa abre TODAS as folhas e marca cada item.

A máquina não reconhece deformação: só aponta onde olhar. A aprovação é a revisão visual, item por item:
- H1 Rostos: dois olhos alinhados, nariz e boca no lugar, sem pele derretida nem metade do rosto borrada.
- H2 Mãos: dedos separados e em número certo, sem mão gigante, sem dedo fundido, sem mão saindo do nada.
- H3 Corpo: braços e pernas no número e no tamanho certos, sem membro trocado de pessoa nem corpo atravessando objeto.
- H4 Movimento: nas cenas animadas por IA, o rosto e a mão não mudam de forma entre um quadro e outro.
- H5 Figuras pintadas: ou têm forma humana completa (cabeça, rosto, braços, mãos), ou não aparecem.
  Boneco sem braço e sem rosto não passa.
- H6 Nitidez: nenhuma cena de gente borrada ou ampliada de resolução baixa.
- H7 Tela: legenda, cartão e carimbo não tapam rosto nem se atropelam; crédito de IA legível quando há cena de IA.
Qualquer item reprovado: refazer a cena ou trocar por imagem sem gente, nunca entregar "porque é rápido".
"""
import os, subprocess, sys
import numpy as np

def args():
    a = sys.argv[1:]
    alvo = a[0]
    saida = a[a.index("--saida") + 1] if "--saida" in a else os.path.splitext(alvo)[0] + "_crivo"
    passo = float(a[a.index("--passo") + 1]) if "--passo" in a else 1.0
    return alvo, saida, passo

def nitidez(arq):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", arq, "-vf", "scale=512:512,format=gray", "-f", "rawvideo", "-"],
                         capture_output=True, check=True).stdout
    g = np.frombuffer(raw, np.uint8).reshape(512, 512).astype(np.float32)
    lap = g[1:-1, 1:-1] * 4 - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:]
    return float(lap.var())

def video(alvo, saida, passo):
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", alvo]))
    ts = [round(t, 2) for t in np.arange(0.2, dur, passo)]
    qs = []
    for t in ts:
        q = os.path.join(saida, f"q_{t:06.2f}.jpg")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", alvo, "-frames:v", "1", "-q:v", "2", q], check=True)
        qs.append(q)
    folhas = []
    for k in range(0, len(qs), 4):
        grupo = qs[k:k + 4]
        while len(grupo) < 4: grupo.append(grupo[-1])
        f = os.path.join(saida, f"folha_{k // 4 + 1:02d}.jpg")
        ent = sum([["-i", g] for g in grupo], [])
        subprocess.run(["ffmpeg", "-v", "error", "-y", *ent, "-filter_complex",
                        "".join(f"[{i}]scale=540:540[s{i}];" for i in range(4)) + "[s0][s1][s2][s3]xstack=inputs=4:layout=0_0|w0_0|0_h0|w0_h0",
                        "-q:v", "2", f], check=True)
        folhas.append((f, ts[k:k + 4]))
    n = [nitidez(q) for q in qs]; med = float(np.median(n))
    baixos = [(t, v) for t, v in zip(ts, n) if v < 0.45 * med]
    return folhas, baixos, med

def imagem(alvo, saida):
    w, h = map(int, subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "stream=width,height", "-of", "csv=p=0", alvo]).decode().strip().split(","))
    folhas = []
    for i in range(3):
        for j in range(3):
            cw, ch = w // 3, h // 3
            f = os.path.join(saida, f"recorte_{i}{j}.jpg")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", alvo, "-vf", f"crop={cw}:{ch}:{j * cw}:{i * ch},scale={cw * 2}:{ch * 2}:flags=lanczos", "-q:v", "2", f], check=True)
            folhas.append((f, [f"linha {i + 1}, coluna {j + 1}"]))
    return folhas, [], nitidez(alvo)

def main():
    alvo, saida, passo = args(); os.makedirs(saida, exist_ok=True)
    eh_video = alvo.lower().endswith((".mp4", ".mov", ".webm"))
    folhas, baixos, med = video(alvo, saida, passo) if eh_video else imagem(alvo, saida)
    L = [f"# Crivo de qualidade: `{os.path.basename(alvo)}`", "",
         "Abra TODAS as folhas abaixo e marque cada item. Sem todos os itens aprovados, não entrega.", "",
         "## Folhas para revisão", ""] + [f"- `{f}` ({', '.join(str(t) + ' s' if eh_video else str(t) for t in tt)})" for f, tt in folhas]
    L += ["", f"## Nitidez (mediana {med:.0f})", ""]
    L += [f"- ⚠️ {t} s: nitidez {v:.0f} (abaixo de 45% da mediana): olhar de perto" for t, v in baixos] or ["- nenhum quadro muito abaixo da mediana"]
    L += ["", "## Revisão visual (preencher)", "", "| Item | Resultado | Onde / observação |", "|---|---|---|"]
    for it in ["H1 Rostos", "H2 Mãos", "H3 Corpo", "H4 Movimento (cenas de IA animadas)", "H5 Figuras pintadas",
               "H6 Nitidez das cenas de gente", "H7 Tela (legenda, cartão, carimbo, crédito de IA)"]:
        L.append(f"| {it} | ☐ aprovado ☐ reprovado | |")
    L += ["", "## Crivo artístico (docs/video/DIRECAO_ARTISTICA.md, cada pintura num quadro parado)", "", "| Item | Resultado | Cena / observação |", "|---|---|---|"]
    for it in ["A1 Cena completa", "A2 Ponto focal", "A3 Linhas que conduzem", "A4 4 planos e moldura", "A5 Luz e sombras",
               "A6 Paleta harmônica", "A7 Detalhe no foco", "A8 Movimento sutil", "A9 Funciona como pôster", "A10 Foco livre de texto"]:
        L.append(f"| {it} | ☐ aprovado ☐ reprovado | |")
    L += ["", "## Crivo de motion (docs/video/DIRECAO_MOTION.md)", "", "| Item | Resultado | Observação |", "|---|---|---|"]
    for it in ["M1 Função de cada cena no plano", "M2 3D só com espaço/geografia", "M3 Câmera motivada e na palavra certa",
               "M4 Uma coisa importante por vez", "M5 Curva de intensidade", "M6 Easing, antecipação, assentamento",
               "M7 Transições com continuidade", "M8 Linguagem visual única"]:
        L.append(f"| {it} | ☐ aprovado ☐ reprovado | |")
    open(os.path.join(saida, "crivo.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L[:6 + len(folhas) + 4 + max(1, len(baixos))]))
    print(f"\n-> {os.path.join(saida, 'crivo.md')}")

if __name__ == "__main__":
    main()
