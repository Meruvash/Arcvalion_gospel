"""Robô de imagens oficiais: capa, mesa montada, jogabilidade e componentes, direto dos sites das editoras.

Uso:
  python3 tools/imagens/robo.py mapear <dominio> [--nome "Editora"]   mapeia o site e grava a receita em editoras.json
  python3 tools/imagens/robo.py triagem <slug> --jogo "Nome" --editora "Editora original" [--nacional "Editora BR"]
                                       ficha mínima em triagem/<slug>.json para buscar fotos antes de escrever a resenha
  python3 tools/imagens/robo.py buscar <slug> [--url URL] [--editora DOMINIO]
                                       acha a página do jogo, baixa as candidatas e monta a folha de contato
  python3 tools/imagens/robo.py aprovar <slug> capa=3 mesa=5,7 jogabilidade=2 componentes=9 [--forcar] [--nota "2ª edição"]
                                       salva as escolhidas em <slug>/fotos/ e registra a origem em fontes.json
                                       (--nota vai no crédito embaixo da foto, ex.: edição diferente da resenhada)
  python3 tools/imagens/robo.py livres <slug> [...]   fotos de usuários com licença livre (categorias do Wikimedia
                                       Commons em livres.json), com autor e licença no crédito; somam-se às candidatas
  python3 tools/imagens/robo.py kit <slug> <zip ou link do zip> --nome "Editora"
                                       imagens de um kit de imprensa (link público ou arquivo baixado pelo usuário)
  python3 tools/imagens/robo.py imagem-noticia noticias/<arquivo-sem-.json> <n> [--nota "..."]
                                       grava a candidata n como imagem da notícia (noticias/capas/<slug>.jpg + campo imagem)
  python3 tools/imagens/robo.py lote [slug ...]   roda `buscar` nos jogos sem fotos e grava lotes/imagens-<data>.md

Boa conduta: confere o robots.txt (RFC 9309, com * e $) de cada host antes de cada pedido, respeita o Crawl-delay
(mínimo de 3 s), se identifica pelo User-Agent e para na hora em 401/403, sem tentar contornar o bloqueio.
Páginas e imagens ficam em .cache/imagens/, fora do git, então rodar de novo não baixa nada duas vezes.
Sites montados com JavaScript ("js": true na receita, marcado pelo `mapear`) abrem num Chromium sem janela
(navegador.js), que pergunta ao robô antes de cada pedido se o robots.txt permite.
"""
import hashlib
import io
import json
import re
import subprocess
import sys
import time
import unicodedata
import zipfile
from datetime import date
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
AQUI = Path(__file__).resolve().parent
RECEITAS = AQUI / "editoras.json"
CACHE = ROOT / ".cache" / "imagens"
UA = "GoldenGeekBot/1.0 (+https://meruvash.github.io/Arcvalion_gospel/)"
TOKEN_UA = "goldengeekbot"
DELAY_MIN = 3.0
CACHE_DIAS = 7
MAX_CANDIDATAS = 30
LADO_MIN = 800  # tamanho preferido; abaixo disso a foto entra marcada "pequena", não é descartada
LADO_PISO = 600  # resenha: abaixo disso a foto fica feia mesmo sem esticar; descartada
TIPOS = ("capa", "mesa", "jogabilidade", "componentes")
PISTAS = {
    "capa": r"box|cover|caixa|capa|schachtel|boite|packshot|3d|front|portada",
    "mesa": r"setup|set-up|table|mesa|tisch|overview|layout|tabletop|preparac|aufbau",
    "jogabilidade": r"gameplay|game-play|play|spiel(?!e?material)|partida|jogand|lifestyle|hand|jeu",
    "componentes": r"component|material|contents|componente|conteudo|cards|cartas|tiles|pecas|meeple|minis",
}
LIXO = r"logo|icon|sprite|flag|bandeira|payment|badge|avatar|banner|newsletter|placeholder|favicon|social|award|selo"
EXPANSAO = {"expansion", "erweiterung", "expansao", "extension", "promo", "sleeve", "sleeves", "insert", "playmat",
            "upgrade", "pack", "deluxe", "bundle", "kit", "acessorio", "accessories", "coin", "coins", "pin", "pins",
            "poster", "shirt", "tshirt", "mug", "plush", "sticker", "organizer", "dice", "portraits", "portrety",
            "calendar", "puzzle", "art", "book", "soundtrack", "neoprene", "storage"}


class Bloqueado(Exception):
    pass


# ---------- robots.txt (RFC 9309) ----------

class Robots:
    def __init__(self, texto, status):
        self.status = status
        self.regras = []
        self.delay = None
        self.sitemaps = []
        if status >= 500 or status == 0:
            self.regras = [(False, "/")]  # servidor fora do ar ou rede caída: não entra em nada (RFC 9309, 2.3.1.4)
            return
        if status >= 400:
            return  # robots.txt ausente (4xx, inclusive o 403 dos CDNs da S3): tudo liberado (RFC 9309, 2.3.1.3)
        grupos, atual, lendo_ua = [], None, False
        for linha in texto.splitlines():
            linha = linha.split("#", 1)[0].strip()
            if ":" not in linha:
                continue
            campo, valor = (p.strip() for p in linha.split(":", 1))
            campo = campo.lower()
            if campo == "sitemap":
                self.sitemaps.append(valor)
            elif campo == "user-agent":
                if not lendo_ua:
                    atual = {"uas": [], "regras": [], "delay": None}
                    grupos.append(atual)
                atual["uas"].append(valor.lower())
                lendo_ua = True
            elif atual is not None:
                lendo_ua = False
                if campo in ("allow", "disallow") and valor:
                    atual["regras"].append((campo == "allow", valor))
                elif campo == "crawl-delay":
                    try:
                        atual["delay"] = float(valor)
                    except ValueError:
                        pass
        meus = [g for g in grupos if any(u != "*" and u in TOKEN_UA for u in g["uas"])]
        meus = meus or [g for g in grupos if "*" in g["uas"]]
        for g in meus:
            self.regras += g["regras"]
            if g["delay"] is not None:
                self.delay = max(self.delay or 0, g["delay"])

    def pode(self, url):
        p = urlsplit(url)
        caminho = (p.path or "/") + (f"?{p.query}" if p.query else "")
        melhor = None
        for permite, padrao in self.regras:
            rx = "^" + re.escape(padrao).replace(r"\*", ".*")
            if rx.endswith(r"\$"):
                rx = rx[:-2] + "$"
            if re.match(rx, caminho):
                chave = (len(padrao), permite)  # regra mais longa vence; empate, Allow vence
                if melhor is None or chave > melhor[0]:
                    melhor = (chave, permite)
        return True if melhor is None else melhor[1]


