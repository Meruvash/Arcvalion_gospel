"""Robô de fotos das matérias: acha candidatas nas fontes da própria matéria, confere a licença e grava a escolhida.

Uso:
  python3 tools/fotos.py buscar <slug> [--url URL ...] [--tema TEMA] [--commons "Categoria"]
        lê as fontes da notícia ou do estudo <slug> (e as --url extras), extrai as fotos de cada página
        (og:image, JSON-LD, <img>/srcset, com o crédito da legenda), soma as categorias do Wikimedia Commons
        (--tema de config/imagens.json ou --commons) e monta .cache/fotos/<slug>/folha.jpg + candidatas.json
  python3 tools/fotos.py local <slug> <arquivo, pasta ou .zip> --credito "Foto: Fulano/Igreja X" --licenca "..."
        candidatas que a redação baixou ou recebeu (banco de imagens, divulgação por e-mail, foto própria)
  python3 tools/fotos.py aprovar <slug> <n> --alt "o que a foto mostra" [--credito "..."] [--licenca "..."]
        grava a candidata n em conteudo/imagens/<slug>.jpg (até 1600 px, ≤ 350 KB) e preenche o campo `imagem`

Portado do robô de imagens das editoras do projeto de origem (tools/imagens/robo.py), com as mesmas regras de boa
conduta: confere o robots.txt (RFC 9309) de cada host antes de cada pedido, espera pelo menos 3 s entre pedidos no
mesmo host (mais, se o Crawl-delay pedir), se identifica no User-Agent e para em 401/403 sem contornar o bloqueio.
O que muda: a busca parte das fontes da matéria, e cada foto carrega a licença da fonte (config/imagens.json).
Foto de agência de terceiros (Reuters, AFP, Getty...) e de domínio sem licença conhecida nunca é aprovada sem
--licenca e --credito escritos por quem conferiu. Nada aqui publica: aprovar só preenche o rascunho.
"""
import hashlib
import io
import json
import re
import sys
import time
import urllib.error
import urllib.request
import zipfile
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, urljoin, urlsplit, urlunsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
import portal  # noqa: E402

CACHE = portal.ROOT / ".cache" / "fotos"
TOKEN_UA = "portalcristao-imagens"
DELAY_MIN = 3.0
CACHE_DIAS = 7
MAX_CANDIDATAS = 30
LARG_MIN = 800  # piso para foto de matéria (o validador das notícias aceita a partir de 500 px no lado menor)
LIXO = r"logo|icon|sprite|flag|bandeira|payment|badge|avatar|banner|newsletter|placeholder|favicon|social|selo|whatsapp|share"
LICENCAS_OK = r"^(CC0|CC BY(-SA)? [\d.]+|Public domain|PD)"


def ua():
    return f"PortalCristao-imagens/1.0 (+{portal.CFG.get('url') or 'sem endereço'}; respeita robots.txt)"


def config():
    return json.loads((portal.ROOT / "config" / "imagens.json").read_text(encoding="utf-8"))


class Bloqueado(Exception):
    pass


# ---------- robots.txt (RFC 9309) ----------

