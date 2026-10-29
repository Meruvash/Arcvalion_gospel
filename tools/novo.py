"""Cria o rascunho de uma matéria em conteudo/artigos/<slug>.json, já no formato do padrão editorial.

Uso: python3 tools/novo.py <editoria> <tipo> "<título>" [--autor <slug>]
     tipos: noticia, analise, opiniao, explicativo, patrocinado
O arquivo nasce com status "rascunho": não aparece no site. Depois de preencher, rode
python3 tools/editorial/checar.py conteudo/artigos/<slug>.json e, com tudo certo, peça a revisão
(status "revisao"). Só uma pessoa revisora publica, com tools/publicar.py.
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import portal  # noqa: E402


def slugify(t):
    t = unicodedata.normalize("NFKD", t.lower()).encode("ascii", "ignore").decode()
    palavras = [p for p in re.sub(r"[^a-z0-9]+", " ", t).split() if p not in {"a", "o", "e", "de", "da", "do", "das", "dos", "em", "um", "uma", "para", "com", "no", "na"}]
    return "-".join(palavras[:9])


def esqueleto(editoria, tipo, titulo, autor=""):
    a = {"slug": slugify(titulo), "status": "rascunho", "tipo": tipo, "editoria": editoria, "titulo": titulo,
         "linha_fina": "", "corpo": ["Parágrafo 1", {"intertitulo": "Intertítulo opcional"},
                                     {"citacao": "Frase exata, como está na fonte", "autor": "Nome de quem disse", "cargo": "cargo", "fonte": 0}],
         "fontes": [{"nome": "Nome da fonte (órgão, documento, veículo)", "url": "https://", "data": "DD/MM/AAAA", "tipo": "primaria"}],
         "autor": autor, "tags": [], "imagem": {"arquivo": "", "credito": "", "alt": ""},
         "ia": {"usada": False, "uso": ""}}
    if tipo in ("noticia", "analise"):
        a["lide"] = ""
    if tipo == "noticia":
        a["analise"] = ""
    if tipo == "opiniao" and not autor:
        a["colaborador"] = {"nome": "", "descricao": ""}
    if tipo == "patrocinado":
        a["patrocinador"] = {"nome": "", "url": ""}
    if tipo == "explicativo":
        a["faq"] = []
        if editoria == "fe-e-biblia":
            a["referencias_biblicas"] = []
            a["versao_biblica"] = ""
    return a


def main(args):
    autor = ""
    if "--autor" in args:
        i = args.index("--autor")
        autor = args[i + 1]
        args = args[:i] + args[i + 2:]
    if len(args) != 3:
        sys.exit(__doc__)
    editoria, tipo, titulo = args
    portal.iniciar()
    if not portal.editoria(editoria):
        sys.exit(f"Editoria inexistente: {editoria}. Opções: {', '.join(x['slug'] for x in portal.EDITORIAS)}")
    if tipo not in portal.TIPOS:
        sys.exit(f"Tipo inválido: {tipo}. Opções: {', '.join(portal.TIPOS)}")
    a = esqueleto(editoria, tipo, titulo, autor)
    arq = portal.CONTEUDO / "artigos" / f"{a['slug']}.json"
    if arq.exists():
        sys.exit(f"Já existe: {arq.relative_to(portal.ROOT)}")
    arq.parent.mkdir(parents=True, exist_ok=True)
    arq.write_text(json.dumps(a, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"ok rascunho criado: {arq.relative_to(portal.ROOT)}")


if __name__ == "__main__":
    main(sys.argv[1:])
