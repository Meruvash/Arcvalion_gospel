"""Baixa a foto de uma notícia ou estudo, respeitando o robots.txt, e grava em conteudo/imagens/ com o crédito.

Uso: python3 tools/imagens/baixar.py <url-da-imagem> <nome-do-arquivo.jpg> --credito "Foto: Fulano/Agência Brasil (CC BY 4.0)" [--pagina <url>]
Equivalente enxuto do robô de imagens do Elite (tools/imagens/robo.py): identifica o robô, respeita o robots.txt,
confere o tamanho (mínimo 500 px no lado menor, 1200 px de largura é o ideal para o Google Discover), converte para
JPEG e registra a origem em conteudo/imagens/creditos.json. Nunca gera imagem por IA.

Onde buscar foto com licença de uso (sempre com crédito):
- Agência Brasil (CC BY 4.0), Agência Senado e Agência Câmara (uso livre com crédito), gov.br/Planalto (Flickr oficial);
- Wikimedia Commons (verifique a licença de cada arquivo); obras de arte em domínio público para os estudos;
- fotos oficiais de divulgação de igrejas, eventos e artistas, quando a página diz que são para imprensa.
"""
import argparse
import io
import json
import sys
import urllib.request
import urllib.robotparser
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import portal  # noqa: E402

UA = "PortalCristaoBot/1.0 (https://github.com/Meruvash/Arcvalion_gospel) python-urllib/3.13"
MIN_LADO = 500


def permitido(url):
    """Lê o robots.txt com a identificação do robô (o leitor padrão do Python usa outra e alguns sites o bloqueiam)."""
    u = urlparse(url)
    rp = urllib.robotparser.RobotFileParser()
    try:
        with urllib.request.urlopen(urllib.request.Request(f"{u.scheme}://{u.netloc}/robots.txt", headers={"User-Agent": UA}), timeout=30) as r:
            rp.parse(r.read().decode("utf-8", "ignore").splitlines())
    except Exception:
        return True  # sem robots.txt acessível vale a regra geral (permitido), como para os buscadores
    return rp.can_fetch(UA, url)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("arquivo")
    ap.add_argument("--credito", required=True)
    ap.add_argument("--pagina", default="")
    ar = ap.parse_args(argv)
    portal.iniciar()
    if not permitido(ar.url):
        sys.exit("robots.txt do site não permite baixar esta imagem automaticamente: procure outra fonte.")
    from PIL import Image
    with urllib.request.urlopen(urllib.request.Request(ar.url, headers={"User-Agent": UA}), timeout=60) as r:
        dados = r.read()
    im = Image.open(io.BytesIO(dados))
    if min(im.size) < MIN_LADO:
        sys.exit(f"Imagem pequena ({im.size[0]}×{im.size[1]}): mínimo {MIN_LADO} px no lado menor. Procure uma maior.")
    destino = portal.ROOT / "conteudo" / "imagens" / ar.arquivo
    destino.parent.mkdir(parents=True, exist_ok=True)
    im.convert("RGB").save(destino, "JPEG", quality=86, optimize=True, progressive=True)
    reg = portal.ROOT / "conteudo" / "imagens" / "creditos.json"
    d = json.loads(reg.read_text(encoding="utf-8")) if reg.exists() else {}
    d[ar.arquivo] = {"credito": ar.credito, "origem": ar.url, "pagina": ar.pagina, "data": date.today().isoformat(), "tamanho": list(im.size)}
    reg.write_text(json.dumps(d, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    aviso = "" if im.size[0] >= 1200 else " (menos de 1200 px de largura: o build gera a versão 1200×675 para o Discover)"
    print(f"ok conteudo/imagens/{ar.arquivo}: {im.size[0]}×{im.size[1]}{aviso}")


if __name__ == "__main__":
    main()