# ---------- cliente HTTP educado ----------

class Cliente:
    def __init__(self):
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": UA, "Accept-Language": "pt-BR,en;q=0.8,de;q=0.6,fr;q=0.5"})
        self.robots = {}
        self.ultimo = {}
        self.pedidos = 0
        self.pausa = {}  # host -> horário até quando o servidor pediu para não voltar

    def _host(self, url):
        p = urlsplit(url)
        return f"{p.scheme}://{p.netloc}"

    def _robots(self, url):
        host = self._host(url)
        if host not in self.robots:
            status, texto = 0, ""
            for espera in (5, 15, None):  # falha de rede não é proibição: tenta de novo antes de desistir
                self._esperar(host, DELAY_MIN)
                try:
                    r = self.s.get(host + "/robots.txt", timeout=20)
                    status, texto = r.status_code, r.text
                    break
                except requests.RequestException:
                    if espera:
                        time.sleep(espera)
            self.robots[host] = Robots(texto, status)
        return self.robots[host]

    def _esperar(self, host, delay):
        falta = self.ultimo.get(host, 0) + delay - time.time()
        if falta > 0:
            time.sleep(falta)
        self.ultimo[host] = time.time()

    def pode(self, url):
        return self._robots(url).pode(url)

    def get(self, url, binario=False, usar_cache=True):
        """Devolve (url_final, conteúdo) ou levanta Bloqueado/LookupError. Nunca acessa o que o robots.txt proíbe."""
        chave = hashlib.sha1(url.encode()).hexdigest()
        corpo_f, meta_f = CACHE / "http" / f"{chave}.bin", CACHE / "http" / f"{chave}.json"
        meta = json.loads(meta_f.read_text()) if meta_f.exists() else None
        if usar_cache and meta and time.time() - meta["quando"] < CACHE_DIAS * 86400:
            return meta["url"], self._ler(corpo_f, binario)
        host = self._host(url)
        if self.pausa.get(host, 0) > time.time():
            raise LookupError(f"{host} pediu pausa até {time.strftime('%H:%M', time.localtime(self.pausa[host]))}; "
                              "rode de novo depois")
        rob = self._robots(url)
        if rob.status == 0:
            raise LookupError(f"robots.txt de {self._host(url)} inacessível (erro de rede); tente mais tarde")
        if not rob.pode(url):
            raise Bloqueado(f"robots.txt proíbe {url}")
        cab = {}
        if meta and meta.get("etag"):
            cab["If-None-Match"] = meta["etag"]
        if meta and meta.get("modificado"):
            cab["If-Modified-Since"] = meta["modificado"]
        for espera in (10, 30, 90, None):
            self._esperar(self._host(url), max(DELAY_MIN, rob.delay or 0))
            self.pedidos += 1
            try:
                r = self.s.get(url, headers=cab, timeout=30, allow_redirects=True)
            except requests.RequestException as e:
                if espera is None:
                    raise LookupError(f"{url}: {e}")
                time.sleep(espera)
                continue
            if r.history and not self.pode(r.url):
                raise Bloqueado(f"robots.txt proíbe o destino do redirecionamento {r.url}")
            if r.status_code == 304 and meta:
                meta["quando"] = time.time()
                meta_f.write_text(json.dumps(meta))
                return meta["url"], self._ler(corpo_f, binario)
            if r.status_code in (401, 403):
                raise Bloqueado(f"{r.status_code} em {url}")
            if r.status_code == 429 or r.status_code >= 500:
                pedida = r.headers.get("Retry-After", "")
                pedida = int(pedida) if pedida.isdigit() else espera
                if espera is None or pedida > 120:
                    # pausa longa: respeita sem travar o lote; o host fica de fora até o horário pedido
                    self.pausa[host] = time.time() + (pedida or 600)
                    raise LookupError(f"{r.status_code} em {url} (servidor pediu {pedida or 600} s de pausa)")
                time.sleep(pedida)
                continue
            if r.status_code >= 400:
                raise LookupError(f"{r.status_code} em {url}")
            corpo_f.parent.mkdir(parents=True, exist_ok=True)
            corpo_f.write_bytes(r.content)
            meta_f.write_text(json.dumps({"url": r.url, "quando": time.time(), "etag": r.headers.get("ETag"),
                                          "modificado": r.headers.get("Last-Modified"),
                                          "tipo": r.headers.get("Content-Type", "")}))
            return r.url, (r.content if binario else r.text)

    @staticmethod
    def _ler(f, binario):
        b = f.read_bytes()
        return b if binario else b.decode("utf-8", "replace")


# ---------- receitas por editora ----------

def receitas():
    return json.loads(RECEITAS.read_text(encoding="utf-8")) if RECEITAS.exists() else {}


