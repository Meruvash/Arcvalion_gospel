"""Avisa Bing e outros buscadores do IndexNow quando uma página é publicada ou muda. Portado do Elite Boardgamers.

Uso: python3 tools/indexnow.py [--tudo]   (depois do deploy, quando o site já está no ar)
Compara o lastmod de cada URL do publico/sitemap.xml com o último aviso (conteudo/indexnow_estado.json) e só avisa o
que é novo ou mudou; confere antes se a página já responde 200. A chave (config/portal.json, indexnow_chave) é
pública por definição: o arquivo <chave>.txt na raiz do site prova que o aviso vem do dono do domínio.
"""
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import portal  # noqa: E402

ENDPOINT = "https://api.indexnow.org/indexnow"


def no_ar(url, ua):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=ua), timeout=30) as r:
            return r.status == 200
    except (urllib.error.URLError, TimeoutError):
        return False


def main(args):
    portal.iniciar()
    if portal.SITE.endswith(".example"):
        sys.exit("Domínio ainda provisório (.example): configure o domínio real em config/portal.json.")
    chave, host = portal.CFG["indexnow_chave"], portal.SITE.removeprefix("https://")
    ua = {"User-Agent": f"{portal.NOME.replace(' ', '')}-indexnow/1.0"}
    estado_arq = portal.ROOT / "conteudo" / "indexnow_estado.json"
    sitemap = {u: lm or None for u, lm in re.findall(r"<loc>([^<]+)</loc>(?:<lastmod>([^<]+)</lastmod>)?",
                                                     (portal.ROOT / "publico" / "sitemap.xml").read_text(encoding="utf-8"))}
    if not no_ar(f"{portal.SITE}/{chave}.txt", ua):
        sys.exit(f"A chave {chave}.txt ainda não está no ar; nada foi enviado.")
    enviado = {} if "--tudo" in args or not estado_arq.exists() else json.loads(estado_arq.read_text(encoding="utf-8"))
    pend = sorted(u for u, lm in sitemap.items() if enviado.get(u) != lm or u not in enviado)
    prontas = [u for u in pend if no_ar(u, ua)]
    if not prontas:
        print("IndexNow: nada novo para avisar.")
        return 0
    corpo = json.dumps({"host": host, "key": chave, "keyLocation": f"{portal.SITE}/{chave}.txt", "urlList": prontas}).encode()
    req = urllib.request.Request(ENDPOINT, data=corpo, headers={**ua, "Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            status = r.status
    except urllib.error.HTTPError as ex:
        status = ex.code
    if status not in (200, 202):
        sys.exit(f"IndexNow recusou ({status}); a próxima rodada tenta de novo.")
    for u in prontas:
        enviado[u] = sitemap[u]
    enviado["_ultimo_envio"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    estado_arq.write_text(json.dumps(enviado, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"IndexNow: {len(prontas)} URL(s) avisada(s) (resposta {status}).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
