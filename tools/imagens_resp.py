"""Versões menores (WebP) das imagens grandes, para o celular não baixar fotos de 1200–1600 px.

As variantes ficam em img/<caminho original>-<hash do conteúdo>-<largura>.webp: se a imagem original for trocada
(mesmo nome, outro conteúdo), o nome da variante muda junto e nunca sai uma versão velha. O arquivo original continua sendo o src (navegador antigo e prévia de compartilhamento).
"""
import hashlib
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DESTINO = ROOT / "img"


def variante(original, largura):
    """Gera (se precisar) e devolve o Path da variante com essa largura."""
    rel = original.relative_to(ROOT)
    h = hashlib.sha256(original.read_bytes()).hexdigest()[:8]
    alvo = DESTINO / rel.parent / f"{rel.stem}-{h}-{largura}.webp"
    if not alvo.exists():
        alvo.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(original) as im:
            im = im.convert("RGB")
            altura = round(im.height * largura / im.width)
            im.resize((largura, altura), Image.LANCZOS).save(alvo, "WEBP", quality=78, method=6)
    return alvo


def srcset(original, pre, larguras=(480, 800, 1200)):
    """Atributo srcset com as variantes menores que o original e o próprio original na largura real.
    pre: prefixo relativo da página até a raiz do site ("", "../", "../../").
    Imagem é preferência, não regra: sem arquivo ou com arquivo ilegível, sai só o original e a página é gerada igual."""
    original = Path(original)
    try:
        with Image.open(original) as im:
            w = im.width
    except Exception:
        return f"{pre}{original.relative_to(ROOT).as_posix()}"
    itens = [f"{pre}{variante(original, lg).relative_to(ROOT).as_posix()} {lg}w" for lg in larguras if lg < w]
    itens.append(f"{pre}{original.relative_to(ROOT).as_posix()} {w}w")
    return ", ".join(itens)


def miniatura(original, pre, largura=160):
    """Caminho de uma variante pequena para miniaturas de tamanho fixo (ex.: 76 px na tela, 2x para retina)."""
    original = Path(original)
    if not original.exists():  # capa ainda não baixada: mantém o caminho (a verificação acusa o link)
        return f"{pre}{original.relative_to(ROOT).as_posix()}"
    try:
        with Image.open(original) as im:
            if im.width <= largura:
                return f"{pre}{original.relative_to(ROOT).as_posix()}"
    except Exception:  # arquivo ilegível: mantém o caminho
        return f"{pre}{original.relative_to(ROOT).as_posix()}"
    return f"{pre}{variante(original, largura).relative_to(ROOT).as_posix()}"
