"""Instala (ou atualiza) o serviço de curtidas e comentários na Cloudflare e liga a seção nas páginas.

Uso: python3 tools/comentarios/instalar.py
Precisa de duas variáveis no ambiente (nunca no código nem no chat):
  CLOUDFLARE_API_TOKEN_COMENTARIOS  chave com Workers Scripts, D1 e Turnstile (editar) na conta e
                                    Workers Routes e DNS (editar) na zona PREENCHER_DOMINIO
  MODERACAO_SENHA                   senha do painel (24+ caracteres); sem ela, o instalador gera uma e a mostra uma vez
Passos (pode rodar de novo sem estragar nada): banco D1 + tabelas, verificador anti-robô (Turnstile),
publicação do worker em api.PREENCHER_DOMINIO, segredos, conteudo/interacoes.json e um teste no ar.
Depois: python3 tools/build_home.py para as páginas ganharem a seção.
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
WORKER = ROOT / "worker"
sys.path.insert(0, str(ROOT / "tools"))
from resumo_visitas import CONTA  # noqa: E402

API = "https://api.PREENCHER_DOMINIO"
WRANGLER = ["npx", "--yes", "wrangler@4.155.0"]


def cf(metodo, caminho, token, corpo=None):
    req = urllib.request.Request(f"https://api.cloudflare.com/client/v4/{caminho}", method=metodo,
                                 data=json.dumps(corpo).encode() if corpo is not None else None,
                                 headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def wrangler(*args, token, entrada=None):
    env = {**os.environ, "CLOUDFLARE_API_TOKEN": token, "CLOUDFLARE_ACCOUNT_ID": CONTA}
    r = subprocess.run(WRANGLER + list(args), cwd=WORKER, env=env, input=entrada, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"wrangler {' '.join(args)} falhou:\n{(r.stderr or r.stdout)[-1500:]}")
    return r.stdout


def main():
    token, senha = os.environ.get("CLOUDFLARE_API_TOKEN_COMENTARIOS"), os.environ.get("MODERACAO_SENHA")
    if not token:
        sys.exit("Falta CLOUDFLARE_API_TOKEN_COMENTARIOS no ambiente.")
    gerada = False
    if not senha:
        # sem senha cadastrada: gera uma forte e grava só na Cloudflare; o editor guarda depois como MODERACAO_SENHA
        import secrets
        senha, gerada = secrets.token_urlsafe(24), True
    elif len(senha) < 24:
        sys.exit("MODERACAO_SENHA precisa ter 24 caracteres ou mais.")

    # 1. banco D1 (reaproveita se já existir) e tabelas
    bancos = cf("GET", f"accounts/{CONTA}/d1/database?name=elite-interacoes", token)["result"]
    uuid = bancos[0]["uuid"] if bancos else cf("POST", f"accounts/{CONTA}/d1/database", token, {"name": "elite-interacoes"})["result"]["uuid"]
    toml = WORKER / "wrangler.toml"
    toml.write_text(re.sub(r'database_id = "[^"]*"', f'database_id = "{uuid}"', toml.read_text(encoding="utf-8")), encoding="utf-8")
    wrangler("d1", "execute", "elite-interacoes", "--remote", "--file", "schema.sql", "--yes", token=token)
    print("ok banco D1", uuid)

    # 2. verificador anti-robô (Turnstile), só para o domínio do site
    widgets = cf("GET", f"accounts/{CONTA}/challenges/widgets", token)["result"]
    w = next((x for x in widgets if x["name"] == "O Paladino comentários"), None)
    if not w:
        w = cf("POST", f"accounts/{CONTA}/challenges/widgets", token,
               {"name": "O Paladino comentários", "domains": ["PREENCHER_DOMINIO"], "mode": "managed"})["result"]
    detalhe = cf("GET", f"accounts/{CONTA}/challenges/widgets/{w['sitekey']}", token)["result"]
    print("ok Turnstile", w["sitekey"])

    # 3. publica o worker (o domínio api.PREENCHER_DOMINIO é criado pela própria Cloudflare) e grava os segredos
    wrangler("deploy", token=token)
    wrangler("secret", "put", "TURNSTILE_SECRET", token=token, entrada=detalhe["secret"])
    wrangler("secret", "put", "MODERACAO_TOKEN", token=token, entrada=senha)
    print("ok worker publicado em", API)

    # 4. liga a seção nas páginas
    (ROOT / "conteudo" / "interacoes.json").write_text(json.dumps({"api": API, "turnstile": w["sitekey"]}, indent=1) + "\n", encoding="utf-8")

    # 5. teste no ar (o certificado do domínio novo pode levar alguns minutos)
    for _ in range(20):
        try:
            # a Cloudflare barra o identificador padrão do Python (Python-urllib)
            teste = urllib.request.Request(f"{API}/v1/pagina?p=/root/", headers={"User-Agent": "PortalCristao-instalador/1.0"})
            with urllib.request.urlopen(teste, timeout=20) as r:
                print("ok serviço no ar:", r.read().decode()[:80])
                break
        except Exception as ex:  # noqa: BLE001
            ultimo = ex
            time.sleep(15)
    else:
        print("⚠️ o serviço ainda não respondeu (", ultimo, "). Espere alguns minutos e teste", f"{API}/v1/pagina?p=/root/")
    print("Painel de moderação:", f"{API}/painel")
    if gerada:
        print("SENHA GERADA (mostre ao editor uma vez; ele deve guardá-la como MODERACAO_SENHA nos segredos do ambiente):", senha)


if __name__ == "__main__":
    main()
