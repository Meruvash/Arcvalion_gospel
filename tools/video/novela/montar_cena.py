#!/usr/bin/env python3
"""Monta um episódio da novela em cena atuada (clipes do Seedance) em Reels 1080×1920 com trilha, legenda e cartões.

Uso: python3 tools/video/novela/montar_cena.py montagem.json saida.mp4

montagem.json (caminhos relativos à pasta do JSON):
{
 "trilha": "trilha/trilha_v1.mp3", "trilha_db": -14,
 "clipes": [
  {"arq": "planos/c01.mp4", "ini": 0.0, "fim": 6.0,
   "fala": "texto do roteiro (opcional: legenda alinhada às palavras da transcrição)",
   "lei": {"png": "cartao_1794.png", "de": 1.0}}           # opcional, tempo relativo ao clipe cortado
 ],
 "parte2": true
}
Regras (docs/video/novela/REGRAS_ROTEIRO.md §8 e skill novela):
- cada fala é nivelada perto de -19 LUFS;
- a trilha abaixa sozinha quando há fala (sidechain);
- legenda amarela, até 6 palavras por vez, no tempo das palavras ditas (transcrição scribe_v1 com tempo por palavra);
- faixa fixa "DRAMATIZAÇÃO · PERSONAGENS FICTÍCIOS".
"""
import json, os, re, subprocess, sys, tempfile, urllib.request, uuid
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
FONTE = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
FONTE2 = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"


def sh(*a):
    subprocess.run(a, check=True)


def png_texto(txt, destino, tam=58, cor="#FFD400", larg=980):
    f = ImageFont.truetype(FONTE, tam)
    pal, linhas, at = txt.split(), [], ""
    for p in pal:
        t = (at + " " + p).strip()
        if f.getlength(t) > larg and at:
            linhas.append(at); at = p
        else:
            at = t
    linhas.append(at)
    alt = int(tam * 1.25) * len(linhas) + 24
    im = Image.new("RGBA", (W, alt), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, l in enumerate(linhas):
        d.text(((W - f.getlength(l)) / 2, 12 + int(tam * 1.25) * i), l, font=f, fill=cor, stroke_width=7, stroke_fill="black")
    im.save(destino)
    return alt


def faixa_drama(destino):
    im = Image.new("RGBA", (W, 56), (11, 26, 42, 200)); d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONTE2, 26); t = "DRAMATIZAÇÃO · PERSONAGENS FICTÍCIOS"
    d.text(((W - f.getlength(t)) / 2, 13), t, font=f, fill="white")
    im.save(destino)


def stt_palavras(arquivo):
    b = uuid.uuid4().hex; data = open(arquivo, "rb").read()
    campos = {"model_id": "scribe_v1", "language_code": "por", "timestamps_granularity": "word"}
    body = b"".join(f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode() for k, v in campos.items())
    body += f'--{b}\r\nContent-Disposition: form-data; name="file"; filename="a.wav"\r\nContent-Type: audio/wav\r\n\r\n'.encode() + data + f'\r\n--{b}--\r\n'.encode()
    r = urllib.request.Request("https://api.elevenlabs.io/v1/speech-to-text", body,
                               {"xi-api-key": "dummy", "Content-Type": f"multipart/form-data; boundary={b}"})
    j = json.loads(urllib.request.urlopen(r, timeout=240).read())
    return [w for w in j.get("words", []) if w.get("type") == "word"], j.get("text", "")


def legendas(texto, palavras, max_pal=6):
    """Divide o texto do roteiro em blocos de até max_pal palavras e dá a cada bloco o tempo das palavras ditas."""
    ditas = palavras
    toks = texto.split()
    if not ditas:
        return []
    blocos, i = [], 0
    while i < len(toks):
        # quebra em pontuação forte quando possível
        j = min(i + max_pal, len(toks))
        for k in range(i + 2, j):
            if re.search(r"[.?!:]$", toks[k - 1]):
                j = k; break
        blocos.append((i, j)); i = j
    n = len(toks); m = len(ditas); out = []
    for a, z in blocos:
        ia = min(m - 1, round(a * m / n)); iz = min(m - 1, max(ia, round(z * m / n) - 1))
        out.append({"txt": " ".join(toks[a:z]), "de": ditas[ia]["start"], "ate": ditas[iz]["end"] + 0.25})
    for k in range(len(out) - 1):
        # termina um pouco antes da próxima: between() inclui as duas pontas e mostraria duas legendas no mesmo quadro
        out[k]["ate"] = min(out[k]["ate"], out[k + 1]["de"] - 0.05)
    return out


