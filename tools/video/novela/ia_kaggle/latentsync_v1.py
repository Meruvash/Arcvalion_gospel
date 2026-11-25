# v2: Python 3.10 isolado (uv). Kaggle (T4, grátis): redesenha a boca de cada clipe da novela para seguir o áudio exato (LatentSync, Apache-2.0).
# Entrada: dataset basedevalores/novela-v1-lipsync-entrada (entrada.zip com cNN.mp4 + cNN.wav).
import glob, os, subprocess, sys, time, zipfile, shutil
def sh(c, ok=False):
    print("$", c, flush=True); r = subprocess.run(c, shell=True, text=True, capture_output=True)
    print(r.stdout[-3000:], r.stderr[-3000:], flush=True)
    if r.returncode and not ok: raise SystemExit(f"falhou: {c}")
    return r.returncode
W = "/kaggle/working"; os.chdir(W)
src = glob.glob("/kaggle/input/**/entrada.zip", recursive=True) + glob.glob("/kaggle/input/**/c01.mp4", recursive=True)
print("entrada:", src, flush=True)
if src[0].endswith(".zip"):
    zipfile.ZipFile(src[0]).extractall(W)
else:
    shutil.copytree(os.path.dirname(src[0]), f"{W}/entrada", dirs_exist_ok=True)
sh("nvidia-smi")
sh("git clone -q https://github.com/bytedance/LatentSync.git")
os.chdir(f"{W}/LatentSync")
sh("git log -1 --oneline; cat setup_env.sh; cat requirements.txt; ls configs/unet")
# Kaggle está em Python 3.13; o LatentSync fixa versões de Python 3.10. Ambiente isolado com uv.
sh("pip install -q uv")
sh("uv venv -q --python 3.10 .venv")
sh("uv pip install -q --python .venv/bin/python -r requirements.txt --index-strategy unsafe-best-match")
sh(".venv/bin/python -c 'import torch,decord,diffusers;print(torch.__version__,torch.cuda.is_available())'")
sh(".venv/bin/python -c \"from huggingface_hub import snapshot_download;snapshot_download('ByteDance/LatentSync-1.5',local_dir='checkpoints')\"")
sh("find checkpoints -maxdepth 3 | head -50")
cfg = "configs/unet/stage2.yaml" if os.path.exists("configs/unet/stage2.yaml") else sorted(glob.glob("configs/unet/stage2*.yaml"))[0]
os.makedirs(f"{W}/saida", exist_ok=True)
for v in sorted(glob.glob(f"{W}/entrada/c*.mp4")):
    k = os.path.basename(v)[:3]; a = v[:-4] + ".wav"; out = f"{W}/saida/{k}_ls.mp4"
    for tent, (gs, seed) in enumerate([(1.5, 1247), (2.0, 7)]):
        t = time.time()
        rc = sh(f".venv/bin/python -m scripts.inference --unet_config_path {cfg} --inference_ckpt_path checkpoints/latentsync_unet.pt "
                f"--inference_steps 20 --guidance_scale {gs} --seed {seed} --video_path {v} --audio_path {a} --video_out_path {out}", ok=True)
        print(f"== {k} tentativa {tent} rc={rc} {time.time()-t:.0f}s existe={os.path.exists(out)}", flush=True)
        if rc == 0 and os.path.exists(out):
            break
sh(f"ls -la {W}/saida")
for f in glob.glob(f"{W}/LatentSync/temp*"):
    shutil.rmtree(f, ignore_errors=True)
shutil.rmtree(f"{W}/LatentSync", ignore_errors=True); shutil.rmtree(f"{W}/entrada", ignore_errors=True)
