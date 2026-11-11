"""Vozes do vídeo "Cinco por dia": narrador Marcio e clone do editor, ambos eleven_multilingual_v2 (sotaque brasileiro estável).
Uso: python3 gerar_vozes.py 1,2,3 [semente_base]"""
import json, sys, urllib.request
VOZES = {"narrador": "plASsyS7JE6GCAvx9uIc", "editor": "jEMMnqfzSCpo1eh8s9YJ"}
ids = {int(x) for x in sys.argv[1].split(",")}; base = int(sys.argv[2]) if len(sys.argv) > 2 else 100
for f in json.load(open("falas.json", encoding="utf-8")):
    if f["id"] not in ids: continue
    body = json.dumps({"text": f["fala"], "model_id": "eleven_multilingual_v2", "seed": base * f["id"],
                       "voice_settings": {"stability": 0.45, "similarity_boost": 0.85, "style": 0.25}}).encode()
    r = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOZES[f['quem']]}?output_format=mp3_44100_128", body,
                               {"xi-api-key": "dummy", "Content-Type": "application/json"})
    open(f"voz/fala{f['id']}.mp3", "wb").write(urllib.request.urlopen(r, timeout=240).read()); print("fala", f["id"], "ok")
