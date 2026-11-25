# Recorta o editor da gravação do celular (fundo removido) para o formato "apresentador no canto".
# Uso: python3 recortar_apresentador.py gravacao.mp4 INICIO FIM saida.webm  (MediaPipe selfie_multiclass_256x256.tflite;
# no container: apt-get install -y libegl1 libgles2). Saída WebM VP9 com alfa (yuva420p).
"""Recorta o fundo de uma gravação de celular (pessoa do peito para cima) e gera um vídeo com transparência (WebM VP9 + alfa).
Segmentação: MediaPipe Image Segmenter, modelo selfie_multiclass_256x256 (Apache-2.0), com média temporal e borda suave.
Uso: python3 recortar.py entrada.mp4 inicio fim saida.webm"""
import sys, subprocess, numpy as np, mediapipe as mp, cv2
from mediapipe.tasks.python import vision, BaseOptions
ent, ini, fim, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
W, H = map(int, subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", ent]).decode().strip().split(","))
seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(base_options=BaseOptions(model_asset_path="selfie_multiclass_256x256.tflite"), output_confidence_masks=True))
rd = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(ini), "-to", str(fim), "-i", ent, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
wr = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", "30", "-i", "-", "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0", "-crf", "24", "-auto-alt-ref", "0", out], stdin=subprocess.PIPE)
prev = None; n = 0
while True:
    buf = rd.stdout.read(W * H * 3)
    if len(buf) < W * H * 3: break
    rgb = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    res = seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb)))
    pessoa = 1.0 - res.confidence_masks[0].numpy_view()          # classe 0 = fundo
    pessoa = cv2.resize(pessoa, (W, H), interpolation=cv2.INTER_LINEAR)
    prev = pessoa if prev is None else 0.6 * pessoa + 0.4 * prev   # média temporal: sem tremor na borda
    a = np.clip((prev - 0.35) / 0.3, 0, 1)                          # curva de contraste da máscara
    a = cv2.GaussianBlur(a, (0, 0), 1.6)                            # borda suave
    rgba = np.dstack([rgb, (a * 255).astype(np.uint8)])
    wr.stdin.write(rgba.tobytes()); n += 1
wr.stdin.close(); wr.wait(); print("quadros", n)
seg.close()
