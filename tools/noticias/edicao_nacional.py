"""Procura sinais de edição nacional de um jogo antes de a notícia dizer que ela não existe.

Uso: python3 tools/noticias/edicao_nacional.py "Galactic Cruise" ["Outro Jogo" ...]
Consulta o ComparaJogos (comparador de lojas brasileiras) e lista as ofertas de jogo novo em lojas
nacionais. Sai com código 2 se algum jogo tem oferta: aí a notícia NÃO pode dizer que não há edição
nacional sem antes abrir a página da loja e conferir editora e idioma.

Não encontrar nada aqui não prova ausência: falta ainda a página do jogo na Ludopedia e a busca
estendida (ver "Edição nacional: verificação obrigatória" no PADRAO_EDITORIAL.md).
"""
import json
import re
import sys
import unicodedata
from urllib.parse import quote

import requests

BASE = "https://www.comparajogos.com.br"
MARKETPLACE = re.compile(r"amazon|mercado ?livre|shopee|magalu|americanas", re.I)
HEADERS = {"User-Agent": "PortalCristao/1.0 (+https://meruvash.github.io/Arcvalion_gospel)"}


def slug(nome):
    s = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def baixar(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    return r.text if r.status_code == 200 else ""


def produto(html, s):
    """Ficha do jogo `s` nos dados da página (existe mesmo quando não há oferta)."""
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        return None
    estado = json.loads(m.group(1))["props"]["pageProps"].get("__APOLLO_STATE__") or {}
    return next((v for k, v in estado.items() if k.startswith("product:") and v.get("slug") == s), None)


def achar_item(nome):
    """Endereço do jogo no ComparaJogos: tenta o slug direto e, se não houver, a busca do site."""
    direto = f"{BASE}/item/{slug(nome)}"
    if produto(baixar(direto), slug(nome)):
        return direto
    busca = baixar(f"{BASE}/all?q={quote(nome)}")
    alvo = slug(nome)
    for s in dict.fromkeys(re.findall(r"/item/([a-z0-9-]+)", busca)):
        if alvo in s or s in alvo:
            return f"{BASE}/item/{s}"
    return None


def ofertas(url):
    html = baixar(url)
    nome = (produto(html, url.rsplit("/", 1)[-1]) or {}).get("name")
    for bloco in re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S):
        d = json.loads(bloco)
        if d.get("@type") == "Product":
            lista = (d.get("offers") or {}).get("offers") or []
            return d.get("name"), [(o["seller"]["name"], float(o["price"])) for o in lista
                                   if o.get("itemCondition", "").endswith("NewCondition")]
    return nome, []


def main(nomes):
    alerta = False
    for nome in nomes:
        url = achar_item(nome)
        if not url:
            print(f"? {nome}: não está no ComparaJogos. Confira a Ludopedia e faça a busca estendida.")
            continue
        titulo, todas = ofertas(url)
        if slug(titulo or "") != slug(nome):
            print(f"  (atenção: pedi \"{nome}\" e o ComparaJogos devolveu \"{titulo}\"; confira se é o mesmo jogo)")
        # Amazon e marketplaces vendem muito importado: contam como pista, não como sinal de edição nacional.
        lojas = [o for o in todas if not MARKETPLACE.search(o[0])]
        importadas = [o for o in todas if MARKETPLACE.search(o[0])]
        if importadas and not lojas:
            desc = ", ".join(f"{loja} R$ {preco:.2f}".replace(".", ",") for loja, preco in importadas)
            print(f"~ {titulo}: só oferta em marketplace ({desc}), em geral importado.\n  {url}\n"
                  "  Confira o idioma no anúncio, a Ludopedia e a busca estendida.")
            continue
        if lojas:
            alerta = True
            desc = ", ".join(f"{loja} R$ {preco:.2f}".replace(".", ",") for loja, preco in lojas)
            print(f"! {titulo}: {len(lojas)} oferta(s) de jogo novo em lojas brasileiras ({desc}).\n"
                  f"  {url}\n  Abra a página de uma loja e confira editora e idioma: provavelmente há edição nacional.")
        else:
            print(f"· {titulo}: sem oferta de jogo novo em lojas brasileiras no ComparaJogos.\n  {url}\n"
                  "  Isso não prova ausência: confira a Ludopedia e faça a busca estendida.")
    return 2 if alerta else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1:]))
