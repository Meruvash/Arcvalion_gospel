"""Validação estatística das medidas do Reel Novela Visual padrão (evidências reprodutíveis).

Uso: python3 tools/video/validar_medicao.py <video.mp4> <pasta_saida> [--seed 42]

Gera em <pasta_saida>:
  cortes_brutos.json      timestamps dos cortes nos limiares 0,25 / 0,30 / 0,40 (dado bruto, reprodutível)
  quadros_1fps.json       Y, saturação e R−B de cada quadro a 1 fps (dado bruto)
  validacao.json          ajuste de distribuição (KS, AIC), IC 95% por bootstrap em blocos, metades, sensibilidade
  prancha_cortes.jpg      24 cortes detectados sorteados: quadro 0,2 s antes | 0,2 s depois (conferir precisão)
  prancha_recall_<n>.jpg  janelas de 12 s a 4 qps com os cortes detectados marcados (conferir revocação)
  prancha_legenda.jpg     48 quadros sorteados com o veredito do detector de legenda (conferir precisão e revocação)
Sem rede, sem IA: ffmpeg + numpy. Mesma semente → mesmos sorteios.
"""
import argparse
import json
import math
import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analisar_visual as av  # noqa: E402


def ffmpeg(*args):
    return subprocess.run(["ffmpeg", "-v", "error", "-y", *args], capture_output=True)


# ---------- ajuste de distribuição ----------

def ks_estat(x, cdf):
    x = np.sort(x)
    n = len(x)
    f = cdf(x)
    return float(max((np.arange(1, n + 1) / n - f).max(), (f - np.arange(0, n) / n).max()))


def phi(z):
    return 0.5 * (1 + np.vectorize(math.erf)(z / math.sqrt(2)))


def gamma_cdf(x, k, theta, termos=200):
    # incompleta inferior regularizada por série: P(k, x/θ)
    out = []
    for xi in np.atleast_1d(x):
        t = xi / theta
        soma, termo = 0.0, 1.0 / k
        soma = termo
        for n in range(1, termos):
            termo *= t / (k + n)
            soma += termo
            if termo < 1e-12 * soma:
                break
        out.append(math.exp(-t + k * math.log(t) - math.lgamma(k)) * soma if t > 0 else 0.0)
    return np.array(out)


def ajustes(d):
    n = len(d)
    ld = np.log(d)
    mu, sg = ld.mean(), ld.std()
    lam = 1 / d.mean()
    m, v = d.mean(), d.var()
    k, th = m * m / v, v / m
    ll_logn = float(np.sum(-np.log(d * sg * math.sqrt(2 * math.pi)) - (ld - mu) ** 2 / (2 * sg * sg)))
    ll_exp = float(np.sum(np.log(lam) - lam * d))
    ll_gam = float(np.sum((k - 1) * np.log(d) - d / th - k * math.log(th) - math.lgamma(k)))
    crit = 1.36 / math.sqrt(n)
    return {
        "n": n, "ks_critico_alfa_0_05": round(crit, 4),
        "lognormal": {"mu": round(mu, 4), "sigma": round(sg, 4), "ks": round(ks_estat(d, lambda x: phi((np.log(x) - mu) / sg)), 4), "aic": round(4 - 2 * ll_logn, 1)},
        "gama": {"k": round(k, 3), "theta": round(th, 3), "ks": round(ks_estat(d, lambda x: gamma_cdf(x, k, th)), 4), "aic": round(4 - 2 * ll_gam, 1)},
        "exponencial": {"lambda": round(lam, 4), "ks": round(ks_estat(d, lambda x: 1 - np.exp(-lam * x)), 4), "aic": round(2 - 2 * ll_exp, 1)},
        "nota": "KS com parâmetros estimados dos próprios dados é conservador (Lilliefors); serve para comparar modelos, AIC decide.",
    }


# ---------- bootstrap em blocos de 1 minuto ----------

def bootstrap_blocos(blocos, estat, reps=2000, rng=None):
    rng = rng or np.random.default_rng(42)
    b = len(blocos)
    vals = []
    for _ in range(reps):
        amostra = [blocos[i] for i in rng.integers(0, b, b)]
        vals.append(estat(np.concatenate(amostra)))
    lo, hi = np.percentile(vals, [2.5, 97.5])
    return [round(float(lo), 4), round(float(hi), 4)]


