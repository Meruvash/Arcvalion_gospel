#!/usr/bin/env python3
"""Monta um episódio da novela (Reels 1080×1920, 30 qps) a partir de um plano de montagem em JSON.

Uso: python3 tools/video/novela/montar_episodio.py montagem.json saida.mp4

montagem.json (caminhos relativos à pasta do JSON):
{
 "duracao": 75,
 "segmentos": [
  {"t": 0, "fim": 9, "fundo": "planos/f1.mp4", "ini": 0, "vel": 0.89, "borrar": false,
   "cartoes": [{"png": "telas/t00.png", "de": 0.4, "ate": 3, "entra": true}, ...],
   "lei": {"png": "telas/t46.png", "de": 1.0},          # recorta o cartão de lei da tela de chamada
   "foto": "../personagem/foto_oficial.jpg",            # fundo de foto parada com zoom lento (no lugar de "fundo")
   "legendas": [{"txt": "...", "de": 3.0, "ate": 6.0}]}
 ],
 "audios": [{"arq": "voz/03_valdir.mp3", "t": 3.0}],
 "blips": [0.4, 3.0, ...]                              # som curto de notificação
}
- Cartão de conversa: a tela inteira reduzida a 80%, no alto, com entrada deslizando de baixo.
- Legenda amarela (padrão da casa), abaixo do cartão.
- Tempos de legenda e cartão são relativos ao início do segmento.
"""
import json, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
FONTE = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"


def legenda_png(txt, destino):
    f = ImageFont.truetype(FONTE, 56)
    pal, linhas, atual = txt.split(), [], ""
    for p in pal:
        teste = (atual + " " + p).strip()
        if f.getlength(teste) > 960 and atual:
            linhas.append(atual); atual = p
        else:
            atual = teste
    linhas.append(atual)
    alt = 70 * len(linhas) + 20
    im = Image.new("RGBA", (W, alt), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, l in enumerate(linhas):
        x = (W - f.getlength(l)) / 2
        d.text((x, 10 + 70 * i), l, font=f, fill="#FFD400", stroke_width=6, stroke_fill="black")
    im.save(destino)
    return alt


def cartao_lei(png, destino):
    Image.open(png).crop((0, 1440, W, 1840)).save(destino)


def segmento(s, base, tmp, i):
    d = s["fim"] - s["t"]
    ins, filt, n = [], [], 0
    if s.get("foto"):
        ins += ["-loop", "1", "-t", f"{d}", "-i", os.path.join(base, s["foto"])]
        filt.append(f"[0]scale={W*2}:-1,crop={W*2}:{H*2},zoompan=z='1+0.0006*on':x='iw/2-(iw/zoom/2)':y='ih/3-(ih/zoom/3)':d=1:s={W}x{H}:fps={FPS},setsar=1[v0]")
    else:
        vel = s.get("vel", 1.0)
        ins += ["-ss", f"{s.get('ini', 0)}", "-i", os.path.join(base, s["fundo"])]
        f0 = f"[0]setpts=PTS/{vel},fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1"
        if s.get("borrar"):
            f0 += ",boxblur=18:2,eq=brightness=-0.18"
        elif s.get("cartoes"):
            f0 += ",eq=brightness=-0.10"
        filt.append(f0 + "[v0]")
    n = 1; atual = "v0"
    for c in s.get("cartoes", []):
        ins += ["-loop", "1", "-i", os.path.join(base, c["png"])]
        cw = int(W * 0.8)
        y = "170" if not c.get("entra", True) else f"170+max(0\\,({c['de']}+0.3-t))*2400"
        filt.append(f"[{n}]scale={cw}:-1,format=rgba[c{n}]")
        filt.append(f"[{atual}][c{n}]overlay=x=(W-w)/2:y='{y}':enable='between(t,{c['de']},{c.get('ate', d)})'[v{n}]")
        atual = f"v{n}"; n += 1
    if s.get("lei"):
        lp = os.path.join(tmp, f"lei{i}.png"); cartao_lei(os.path.join(base, s["lei"]["png"]), lp)
        ins += ["-loop", "1", "-i", lp]
        de = s["lei"]["de"]
        filt.append(f"[{atual}][{n}]overlay=x=0:y='1420+max(0\\,({de}+0.3-t))*1600':enable='gte(t,{de})'[v{n}]")
        atual = f"v{n}"; n += 1
    for k, lg in enumerate(s.get("legendas", [])):
        lp = os.path.join(tmp, f"leg{i}_{k}.png"); alt = legenda_png(lg["txt"], lp)
        ins += ["-loop", "1", "-i", lp]
        y = lg.get("y", 1725 if s.get("cartoes") else 1200)
        filt.append(f"[{atual}][{n}]overlay=x=0:y={y}:enable='between(t,{lg['de']},{lg['ate']})'[v{n}]")
        atual = f"v{n}"; n += 1
    saida = os.path.join(tmp, f"seg{i:02d}.mp4")
    cmd = ["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(filt), "-map", f"[{atual}]", "-t", f"{d}",
           "-r", f"{FPS}", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-an", saida]
    subprocess.run(cmd, check=True)
    return saida


def main():
    mj = os.path.abspath(sys.argv[1]); base = os.path.dirname(mj); m = json.load(open(mj, encoding="utf-8"))
    saida = os.path.abspath(sys.argv[2])
    with tempfile.TemporaryDirectory() as tmp:
        segs = [segmento(s, base, tmp, i) for i, s in enumerate(m["segmentos"])]
        lista = os.path.join(tmp, "l.txt"); open(lista, "w").write("".join(f"file '{p}'\n" for p in segs))
        video = os.path.join(tmp, "v.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", video], check=True)
        ins, fl = ["-i", video], []
        for k, a in enumerate(m["audios"]):
            ins += ["-i", os.path.join(base, a["arq"])]
            fl.append(f"[{k+1}]adelay={int(a['t']*1000)}|{int(a['t']*1000)},volume={a.get('vol', 1.0)}[a{k}]")
        nb = len(m["audios"])
        for j, t in enumerate(m.get("blips", [])):
            ins += ["-f", "lavfi", "-t", "0.09", "-i", "sine=frequency=1320:sample_rate=44100"]
            fl.append(f"[{nb+1+j}]volume=0.18,afade=t=out:st=0.03:d=0.06,adelay={int(t*1000)}|{int(t*1000)}[b{j}]")
        mix = "".join(f"[a{k}]" for k in range(nb)) + "".join(f"[b{j}]" for j in range(len(m.get("blips", []))))
        tot = nb + len(m.get("blips", []))
        fl.append(f"{mix}amix=inputs={tot}:normalize=0,apad,atrim=0:{m['duracao']}[a]")
        subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fl), "-map", "0:v", "-map", "[a]",
                        "-t", f"{m['duracao']}", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", saida], check=True)
    print("ok", saida)


if __name__ == "__main__":
    main()
