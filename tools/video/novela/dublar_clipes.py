#!/usr/bin/env python3
"""Regrava a fala de cada clipe no ElevenLabs e encaixa a fala na janela em que a boca mexe (medida por sincronia.py).

Uso: python3 tools/video/novela/dublar_clipes.py pasta_producao sincronia.json [--so c02,c12]

Para cada clipe com fala (clipes/cNN_*.json):
1. Gera a fala com a voz fixa do personagem (ELENCO_FIXO.md). O Dr. Pelicioni sai sempre de
   tools/video/agro-arte/voz_editor_s_neutro.py (voz clonada, "S" neutro).
2. Tira o silêncio das pontas e ajusta a velocidade (atempo de 0,80 a 1,25) para a fala caber exatamente entre o
   começo da primeira abertura de boca e o fim da última, dentro do plano do falante.
3. Troca o áudio do clipe (o vídeo fica igual) e grava planos/cNN_dub.mp4, mais voz/cNN.wav com a fala encaixada
   (é esse áudio que vai para o Sync Lipsync, quando o editor aprovar).
"""
import glob, json, os, subprocess, sys, urllib.request

VOZ = {"Valdir": "rnJZLKxtlBZt77uIED10", "Cleide": "HReOQZPV9tH5iTEnSbGo", "Tavares": "5caTbRMcqFgu2Gjuby8U",
       "Rosa": "CS2gH5fPqUCmkVNpHsy4", "Bruna": "GDzHdQOi6jjf8zaXhCYD", "Antônio": "zoe2cQFqDDW4DteHDEWI",
       "Zuleide": "fs3nd19KF2GO2hLTzkBm"}
AQUI = os.path.dirname(os.path.abspath(__file__))
S_NEUTRO = os.path.join(AQUI, "..", "agro-arte", "voz_editor_s_neutro.py")


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                capture_output=True, text=True).stdout)


def tts(voice, texto, destino, emocao=""):
    estilo = 0.35 if any(k in emocao for k in ("mock", "arrog", "smug", "laugh")) else 0.2
    body = json.dumps({"text": texto, "model_id": "eleven_multilingual_v2",
                       "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "style": estilo}}).encode()
    r = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128", body,
                               {"xi-api-key": "dummy", "Content-Type": "application/json"})
    open(destino, "wb").write(urllib.request.urlopen(r, timeout=240).read())


def main():
    base = os.path.abspath(sys.argv[1]); sinc = {os.path.basename(x["video"]): x for x in json.load(open(sys.argv[2]))}
    so = sys.argv[sys.argv.index("--so") + 1].split(",") if "--so" in sys.argv else None
    os.makedirs(os.path.join(base, "voz"), exist_ok=True)
    dr = []
    clipes = []
    for cj in sorted(glob.glob(os.path.join(base, "clipes", "c*.json"))):
        c = json.load(open(cj, encoding="utf-8")); k = os.path.basename(cj)[:3]
        if not c.get("fala") or (so and k not in so):
            continue
        clipes.append((k, c))
        if c["voz"] == "Dr. Pelicioni":
            dr.append({"id": int(k[1:]), "fala": c["fala"]["texto"], "texto": c["fala"]["texto"]})
    # voz do editor: sempre pelo script do "S" neutro
    if dr:
        pasta = os.path.join(base, "voz", "editor"); os.makedirs(pasta, exist_ok=True)
        json.dump(dr, open(os.path.join(pasta, "falas.json"), "w"), ensure_ascii=False)
        subprocess.run([sys.executable, S_NEUTRO, "falas.json", ",".join(str(x["id"]) for x in dr), "--n", "3"], cwd=pasta,
                       check=True, stdout=subprocess.DEVNULL)
    for k, c in clipes:
        bruto = os.path.join(base, "voz", f"{k}_bruto.mp3")
        if c["voz"] == "Dr. Pelicioni":
            bruto = os.path.join(base, "voz", "editor", "voz", f"fala{int(k[1:])}.mp3")
        else:
            tts(VOZ[c["voz"]], c["fala"]["texto"], bruto, c["fala"].get("emocao", ""))
        limpo = os.path.join(base, "voz", f"{k}_limpo.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", bruto, "-af",
                        "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse",
                        "-ar", "44100", "-ac", "1", limpo], check=True)
        # janela da boca dentro do(s) plano(s) do falante
        planos = [p for p in c["planos"] if p.get("fala")] or c["planos"]
        p0, p1 = min(p["de"] for p in planos), max(p["ate"] for p in planos)
        src = os.path.join(base, "planos", f"{k}.mp4")
        s = sinc.get(f"{k}.mp4", {})
        bocas = [b for b in s.get("boca_falando", []) if b[1] > p0 and b[0] < p1]
        if bocas:
            a, z = max(p0, bocas[0][0]), min(p1, bocas[-1][1])
        else:
            a, z = p0 + 0.3, p1 - 0.8
        a = max(a, 0.05)
        alvo = max(0.6, z - a); real = dur(limpo)
        r = max(0.80, min(1.25, real / alvo))
        enc = os.path.join(base, "voz", f"{k}.wav")
        D = dur(src)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", limpo, "-af",
                        f"atempo={r:.4f},adelay={int(a * 1000)},apad=whole_dur={D},atrim=0:{D},loudnorm=I=-19:TP=-2",
                        "-ar", "44100", "-ac", "2", enc], check=True)
        out = os.path.join(base, "planos", f"{k}_dub.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-i", enc, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                        "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
        print(f"{k} {c['voz']}: janela da boca {a:.2f}–{z:.2f} s, fala {real:.2f} s, atempo {r:.2f}"
              + ("  ⚠ não coube" if abs(real / r - alvo) > 0.25 else ""))


if __name__ == "__main__":
    main()
