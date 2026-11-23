"""Mede a linguagem visual de um vídeo e grava as métricas em JSON (base das fórmulas de docs/video/REEL_NOVELA_VISUAL_PADRAO.md).

Uso: python3 tools/video/analisar_visual.py <video.mp4> <saida.json> [--fps 2] [--limiar-corte 0.30] [--folha folha.jpg]

Mede, sem IA e sem rede (só ffmpeg + numpy):
- cortes (detector de cena do ffmpeg) → duração dos planos, cortes por minuto ao longo do vídeo, ajuste log-normal;
- cor por quadro: luminância (Y), contraste (desvio de Y), saturação, colorido de Hasler-Süsstrunk, temperatura (R−B),
  paleta dominante (k-means em numpy);
- enquadramento: fração de pixels de pele (YCbCr) como indicador de escala do plano (close × aberto) e altura do centro
  de massa da pele (onde fica o rosto);
- movimento: diferença média absoluta entre quadros vizinhos do mesmo plano;
- legenda: presença de texto claro de alto contraste no terço inferior e no topo;
- áudio: loudness integrada (EBU R128) e faixa de loudness.
"""
import argparse
import json
import re
import subprocess
import sys

import numpy as np

W, H = 90, 160  # amostra 9:16 pequena: suficiente para estatística de cor e composição


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def probe(video):
    r = sh(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height,avg_frame_rate,codec_name",
            "-of", "json", video])
    d = json.loads(r.stdout)
    v = next(s for s in d["streams"] if s["codec_type"] == "video")
    num, den = (int(x) for x in v["avg_frame_rate"].split("/"))
    return {"duracao": float(d["format"]["duration"]), "largura": v["width"], "altura": v["height"],
            "fps": round(num / den, 3) if den else None, "codec": v["codec_name"]}


def cortes(video, limiar):
    """Timestamps dos cortes pelo detector de cena do ffmpeg (quadros reduzidos para acelerar)."""
    r = sh(["ffmpeg", "-hide_banner", "-nostats", "-i", video, "-an", "-vf",
            f"scale=180:-2,select='gt(scene,{limiar})',showinfo", "-f", "null", "-"])
    return [float(m) for m in re.findall(r"pts_time:([0-9.]+)", r.stderr)]


def quadros(video, fps):
    p = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", video, "-an", "-vf",
                          f"fps={fps},scale={W}:{H}:flags=area", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         stdout=subprocess.PIPE)
    tam = W * H * 3
    while True:
        b = p.stdout.read(tam)
        if len(b) < tam:
            break
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3).astype(np.float32)
    p.wait()


def hsv_sat(rgb):
    mx, mn = rgb.max(-1), rgb.min(-1)
    return np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)


def metricas_quadro(f):
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    y = 0.299 * r + 0.587 * g + 0.114 * b
    cb = 128 - 0.168736 * r - 0.331264 * g + 0.5 * b
    cr = 128 + 0.5 * r - 0.418688 * g - 0.081312 * b
    pele = (cr > 135) & (cr < 180) & (cb > 85) & (cb < 135) & (y > 60)
    rg, yb = r - g, 0.5 * (r + g) - b
    colorido = np.sqrt(rg.std() ** 2 + yb.std() ** 2) + 0.3 * np.sqrt(rg.mean() ** 2 + yb.mean() ** 2)
    linhas = np.nonzero(pele.any(1))[0]
    cy = float((np.arange(H)[:, None] * pele).sum() / pele.sum() / H) if pele.sum() > 20 else None
    # texto de legenda: pixels muito claros (ou amarelos) com borda forte no terço inferior / no topo
    claro = (y > 215) | ((r > 200) & (g > 180) & (b < 90))
    borda = np.abs(np.diff(y, axis=1, prepend=y[:, :1])) > 60
    txt = claro & borda
    return {
        "y": float(y.mean()), "contraste": float(y.std()), "sat": float(hsv_sat(f / 255).mean()),
        "colorido": float(colorido), "quente": float((r - b).mean()), "pele": float(pele.mean()),
        "pele_cy": cy, "txt_baixo": float(txt[int(H * 0.62):int(H * 0.90)].mean()), "txt_topo": float(txt[:int(H * 0.18)].mean()),
        "preto_topo": float((y[:8] < 16).mean()), "preto_base": float((y[-8:] < 16).mean()),
    }


def kmeans(px, k=6, it=25, seed=7):
    rng = np.random.default_rng(seed)
    c = px[rng.choice(len(px), k, replace=False)]
    for _ in range(it):
        lab = ((px[:, None, :] - c[None]) ** 2).sum(-1).argmin(1)
        c = np.array([px[lab == i].mean(0) if (lab == i).any() else c[i] for i in range(k)])
    peso = np.bincount(lab, minlength=k) / len(lab)
    ordem = np.argsort(-peso)
    return [{"hex": "#%02x%02x%02x" % tuple(int(v) for v in c[i]), "peso": round(float(peso[i]), 3)} for i in ordem]


def resumo(xs):
    a = np.array([x for x in xs if x is not None], dtype=float)
    if not len(a):
        return None
    q = np.percentile(a, [10, 25, 50, 75, 90])
    return {"media": round(float(a.mean()), 4), "dp": round(float(a.std()), 4), "p10": round(float(q[0]), 4),
            "p25": round(float(q[1]), 4), "mediana": round(float(q[2]), 4), "p75": round(float(q[3]), 4), "p90": round(float(q[4]), 4)}


