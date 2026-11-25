#!/usr/bin/env python3
"""Mede a sincronia entre a boca e a voz em cada clipe da novela (pedido do editor, 23/11/2026).

Uso (com o Python que tem mediapipe e opencv; ver docs/video/novela/SINCRONIA.md):
  python sincronia.py --modelo face_landmarker.task --video clipe.mp4 [--audio voz.wav] [--json saida.json]

O que mede:
- **Boca:** MediaPipe Face Landmarker (478 pontos) em cada quadro. Abertura = distância entre os pontos 13 e 14 (lábios
  internos) dividida pela largura da boca (61 a 291), no maior rosto do quadro. A boca está "falando" nos trechos em que a
  abertura passa de base + 35% da faixa (base = percentil 20, faixa = p95 − p20), juntando falhas menores que 0,25 s e
  descartando trechos menores que 0,2 s.
- **Voz:** tempo de cada palavra pela transcrição scribe_v1 (ElevenLabs). Palavras a menos de 0,3 s viram um trecho só.
- **Números:**
  - `boca_sem_voz`: segundos em que a boca fala e não há voz;
  - `voz_sem_boca`: segundos de voz com a boca parada;
  - `atraso_ms`: deslocamento que maximiza a correlação entre a abertura da boca e a presença de voz (±600 ms;
    positivo = o áudio vem depois da boca).
- **Aprovação:** |atraso| ≤ 120 ms, boca_sem_voz ≤ 0,5 s e voz_sem_boca ≤ 0,5 s.
"""
import argparse, json, os, subprocess, sys, tempfile, urllib.request, uuid
import numpy as np


def stt_palavras(wav):
    b = uuid.uuid4().hex; data = open(wav, "rb").read()
    campos = {"model_id": "scribe_v1", "language_code": "por", "timestamps_granularity": "word"}
    body = b"".join(f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode() for k, v in campos.items())
    body += f'--{b}\r\nContent-Disposition: form-data; name="file"; filename="a.wav"\r\nContent-Type: audio/wav\r\n\r\n'.encode() + data + f'\r\n--{b}--\r\n'.encode()
    r = urllib.request.Request("https://api.elevenlabs.io/v1/speech-to-text", body,
                               {"xi-api-key": "dummy", "Content-Type": f"multipart/form-data; boundary={b}"})
    j = json.loads(urllib.request.urlopen(r, timeout=240).read())
    return [w for w in j.get("words", []) if w.get("type") == "word"], j.get("text", "")


def trechos(mask, fps, junta=0.25, minimo=0.2):
    out, ini = [], None
    for i, v in enumerate(list(mask) + [False]):
        if v and ini is None:
            ini = i
        if not v and ini is not None:
            out.append([ini / fps, i / fps]); ini = None
    j = []
    for a, z in out:
        if j and a - j[-1][1] < junta:
            j[-1][1] = z
        else:
            j.append([a, z])
    return [[round(a, 2), round(z, 2)] for a, z in j if z - a >= minimo]


def abertura_boca(video, modelo):
    import cv2, mediapipe as mp
    from mediapipe.tasks import python as mpt
    from mediapipe.tasks.python import vision
    opt = vision.FaceLandmarkerOptions(base_options=mpt.BaseOptions(model_asset_path=modelo),
                                       running_mode=vision.RunningMode.VIDEO, num_faces=3)
    det = vision.FaceLandmarker.create_from_options(opt)
    cap = cv2.VideoCapture(video); fps = cap.get(cv2.CAP_PROP_FPS) or 24
    vals, i = [], 0
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        img = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(fr, cv2.COLOR_BGR2RGB))
        res = det.detect_for_video(img, int(i * 1000 / fps)); i += 1
        if not res.face_landmarks:
            vals.append(np.nan); continue
        def area(lm):
            xs = [p.x for p in lm]; ys = [p.y for p in lm]
            return (max(xs) - min(xs)) * (max(ys) - min(ys))
        lm = max(res.face_landmarks, key=area)
        d = lambda a, b: np.hypot(lm[a].x - lm[b].x, lm[a].y - lm[b].y)
        vals.append(d(13, 14) / max(d(61, 291), 1e-6))
    det.close()
    return np.array(vals, dtype=float), fps


