"""Vídeo completo: narração das 11 falas, palavras com tempo absoluto, recortes dos prints (BCB e Congresso) -> hf/assets."""
import json, subprocess
from PIL import Image
LEAD = 0.10
GAP = {1: .15, 2: .15, 3: .15, 4: .2, 5: .15, 6: .25, 7: .2, 8: .2, 9: .2, 10: .45}
def dur(p): return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",p],capture_output=True,text=True).stdout)
t, falas, ent, filt, words = LEAD, [], [], [], []
for i in range(1, 12):
    p = f"voz/proc/fala{i}.wav"; d = dur(p)
    ent += ["-i", p]; filt.append(f"[{i-1}]adelay={int(t*1000)}|{int(t*1000)}[a{i-1}]")
    falas.append({"fala": i, "inicio": round(t, 3), "fim": round(t + d, 3)})
    for w in json.load(open(f"voz/stt/fala{i}.json"))["words"]:
        if w["type"] == "word": words.append({"fala": i, "w": w["text"], "s": round(t + w["start"], 3), "e": round(t + w["end"], 3)})
    t += d + GAP.get(i, 0)
FIM = round(t, 3)
TOTAL = round(FIM + 1.0, 2)
fc = ";".join(filt) + ";" + "".join(f"[a{k}]" for k in range(11)) + f"amix=inputs=11:normalize=0,apad,atrim=0:{TOTAL}[out]"
subprocess.run(["ffmpeg","-v","error","-y",*ent,"-filter_complex",fc,"-map","[out]","-ar","48000","hf/assets/audio/narracao.wav"],check=True)
json.dump({"total": TOTAL, "falas": falas, "palavras": words}, open("hf/assets/data/tempos.json","w"), ensure_ascii=False, indent=1)
# print do BCB (coluna do documento)
tr = json.load(open("prints/trechos.json")); S = tr["escala"]
X0, Y0, X1, Y1 = 0, 250, 745, 2900
Image.open("prints/res5330-full.png").crop((X0*S, Y0*S, X1*S, Y1*S)).save("hf/assets/docs/res5330.png", optimize=True)
rects = {k: [{"x": (r["x"]-X0)*S, "y": (r["y"]-Y0)*S, "w": r["w"]*S, "h": r["h"]*S} for r in v] for k, v in tr["rects"].items()}
json.dump({"largura": (X1-X0)*S, "altura": (Y1-Y0)*S, "rects": rects, "url": tr["url"], "capturado": tr["capturado"]}, open("hf/assets/docs/res5330.json","w"), ensure_ascii=False, indent=1)
# print do Congresso (andamento), sem a margem direita onde fica o botão de acessibilidade do site
cn = json.load(open("prints/cn-andamento.json")); S = cn["escala"]; CX1 = 940
Image.open("prints/cn-andamento.png").convert("RGB").crop((0, 0, CX1*S, 1100*S)).save("hf/assets/docs/cn-andamento.png", optimize=True)
cr = {k: [{"x": r["x"]*S, "y": r["y"]*S, "w": r["w"]*S, "h": r["h"]*S} for r in v] for k, v in cn["rects"].items()}
json.dump({"largura": CX1*S, "altura": 1100*S, "rects": cr, "url": cn["url"], "capturado": cn["capturado"]}, open("hf/assets/docs/cn-andamento.json","w"), ensure_ascii=False, indent=1)
print("total", TOTAL); [print(f) for f in falas]; print(len(words), "palavras")
