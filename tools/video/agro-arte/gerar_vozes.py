"""Gera as falas na ElevenLabs (eleven_v3) com tempos por caractere. Uso: python3 gerar_vozes.py 1,2,3,4"""
import json, sys, base64, urllib.request
VOZES = {"narrador": "plASsyS7JE6GCAvx9uIc", "segunda": "36rVQA1AOIPwpA3Hg1tC", "editor": "jEMMnqfzSCpo1eh8s9YJ"}
ids = {int(x) for x in sys.argv[1].split(",")}
for f in json.load(open("falas.json", encoding="utf-8")):
    if f["id"] not in ids: continue
    body = json.dumps({"text": f["fala"], "model_id": "eleven_multilingual_v2" if f["quem"] == "editor" else "eleven_v3", "language_code": "pt", "seed": 100 * f["id"]}).encode()
    r = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOZES[f['quem']]}/with-timestamps?output_format=mp3_44100_128",
                               body, {"xi-api-key": "dummy", "Content-Type": "application/json"})
    d = json.loads(urllib.request.urlopen(r, timeout=240).read())
    open(f"voz/fala{f['id']}.mp3", "wb").write(base64.b64decode(d["audio_base64"]))
    json.dump(d.get("alignment"), open(f"voz/fala{f['id']}.align.json", "w"))
    print("fala", f["id"], "ok", len(d["audio_base64"]))
