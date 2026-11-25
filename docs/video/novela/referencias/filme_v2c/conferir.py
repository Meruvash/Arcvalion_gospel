import json,urllib.request,uuid,subprocess,sys
v=sys.argv[1]; w=v.replace(".mp4",".wav")
subprocess.run(["ffmpeg","-v","error","-y","-i",v,"-vn","-ac","1","-ar","44100",w],check=True)
pr=subprocess.run(["ffprobe","-v","error","-show_entries","stream=width,height:format=duration","-of","csv=p=0",v],capture_output=True,text=True).stdout.split()
b=uuid.uuid4().hex;d=open(w,"rb").read()
f={"model_id":"scribe_v1","language_code":"por","timestamps_granularity":"word"}
body=b"".join(f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{x}\r\n'.encode() for k,x in f.items())
body+=f'--{b}\r\nContent-Disposition: form-data; name="file"; filename="a.wav"\r\nContent-Type: audio/wav\r\n\r\n'.encode()+d+f'\r\n--{b}--\r\n'.encode()
j=json.loads(urllib.request.urlopen(urllib.request.Request("https://api.elevenlabs.io/v1/speech-to-text",body,{"xi-api-key":"dummy","Content-Type":f"multipart/form-data; boundary={b}"}),timeout=240).read())
cuts=subprocess.run(["ffmpeg","-i",v,"-vf","scdet=threshold=8","-f","null","-"],capture_output=True,text=True).stderr
import re
print(v.split("/")[-1],pr,"cortes",[round(float(x),2) for x in re.findall(r"lavfi.scd.time: ([0-9.]+)",cuts)])
print("  ",j["text"])
print("  ","|".join(f'{x["start"]:.1f} {x["text"]}' for x in j["words"] if x["type"]=="word"))
json.dump(j,open(v.replace(".mp4","_stt.json"),"w"),ensure_ascii=False)
