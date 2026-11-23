#!/usr/bin/env python3
"""Portão de sincronia da novela: nenhuma cena entra na montagem sem passar na medida de boca × voz.

Uso (com o Python que tem mediapipe; ver docs/video/novela/SINCRONIA.md):
  python garantir_sincronia.py pasta_producao --modelo face_landmarker.task [--lipsync lipsync/saida]

Para cada clipe da montagem (montagem.json):
1. Pega a imagem com a boca redesenhada (lipsync/saida/cNN_ls.mp4, LatentSync) e põe por baixo o áudio exato
   (lipsync/entrada/cNN.wav: a fala do roteiro na voz fixa; a do Dr. Pelicioni na voz clonada do editor).
   Grava planos/cNN_sync.mp4.
2. Mede com sincronia.py (boca × palavras da transcrição do áudio exato).
3. Aprovada: a montagem usa cNN_sync.mp4. Reprovada: a cena fica fora e o script sai com erro, listando o que refazer.
Grava sincronia_final.json e montagem_sync.json (com "exigir_sincronia": true, que o montar_cena.py confere).
"""
import argparse, json, os, subprocess, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
from sincronia import medir


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                capture_output=True, text=True).stdout)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pasta"); ap.add_argument("--modelo", required=True)
    ap.add_argument("--lipsync", default="lipsync/saida"); ap.add_argument("--audio", default="lipsync/entrada")
    a = ap.parse_args(); base = os.path.abspath(a.pasta)
    m = json.load(open(os.path.join(base, "montagem.json"), encoding="utf-8"))
    res, falhas = [], []
    for c in m["clipes"]:
        k = os.path.basename(c["arq"])[:3]
        ls = os.path.join(base, a.lipsync, f"{k}_ls.mp4"); wav = os.path.join(base, a.audio, f"{k}.wav")
        if not os.path.exists(ls):
            falhas.append((k, "sem boca redesenhada")); continue
        out = os.path.join(base, "planos", f"{k}_sync.mp4"); D = dur(ls)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", ls, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                        "-af", f"apad=whole_dur={D},atrim=0:{D}", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", out],
                       check=True)
        r = medir(out, a.modelo, wav)
        # só conta o trecho que vai para a montagem
        r["clipe"] = k; r["janela_montagem"] = [c["ini"], c["fim"]]
        res.append(r)
        ok = r.get("aprovado") if c.get("fala") else (r.get("boca_sem_voz_s", 9) <= 0.5)
        if "erro" in r:
            ok = not c.get("fala")  # sem rosto e sem fala: nada a sincronizar
        print(f"{k}: atraso {r.get('atraso_ms')} ms · boca sem voz {r.get('boca_sem_voz_s')} s · "
              f"voz sem boca {r.get('voz_sem_boca_s')} s · {'OK' if ok else 'FALHA'}", flush=True)
        if ok:
            c["arq"] = f"planos/{k}_sync.mp4"; c["sincronia_ok"] = True
        else:
            falhas.append((k, "medida reprovada"))
    json.dump(res, open(os.path.join(base, "sincronia_final.json"), "w"), ensure_ascii=False, indent=1)
    m["exigir_sincronia"] = True
    json.dump(m, open(os.path.join(base, "montagem_sync.json"), "w"), ensure_ascii=False, indent=1)
    if falhas:
        print("REFAZER:", ", ".join(f"{k} ({p})" for k, p in falhas)); sys.exit(1)
    print("todas as cenas passaram")


if __name__ == "__main__":
    main()
