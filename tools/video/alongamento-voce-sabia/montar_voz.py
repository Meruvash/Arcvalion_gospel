"""Monta a linha do tempo da narração (falas + respiros) e grava voz/previa.mp3 e linha_do_tempo.json.

A fala 9 (Dr. Pelicioni, voz clonada) entra quando existir voz/fala9.mp3; até lá fica uma janela de silêncio reservada.
"""
import json, os, subprocess
RESPIRO = {1: .15, 2: .25, 3: .2, 4: .3, 5: .35, 6: .25, 7: .25, 8: .5}
JANELA_9, CAUDA = 5.5, 0.8
def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                capture_output=True, text=True).stdout)
t, linha, ent, filt = 0.0, [], [], []
for i in range(1, 10):
    p = f"voz_v3/proc/fala{i}.wav"
    if os.path.exists(p):
        d = dur(p)
        ent += ["-i", p]
        k = len(ent) // 2 - 1
        filt.append(f"[{k}]adelay={int(t*1000)}|{int(t*1000)}[a{k}]")
        linha.append({"fala": i, "inicio": round(t, 2), "fim": round(t + d, 2)})
        t += d + RESPIRO.get(i, 0)
    else:
        linha.append({"fala": i, "inicio": round(t, 2), "fim": round(t + JANELA_9, 2), "pendente": True})
        t += JANELA_9
total = round(t + CAUDA, 2)
json.dump({"total": total, "falas": linha}, open("linha_do_tempo.json", "w"), indent=1)
n = len(filt)
fc = ";".join(filt) + ";" + "".join(f"[a{k}]" for k in range(n)) + f"amix=inputs={n}:normalize=0,apad,atrim=0:{total},loudnorm=I=-15:TP=-1.5:LRA=11[out]"
subprocess.run(["ffmpeg", "-v", "error", "-y", *ent, "-filter_complex", fc, "-map", "[out]", "-ar", "48000", "voz_v3/narracao_completa.wav"], check=True)
print("total", total); [print(x) for x in linha]