def loudness(video):
    r = sh(["ffmpeg", "-hide_banner", "-nostats", "-i", video, "-vn", "-af", "ebur128", "-f", "null", "-"])
    i = re.findall(r"I:\s+(-?[0-9.]+) LUFS", r.stderr)
    lra = re.findall(r"LRA:\s+([0-9.]+) LU", r.stderr)
    return {"lufs_integrado": float(i[-1]) if i else None, "lra": float(lra[-1]) if lra else None}


def folha_contato(video, saida, n=24):
    """Folha de contato só para inspeção interna (não versionar: o vídeo é de terceiros)."""
    dur = probe(video)["duracao"]
    passo = dur / n
    sh(["ffmpeg", "-y", "-v", "error", "-i", video, "-vf", f"fps=1/{passo:.3f},scale=180:-2,tile=8x3", "-frames:v", "1", saida])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("saida")
    ap.add_argument("--fps", type=float, default=2.0)
    ap.add_argument("--limiar-corte", type=float, default=0.30)
    ap.add_argument("--folha")
    a = ap.parse_args()

    info = probe(a.video)
    print(f"vídeo: {info}", file=sys.stderr)
    ts = cortes(a.video, a.limiar_corte)
    bordas = [0.0] + ts + [info["duracao"]]
    planos = np.diff(bordas)
    planos = planos[planos > 0.15]  # descarta flashes / cortes duplos
    lp = np.log(planos)
    por_min = np.histogram(ts, bins=np.arange(0, info["duracao"] + 60, 60))[0]
    print(f"cortes: {len(ts)} · plano médio {planos.mean():.2f}s", file=sys.stderr)

    ms, amostra, movimento, ant = [], [], [], None
    corte_idx = np.array(ts)
    for i, f in enumerate(quadros(a.video, a.fps)):
        t = i / a.fps
        m = metricas_quadro(f); m["t"] = t; ms.append(m)
        if i % 3 == 0:
            amostra.append(f.reshape(-1, 3)[::7])
        if ant is not None and not ((corte_idx > t - 1 / a.fps) & (corte_idx <= t)).any():
            movimento.append(float(np.abs(f - ant).mean()))
        ant = f
    print(f"quadros analisados: {len(ms)}", file=sys.stderr)
    px = np.concatenate(amostra)
    px = px[np.random.default_rng(1).choice(len(px), min(len(px), 60000), replace=False)]

    k = lambda nome: [m[nome] for m in ms]
    abertura = [m for m in ms if m["t"] < 3]
    res = {
        "video": info,
        "ritmo": {
            "cortes": len(ts), "planos": len(planos),
            "duracao_plano_s": resumo(planos), "lognormal": {"mu": round(float(lp.mean()), 4), "sigma": round(float(lp.std()), 4)},
            "cortes_por_minuto": resumo(por_min.tolist()),
            "primeiro_corte_s": round(ts[0], 2) if ts else None,
            "cortes_por_minuto_serie": por_min.tolist(),
            "fracao_planos_menores_que_2s": round(float((planos < 2).mean()), 3),
            "fracao_planos_maiores_que_6s": round(float((planos > 6).mean()), 3),
        },
        "cor": {
            "luminancia_Y_0a255": resumo(k("y")), "contraste_dpY": resumo(k("contraste")), "saturacao_0a1": resumo(k("sat")),
            "colorido_HS": resumo(k("colorido")), "temperatura_R_menos_B": resumo(k("quente")),
            "paleta_dominante": kmeans(px),
        },
        "enquadramento": {
            "fracao_pele": resumo(k("pele")), "altura_centro_pele_0topo_1base": resumo(k("pele_cy")),
            "fracao_quadros_close_pele_maior_8pct": round(float(np.mean([m["pele"] > 0.08 for m in ms])), 3),
            "fracao_quadros_sem_pessoa_pele_menor_1pct": round(float(np.mean([m["pele"] < 0.01 for m in ms])), 3),
            "tarjas_pretas": {"topo": resumo(k("preto_topo")), "base": resumo(k("preto_base"))},
        },
        "movimento_dif_media_0a255": resumo(movimento),
        "legenda": {
            "fracao_quadros_texto_terco_inferior": round(float(np.mean([m["txt_baixo"] > 0.004 for m in ms])), 3),
            "fracao_quadros_texto_topo": round(float(np.mean([m["txt_topo"] > 0.004 for m in ms])), 3),
        },
        "abertura_3s": {"y": resumo([m["y"] for m in abertura]), "sat": resumo([m["sat"] for m in abertura]),
                        "pele": resumo([m["pele"] for m in abertura])},
        "audio": loudness(a.video),
        "parametros": {"fps_amostra": a.fps, "limiar_corte": a.limiar_corte, "amostra_px": [W, H]},
    }
    with open(a.saida, "w") as fh:
        json.dump(res, fh, ensure_ascii=False, indent=2)
    if a.folha:
        folha_contato(a.video, a.folha)
    print(f"ok: {a.saida}", file=sys.stderr)


if __name__ == "__main__":
    main()