def wilson(k, n, z=1.96):
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [round(c - m, 3), round(c + m, 3)]


# ---------- pranchas para conferência visual ----------

def quadro_jpg(video, t, saida, rotulo, cor="white"):
    txt = rotulo.replace(":", "\\:")
    ffmpeg("-ss", f"{max(t, 0):.3f}", "-i", video, "-frames:v", "1", "-vf",
           f"scale=160:-2,drawtext=text='{txt}':x=4:y=4:fontsize=14:fontcolor={cor}:box=1:boxcolor=black@0.7", saida)


def prancha(arquivos, colunas, saida):
    lista = saida + ".txt"
    with open(lista, "w") as fh:
        for a in arquivos:
            fh.write(f"file '{a}'\n")
    linhas = math.ceil(len(arquivos) / colunas)
    ffmpeg("-f", "concat", "-safe", "0", "-i", lista, "-vf", f"tile={colunas}x{linhas}", "-frames:v", "1", saida)
    os.remove(lista)
    for a in arquivos:
        os.remove(a)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("saida")
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    os.makedirs(a.saida, exist_ok=True)
    rng = np.random.default_rng(a.seed)
    info = av.probe(a.video)
    dur = info["duracao"]

    # 1. cortes em três limiares (sensibilidade) — dado bruto salvo
    cortes = {str(l): av.cortes(a.video, l) for l in (0.25, 0.30, 0.40)}
    json.dump(cortes, open(os.path.join(a.saida, "cortes_brutos.json"), "w"))
    print("cortes:", {k: len(v) for k, v in cortes.items()}, file=sys.stderr)

    def planos(ts):
        d = np.diff([0.0] + ts + [dur])
        return d[d > 0.15]

    sens = {}
    for l, ts in cortes.items():
        d = planos(ts)
        sens[l] = {"cortes": len(ts), "mediana_plano_s": round(float(np.median(d)), 3), "cortes_por_minuto": round(len(ts) / (dur / 60), 2),
                   "frac_menor_2s": round(float((d < 2).mean()), 3), "frac_maior_6s": round(float((d > 6).mean()), 3)}

    ts = cortes["0.3"]
    d = planos(ts)
    # blocos por minuto: planos agrupados pelo minuto em que começam
    inicios = np.cumsum(np.concatenate([[0], d[:-1]]))
    blocos_planos = [d[(inicios >= m * 60) & (inicios < (m + 1) * 60)] for m in range(int(dur // 60) + 1)]
    blocos_planos = [b for b in blocos_planos if len(b)]
    cpm = np.histogram(ts, bins=np.arange(0, dur + 60, 60))[0].astype(float)
    metade = dur / 2

    # 2. cor por quadro a 1 fps — dado bruto salvo
    q = [{"t": i, **{k: round(v, 4) for k, v in av.metricas_quadro(f).items() if k in ("y", "sat", "quente")}}
         for i, f in enumerate(av.quadros(a.video, 1.0))]
    json.dump(q, open(os.path.join(a.saida, "quadros_1fps.json"), "w"))
    arr = {k: np.array([x[k] for x in q]) for k in ("y", "sat", "quente")}
    minuto = np.array([x["t"] // 60 for x in q])
    blocos_cor = {k: [arr[k][minuto == m] for m in np.unique(minuto)] for k in arr}

    val = {
        "video": info,
        "reprodutibilidade_limiar_0_30": sens["0.3"],
        "sensibilidade_limiar_corte": sens,
        "ajuste_duracao_plano": ajustes(d),
        "ic95_bootstrap_blocos_1min": {
            "mediana_plano_s": bootstrap_blocos(blocos_planos, np.median, rng=rng),
            "frac_planos_menor_2s": bootstrap_blocos(blocos_planos, lambda x: (x < 2).mean(), rng=rng),
            "cortes_por_minuto_media": bootstrap_blocos([np.array([c]) for c in cpm], np.mean, rng=rng),
            "luminancia_media": bootstrap_blocos(blocos_cor["y"], np.mean, rng=rng),
            "saturacao_media": bootstrap_blocos(blocos_cor["sat"], np.mean, rng=rng),
            "temperatura_media": bootstrap_blocos(blocos_cor["quente"], np.mean, rng=rng),
        },
        "metades": {
            nome: {
                "mediana_plano_s": round(float(np.median(d[sel])), 3),
                "cortes_por_minuto": round(float(np.sum((np.array(ts) >= lo) & (np.array(ts) < hi)) / ((hi - lo) / 60)), 2),
                "luminancia_media": round(float(arr["y"][(minuto * 60 >= lo) & (minuto * 60 < hi)].mean()), 2),
                "saturacao_media": round(float(arr["sat"][(minuto * 60 >= lo) & (minuto * 60 < hi)].mean()), 4),
                "temperatura_media": round(float(arr["quente"][(minuto * 60 >= lo) & (minuto * 60 < hi)].mean()), 2),
            }
            for nome, lo, hi, sel in (("primeira", 0, metade, inicios < metade), ("segunda", metade, dur + 1, inicios >= metade))
        },
        "wilson_ic95_folha_contato_24": {"uma_pessoa_11_de_24": wilson(11, 24), "duas_pessoas_6_de_24": wilson(6, 24), "grupo_6_de_24": wilson(6, 24)},
        "semente": a.seed,
    }
    json.dump(val, open(os.path.join(a.saida, "validacao.json"), "w"), ensure_ascii=False, indent=2)

    # 3. prancha de precisão dos cortes: 24 cortes sorteados, antes|depois
    tmp = []
    for j, t in enumerate(sorted(rng.choice(ts, 24, replace=False))):
        for lado, dt in (("A", -0.2), ("D", 0.2)):
            p = os.path.join(a.saida, f"_c{j:02d}{lado}.jpg")
            quadro_jpg(a.video, t + dt, p, f"{j+1} {lado} {t:.1f}s")
            tmp.append(p)
    prancha(tmp, 8, os.path.join(a.saida, "prancha_cortes.jpg"))

    # 4. pranchas de revocação: 2 janelas de 12 s a 4 qps, quadro marcado em amarelo se há corte detectado antes dele
    for w, inicio in enumerate(sorted(rng.uniform(60, dur - 60, 2))):
        tmp = []
        for i in range(48):
            t = inicio + i * 0.25
            corte = any(t - 0.25 < c <= t for c in ts)
            p = os.path.join(a.saida, f"_r{i:02d}.jpg")
            quadro_jpg(a.video, t, p, f"{t:.2f}" + (" CORTE" if corte else ""), "yellow" if corte else "white")
            tmp.append(p)
        prancha(tmp, 12, os.path.join(a.saida, f"prancha_recall_{w+1}.jpg"))

    # 5. prancha do detector de legenda: 48 quadros sorteados com veredito
    tmp, vereditos = [], []
    for i, t in enumerate(sorted(rng.uniform(1, dur - 1, 48))):
        r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", a.video, "-frames:v", "1", "-vf", "scale=480:-2",
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        Hl = len(r) // (480 * 3)
        f = np.frombuffer(r[:480 * Hl * 3], np.uint8).reshape(Hl, 480, 3).astype(np.int16)
        mx, mn = f.max(-1), f.min(-1)
        br = (mn > 225) & ((mx - mn) < 25)
        xs = np.arange(480)
        cand = [y for y in range(int(Hl * .5), int(Hl * .9)) if br[y].sum() > 8 and abs((br[y] * xs).sum() / br[y].sum() - 240) < 480 * .12]
        sim = len(cand) >= 6
        vereditos.append({"i": i + 1, "t": round(float(t), 2), "detector": sim})
        p = os.path.join(a.saida, f"_l{i:02d}.jpg")
        quadro_jpg(a.video, t, p, f"{i+1} {'LEG' if sim else 'sem'}", "lime" if sim else "red")
        tmp.append(p)
    prancha(tmp, 8, os.path.join(a.saida, "prancha_legenda.jpg"))
    json.dump(vereditos, open(os.path.join(a.saida, "legenda_vereditos.json"), "w"))
    print("ok", file=sys.stderr)


if __name__ == "__main__":
    main()