def segmento(c, base, tmp, i, faixa):
    src = os.path.join(base, c["arq"]); d = c["fim"] - c["ini"]
    wav = os.path.join(tmp, f"a{i}.wav")
    sh("ffmpeg", "-v", "error", "-y", "-ss", str(c["ini"]), "-t", str(d), "-i", src, "-vn", "-ac", "1", "-ar", "44100", wav)
    legs = []
    if c.get("fala"):
        palavras, texto = stt_palavras(wav)
        c["_transcricao"] = texto
        legs = legendas(c["fala"], palavras)
    ins = ["-ss", str(c["ini"]), "-t", str(d), "-i", src, "-loop", "1", "-i", faixa]
    filt = [f"[0:v]fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1[v0]",
            "[v0][1]overlay=0:0[v1]"]
    at, n = "v1", 2
    if c.get("lei"):
        ins += ["-loop", "1", "-i", os.path.join(base, c["lei"]["png"])]
        de = c["lei"]["de"]
        filt.append(f"[{at}][{n}]overlay=x=0:y='1330+max(0\\,({de}+0.3-t))*1600':enable='gte(t,{de})'[v{n}]"); at = f"v{n}"; n += 1
    for k, lg in enumerate(legs):
        p = os.path.join(tmp, f"l{i}_{k}.png"); png_texto(lg["txt"], p)
        ins += ["-loop", "1", "-i", p]
        y = 1120 if c.get("lei") else 1560
        filt.append(f"[{at}][{n}]overlay=x=0:y={y}:enable='between(t,{lg['de']:.2f},{lg['ate']:.2f})'[v{n}]"); at = f"v{n}"; n += 1
    filt.append(f"[0:a]aresample=44100,loudnorm=I=-19:TP=-2:LRA=9,aresample=44100,aformat=channel_layouts=stereo,apad=whole_dur={d},atrim=0:{d},asetpts=N/SR/TB[a]")
    out = os.path.join(tmp, f"s{i:02d}.mp4")
    sh("ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(filt), "-map", f"[{at}]", "-map", "[a]",
       "-t", str(d), "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-ar", "44100", out)
    return out, d


def main():
    mj = os.path.abspath(sys.argv[1]); base = os.path.dirname(mj); m = json.load(open(mj, encoding="utf-8"))
    saida = os.path.abspath(sys.argv[2])
    if m.get("exigir_sincronia"):
        sem = [c["arq"] for c in m["clipes"] if not c.get("sincronia_ok")]
        if sem:
            sys.exit("cenas sem sincronia aprovada (garantir_sincronia.py): " + ", ".join(sem))
    with tempfile.TemporaryDirectory() as tmp:
        faixa = os.path.join(tmp, "faixa.png"); faixa_drama(faixa)
        segs = [segmento(c, base, tmp, i, faixa) for i, c in enumerate(m["clipes"])]
        tot = sum(d for _, d in segs)
        # Emenda com recodificação (filtro concat): áudio e vídeo de cada clipe têm a mesma duração, sem deriva acumulada
        cena = os.path.join(tmp, "cena.mp4")
        ins_c = sum([["-i", p] for p, _ in segs], [])
        fc = "".join(f"[{k}:v][{k}:a]" for k in range(len(segs))) + f"concat=n={len(segs)}:v=1:a=1[v][a]"
        sh("ffmpeg", "-v", "error", "-y", *ins_c, "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-c:v", "libx264",
           "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", cena.replace(".mp4", ".mov"))
        cena = cena.replace(".mp4", ".mov")
        ins = ["-i", cena, "-i", os.path.join(base, m["trilha"])]
        fl = [f"[1:a]atrim=0:{tot},volume={m.get('trilha_db', -14)}dB,afade=t=out:st={tot - 1.5}:d=1.5[mus]",
              "[0:a]asplit=2[fala][sc]",
              "[mus][sc]sidechaincompress=threshold=0.03:ratio=6:attack=30:release=500[duck]",
              "[fala][duck]amix=inputs=2:normalize=0,alimiter=limit=0.95[a]"]
        vmap = "0:v"
        if m.get("parte2"):
            # cartão final: a imagem escurece e "PARTE 2" aparece no centro, sem tapar rosto enquanto alguém fala
            p2t = os.path.join(tmp, "p2t.png"); alt = png_texto("PARTE 2", p2t, tam=150)
            fundo = Image.new("RGBA", (W, H), (0, 0, 0, 170)); fundo.alpha_composite(Image.open(p2t), (0, (H - alt) // 2))
            p2 = os.path.join(tmp, "p2.png"); fundo.save(p2)
            ins += ["-loop", "1", "-i", p2]
            fl.append(f"[0:v][2]overlay=x=0:y=0:enable='gte(t,{tot - 1.6})'[vf]"); vmap = "[vf]"
        sh("ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fl), "-map", vmap, "-map", "[a]",
           "-t", str(tot), "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", saida)
    rel = {c["arq"]: c.get("_transcricao") for c in m["clipes"] if c.get("fala")}
    json.dump(rel, open(saida.replace(".mp4", "_transcricoes.json"), "w"), ensure_ascii=False, indent=1)
    print("ok", saida, f"{tot:.1f} s")


if __name__ == "__main__":
    main()
