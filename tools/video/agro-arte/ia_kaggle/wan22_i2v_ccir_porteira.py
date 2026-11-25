# Modelo do script que roda no Kaggle (GPU T4 grátis). IMAGEM_BASE64 é preenchido pelo envio (a pintura em JPG 576x576).
IMAGEM_BASE64 = ''  # preenchido no envio (ccir-cena1_s11.jpg em 576x576)
# Wan 2.2 TI2V-5B (Apache 2.0): anima uma pintura dos vídeos do agro. GPU gratuita do Kaggle. Gerado pelo pipeline video-agro.
import subprocess, sys, base64, io, time, os
os.environ["PYTORCH_CUDA_ALLOC_CONF"]="expandable_segments:True"
subprocess.run([sys.executable,"-m","pip","install","-q","-U","diffusers>=0.35","transformers","accelerate","ftfy","imageio","imageio-ffmpeg"],check=True)
import torch
from PIL import Image
from diffusers import WanImageToVideoPipeline, AutoencoderKLWan
from diffusers.utils import export_to_video
print("torch",torch.__version__,"gpu",torch.cuda.get_device_name(0),"bf16",torch.cuda.is_bf16_supported())
t0=time.time()
mid="Wan-AI/Wan2.2-TI2V-5B-Diffusers"
vae=AutoencoderKLWan.from_pretrained(mid,subfolder="vae",torch_dtype=torch.float32)
pipe=WanImageToVideoPipeline.from_pretrained(mid,vae=vae,torch_dtype=torch.bfloat16)
import gc
on=torch.device("cuda"); off=torch.device("cpu")
PROMPT="photorealistic documentary footage: two Brazilian farmers at a wooden farm gate shake hands firmly and smile, the man on the right holds a folder of documents under his arm, grass and corn leaves sway gently in the breeze, soft morning sunlight, very slow push-in camera, natural motion, no other people"; NEG="painting, cartoon, illustration, 3d render, text, watermark, subtitles, blurry, low quality, deformed hands, extra fingers, distorted face, new person appearing, extra people, sudden camera cut, static frame, flicker"
pipe.text_encoder.to(on)
with torch.no_grad():
    pe,ne=pipe.encode_prompt(prompt=PROMPT,negative_prompt=NEG,do_classifier_free_guidance=True,device=on)
pipe.text_encoder.to(off); pipe.text_encoder=None; gc.collect(); torch.cuda.empty_cache()
print("texto codificado")
pipe.transformer.enable_group_offload(onload_device=on, offload_device=off, offload_type="block_level", num_blocks_per_group=6, use_stream=False)
pipe.vae.to(on); pipe.vae.enable_tiling() if hasattr(pipe.vae,"enable_tiling") else None
print("carregado em",round(time.time()-t0),"s")
img=Image.open(io.BytesIO(base64.b64decode(IMAGEM_BASE64))).convert("RGB").resize((576,576))
t1=time.time()
frames=pipe(image=img,prompt_embeds=pe,negative_prompt_embeds=ne,height=576,width=576,num_frames=61,num_inference_steps=30,guidance_scale=5.0,generator=torch.Generator("cpu").manual_seed(7)).frames[0]
export_to_video(frames,"/kaggle/working/ccir_a.mp4",fps=24)
print("gerado em",round(time.time()-t1),"s ->",os.path.getsize("/kaggle/working/ccir_a.mp4"),"bytes")
