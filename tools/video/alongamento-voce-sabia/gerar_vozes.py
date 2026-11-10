"""Gera cada fala aprovada do roteiro na ElevenLabs, com tempos por palavra. Uso: python3 gerar_vozes.py [ids...]

narrador = Adriano-Narrador; segunda voz = Lucas (masculina, mais jovem, para a reação);
editor = clone da voz do Dr. Pelicioni (definir VOZ_EDITOR quando a amostra chegar; até lá a fala 9 não é gerada).
"""
import base64, json, os, sys, urllib.request
VOZES = {"narrador": ("hwnuNyWkl9DjdTFykrN6", 1.15, 0.45, 0.30),
         "segunda": ("7lu3ze7orhWaNeSPowWx", 1.0, 0.35, 0.55),
         "editor": (os.environ.get("VOZ_EDITOR"), 1.0, 0.5, 0.2)}
falas = json.load(open("falas.json", encoding="utf-8"))
ids = {int(x) for x in sys.argv[1:]}
for f in falas:
    if ids and f["id"] not in ids: continue
    voz, vel, estab, estilo = VOZES[f["quem"]]
    if not voz:
        print(f"fala {f['id']}: sem voz definida ({f['quem']}), pulada"); continue
    body = json.dumps({"text": f["texto"], "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": estab, "similarity_boost": 0.8, "style": estilo, "speed": vel}}).encode()
    r = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{voz}/with-timestamps", body,
                               {"xi-api-key": "dummy", "Content-Type": "application/json"})
    d = json.load(urllib.request.urlopen(r))
    open(f"voz/fala{f['id']}.mp3", "wb").write(base64.b64decode(d["audio_base64"]))
    json.dump(d["alignment"], open(f"voz/fala{f['id']}.json", "w"))
    print(f"fala {f['id']} ok: {d['alignment']['character_end_times_seconds'][-1]:.2f} s")
