# Wan 2.2 TI2V-5B (Apache 2.0) em modo imagem (1 quadro): prévias realistas para o editor. GPU T4 grátis do Kaggle.
import subprocess, sys, os, time, gc, json
os.environ["PYTORCH_CUDA_ALLOC_CONF"]="expandable_segments:True"
subprocess.run([sys.executable,"-m","pip","install","-q","-U","diffusers>=0.35","transformers","accelerate","ftfy"],check=True)
import torch
from diffusers import WanPipeline, AutoencoderKLWan
P=[["cart", "RAW photo, DSLR photograph, close-up of an old wooden notary office desk in a small Brazilian town, an open land registry book with handwritten entries, a rubber stamp and ink pad, a pile of property documents with a red ribbon, reading glasses, window light through blinds, shallow depth of field, no people, no hands, film grain, documentary photojournalism, 50mm lens"]]; NEG="person, people, human, hands, fingers, face, cartoon, flat illustration, drawing, painting, illustration, 3d render, anime, text, watermark, subtitles, blurry, deformed hands, extra fingers, distorted face, low quality"
mid="Wan-AI/Wan2.2-TI2V-5B-Diffusers"
vae=AutoencoderKLWan.from_pretrained(mid,subfolder="vae",torch_dtype=torch.float32)
pipe=WanPipeline.from_pretrained(mid,vae=vae,torch_dtype=torch.bfloat16)
on=torch.device("cuda"); off=torch.device("cpu")
pipe.text_encoder.to(on); emb={}
with torch.no_grad():
    for nome,p in P: emb[nome]=pipe.encode_prompt(prompt=p,negative_prompt=NEG,do_classifier_free_guidance=True,device=on)
pipe.text_encoder.to(off); pipe.text_encoder=None; gc.collect(); torch.cuda.empty_cache()
pipe.transformer.enable_group_offload(onload_device=on, offload_device=off, offload_type="block_level", num_blocks_per_group=6, use_stream=False)
pipe.vae.to(on)
for nome,_ in P:
    for seed in (11,23):
        t=time.time(); pe,ne=emb[nome]
        out=pipe(prompt_embeds=pe,negative_prompt_embeds=ne,height=960,width=960,num_frames=1,num_inference_steps=40,guidance_scale=5.0,generator=torch.Generator("cpu").manual_seed(seed),output_type="pil")
        img=out.frames[0][0]
        img.save(f"/kaggle/working/{nome}_s{seed}.png"); print(nome,seed,round(time.time()-t),"s")