class Robots:
    def __init__(self, texto, status):
        self.status, self.regras, self.delay = status, [], None
        if status >= 500 or status == 0:
            self.regras = [(False, "/")]  # servidor fora do ar ou rede caída: não entra em nada (RFC 9309, 2.3.1.4)
            return
        if status >= 400:
            return  # robots.txt ausente: tudo liberado (RFC 9309, 2.3.1.3)
        grupos, atual, lendo_ua = [], None, False
        for linha in texto.splitlines():
            linha = linha.split("#", 1)[0].strip()
            if ":" not in linha:
                continue
            campo, valor = (p.strip() for p in linha.split(":", 1))
            campo = campo.lower()
            if campo == "user-agent":
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
        for g in meus or [g for g in grupos if "*" in g["uas"]]:
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
        self.robots, self.ultimo, self.pedidos, self.pausa = {}, {}, 0, set()

    @staticmethod
    def _host(url):
        p = urlsplit(url)
        return f"{p.scheme}://{p.netloc}"

    def _esperar(self, host, delay):
        falta = self.ultimo.get(host, 0) + delay - time.time()
        if falta > 0:
            time.sleep(falta)
        self.ultimo[host] = time.time()

    def _pedir(self, url):
        req = urllib.request.Request(url, headers={"User-Agent": ua(), "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.6"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.geturl(), r.read()

    def _robots(self, url):
        host = self._host(url)
        if host not in self.robots:
            status, texto = 0, ""
            for espera in (5, 15, None):  # falha de rede não é proibição: tenta de novo antes de desistir
                self._esperar(host, DELAY_MIN)
                try:
                    status, _, corpo = self._pedir(host + "/robots.txt")
                    texto = corpo.decode("utf-8", "replace")
                    break
                except urllib.error.HTTPError as e:
                    status = e.code
                    break
                except (urllib.error.URLError, OSError):
                    if espera:
                        time.sleep(espera)
            self.robots[host] = Robots(texto, status)
        return self.robots[host]

    def pode(self, url):
        return self._robots(url).pode(url)

    def get(self, url):
        """Devolve (url_final, bytes) ou levanta Bloqueado/LookupError. Nunca acessa o que o robots.txt proíbe."""
        chave = hashlib.sha1(url.encode()).hexdigest()
        corpo_f, meta_f = CACHE / "http" / f"{chave}.bin", CACHE / "http" / f"{chave}.json"
        if meta_f.exists():
            meta = json.loads(meta_f.read_text())
            if time.time() - meta["quando"] < CACHE_DIAS * 86400:
                return meta["url"], corpo_f.read_bytes()
        if self._host(url) in self.pausa:
            raise LookupError(f"{self._host(url)} pediu pausa (429); rode de novo mais tarde")
        rob = self._robots(url)
        if rob.status == 0:
            raise LookupError(f"robots.txt de {self._host(url)} inacessível (erro de rede); tente mais tarde")
        if not rob.pode(url):
            raise Bloqueado(f"robots.txt proíbe {url}")
        for espera in (10, 30, None):
            self._esperar(self._host(url), max(DELAY_MIN, rob.delay or 0))
            self.pedidos += 1
            try:
                _, final, corpo = self._pedir(url)
            except urllib.error.HTTPError as e:
                if e.code in (401, 403):
                    raise Bloqueado(f"{e.code} em {url}")
                if e.code == 429:  # o servidor pediu para parar: o host fica de fora até o fim desta execução
                    self.pausa.add(self._host(url))
                    raise LookupError(f"429 em {self._host(url)}: pediu pausa; rode de novo mais tarde (do computador da redação costuma passar)")
                if e.code >= 500 and espera:
                    time.sleep(espera)
                    continue
                raise LookupError(f"{e.code} em {url}")
            except (urllib.error.URLError, OSError) as e:
                if espera is None:
                    raise LookupError(f"{url}: {e}")
                time.sleep(espera)
                continue
            if final != url and not self.pode(final):
                raise Bloqueado(f"robots.txt proíbe o destino do redirecionamento {final}")
            corpo_f.parent.mkdir(parents=True, exist_ok=True)
            corpo_f.write_bytes(corpo)
            meta_f.write_text(json.dumps({"url": final, "quando": time.time()}))
            return final, corpo
        raise LookupError(f"{url}: sem resposta")


# ---------- licença e crédito ----------

def regra(url):
    """Regra de licença do domínio (config/imagens.json); domínio desconhecido volta como 'a confirmar'."""
    host = urlsplit(url).netloc.lower()
    base = re.sub(r"^www\d*\.", "", host)
    for dom, r in config()["fontes"].items():
        d = re.sub(r"^www\d*\.", "", dom)
        if base == d or base.endswith("." + d):
            return {"dominio": dom, **r}
    return {"dominio": host, "nome": host, "uso": "a confirmar"}


def autor_do_credito(texto):
    """'Foto: Fulana de Tal/Agência Brasil' -> 'Fulana de Tal'."""
    m = re.search(r"(?:Fotos?|Imagem|Crédito)\s*:\s*([^|/\n]{3,60})", texto or "", re.I)
    return m.group(1).strip(" .-–") if m else ""


def montar_credito(r, legenda, licenca=""):
    terceiros = config()["terceiros"]
    if legenda and re.search(terceiros, legenda, re.I):
        return None, f"foto de agência de terceiros ({legenda.strip()[:80]}): não entra na licença de {r['nome']}"
    if r["uso"] == "proibido":
        return None, f"{r['nome']}: fonte proibida em config/imagens.json"
    if r["uso"] == "a confirmar":
        return "", "licença a confirmar: só aprova com --licenca e --credito de quem conferiu"
    autor = autor_do_credito(legenda)
    modelo = r.get("credito") or "Foto: {autor}"
    if "{autor}" in modelo and not autor:
        modelo = modelo.replace("{autor}/", "").replace("{autor}", r["nome"])
    return modelo.format(autor=autor, licenca=licenca), r.get("aviso", "")


# ---------- extrair fotos de uma página ----------

class _Pagina(HTMLParser):
    """Coleta og:image, imagens do JSON-LD e <img>/<source> com alt, title e a legenda (<figcaption>) da figura."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.meta, self.imgs, self.ld = [], [], []
        self._fig, self._cap, self._em_cap, self._em_ld = None, [], False, False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta" and re.match(r"(og:image(:url)?|twitter:image)$", a.get("property") or a.get("name") or ""):
            self.meta.append(a.get("content") or "")
        elif tag == "script" and (a.get("type") or "").startswith("application/ld+json"):
            self._em_ld = True
        elif tag == "figure":
            self._fig, self._cap = [], []
        elif tag == "figcaption":
            self._em_cap = True
        elif tag in ("img", "source"):
            srcs = [a.get(k) for k in ("data-large_image", "data-zoom-image", "data-src", "data-original", "src") if a.get(k)]
            for k in ("srcset", "data-srcset"):
                if a.get(k):
                    maior = max(a[k].split(","), key=lambda x: int(re.sub(r"\D", "", x.strip().split(" ")[-1]) or 0))
                    srcs.insert(0, maior.strip().split(" ")[0])
            item = {"src": srcs[0] if srcs else "", "texto": " ".join(filter(None, (a.get("alt"), a.get("title"))))}
            self.imgs.append(item)
            if self._fig is not None:
                self._fig.append(item)

    def handle_endtag(self, tag):
        if tag == "figcaption":
            self._em_cap = False
        elif tag == "script":
            self._em_ld = False
        elif tag == "figure" and self._fig is not None:
            legenda = " ".join(self._cap).strip()
            for item in self._fig:
                item["texto"] = f"{item['texto']} {legenda}".strip()
            self._fig = None

    def handle_data(self, data):
        if self._em_cap:
            self._cap.append(data.strip())
        if self._em_ld:
            self.ld.append(data)


def original(url):
    """Pede a maior versão da imagem: tira sufixos de miniatura do WordPress e parâmetros de tamanho."""
    p = urlsplit(url)
    caminho = re.sub(r"-\d{2,4}x\d{2,4}(?=\.\w+$)", "", p.path)
    query = "&".join(q for q in p.query.split("&") if q and not re.match(r"(width|height|w|h|crop|resize|fit)=", q))
    return urlunsplit((p.scheme, p.netloc, caminho, query, ""))


def imagens_da_pagina(html, url):
    """Lista de {url, legenda, pagina} sem duplicatas nem lixo de layout; og:image herda o primeiro crédito da página."""
    pg = _Pagina()
    pg.feed(html)
    creditos = [i["texto"] for i in pg.imgs if autor_do_credito(i["texto"])]
    achadas = [(u, creditos[0] if creditos else "") for u in pg.meta]
    for bloco in pg.ld:
        achadas += [(u, creditos[0] if creditos else "") for u in re.findall(r'"(?:url|contentUrl|image)"\s*:\s*"([^"]+\.(?:jpe?g|png|webp)[^"]*)"', bloco, re.I)]
    achadas += [(i["src"], i["texto"]) for i in pg.imgs]
    vistos, res = set(), []
    for u, legenda in achadas:
        if not u or u.startswith("data:"):
            continue
        u = unescape(urljoin(url, u.strip()))
        if not re.search(r"\.(jpe?g|png|webp)(\?|$)", u, re.I) and "imagens.ebc.com.br" not in u:
            continue
        if u.split("?")[0].rsplit("/", 1)[-1] and re.search(LIXO, u.split("?")[0].rsplit("/", 1)[-1], re.I):
            continue
        u = original(u) if "imagens.ebc.com.br" not in u else u
        if u not in vistos:
            vistos.add(u)
            res.append({"url": u, "legenda": re.sub(r"\s+", " ", legenda)[:200], "pagina": url})
    return res


# ---------- Wikimedia Commons (páginas de categoria e de arquivo, que o robots.txt permite) ----------

def commons(cli, categoria):
    url = "https://commons.wikimedia.org/wiki/Category:" + quote(categoria.replace(" ", "_"))
    res, avisos = [], []
    try:
        _, html = cli.get(url)
    except (Bloqueado, LookupError) as e:
        return [], [str(e)]
    paginas = list(dict.fromkeys(urljoin(url, h) for h in re.findall(r'href="(/wiki/File:[^"#]+)"', html.decode("utf-8", "replace"))))
    for pg in paginas[:12]:
        try:
            _, h = cli.get(pg)
        except (Bloqueado, LookupError) as e:
            avisos.append(str(e))
            continue
        h = h.decode("utf-8", "replace").replace("&#95;", "_")  # o Commons escreve os _ das classes como entidade
        link = re.search(r'class="(?:fullMedia|fullImageLink)"[^>]*>.*?href="([^"]+upload\.wikimedia\.org[^"]+)"', h, re.S)
        lic = next((unescape(x).strip() for x in re.findall(r'class="licensetpl_short"[^>]*>([^<]+)<', h)
                    if re.match(LICENCAS_OK, unescape(x).strip())), None)
        aut = re.search(r'id="fileinfotpl_aut"[^>]*>.*?</td>\s*<td[^>]*>(.*?)</td>', h, re.S)
        autor = re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", aut.group(1)))).strip()[:80] if aut else ""
        if not link or not lic:
            avisos.append(f"sem licença livre clara: {pg}")
            continue
        arq = urljoin(pg, unescape(link.group(1))).split("?")[0]
        if not re.search(r"\.(jpe?g|png|webp)$", arq, re.I):
            continue  # vídeo, SVG, PDF: não serve de foto
        # miniatura de 1280 px (um dos tamanhos padronizados do Commons; outros dão 400): o original pode ter dezenas de MB
        m = re.match(r"(https://upload\.wikimedia\.org/wikipedia/commons)/(\w/\w\w)/(.+)$", arq)
        if m:
            arq = f"{m.group(1)}/thumb/{m.group(2)}/{m.group(3)}/1280px-{m.group(3)}"
        res.append({"url": arq, "legenda": "", "pagina": pg, "licenca": lic,
                    "fonte": "Wikimedia Commons", "uso": "cc",
                    "credito": f"Foto: {autor or 'autor no Wikimedia Commons'} · {lic} · Wikimedia Commons"})
    return res, avisos


# ---------- baixar, filtrar e montar a folha ----------

def dhash(im):
    from PIL import Image
    g = im.convert("L").resize((9, 8), Image.LANCZOS)
    px = list(g.tobytes())
    return sum(1 << i for i in range(64) if px[(i // 8) * 9 + i % 8] > px[(i // 8) * 9 + i % 8 + 1])


def baixar(cli, candidatas, pasta):
    """Baixa, descarta as estreitas (< 800 px), as tiras e as repetidas (fica a maior) e grava em `pasta`."""
    from PIL import Image
    pasta.mkdir(parents=True, exist_ok=True)
    boas, hashes, avisos = [], [], []
    for c in candidatas[:MAX_CANDIDATAS]:
        try:
            dados = c.pop("_dados", None) or cli.get(c["url"])[1]
            im = Image.open(io.BytesIO(dados))
            im.load()
        except Bloqueado as e:
            avisos.append(str(e))
            continue
        except (LookupError, OSError) as e:
            avisos.append(f"não baixou {c['url']}: {e}")
            continue
        w, h = im.size
        if w < LARG_MIN or max(w, h) / min(w, h) > 3:
            continue
        hsh = dhash(im)
        dup = next((b for b, hb in zip(boas, hashes) if bin(hb ^ hsh).count("1") <= 6), None)
        if dup:
            if w * h <= dup["w"] * dup["h"]:
                continue
            i = boas.index(dup)
            boas.pop(i)
            hashes.pop(i)
        arq = pasta / f"{hashlib.sha1(c['url'].encode()).hexdigest()[:12]}.{(im.format or 'jpg').lower()}"
        arq.write_bytes(dados)
        c.update(w=w, h=h, arquivo=str(arq.relative_to(portal.ROOT)))
        boas.append(c)
        hashes.append(hsh)
    return boas, avisos


def folha_de_contato(cands, destino):
    """Grade numerada para a revisão visual: número, tamanho e situação da licença de cada candidata."""
    from PIL import Image, ImageDraw, ImageFont
    lado, cols = 320, 4
    linhas = max(1, -(-len(cands) // cols))
    folha = Image.new("RGB", (cols * lado, linhas * (lado + 34)), "white")
    d = ImageDraw.Draw(folha)
    try:
        fonte = ImageFont.load_default(size=16)
    except TypeError:
        fonte = ImageFont.load_default()
    for i, c in enumerate(cands):
        with Image.open(portal.ROOT / c["arquivo"]) as im:
            im = im.convert("RGB")
            im.thumbnail((lado - 8, lado - 8))
            x, y = (i % cols) * lado, (i // cols) * (lado + 34)
            folha.paste(im, (x + (lado - im.width) // 2, y + 4 + (lado - 8 - im.height) // 2))
        selo = "ok" if c.get("credito") else ("BLOQ" if c.get("credito") is None else "a confirmar")
        d.text((x + 6, y + lado + 6), f"#{c['n']} {c['w']}x{c['h']} {selo}", fill="black", font=fonte)
    folha.save(destino, quality=82)


def juntar(slug, novas):
    """Acrescenta candidatas às que já existem (a numeração continua) e refaz a folha de contato."""
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


def classificar(c, r):
    """Preenche fonte, uso, licença e crédito da candidata pela regra do domínio da página."""
    if c.get("uso") == "cc":
        return c
    credito, aviso = montar_credito(r, c.get("legenda", ""))
    c.update(fonte=r["nome"], uso=r["uso"], licenca=r.get("licenca", ""), credito=credito, aviso=aviso,
             sem_derivacao=bool(r.get("sem_derivacao")))
    return c


# ---------- comandos ----------

def artigo(slug):
    """A notícia (conteudo/noticias/<data>-<slug>.json) ou o estudo (conteudo/estudos/<slug>.json) com esse slug."""
    cands = [p for p in (portal.CONTEUDO / "noticias").glob(f"*{slug}.json") if json.loads(p.read_text(encoding="utf-8")).get("slug") == slug]
    cands += [p for p in [portal.CONTEUDO / "estudos" / f"{slug}.json"] if p.exists()]
    if not cands:
        raise SystemExit(f"não achei a notícia nem o estudo {slug} em conteudo/noticias/ ou conteudo/estudos/")
    a = json.loads(cands[0].read_text(encoding="utf-8"))
    # estudos guardam as fontes como [nome, link, uso]; notícias, como {nome, url, data}
    a["fontes"] = [f if isinstance(f, dict) else {"nome": f[0], "url": f[1]} for f in a.get("fontes") or []]
    return cands[0], a


def buscar(cli, slug, urls=(), temas=(), categorias=()):
    _, a = artigo(slug)
    paginas = [f["url"] for f in a.get("fontes") or [] if str(f.get("url", "")).startswith("http")] + list(urls)
    cats = list(categorias)
    temas_cfg = config().get("commons_temas", {})
    for t in temas:
        if t not in temas_cfg:
            raise SystemExit(f"tema {t} não está em config/imagens.json (commons_temas)")
        cats += temas_cfg[t]
    novas, avisos = [], []
    for url in dict.fromkeys(paginas):
        r = regra(url)
        if r["uso"] == "proibido":
            avisos.append(f"{url}: {r['nome']} é fonte proibida para fotos")
            continue
        try:
            final, html = cli.get(url)
        except (Bloqueado, LookupError) as e:
            avisos.append(str(e))
            continue
        novas += [classificar(c, r) for c in imagens_da_pagina(html.decode("utf-8", "replace"), final)]
    for cat in cats:
        res, av = commons(cli, cat)
        novas += res
        avisos += av
    boas, av = baixar(cli, novas, CACHE / slug)
    todas = juntar(slug, boas)
    relatorio(slug, todas, avisos + av)
    return todas


def local(slug, origem, credito, licenca):
    """Candidatas de arquivos que a redação baixou ou recebeu: imagem solta, pasta ou .zip."""
    p = Path(origem).expanduser()
    if p.suffix.lower() == ".zip":
        z = zipfile.ZipFile(p)
        itens = [(n.rsplit("/", 1)[-1], z.read(n)) for n in z.namelist()]
    elif p.is_dir():
        itens = [(f.name, f.read_bytes()) for f in sorted(p.iterdir()) if f.is_file()]
    else:
        itens = [(p.name, p.read_bytes())]
    novas = []
    for nome, dados in itens:
        if nome.startswith(".") or not re.search(r"\.(jpe?g|png|webp|tiff?)$", nome, re.I):
            continue
        novas.append({"url": f"local:{p.name}#{nome}:{hashlib.sha1(dados).hexdigest()[:8]}", "legenda": "",
                      "pagina": f"arquivo da redação ({p.name})", "fonte": "redação", "uso": "local",
                      "licenca": licenca, "credito": credito, "_dados": dados})
    boas, avisos = baixar(None, novas, CACHE / slug)
    relatorio(slug, juntar(slug, boas), avisos)


def relatorio(slug, todas, avisos):
    for c in todas:
        selo = "✅" if c.get("credito") else ("⛔" if c.get("credito") is None else "⚠️")
        print(f"{selo} #{c['n']:>2} {c['w']}x{c['h']} {c.get('fonte', '')}: {c.get('credito') or c.get('aviso')}")
    pausados = set()
    for a in dict.fromkeys(avisos):
        host = re.search(r"(https?://[^/\s:]+)[^\s]*:? pediu pausa|429 em (https?://[^/\s:]+)", a)
        if host:  # um aviso por servidor que pediu pausa, não um por foto
            h = host.group(1) or host.group(2)
            if h not in pausados:
                pausados.add(h)
                print(f"aviso: {h} pediu pausa (429); rode de novo mais tarde (do computador da redação costuma passar)")
            continue
        print("aviso:", a)
    if todas:
        print(f"folha de contato: .cache/fotos/{slug}/folha.jpg")
    else:
        print("nenhuma candidata com 800 px ou mais: tente --url de outra fonte oficial, --tema, ou foto da redação (local)")


def aprovar(slug, n, alt, credito=None, licenca=None):
    from PIL import Image
    if not alt or len(alt.split()) < 3:
        raise SystemExit("--alt precisa descrever o que a foto mostra (pelo menos 3 palavras)")
    f, a = artigo(slug)
    cands = {c["n"]: c for c in json.loads((CACHE / slug / "candidatas.json").read_text(encoding="utf-8"))}
    if n not in cands:
        raise SystemExit(f"candidata #{n} não existe; veja .cache/fotos/{slug}/folha.jpg")
    c = cands[n]
    if c.get("credito") is None and not (credito and licenca):
        raise SystemExit(f"#{n} está bloqueada: {c.get('aviso')}")
    if not c.get("credito") and not (credito and licenca):
        raise SystemExit(f"#{n} tem licença a confirmar: confira a página {c['pagina']} e passe --licenca e --credito")
    im = Image.open(portal.ROOT / c["arquivo"])
    if im.mode in ("RGBA", "LA", "P"):  # fundo transparente vira branco no JPG
        im = im.convert("RGBA")
        fundo = Image.new("RGB", im.size, "white")
        fundo.paste(im, mask=im.split()[-1])
        im = fundo
    im = im.convert("RGB")
    im.thumbnail((1600, 1600), Image.LANCZOS)  # só reduz: não recorta nem monta (vale para licença sem derivação)
    destino = portal.CONTEUDO / "imagens" / f"{a['slug']}.jpg"
    destino.parent.mkdir(parents=True, exist_ok=True)
    for q in range(86, 55, -5):
        im.save(destino, quality=q, optimize=True, progressive=True)
        if destino.stat().st_size <= 350_000:
            break
    a["imagem"] = {"arquivo": destino.name, "credito": credito or c["credito"], "alt": alt,
                   "licenca": licenca or c.get("licenca", ""), "origem": c["url"], "pagina": c["pagina"]}
    if c.get("sem_derivacao"):
        a["imagem"]["sem_derivacao"] = True
    # grava só o campo imagem no arquivo original (as fontes de `a` foram normalizadas só para a busca)
    bruto = json.loads(f.read_text(encoding="utf-8"))
    bruto["imagem"] = a["imagem"]
    f.write_text(json.dumps(bruto, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"conteudo/imagens/{destino.name}  {im.width}x{im.height}  {destino.stat().st_size // 1024} KB  {a['imagem']['credito']}")
    if c.get("sem_derivacao") and im.width < 1200:
        print("aviso: licença sem derivação e foto com menos de 1200 px; o build monta a versão do Discover com fundo desfocado")


def _opcoes(args, nome, varias=False):
    vals = [args[i + 1] for i, x in enumerate(args) if x == nome and i + 1 < len(args)]
    return vals if varias else (vals[-1] if vals else None)


def main(args):
    portal.iniciar()
    if len(args) < 2 or args[0] not in ("buscar", "local", "aprovar"):
        print(__doc__)
        return 2
    cmd, slug = args[0], args[1]
    if cmd == "buscar":
        buscar(Cliente(), slug, _opcoes(args, "--url", True), _opcoes(args, "--tema", True), _opcoes(args, "--commons", True))
    elif cmd == "local":
        cred, lic = _opcoes(args, "--credito"), _opcoes(args, "--licenca")
        if len(args) < 3 or not cred or not lic:
            raise SystemExit("uso: local <slug> <arquivo|pasta|zip> --credito \"Foto: ...\" --licenca \"...\"")
        local(slug, args[2], cred, lic)
    else:
        aprovar(slug, int(args[2]), _opcoes(args, "--alt"), _opcoes(args, "--credito"), _opcoes(args, "--licenca"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
