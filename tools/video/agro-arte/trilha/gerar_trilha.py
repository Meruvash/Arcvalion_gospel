"""Trilha original estilo moda de viola / sertanejo raiz, instrumental, para vídeos do agro (ElevenLabs Music).
Uso: python3 gerar_trilha.py saida.mp3 [duracao_ms]. Depois confira que não há voz cantada (speech-to-text deve achar 0 palavras)
e entre na mixagem com volume ~0,16 por baixo da narração."""
import json, sys, time, urllib.request, urllib.error
PROMPT = ("Instrumental original Brazilian 'moda de viola' / sertanejo raiz background score, no vocals. "
          "Lead: viola caipira (10-string Brazilian guitar) fingerpicked melody with ponteio; steel-string acoustic guitar strumming in a slow toada/guarânia feel; "
          "soft accordion (sanfona) pads entering in the second half; light upright bass. 84 BPM, key of D major, warm, nostalgic, countryside at dusk. "
          "Dynamics: starts reflective and slightly melancholic, builds gently, ends hopeful and resolved. Leave space for a narrator (no busy solos), "
          "mixed for voice-over underscore. Do not imitate any existing song.")
out = sys.argv[1]; ms = int(sys.argv[2]) if len(sys.argv) > 2 else 62000
body = json.dumps({"prompt": PROMPT, "music_length_ms": ms, "model_id": "music_v1"}).encode()
for i, wait in enumerate([0, 20, 40, 80, 120, 180]):
    time.sleep(wait)
    req = urllib.request.Request("https://api.elevenlabs.io/v1/music?output_format=mp3_44100_128", body, {"xi-api-key": "dummy", "Content-Type": "application/json"})
    try:
        open(out, "wb").write(urllib.request.urlopen(req, timeout=600).read()); print("ok", out); break
    except urllib.error.HTTPError as e:
        print("tentativa", i + 1, "HTTP", e.code)   # 429 = serviço ocupado: tenta de novo