def medir(video, modelo, audio=None):
    mar, fps = abertura_boca(video, modelo)
    n = len(mar)
    with tempfile.TemporaryDirectory() as t:
        wav = os.path.join(t, "a.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", audio or video, "-vn", "-ac", "1", "-ar", "16000", wav], check=True)
        palavras, texto = stt_palavras(wav)
    rosto = ~np.isnan(mar)
    m = np.where(rosto, mar, np.nan)
    if rosto.sum() < 5:
        return {"video": video, "erro": "rosto não detectado", "texto": texto}
    p20, p95 = np.nanpercentile(m, 20), np.nanpercentile(m, 95)
    lim = p20 + 0.35 * max(p95 - p20, 0.02)
    aberta = np.nan_to_num(m, nan=0) > lim
    boca = trechos(aberta, fps)
    voz_mask = np.zeros(n, bool)
    voz = []
    for w in palavras:
        a, z = w["start"], w["end"]
        if voz and a - voz[-1][1] < 0.3:
            voz[-1][1] = z
        else:
            voz.append([a, z])
    for a, z in voz:
        voz_mask[int(a * fps):min(n, int(z * fps) + 1)] = True
    boca_mask = np.zeros(n, bool)
    for a, z in boca:
        boca_mask[int(a * fps):min(n, int(z * fps) + 1)] = True
    so_rosto = rosto  # só conta onde há rosto visível
    boca_sem_voz = float(((boca_mask & ~voz_mask) & so_rosto).sum() / fps)
    voz_sem_boca = float(((voz_mask & ~boca_mask) & so_rosto).sum() / fps)
    # atraso por correlação cruzada (abertura normalizada × presença de voz)
    x = np.nan_to_num((m - p20) / max(p95 - p20, 1e-6), nan=0); y = voz_mask.astype(float)
    melhor, lag_best = -1, 0
    for lag in range(-int(0.6 * fps), int(0.6 * fps) + 1):
        if lag >= 0:
            c = np.dot(x[:n - lag], y[lag:])
        else:
            c = np.dot(x[-lag:], y[:n + lag])
        if c > melhor:
            melhor, lag_best = c, lag
    atraso = round(1000 * lag_best / fps)
    ok = abs(atraso) <= 120 and boca_sem_voz <= 0.5 and voz_sem_boca <= 0.5
    return {"video": video, "fps": fps, "duracao": round(n / fps, 2), "texto": texto,
            "boca_falando": boca, "voz": [[round(a, 2), round(z, 2)] for a, z in voz],
            "boca_sem_voz_s": round(boca_sem_voz, 2), "voz_sem_boca_s": round(voz_sem_boca, 2),
            "atraso_ms": atraso, "aprovado": ok, "rosto_pct": round(100 * rosto.mean())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo", required=True); ap.add_argument("--video", required=True, nargs="+")
    ap.add_argument("--audio"); ap.add_argument("--json")
    a = ap.parse_args()
    res = [medir(v, a.modelo, a.audio) for v in a.video]
    for r in res:
        if "erro" in r:
            print(f"{os.path.basename(r['video'])}: {r['erro']}"); continue
        print(f"{os.path.basename(r['video'])}: atraso {r['atraso_ms']:+} ms · boca sem voz {r['boca_sem_voz_s']} s · "
              f"voz sem boca {r['voz_sem_boca_s']} s · rosto {r['rosto_pct']}% · {'OK' if r['aprovado'] else 'FALHA'}")
        print(f"   boca {r['boca_falando']}  voz {r['voz']}")
    if a.json:
        json.dump(res, open(a.json, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
