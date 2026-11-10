import json,base64,urllib.request
txt=("Prorrogar dívida rural virou decisão do banco. "
     "Desde julho, o Manual de Crédito Rural diz: por sua conveniência e decisão. "
     "Mas a parte mais estranha? O STJ diz que é direito do devedor.")
body=json.dumps({"text":txt,"model_id":"eleven_multilingual_v2",
 "voice_settings":{"stability":0.4,"similarity_boost":0.8,"style":0.35,"speed":1.2}}).encode()
r=urllib.request.Request("https://api.elevenlabs.io/v1/text-to-speech/plASsyS7JE6GCAvx9uIc/with-timestamps",body,{"xi-api-key":"dummy","Content-Type":"application/json"})
d=json.load(urllib.request.urlopen(r))
open("voz.mp3","wb").write(base64.b64decode(d["audio_base64"]))
a=d["alignment"];json.dump(a,open("align.json","w"))
# words
w=[];cur="";t0=None
for c,s,e in zip(a["characters"],a["character_start_times_seconds"],a["character_end_times_seconds"]):
    if c==" ":
        if cur:w.append((cur,t0,last));cur="";t0=None
    else:
        if t0 is None:t0=s
        cur+=c;last=e
if cur:w.append((cur,t0,last))
json.dump(w,open("words.json","w"),ensure_ascii=False)
for x in w:print(f"{x[1]:.2f} {x[2]:.2f} {x[0]}")
