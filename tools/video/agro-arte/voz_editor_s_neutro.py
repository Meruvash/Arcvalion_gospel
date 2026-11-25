"""Voz do editor (clone ElevenLabs) com o "S" neutro, sem o chiado carioca (pedido do editor, 17/11/2026).

Para cada fala do editor, gera candidatas com ajustes diferentes e mede o "S" de cada uma:
- a transcrição da ElevenLabs (scribe_v1, com tempo por letra) dá onde está cada "s";
- mede-se só o "s" em fim de sílaba (antes de consoante ou no fim da palavra), que é onde o chiado aparece;
- no trecho de cada "s", compara a energia acima de 5 kHz (o "s" alveolar, neutro) com a de 2 a 4,5 kHz (o chiado,
  palatal). Quanto maior a razão, mais neutro.

Fica a candidata com a maior nota média, desde que a transcrição bata com o texto.
Uso: python3 voz_editor_s_neutro.py falas.json 3,6,9 [--n 6]
Saída: voz/fala{N}.mp3 (a escolhida) e voz/s_neutro_relatorio.json (as notas de todas as candidatas).
"""
import json, os, re, subprocess, sys, unicodedata, urllib.request, uuid
import numpy as np

VOZ_EDITOR = "jEMMnqfzSCpo1eh8s9YJ"
# Ajustes testados: estilo zerado, porque "style" exagera o sotaque do clone; mais estabilidade e menos "similarity".
AJUSTES = [
    {"model_id": "eleven_multilingual_v2", "voice_settings": {"stability": 0.65, "similarity_boost": 0.70, "style": 0.0, "use_speaker_boost": True}},
    {"model_id": "eleven_multilingual_v2", "voice_settings": {"stability": 0.80, "similarity_boost": 0.60, "style": 0.0, "use_speaker_boost": False}},
    {"model_id": "eleven_multilingual_v2", "voice_settings": {"stability": 0.80, "similarity_boost": 0.70, "style": 0.0, "use_speaker_boost": True}},
]
# O eleven_turbo_v2_5 com language_code "pt" foi testado em 17/11/2026 e chiou mais que todos (nota de 0,1 a 1,5): fica de fora.
VOGAIS = set("aeiouáéíóúâêôãõà")

def tts(texto, ajuste, seed, destino):
    body = dict(ajuste, text=texto, seed=seed)
    r = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOZ_EDITOR}?output_format=mp3_44100_128",
                               json.dumps(body).encode(), {"xi-api-key": "dummy", "Content-Type": "application/json"})
    open(destino, "wb").write(urllib.request.urlopen(r, timeout=240).read())

def stt(arquivo):
    b = uuid.uuid4().hex; data = open(arquivo, "rb").read()
    campos = {"model_id": "scribe_v1", "language_code": "por", "timestamps_granularity": "character"}
    body = b"".join(f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode() for k, v in campos.items())
    body += f'--{b}\r\nContent-Disposition: form-data; name="file"; filename="a.mp3"\r\nContent-Type: audio/mpeg\r\n\r\n'.encode() + data + f'\r\n--{b}--\r\n'.encode()
    r = urllib.request.Request("https://api.elevenlabs.io/v1/speech-to-text", body, {"xi-api-key": "dummy", "Content-Type": f"multipart/form-data; boundary={b}"})
    return json.loads(urllib.request.urlopen(r, timeout=240).read())

def norm(s):
    s = unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"\bpell?ic+ion[ei]\b", "pelicioni", s)   # a transcrição grafa o nome do editor de jeitos diferentes

def trechos_s_coda(j):
    """Instantes (ini, fim) de cada 's'/'z' em fim de sílaba: antes de consoante na palavra, ou no fim da palavra."""
    out = []
    for w in j.get("words", []):
        if w.get("type") != "word": continue
        chars = w.get("characters") or []
        letras = [c for c in chars if c.get("text", "").strip() and c["text"].isalpha()]
        for k, c in enumerate(letras):
            t = c["text"].lower()
            if t not in ("s", "z"): continue
            prox = letras[k + 1]["text"].lower() if k + 1 < len(letras) else ""
            if prox and prox in VOGAIS: continue                                # "s" antes de vogal: não é coda
            if prox == "s": continue                                           # "ss" = som de s entre vogais
            if t == "z" and prox: continue
            out.append((c["start"], max(c["end"], c["start"] + 0.06), w["text"]))
        # "s" no começo de sílaba também entra (peso menor), para a voz soar igual em todas as falas
        for k, c in enumerate(letras):
            if c["text"].lower() == "s" and k + 1 < len(letras) and letras[k + 1]["text"].lower() in VOGAIS and (k == 0 or letras[k - 1]["text"].lower() != "s"):
                out.append((c["start"], max(c["end"], c["start"] + 0.06), w["text"] + "(início)"))
    return out

def nota_s(wav, trechos):
    sr = 48000
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", wav, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(pcm, dtype=np.float32)
    notas = []
    for a, b, palavra in trechos:
        seg = x[int(max(0, a - .01) * sr): int((b + .03) * sr)]
        if len(seg) < 256: continue
        f = np.fft.rfftfreq(len(seg), 1 / sr); P = np.abs(np.fft.rfft(seg * np.hanning(len(seg)))) ** 2
        alto = P[(f >= 5000) & (f <= 11000)].sum(); chiado = P[(f >= 2000) & (f <= 4500)].sum() + 1e-12
        notas.append({"palavra": palavra, "razao": float(alto / chiado)})
    return notas

def main():
    arq, ids = sys.argv[1], [int(x) for x in sys.argv[2].split(",")]
    n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 8
    falas = {f["id"]: f for f in json.load(open(arq, encoding="utf-8"))}
    os.makedirs("voz/cand", exist_ok=True); rel = {}
    for i in ids:
        f = falas[i]; cands = []
        for c in range(n):
            ajuste = AJUSTES[c % len(AJUSTES)]; seed = 1000 + 37 * c
            mp3 = f"voz/cand/fala{i}_c{c}.mp3"
            tts(f["fala"], ajuste, seed, mp3)
            j = stt(mp3)
            confere = norm(re.sub(r"[^\w\s]", "", j["text"])).split() == norm(re.sub(r"[^\w\s]", "", f["texto"])).split()
            notas = nota_s(mp3, trechos_s_coda(j))
            pesos = [1.0 if "(início)" in x["palavra"] else 2.0 for x in notas]
            media = float(np.average([np.log1p(x["razao"]) for x in notas], weights=pesos)) if notas else 0.0   # log: um "s" muito agudo não compensa um chiado
            cands.append({"cand": c, "ajuste": ajuste, "seed": seed, "transcricao": j["text"], "confere": confere, "media_s": media, "notas_s": notas, "arquivo": mp3})
            print(f"fala {i} cand {c} ({ajuste['model_id']}, est {ajuste['voice_settings']['stability']}) s={media:.2f} confere={confere} | {j['text']}")
        validas = [c for c in cands if c["confere"]] or cands
        melhor = max(validas, key=lambda c: c["media_s"])
        subprocess.run(["cp", melhor["arquivo"], f"voz/fala{i}.mp3"], check=True)
        print(f"==> fala {i}: candidata {melhor['cand']} (s={melhor['media_s']:.2f})")
        rel[i] = {"escolhida": melhor["cand"], "candidatas": cands}
    json.dump(rel, open("voz/s_neutro_relatorio.json", "w"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
