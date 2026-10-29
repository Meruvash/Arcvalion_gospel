"""Avisa Bing, Yandex e outros buscadores do IndexNow quando uma página é publicada ou muda.

Uso: python3 tools/indexnow.py [--tudo]
Roda depois do push, quando o site já está no ar (rotinas de notícias e resenhas, e na verificação das 22h).

- Compara o lastmod de cada URL do sitemap.xml com o último aviso enviado
  (conteudo/indexnow_estado.json) e só avisa o que é novo ou mudou. --tudo reenvia todas.
- Antes de avisar, confere se a página já responde 200 no ar. A que ainda não subiu (o GitHub Pages leva alguns
  minutos) fica para a próxima rodada, para o buscador não visitar um 404.
- A chave é pública por definição: o arquivo <chave>.txt na raiz do site prova que o aviso vem do dono do domínio.
"""
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOST = "meruvash.github.io"
SITE = "https://meruvash.github.io/Arcvalion_gospel"
CHAVE = "e6a19fbeb58d105a3023be74cd36764e"
ESTADO = ROOT / "conteudo" / "indexnow_estado.json"
SITEMAP = ROOT / "sitemap.xml"
ENDPOINT = "https://api.indexnow.org/indexnow"
UA = {"User-Agent": "PortalCristao-indexnow/1.0"}


def no_ar(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
            return r.status == 200
    except (urllib.error.URLError, TimeoutError):
        return False


def lastmods():
    """{url: lastmod ou None} lido do sitemap.xml."""
    return {u: lm or None for u, lm in re.findall(r"<loc>([^<]+)</loc>(?:<lastmod>([^<]+)</lastmod>)?", SITEMAP.read_text(encoding="utf-8"))}


def pendentes(tudo=False):
    """URLs do sitemap cujo lastmod ainda não foi avisado (página sem lastmod entra uma vez)."""
    sitemap = lastmods()
    enviado = {} if tudo or not ESTADO.exists() else json.loads(ESTADO.read_text(encoding="utf-8"))
    return sorted(u for u, lm in sitemap.items() if u not in enviado or enviado[u] != lm)


def enviar(urls):
    corpo = json.dumps({"host": HOST, "key": CHAVE, "keyLocation": f"{SITE}/{CHAVE}.txt", "urlList": urls}).encode()
    req = urllib.request.Request(ENDPOINT, data=corpo, headers={**UA, "Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status
    except urllib.error.HTTPError as ex:
        return ex.code


def main():
    if not no_ar(f"{SITE}/{CHAVE}.txt"):
        sys.exit(f"A chave {CHAVE}.txt ainda não está no ar; nada foi enviado.")
    candidatas = pendentes("--tudo" in sys.argv)
    if not candidatas:
        print("IndexNow: nada novo para avisar.")
        return
    prontas = [u for u in candidatas if no_ar(u)]
    for u in sorted(set(candidatas) - set(prontas)):
        print("  ainda não está no ar, fica para a próxima:", u)
    if not prontas:
        return
    status = enviar(prontas)
    # 200 = recebido; 202 = recebido, chave ainda em validação. Qualquer outro código: não grava, tenta de novo depois.
    if status not in (200, 202):
        sys.exit(f"IndexNow recusou ({status}); nada foi gravado, a próxima rodada tenta de novo.")
    sitemap = lastmods()
    enviado = json.loads(ESTADO.read_text(encoding="utf-8")) if ESTADO.exists() else {}
    for u in prontas:
        enviado[u] = sitemap.get(u)
    enviado["_ultimo_envio"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    ESTADO.write_text(json.dumps(enviado, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"IndexNow: {len(prontas)} URL(s) avisada(s) (resposta {status}).")


if __name__ == "__main__":
    main()