def gravar_receitas(r):
    RECEITAS.write_text(json.dumps(r, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def mapear(cli, dominio, nome=None):
    """Descobre plataforma, robots, sitemaps e kit de imprensa. A IA revisa o resultado e ajusta a receita."""
    url = dominio if dominio.startswith("http") else f"https://{dominio}"
    rec = {"nome": nome or dominio, "apelidos": [nome] if nome else [], "site": url, "plataforma": "html",
           "estrategia": "sitemap+html", "press_kit": None, "paginas": {}, "status": "ok", "obs": ""}
    try:
        final, html = cli.get(url, usar_cache=False)
    except Bloqueado as e:
        rec.update(status="bloqueado", obs=str(e))
        return rec
    except LookupError as e:
        rec.update(status="erro", obs=str(e))
        return rec
    host = cli._host(final)
    rec["site"] = host
    rob = cli._robots(host)
    rec["robots"] = {"status": rob.status, "crawl_delay": rob.delay, "sitemaps": rob.sitemaps,
                     "verificado_em": date.today().isoformat()}
    if "cdn.shopify.com" in html or "Shopify.theme" in html:
        rec.update(plataforma="shopify", estrategia="sitemap+shopify_json")
    elif "wp-content" in html or "wp-json" in html:
        rec["plataforma"] = "woocommerce" if "woocommerce" in html else "wordpress"
    if len(BeautifulSoup(html, "lxml").get_text(" ", strip=True)) < 300 and "<script" in html:
        rec.update(js=True, obs="site montado com JavaScript: o robô abre as páginas no navegador")
        html = renderizar(cli, final)
    soup = BeautifulSoup(html, "lxml")
    for a in soup.find_all("a", href=True):
        txt = (a.get_text(" ", strip=True) + " " + a["href"]).lower()
        if re.search(r"\b(press|presse|media|imprensa|prensa|medien|retailer|downloads?)\b", txt):
            rec["press_kit"] = urljoin(host + "/", a["href"])
            break
    return rec


def receitas_por_nome(texto):
    """Acha as receitas pelo nome da editora como aparece na ficha ("Flatout Games (com AEG)" dá duas)."""
    t = normalizar(texto or "")
    achadas = []
    for dominio, rec in receitas().items():
        for apelido in [rec["nome"], *rec.get("apelidos", [])]:
            a = normalizar(apelido)
            if a and re.search(rf"(^| ){re.escape(a)}( |$)", t):
                achadas.append((t.index(a), dominio, rec))
                break
    return [(d, r) for _, d, r in sorted(achadas, key=lambda x: x[0])]


# ---------- achar a página do jogo ----------

def normalizar(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return " ".join(re.findall(r"[a-z0-9]+", s))


def tokens(s):
    return [t for t in normalizar(s).split() if t not in {"the", "a", "o", "os", "as", "de", "do", "da", "der", "die",
                                                           "das", "le", "la", "les", "of", "em", "e", "and", "und"}]


def ler_sitemaps(cli, rec, limite=40):
    """Lista (url, [(img, título)]) de todos os sitemaps do site, priorizando os de produtos."""
    fila = list(rec.get("robots", {}).get("sitemaps") or [])
    if not fila:
        fila = [rec["site"] + p for p in ("/sitemap.xml", "/sitemap_index.xml", "/wp-sitemap.xml")]
    vistos, urls = set(), {}
    while fila and len(vistos) < limite:
        sm = fila.pop(0)
        if sm in vistos:
            continue
        vistos.add(sm)
        try:
            _, xml = cli.get(sm)
        except (Bloqueado, LookupError):
            continue
        soup = BeautifulSoup(xml, "xml")
        filhos = [l.get_text(strip=True) for s in soup.find_all("sitemap") for l in s.find_all("loc")]
        filhos.sort(key=lambda u: 0 if re.search(r"product|produto|jogo|game|spiel|jeu|shop", u) else 1)
        fila = filhos + fila
        for u in soup.find_all("url"):
            loc = u.find("loc")
            if loc:
                imgs = [(i.find("loc").get_text(strip=True), (i.find("title") or i.find("caption") or loc).get_text(strip=True))
                        for i in u.find_all("image") if i.find("loc")]
                urls[loc.get_text(strip=True)] = imgs
    return urls


def achar_paginas(cli, rec, nomes):
    """Ranqueia URLs do sitemap pelo nome do jogo; edições e expansões perdem pontos."""
    urls = ler_sitemaps(cli, rec)
    res = []
    for url, imgs in urls.items():
        caminho = urlsplit(url).path.rstrip("/")
        ult = tokens(caminho.rsplit("/", 1)[-1])
        if not ult:
            continue
        for nome in nomes:
            alvo = tokens(nome)
            if alvo and all(t in ult for t in alvo):
                extras = [t for t in ult if t not in alvo and not t.isdigit()]
                nota = 1 - 0.08 * len(extras) - 0.5 * len(EXPANSAO & set(extras)) - 0.02 * caminho.count("/")
                nota += 0.1 if re.search(r"/(products?|produtos?|jogos?|games?|spiele|jeux)/", caminho) else 0
                res.append((round(nota, 2), url, imgs))
                break
    res.sort(key=lambda x: -x[0])
    return res[:5]


def nomes_do_jogo(c):
    nomes = [c["jogo"]]
    if ":" in c["jogo"]:
        nomes.append(c["jogo"].split(":")[0])
    fi = dict(c.get("ficha", []))
    for campo in ("Editora no Brasil",):
        for m in re.findall(r"\(([^)]*[A-Za-zÀ-ú][^)]*)\)", fi.get(campo) or ""):
            if not re.search(r"\d{4}|edi[cç]", m):
                nomes.append(m)
    m = re.search(r"publica(?:m|do)? o jogo como ([^,.]+)", c.get("edicao_nacional") or "")
    if m:
        nomes.append(m.group(1))
    return list(dict.fromkeys(n.strip() for n in nomes if n.strip()))


# ---------- sites montados com JavaScript ----------

def renderizar(cli, url):
    """Abre a página num Chromium sem janela e devolve o HTML já montado pelo JavaScript.

    Mesmas regras do cliente: confere o robots.txt da página e de cada script ou chamada que o navegador fizer
    (o que for proibido é cancelado), se identifica com o mesmo User-Agent e não baixa imagens, fontes nem CSS
    (as imagens vêm depois pelo cliente educado, com pausa entre pedidos).
    """
    chave = hashlib.sha1(("js:" + url).encode()).hexdigest()
    corpo_f = CACHE / "http" / f"{chave}.html"
    if corpo_f.exists() and time.time() - corpo_f.stat().st_mtime < CACHE_DIAS * 86400:
        return corpo_f.read_text(encoding="utf-8")
    if not cli.pode(url):
        raise Bloqueado(f"robots.txt proíbe {url}")
    cli._esperar(cli._host(url), max(DELAY_MIN, cli._robots(url).delay or 0))
    cli.pedidos += 1
    proc = subprocess.Popen(["node", str(AQUI / "navegador.js"), url, UA], stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, text=True, cwd=ROOT)
    cancelados, fim = [], None
    try:
        for linha in proc.stdout:
            msg = json.loads(linha)
            if "id" in msg:  # o navegador pergunta se pode pedir esta URL
                try:
                    ok = cli.pode(msg["url"])
                except Exception:
                    ok = False
                if not ok:
                    cancelados.append(msg["url"])
                proc.stdin.write(f"{msg['id']} {1 if ok else 0}\n")
                proc.stdin.flush()
            else:
                fim = msg
                break
    finally:
        proc.kill()
    if not fim or fim["status"] == 0:
        raise LookupError(f"navegador não abriu {url}: {(fim or {}).get('erro', 'sem resposta')}")
    if fim["status"] in (401, 403):
        raise Bloqueado(f"{fim['status']} em {url}")
    if fim["status"] >= 400:
        raise LookupError(f"{fim['status']} em {url}")
    html = fim["html"]
    if cancelados:
        print(f"navegador: {len(cancelados)} pedidos cancelados pelo robots.txt", file=sys.stderr)
    corpo_f.parent.mkdir(parents=True, exist_ok=True)
    corpo_f.write_text(html, encoding="utf-8")
    return html


# ---------- extrair imagens de uma página ----------

def original(url):
    """Pede a maior versão da imagem: tira sufixos de miniatura do Shopify e do WordPress."""
    p = urlsplit(url)
    caminho = re.sub(r"_(\d+x\d*|\d*x\d+|small|medium|large|grande|compact|thumb)(?=(@\dx)?\.\w+$)", "", p.path)
    caminho = re.sub(r"-\d{2,4}x\d{2,4}(?=\.\w+$)", "", caminho)
    query = "&".join(q for q in p.query.split("&") if q and not re.match(r"(width|height|w|h|crop|v)=", q))
    return urlunsplit((p.scheme, p.netloc, caminho, query, ""))


def imagens_da_pagina(cli, url, rec):
    achadas = []  # (url, alt)

    def add(u, alt=""):
        if u and not u.startswith("data:"):
            u = urljoin(url, u.strip())
            if re.search(r"\.(jpe?g|png|webp)(\?|$)", u, re.I) or "/cdn/shop/" in u or "cdn.shopify.com" in u:
                achadas.append((original(u), alt))

    if rec.get("plataforma") == "shopify" and "/products/" in url:
        try:
            _, js = cli.get(url.split("?")[0].rstrip("/") + ".json")
            for im in json.loads(js)["product"]["images"]:
                add(im["src"], im.get("alt") or "")
        except (Bloqueado, LookupError, ValueError, KeyError):
            pass
    html = renderizar(cli, url) if rec.get("js") else cli.get(url)[1]
    soup = BeautifulSoup(html, "lxml")
    titulo = soup.title.get_text(strip=True) if soup.title else ""
    for m in soup.find_all("meta", attrs={"property": re.compile("og:image")}) + \
            soup.find_all("meta", attrs={"name": re.compile("twitter:image")}):
        add(m.get("content"), titulo)
    for s in soup.find_all("script", type="application/ld+json"):
        for u in re.findall(r'"image"\s*:\s*\[?\s*"([^"]+)"', s.string or ""):
            add(u, titulo)
    for el in soup.find_all(["img", "source", "a"]):
        alt = el.get("alt") or el.get("title") or el.get_text(" ", strip=True)[:80]
        for attr in ("data-large_image", "data-zoom-image", "data-src", "data-original", "src"):
            if el.get(attr):
                add(el[attr], alt)
                break
        for attr in ("srcset", "data-srcset"):
            if el.get(attr):
                maior = max(el[attr].split(","), key=lambda x: int(re.sub(r"\D", "", x.strip().split(" ")[-1]) or 0))
                add(maior.strip().split(" ")[0], alt)
        if el.name == "a":
            add(el.get("href"), alt)
    vistos, res = set(), []
    for u, alt in achadas:
        if u not in vistos and not re.search(LIXO, u.rsplit("/", 1)[-1], re.I):
            vistos.add(u)
            res.append({"url": u, "alt": alt, "pagina": url})
    return res


# ---------- baixar, filtrar e classificar ----------

def dhash(im):
    g = im.convert("L").resize((9, 8), Image.LANCZOS)
    px = list(g.tobytes())
    return sum(1 << i for i in range(64) if px[(i // 8) * 9 + i % 8] > px[(i // 8) * 9 + i % 8 + 1])


def palpite(c):
    texto = normalizar(c["url"].rsplit("/", 1)[-1] + " " + c.get("alt", "")).replace(" ", "-")
    for tipo in TIPOS:
        if re.search(PISTAS[tipo], texto):
            return tipo
    w, h = c["w"], c["h"]
    return "capa" if c.get("fundo_liso") and 0.75 < w / h < 1.35 else "?"


def baixar_candidatas(cli, candidatas, pasta, lado_min=LADO_MIN, piso=LADO_PISO):
    pasta.mkdir(parents=True, exist_ok=True)
    boas, hashes, avisos = [], [], []
    for c in candidatas[:MAX_CANDIDATAS]:
        try:
            dados = c.pop("_dados", None) or cli.get(c["url"], binario=True)[1]
            im = Image.open(io.BytesIO(dados))
            im.load()
        except Bloqueado as e:
            avisos.append(str(e))
            continue
        except (LookupError, OSError) as e:
            avisos.append(f"não baixou {c['url']}: {e}")
            continue
        w, h = im.size
        # resenha: foto entre o piso e o ideal fica na folha, marcada, para não travar a produção (último recurso)
        if min(w, h) < piso or max(w, h) / min(w, h) > 3:
            continue
        hsh = dhash(im)
        dup = next((b for b, hb in zip(boas, hashes) if bin(hb ^ hsh).count("1") <= 6), None)
        if dup:
            if w * h <= dup["w"] * dup["h"]:
                continue
            i = boas.index(dup)
            boas.pop(i)
            hashes.pop(i)
        rgb = im.convert("RGBA") if im.mode in ("RGBA", "LA", "P") else im.convert("RGB")
        cantos = [rgb.getpixel(p) for p in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))]
        c.update(w=w, h=h, bytes=len(dados), pequena=min(w, h) < lado_min, fundo_liso=all(
            (len(px) == 4 and px[3] < 20) or min(px[:3]) > 235 for px in cantos))
        arq = pasta / f"{hashlib.sha1(c['url'].encode()).hexdigest()[:12]}.{(im.format or 'jpg').lower()}"
        arq.write_bytes(dados)
        c["arquivo"] = str(arq.relative_to(ROOT))
        c["palpite"] = palpite(c)
        boas.append(c)
        hashes.append(hsh)
    return boas, avisos


def folha_de_contato(cands, destino):
    """Grade numerada para a revisão visual (a IA escolhe capa, mesa, jogabilidade e componentes por aqui)."""
    lado, cols = 320, 4
    linhas = max(1, -(-len(cands) // cols))
    folha = Image.new("RGB", (cols * lado, linhas * (lado + 34)), "white")
    d = ImageDraw.Draw(folha)
    try:
        fonte = ImageFont.load_default(size=18)
    except TypeError:
        fonte = ImageFont.load_default()
    for i, c in enumerate(cands):
        im = Image.open(ROOT / c["arquivo"]).convert("RGB")
        im.thumbnail((lado - 8, lado - 8))
        x, y = (i % cols) * lado, (i // cols) * (lado + 34)
        folha.paste(im, (x + (lado - im.width) // 2, y + 4 + (lado - 8 - im.height) // 2))
        d.text((x + 6, y + lado + 4), f"#{c['n']} {c['w']}x{c['h']} {c['palpite']}{' pequena' if c.get('pequena') else ''}", fill="black", font=fonte)
    folha.save(destino, quality=82)


# ---------- fotos de usuários com licença livre (Wikimedia Commons) ----------

LIVRES = AQUI / "livres.json"
LICENCAS_OK = r"^(CC0|CC BY(-SA)? [\d.]+|Public domain|PD)"


def commons(cli, slug):
    """Fotos de usuários das categorias do jogo no Commons (lista em livres.json), com autor e licença de cada uma."""
    cats = json.loads(LIVRES.read_text(encoding="utf-8")).get(slug, []) if LIVRES.exists() else []
    res, avisos = [], []
    for cat in cats:
        url = "https://commons.wikimedia.org/wiki/Category:" + cat.replace(" ", "_")
        try:
            _, html = cli.get(url)
        except (Bloqueado, LookupError) as e:
            avisos.append(str(e))
            continue
        soup = BeautifulSoup(html, "lxml")
        arquivos = list(dict.fromkeys(urljoin(url, a["href"]) for a in soup.select("li.gallerybox a.mw-file-description")))
        for pg in arquivos[:MAX_CANDIDATAS]:
            try:
                _, h = cli.get(pg)
            except (Bloqueado, LookupError) as e:
                avisos.append(str(e))
                continue
            fs = BeautifulSoup(h, "lxml")
            link = fs.select_one(".fullMedia a.internal") or fs.select_one(".fullImageLink a")
            lic = [x.get_text(strip=True) for x in fs.select(".licensetpl_short")]
            lic = next((l for l in lic if re.match(LICENCAS_OK, l)), None)
            aut = fs.select_one("#fileinfotpl_aut")
            autor = aut.find_next_sibling("td").get_text(" ", strip=True) if aut and aut.find_next_sibling("td") else ""
            autor = re.sub(r"\s+", " ", autor)[:80] or "autor no Wikimedia Commons"
            if not link or not lic:
                avisos.append(f"sem licença livre clara: {pg}")
                continue
            titulo = pg.rsplit("File:", 1)[-1]
            res.append({"url": urljoin(pg, link["href"]), "alt": titulo, "pagina": pg, "editora": autor,
                        "dominio": "commons.wikimedia.org", "licenca": lic,
                        "credito": f"Foto: {autor} · {lic} · Wikimedia Commons"})
    return res, avisos


def kit(cli, origem, editora):
    """Imagens de um kit de imprensa em ZIP: link público (respeitando o robots.txt) ou arquivo que o usuário baixou."""
    local = Path(origem).expanduser()
    dados = local.read_bytes() if local.exists() else cli.get(origem, binario=True)[1]
    pagina = origem if not local.exists() else f"kit de imprensa ({local.name})"
    z = zipfile.ZipFile(io.BytesIO(dados))
    res = []
    for nome in z.namelist():
        base = nome.rsplit("/", 1)[-1]
        if base.startswith(("._", ".")) or not re.search(r"\.(jpe?g|png|webp|tiff?)$", base, re.I):
            continue  # pula lixo do macOS e o que não é imagem
        res.append({"url": f"{pagina}#{base}", "alt": base, "pagina": pagina, "editora": editora,
                    "credito": f"Imagem: {editora}" + ("" if local.exists() else " (kit de imprensa)"),
                    "_dados": z.read(nome)})
    return res


def juntar_candidatas(slug, novas):
    """Acrescenta candidatas às que já existem (numeração continua) e refaz a folha de contato."""
    pasta = CACHE / slug
    f = pasta / "candidatas.json"
    velhas = json.loads(f.read_text(encoding="utf-8")) if f.exists() else []
    urls = {c["url"] for c in velhas}
    n = max((c["n"] for c in velhas), default=0)
    for c in novas:
        if c["url"] not in urls:
            n += 1
            c["n"] = n
            velhas.append(c)
    pasta.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(velhas, ensure_ascii=False, indent=1), encoding="utf-8")
    if velhas:
        folha_de_contato(velhas, pasta / "folha.jpg")
    return velhas


# ---------- comandos ----------

def conteudo(slug):
    f = ROOT / "conteudo" / f"{slug}.json"
    if not f.exists():  # triagem de fotos: o jogo ainda não tem resenha, só nome e editoras
        f = ROOT / "triagem" / f"{slug}.json"
    if not f.exists():
        sys.exit(f"Não achei conteudo/{slug}.json nem triagem/{slug}.json (crie com `triagem`)")
    return json.loads(f.read_text(encoding="utf-8"))


def triagem(slug, jogo, editora, nacional=None):
    """Ficha mínima para buscar fotos antes de escrever a resenha (etapa 1 da skill resenha)."""
    ficha = [["Editora original", editora]] + ([["Editora no Brasil", nacional]] if nacional else [])
    f = ROOT / "triagem" / f"{slug}.json"
    f.parent.mkdir(exist_ok=True)
    f.write_text(json.dumps({"slug": slug, "jogo": jogo, "ficha": ficha}, ensure_ascii=False, indent=1) + "\n",
                 encoding="utf-8")
    return f


def paginas_oficiais(c, todas):
    """Links das fontes de uma notícia que são páginas de editoras mapeadas (o anúncio traz a imagem de divulgação)."""
    urls = [f if isinstance(f, str) else f.get("url", "") if isinstance(f, dict) else (f[1] if len(f) > 1 else "")
            for f in c.get("fontes", [])]
    achadas = []
    for u in urls:
        host = urlsplit(u).netloc.removeprefix("www.")
        dom = next((d for d in todas if host == d or host.endswith("." + d) or urlsplit(todas[d]["site"]).netloc.removeprefix("www.") == host), None)
        if dom:
            achadas.append((dom, u))
    return achadas


def buscar(cli, slug, url_fixa=None, so_editora=None):
    c = conteudo(slug)
    fi = dict(c.get("ficha", []))
    if c.get("editora") and not fi.get("Editora original"):  # notícia: editora num campo próprio, sem ficha
        fi["Editora original"] = c["editora"]
    # Notícia: `jogos` lista resenhas nossas relacionadas, não o assunto da nota; a busca usa só as fontes oficiais.
    nomes = []
    c.setdefault("jogo", c.get("titulo", slug))
    if c.get("ficha") or c.get("editora"):
        nomes = nomes_do_jogo(c) + nomes
    nomes = [n for n in dict.fromkeys(nomes) if n]
    todas = receitas()
    fontes = []
    for campo in ("Editora original", "Editora no Brasil"):
        for dominio, rec in receitas_por_nome(fi.get(campo)):
            if not so_editora or so_editora == dominio:
                fontes.append((campo, dominio, rec))
    for dominio, rec in todas.items():  # página fixada na receita vale mesmo sem a editora na ficha
        if slug in rec.get("paginas", {}) and dominio not in [d for _, d, _ in fontes]:
            if not so_editora or so_editora == dominio:
                fontes.append(("Página fixada", dominio, rec))
    if so_editora and not fontes and so_editora in todas:
        fontes.append(("Editora", so_editora, todas[so_editora]))
    rel = {"slug": slug, "jogo": c["jogo"], "nomes": nomes, "editoras": [], "candidatas": 0, "avisos": []}
    if not fontes and not url_fixa:
        rel["avisos"].append(f"sem receita para {fi.get('Editora original')!r} nem {fi.get('Editora no Brasil')!r}: "
                             "rode `mapear` no site da editora")
    candidatas = []
    for campo, dominio, rec in fontes:
        info = {"editora": rec["nome"], "dominio": dominio, "campo": campo, "paginas": []}
        rel["editoras"].append(info)
        if rec["status"] != "ok":
            info["status"] = rec["status"]
            continue
        paginas = [rec["paginas"][slug]] if slug in rec.get("paginas", {}) else []
        if not paginas:
            try:
                achadas = achar_paginas(cli, rec, nomes)
            except Bloqueado as e:
                info["status"] = f"bloqueado: {e}"
                continue
            topo = achadas[0][0] if achadas else 0
            paginas = [u for nota, u, _ in achadas if nota >= 0.7 and nota >= topo - 0.1][:2]
            info["ranking"] = [(nota, u) for nota, u, _ in achadas]
        for pg in paginas:
            try:
                ims = imagens_da_pagina(cli, pg, rec)
            except (Bloqueado, LookupError) as e:
                rel["avisos"].append(str(e))
                continue
            info["paginas"].append(pg)
            for im in ims:
                im.update(editora=rec["nome"], dominio=dominio)
            candidatas += ims
    for dominio, pg in ([] if url_fixa else paginas_oficiais(c, todas)):
        if so_editora and so_editora != dominio:
            continue
        rec = todas[dominio]
        try:
            ims = imagens_da_pagina(cli, pg, rec)
        except (Bloqueado, LookupError) as e:
            rel["avisos"].append(str(e))
            continue
        rel["editoras"].append({"editora": rec["nome"], "dominio": dominio, "campo": "Fonte da notícia", "paginas": [pg]})
        for im in ims:
            im.update(editora=rec["nome"], dominio=dominio)
        candidatas += ims
    if url_fixa:
        dominio = urlsplit(url_fixa).netloc.removeprefix("www.")
        rec = todas.get(dominio) or {"nome": dominio, "plataforma": "html"}
        for im in imagens_da_pagina(cli, url_fixa, rec):
            im.update(editora=rec["nome"], dominio=dominio)
            candidatas.append(im)
    pasta = CACHE / slug
    # notícia usa a imagem menor (destaque, miniatura e prévia do WhatsApp): 500 px no lado menor é o mínimo firme,
    # notícia sem foto boa não é publicada (procure em outras fontes ou troque de notícia). Resenha: 800 px ideal, 600 px como último recurso ("pequena").
    noticia = slug.startswith("noticias/")
    boas, avisos = baixar_candidatas(cli, candidatas, pasta / "candidatas", 500 if noticia else LADO_MIN, 500 if noticia else LADO_PISO)
    rel["avisos"] += avisos
    ordem = {"capa": 0, "mesa": 1, "jogabilidade": 2, "componentes": 3, "?": 4}
    boas.sort(key=lambda b: (b["pequena"], ordem[b["palpite"]], -b["w"] * b["h"]))
    for n, b in enumerate(boas, 1):
        b["n"] = n
    (pasta / "candidatas.json").write_text(json.dumps(boas, ensure_ascii=False, indent=1), encoding="utf-8")
    if boas:
        folha_de_contato(boas, pasta / "folha.jpg")
    rel["candidatas"] = len(boas)
    rel["folha"] = str((pasta / "folha.jpg").relative_to(ROOT)) if boas else None
    return rel


def aprovar(slug, escolhas, forcar=False, nota=None):
    cands = {c["n"]: c for c in json.loads((CACHE / slug / "candidatas.json").read_text(encoding="utf-8"))}
    pasta = ROOT / slug / "fotos"
    pasta.mkdir(parents=True, exist_ok=True)
    reg_f = pasta / "fontes.json"
    reg = json.loads(reg_f.read_text(encoding="utf-8")) if reg_f.exists() else {"slug": slug, "fotos": []}
    for tipo, nums in escolhas.items():
        ja = [f for f in reg["fotos"] if f["tipo"] == tipo]
        if ja and not forcar:
            print(f"{tipo}: já aprovada ({', '.join(f['arquivo'] for f in ja)}); use --forcar para trocar")
            continue
        reg["fotos"] = [f for f in reg["fotos"] if f["tipo"] != tipo]
        for velho in pasta.glob(f"{tipo}-*.webp"):
            velho.unlink()
        for i, n in enumerate(nums, 1):
            c = cands[n]
            im = Image.open(ROOT / c["arquivo"])
            im = im.convert("RGBA") if im.mode in ("RGBA", "LA", "P") else im.convert("RGB")
            if im.mode == "RGBA" and tipo != "capa":
                # Recorte com fundo transparente vira serrilhado escuro no tema da página: achata no branco.
                fundo = Image.new("RGB", im.size, "white")
                fundo.paste(im, mask=im.split()[3])
                im = fundo
            im.thumbnail((1600, 1600), Image.LANCZOS)
            nome = f"{tipo}-{i}.webp"
            for q in range(86, 55, -6):
                im.save(pasta / nome, quality=q, method=6)
                if (pasta / nome).stat().st_size <= 400_000:
                    break
            reg["fotos"].append({"arquivo": f"fotos/{nome}", "tipo": tipo, "largura": im.width, "altura": im.height,
                                 "editora": c["editora"], "credito": (c.get("credito") or f"Imagem: {c['editora']}") + (f" · {nota}" if nota else ""),
                                 **({"licenca": c["licenca"]} if c.get("licenca") else {}), "pagina": c["pagina"],
                                 "imagem": c["url"], "baixada_em": date.today().isoformat(), "aprovada": True})
            print(f"{slug}/fotos/{nome}  {im.width}x{im.height}  {(pasta / nome).stat().st_size // 1024} KB")
    reg["fotos"].sort(key=lambda f: (TIPOS.index(f["tipo"]), f["arquivo"]))
    reg_f.write_text(json.dumps(reg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def imagem_noticia(slug, n, nota=None):
    """Grava a candidata n como imagem da notícia (noticias/capas/<slug>.jpg) e preenche o campo `imagem` do JSON."""
    arq_json = ROOT / "conteudo" / f"{slug}.json"
    c = json.loads(arq_json.read_text(encoding="utf-8"))
    cand = {x["n"]: x for x in json.loads((CACHE / slug / "candidatas.json").read_text(encoding="utf-8"))}[n]
    im = Image.open(ROOT / cand["arquivo"])
    if im.mode in ("RGBA", "LA", "P"):  # fundo transparente vira branco no JPG
        im = im.convert("RGBA")
        fundo = Image.new("RGB", im.size, "white")
        fundo.paste(im, mask=im.split()[-1])
        im = fundo
    im = im.convert("RGB")
    im.thumbnail((1200, 1200), Image.LANCZOS)
    destino = ROOT / "noticias" / "capas" / f"{c['slug']}.jpg"
    destino.parent.mkdir(parents=True, exist_ok=True)
    for q in range(85, 55, -5):
        im.save(destino, quality=q, optimize=True, progressive=True)
        if destino.stat().st_size <= 250_000:
            break
    credito = (cand.get("credito") or f"Imagem: {cand['editora']}") + (f" · {nota}" if nota else "")
    c["imagem"] = {"arquivo": f"capas/{c['slug']}.jpg", "credito": credito, "origem": cand["url"], "pagina": cand["pagina"]}
    arq_json.write_text(json.dumps(c, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"noticias/capas/{c['slug']}.jpg  {im.width}x{im.height}  {destino.stat().st_size // 1024} KB  {credito}")


def email_pedido(editora, jogo):
    return (f"Assunto: Pedido de kit de imprensa – {jogo}\n\n"
            f"Olá, equipe {editora},\n\n"
            f"Escrevo pelo Golden Geek (https://meruvash.github.io/Arcvalion_gospel/), um site brasileiro de resenhas de "
            f"jogos de tabuleiro premiados. Estamos preparando a resenha de {jogo} e gostaríamos de usar imagens "
            f"oficiais (capa, jogo montado na mesa e componentes), sempre com crédito à editora e link para o site de "
            f"vocês.\n\nVocês têm um kit de imprensa ou podem nos autorizar a usar as imagens do site?\n\nObrigado!\n")


def relatorio(rels, cli):
    linhas = [f"# Imagens oficiais – {date.today().isoformat()}", "",
              f"{cli.pedidos} pedidos HTTP (o resto veio do cache).", ""]
    for r in rels:
        sit = "✅" if r["candidatas"] >= 3 else "⚠️" if r["candidatas"] else "⛔"
        linhas.append(f"## {sit} {r['jogo']} (`{r['slug']}`): {r['candidatas']} candidatas")
        if r.get("folha"):
            linhas.append(f"- Folha de contato: `{r['folha']}`")
        for e in r["editoras"]:
            linhas.append(f"- {e['editora']} ({e['campo']}): " + (", ".join(e["paginas"]) or e.get("status") or
                                                                    "página do jogo não encontrada no sitemap"))
            if "bloque" in str(e.get("status", "")):
                linhas += ["", "```", email_pedido(e["editora"], r["jogo"]), "```"]
        linhas += [f"- ⚠️ {a}" for a in r["avisos"]] + [""]
    f = ROOT / "lotes" / f"imagens-{date.today().isoformat()}.md"
    n = 2
    while f.exists():  # um lote não apaga o relatório de outro do mesmo dia
        f = ROOT / "lotes" / f"imagens-{date.today().isoformat()}-{n}.md"
        n += 1
    f.write_text("\n".join(linhas), encoding="utf-8")
    return f


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    cmd, resto = args[0], args[1:]
    opc = {}
    for flag in ("--nome", "--url", "--editora", "--nota", "--jogo", "--nacional"):
        if flag in resto:
            i = resto.index(flag)
            opc[flag] = resto[i + 1]
            del resto[i:i + 2]
    forcar = "--forcar" in resto
    resto = [a for a in resto if a != "--forcar"]
    cli = Cliente()
    if cmd == "mapear":
        todas = receitas()
        for dominio in resto:
            chave = dominio.removeprefix("https://").removeprefix("http://").removeprefix("www.").rstrip("/")
            rec = mapear(cli, dominio, opc.get("--nome"))
            antigo = todas.get(chave, {})
            rec["paginas"] = antigo.get("paginas", {})
            rec["apelidos"] = list(dict.fromkeys(antigo.get("apelidos", []) + rec["apelidos"]))
            if antigo.get("nome") and not opc.get("--nome"):
                rec["nome"] = antigo["nome"]
            todas[chave] = rec
            print(json.dumps({chave: rec}, ensure_ascii=False, indent=1))
        gravar_receitas(todas)
    elif cmd == "triagem":
        if not (opc.get("--jogo") and opc.get("--editora")):
            sys.exit('Uso: triagem <slug> --jogo "Nome" --editora "Editora original" [--nacional "Editora no Brasil"]')
        print(triagem(resto[0], opc["--jogo"], opc["--editora"], opc.get("--nacional")).relative_to(ROOT))
    elif cmd == "buscar":
        rel = buscar(cli, resto[0], opc.get("--url"), opc.get("--editora"))
        print(json.dumps(rel, ensure_ascii=False, indent=1))
    elif cmd == "livres":
        for slug in resto:
            achadas, avisos = commons(cli, slug)
            boas, av2 = baixar_candidatas(cli, achadas, CACHE / slug / "candidatas")
            todas = juntar_candidatas(slug, boas)
            print(f"{slug}: {len(boas)} fotos livres novas ({len(todas)} candidatas no total); folha em "
                  f"{(CACHE / slug / 'folha.jpg').relative_to(ROOT)}")
            for a in (avisos + av2)[:5]:
                print("  ⚠️", a)
    elif cmd == "imagem-noticia":
        imagem_noticia(resto[0], int(resto[1]), opc.get("--nota"))
    elif cmd == "kit":
        if not opc.get("--nome"):
            sys.exit('Informe a editora: kit <slug> <zip ou link> --nome "Editora"')
        boas, avisos = baixar_candidatas(cli, kit(cli, resto[1], opc["--nome"]), CACHE / resto[0] / "candidatas")
        todas = juntar_candidatas(resto[0], boas)
        print(f"{resto[0]}: {len(boas)} imagens do kit ({len(todas)} candidatas no total); folha em "
              f"{(CACHE / resto[0] / 'folha.jpg').relative_to(ROOT)}")
    elif cmd == "aprovar":
        escolhas = {}
        for a in resto[1:]:
            tipo, nums = a.split("=")
            if tipo not in TIPOS:
                sys.exit(f"Tipo inválido: {tipo} (use {', '.join(TIPOS)})")
            escolhas[tipo] = [int(n) for n in nums.split(",")]
        aprovar(resto[0], escolhas, forcar, opc.get("--nota"))
    elif cmd == "lote":
        slugs = resto or sorted(p.stem for p in (ROOT / "conteudo").glob("*.json")
                                if not (ROOT / p.stem / "fotos" / "fontes.json").exists())
        rels = []
        for s in slugs:
            try:
                rels.append(buscar(cli, s))
            except Exception as e:  # um jogo com problema não derruba o lote
                rels.append({"slug": s, "jogo": s, "editoras": [], "candidatas": 0, "avisos": [f"falhou: {e}"]})
            print(s, rels[-1]["candidatas"], "candidatas", flush=True)
        print("Relatório:", relatorio(rels, cli).relative_to(ROOT))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
