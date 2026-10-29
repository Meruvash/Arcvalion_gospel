"""Imagens responsivas e versão larga para o Google Discover. Portado de imagens_resp.py e capas_grandes.py.

- As fotos das matérias ficam em conteudo/imagens/ e são copiadas para publico/imagens/ (o original continua sendo o src).
- Variantes WebP menores (480/800/1200 px) ficam em publico/img/<nome>-<hash>-<largura>.webp: se a foto for trocada,
  o nome muda junto e nunca sai uma versão velha.
- larga(): versão 1200×675 (16:9) para o JSON-LD quando a foto tem menos de 1200 px de largura (o Discover pede 1200),
  com a foto inteira no centro e as laterais preenchidas por ela mesma desfocada. Sem texto por cima.
Tudo é preferência, não regra: imagem com problema deixa de fora só a variante, e a página sai igual.
As variantes ficam em cache (.cache/img/) para o build não refazer o que não mudou.
"""
import hashlib
import shutil
from pathlib import Path

from PIL import Image, ImageFilter

import portal

CACHE = portal.ROOT / ".cache" / "img"
LARG, ALT = 1200, 675


def _hash(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()[:8]


def fonte(arquivo):
    return portal.CONTEUDO / "imagens" / arquivo


def publicar(arquivo):
    """Copia a foto original para publico/imagens/ e devolve o caminho relativo à raiz do site."""
    src = fonte(arquivo)
    alvo = portal.SAIDA / "imagens" / arquivo
    if src.is_file() and not alvo.exists():
        alvo.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, alvo)
    return f"imagens/{arquivo}"


def _variante(src, largura):
    nome = f"{src.stem}-{_hash(src)}-{largura}.webp"
    cache = CACHE / nome
    if not cache.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        with Image.open(src) as im:
            im = im.convert("RGB")
            im.resize((largura, round(im.height * largura / im.width)), Image.LANCZOS).save(cache, "WEBP", quality=78, method=6)
    alvo = portal.SAIDA / "img" / nome
    if not alvo.exists():
        alvo.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(cache, alvo)
    return f"img/{nome}"


def dimensoes(arquivo):
    try:
        with Image.open(fonte(arquivo)) as im:
            return im.size
    except Exception:
        return None


def srcset(arquivo, pre, larguras=(480, 800, 1200)):
    """srcset com as variantes menores que o original e o próprio original na largura real."""
    src = fonte(arquivo)
    original = publicar(arquivo)
    dim = dimensoes(arquivo)
    if not dim:
        return f"{pre}{original}"
    itens = [f"{pre}{_variante(src, lg)} {lg}w" for lg in larguras if lg < dim[0]]
    itens.append(f"{pre}{original} {dim[0]}w")
    return ", ".join(itens)


def miniatura(arquivo, pre, largura=200):
    src = fonte(arquivo)
    dim = dimensoes(arquivo)
    if not dim or dim[0] <= largura:
        return f"{pre}{publicar(arquivo)}"
    return f"{pre}{_variante(src, largura)}"


def larga(arquivo):
    """Caminho relativo (à raiz do site) da versão 1200×675; foto que já tem 1200 px volta como está."""
    src = fonte(arquivo)
    with Image.open(src) as im:
        if im.width >= LARG:
            return publicar(arquivo)
        nome = f"{src.stem}-{_hash(src)}-{LARG}.jpg"
        cache = CACHE / "discover" / nome
        if not cache.exists():
            im = im.convert("RGB")
            esc = max(LARG / im.width, ALT / im.height)
            fundo = im.resize((round(im.width * esc), round(im.height * esc)), Image.LANCZOS)
            x, y = (fundo.width - LARG) // 2, (fundo.height - ALT) // 2
            fundo = fundo.crop((x, y, x + LARG, y + ALT)).filter(ImageFilter.GaussianBlur(28)).point(lambda v: int(v * 0.55))
            f = min(ALT / im.height, LARG / im.width, 1.0) if im.height > ALT else min(ALT / im.height, 1.35)
            frente = im.resize((round(im.width * f), round(im.height * f)), Image.LANCZOS)
            fundo.paste(frente, ((LARG - frente.width) // 2, (ALT - frente.height) // 2))
            cache.parent.mkdir(parents=True, exist_ok=True)
            fundo.save(cache, "JPEG", quality=84, optimize=True, progressive=True)
    alvo = portal.SAIDA / "img" / "discover" / nome
    alvo.parent.mkdir(parents=True, exist_ok=True)
    if not alvo.exists():
        shutil.copy2(cache, alvo)
    return f"img/discover/{nome}"
