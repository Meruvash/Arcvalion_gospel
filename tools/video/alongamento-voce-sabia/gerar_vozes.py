"""Gera as falas aprovadas na ElevenLabs (eleven_v3, como nos vídeos do Colt Express) e confere por transcrição.

Uso: python3 gerar_vozes.py <ids separados por vírgula> [voz_da_segunda] [pasta]
narrador = Marcio - Viral Hook Narrator (a voz dos vídeos do Colt Express);
segunda voz = escolhida pelo editor; editor = clone da voz do Dr. Pelicioni (VOZ_EDITOR, quando a amostra chegar).
"fala" pode ter marcações de emoção do v3 ([surprised], [curious]); "texto" é o que vai na legenda.
"""
import json, os, sys, urllib.request
VOZES = {"narrador": "plASsyS7JE6GCAvx9uIc", "segunda": sys.argv[2] if len(sys.argv) > 2 else None,
         "editor": "jEMMnqfzSCpo1eh8s9YJ"}  # clone da voz do Dr. Pelicioni (amostra dele, 10/11/2026); usar eleven_multilingual_v2: o v3 erra o nome
PASTA = sys.argv[3] if len(sys.argv) > 3 else "voz"
os.makedirs(PASTA, exist_ok=True)
ids = {int(x) for x in sys.argv[1].split(",")}
for f in json.load(open("falas.json", encoding="utf-8")):
    if f["id"] not in ids: continue
    voz = VOZES[f["quem"]]
    if not voz:
        print(f"fala {f['id']}: sem voz ({f['quem']}), pulada"); continue
    body = json.dumps({"text": f.get("fala", f["texto"]), "model_id": "eleven_v3", "language_code": "pt",
                       "seed": 100 * f["id"]}).encode()
    r = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{voz}?output_format=mp3_44100_128", body,
                               {"xi-api-key": "dummy", "Content-Type": "application/json"})
    open(f"{PASTA}/fala{f['id']}.mp3", "wb").write(urllib.request.urlopen(r, timeout=180).read())
    print(f"fala {f['id']} ok")
