#!/usr/bin/env python3
"""Triagem de clipes gerados (REGRAS_ROTEIRO.md §7): baixa, transcreve, compara com a fala do roteiro e monta folhas de quadros.

Uso: python3 tools/video/novela/triagem_clipe.py pasta_producao idx=url [idx=url ...] [--folhas pasta_folhas]
- pasta_producao tem clipes/cNN_*.json; o vídeo vai para planos/cNN.mp4.
- Imprime, por clipe: duração, transcrição, palavras que faltam e um veredito ("ok" ou "REFAZER").
- A revisão visual (rosto, mãos, texto na tela) continua sendo feita olhando as folhas.
"""
import glob, json, os, re, subprocess, sys, unicodedata, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from montar_cena import stt_palavras  # noqa: E402


def norm(s):
    s = unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode()
    s = s.replace("180", "cento e oitenta")
    return re.findall(r"[a-z]+", s)


def main():
    base = os.path.abspath(sys.argv[1]); pares = [a for a in sys.argv[2:] if "=" in a]
    folhas = sys.argv[sys.argv.index("--folhas") + 1] if "--folhas" in sys.argv else os.path.join(base, "folhas_triagem")
    os.makedirs(os.path.join(base, "planos"), exist_ok=True); os.makedirs(folhas, exist_ok=True)
    for par in pares:
        idx, url = par.split("=", 1); idx = int(idx)
        cj = glob.glob(os.path.join(base, "clipes", f"c{idx:02d}_*.json"))[0]; c = json.load(open(cj, encoding="utf-8"))
        mp4 = os.path.join(base, "planos", f"c{idx:02d}.mp4")
        if not os.path.exists(mp4):
            urllib.request.urlretrieve(url, mp4)
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp4],
                                   capture_output=True, text=True).stdout)
        wav = mp4.replace(".mp4", ".wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp4, "-vn", "-ac", "1", "-ar", "44100", wav], check=True)
        palavras, texto = stt_palavras(wav)
        os.remove(wav)
        falta, extra = [], []
        if c.get("fala"):
            alvo, dito = norm(c["fala"]["texto"]), norm(texto)
            falta = [w for w in alvo if w not in dito]
        else:
            extra = [w["text"] for w in palavras]
        # folha de quadros: 4 quadros
        qs = [dur * f for f in (0.1, 0.35, 0.6, 0.9)]
        imgs = []
        for k, t in enumerate(qs):
            p = os.path.join(folhas, f"c{idx:02d}_{k}.png")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", mp4, "-frames:v", "1", "-vf", "scale=300:-1", p], check=True)
            imgs.append(p)
        subprocess.run(["ffmpeg", "-v", "error", "-y", *sum([["-i", p] for p in imgs], []), "-filter_complex",
                        "hstack=inputs=4", os.path.join(folhas, f"c{idx:02d}.jpg")], check=True)
        for p in imgs:
            os.remove(p)
        ok = not falta and not (not c.get("fala") and len(extra) > 2)
        fim_fala = palavras[-1]["end"] if palavras else None
        print(f"c{idx:02d} {dur:.1f}s | fala termina {fim_fala} | {texto!r} | faltam {falta} | {'ok' if ok else 'REFAZER?'}")


if __name__ == "__main__":
    main()
