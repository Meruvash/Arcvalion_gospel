#!/usr/bin/env python3
"""Envia um script ao Kaggle (GPU grátis) e acompanha. O proxy do ambiente injeta a credencial do Kaggle.
Uso: python3 kaggle.py push <script.py> <slug> [--maquina NvidiaTeslaT4] [--dataset dono/slug]
     python3 kaggle.py status <slug> | python3 kaggle.py saida <slug> <pasta>"""
import json, sys, os, urllib.request
API = "https://www.kaggle.com/api/v1"; USER = "basedevalores"
def req(path, data=None):
    r = urllib.request.Request(API + path, data=json.dumps(data).encode() if data else None,
                               headers={"Content-Type": "application/json", "Authorization": "Bearer dummy"})
    return json.load(urllib.request.urlopen(r, timeout=120))
cmd = sys.argv[1]
if cmd == "push":
    maq = sys.argv[sys.argv.index("--maquina") + 1] if "--maquina" in sys.argv else "NvidiaTeslaT4"
    print(req("/kernels/push", {"slug": f"{USER}/{sys.argv[3]}", "newTitle": sys.argv[3], "text": open(sys.argv[2]).read(),
          "language": "python", "kernelType": "script", "isPrivate": True, "enableGpu": True, "enableInternet": True,
          "machineShape": maq,
          "datasetDataSources": [sys.argv[sys.argv.index("--dataset") + 1]] if "--dataset" in sys.argv else []}))
elif cmd == "status":
    print(req(f"/kernels/status?userName={USER}&kernelSlug={sys.argv[2]}"))
elif cmd == "saida":
    d = req(f"/kernels/output?userName={USER}&kernelSlug={sys.argv[2]}"); os.makedirs(sys.argv[3], exist_ok=True)
    print((d.get("log") or "")[-3000:])
    for f in d.get("files", []):
        dest = os.path.join(sys.argv[3], os.path.basename(f["fileName"] if "fileName" in f else f["url"].split("?")[0]))
        urllib.request.urlretrieve(f["url"], dest); print("baixado", dest)
