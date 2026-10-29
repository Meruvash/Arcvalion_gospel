"""Gera o site inteiro em publico/, no formato do Elite Boardgamers.

Uso:
  python3 tools/build.py              site real (só o que tem status "publicado"; o que está em "revisao" vai para /previa/)
  python3 tools/build.py --producao   igual, recusando configuração com problema
  python3 tools/build.py --exemplo    prévia com o conteúdo FICTÍCIO de exemplos/ em publico-exemplo/ (noindex)
  opções: --saida DIR  --sem-og

Ordem (a mesma do __main__ do build_home.py do Elite): cartões de prévia, home e notícias, estudos (as resenhas),
agenda e livros da Bíblia (calendário e consulta), institucionais, 404, RSS, sitemaps, robots, llms.txt e busca.
"""
import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import portal  # noqa: E402
import pagina  # noqa: E402


def limpar_saida():
    s = portal.SAIDA.resolve()
    if s.parent != portal.ROOT.resolve() or not s.name.startswith("publico"):
        sys.exit(f"Saída recusada: {s} (use uma pasta publico* dentro do projeto)")
    if s.exists():
        shutil.rmtree(s)
    s.mkdir()


def copiar_estaticos():
    for pasta in ("fontes", "marca", "js"):
        shutil.copytree(portal.ROOT / "assets" / pasta, portal.SAIDA / pasta, dirs_exist_ok=True)
    chave = portal.CFG.get("indexnow_chave")
    if chave and not portal.EXEMPLO:
        pagina.escrever(f"{chave}.txt", chave)
    pagina.escrever(".nojekyll", "")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--producao", action="store_true")
    ap.add_argument("--exemplo", action="store_true")
    ap.add_argument("--saida")
    ap.add_argument("--sem-og", action="store_true")
    ar = ap.parse_args(argv)
    ex = portal.ROOT / "exemplos"
    saida = Path(ar.saida) if ar.saida else portal.ROOT / ("publico-exemplo" if ar.exemplo else "publico")
    saida = saida if saida.is_absolute() else portal.ROOT / saida
    portal.iniciar(conteudo=ex / "conteudo" if ar.exemplo else None, config=ex / "config" if ar.exemplo else None, saida=saida, exemplo=ar.exemplo)
    erros = portal.problemas_config(producao=ar.producao)
    if erros:
        sys.exit("Configuração com problema:\n - " + "\n - ".join(erros))
    for aviso in portal.avisos_config() if not ar.exemplo else []:
        print("⚠️ " + aviso)
    import og
    og.DESLIGADO = ar.sem_og
    import build_noticias as bn
    import build_estudos as be
    import build_extras as bx
    pagina.ESCRITOS.clear()
    ns = bn.notas(incluir_revisao=True)
    es = be.estudos(incluir_revisao=True)
    evs = bx.agenda_eventos()
    limpar_saida()
    copiar_estaticos()
    og.gerar(ns, es)
    bn.build_home(ns, es, evs)
    bn.build_arquivo(ns)
    for n in ns:
        bn.build_nota(n, ns, previa=n.get("status") == "revisao")
    for c in es:
        be.build_estudo(c, es, ns, previa=c.get("status") == "revisao")
    be.build_lista(es)
    bn.build_previa_indice(ns, es)
    bx.build_agenda(evs)
    bx.build_biblia(es)
    inst = bx.build_institucionais(ns)
    bx.build_404()
    bx.build_feed(ns)
    total, recentes = bx.build_sitemaps(ns, es, evs, inst)
    bx.build_robots()
    bx.build_llms(ns, es)
    n_busca = bx.build_busca(ns, es)
    pub = sum(1 for n in ns if n.get("status", "publicado") == "publicado")
    rev = sum(1 for n in ns if n.get("status") == "revisao") + sum(1 for c in es if c.get("status") == "revisao")
    print(f"ok {portal.SAIDA.name}/: {pub} notícias publicadas, {sum(1 for c in es if c.get('status') == 'publicado')} estudos, {rev} em revisão (/previa/), "
          f"{total} URLs no sitemap, {recentes} no de notícias, {n_busca} registros na busca, {len(pagina.ESCRITOS)} arquivos")
    return ns, es


if __name__ == "__main__":
    main()
