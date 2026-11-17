"""Pós-processa as falas (silêncios; atempo 1.08 só no narrador) e transcreve cada uma (ElevenLabs scribe_v1)."""
import json, subprocess, urllib.request, uuid, sys
ids = {int(x) for x in sys.argv[1].split(",")} if len(sys.argv) > 1 else None
for f in json.load(open('falas.json', encoding='utf-8')):
    i = f['id']
    if ids and i not in ids: continue
    af = "silenceremove=start_periods=1:start_threshold=-50dB:stop_periods=-1:stop_duration=0.3:stop_threshold=-45dB"
    if f['quem'] == 'narrador': af += ",atempo=1.08"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"voz/fala{i}.mp3", "-af", af, "-ar", "48000", f"voz/proc/fala{i}.wav"], check=True)
    b = uuid.uuid4().hex; data = open(f"voz/proc/fala{i}.wav", "rb").read()
    body = (f'--{b}\r\nContent-Disposition: form-data; name="model_id"\r\n\r\nscribe_v1\r\n--{b}\r\nContent-Disposition: form-data; name="language_code"\r\n\r\npor\r\n--{b}\r\nContent-Disposition: form-data; name="file"; filename="a.wav"\r\nContent-Type: audio/wav\r\n\r\n').encode() + data + f'\r\n--{b}--\r\n'.encode()
    r = urllib.request.Request("https://api.elevenlabs.io/v1/speech-to-text", body, {"xi-api-key": "dummy", "Content-Type": f"multipart/form-data; boundary={b}"})
    j = json.loads(urllib.request.urlopen(r, timeout=240).read()); json.dump(j, open(f"voz/stt/fala{i}.json", "w"), ensure_ascii=False)
    n = len([w for w in j['words'] if w['type'] == 'word'])
    print(i, f['quem'], n, len(f['texto'].split()), '|', j['text'])
