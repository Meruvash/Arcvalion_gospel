"""Cria o esqueleto de uma notícia ou de um estudo bíblico no padrão editorial, com status "rascunho".

Uso:
  python3 tools/novo.py noticia <categoria> "<título>"     -> conteudo/noticias/<hoje>-<slug>.json
  python3 tools/novo.py estudo "<título>"                  -> conteudo/estudos/<slug>.json
Depois de preencher: python3 tools/noticias/checar_noticia.py <arquivo> (ou tools/estudos/checar_estudo.py) e
"status": "revisao". Só uma pessoa revisora publica, com tools/publicar.py.
"""
import json
import re
import sys
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import portal  # noqa: E402

PARADAS = {"a", "o", "e", "de", "da", "do", "das", "dos", "em", "um", "uma", "para", "com", "no", "na", "que", "por"}


def slugify(t):
    t = unicodedata.normalize("NFKD", t.lower()).encode("ascii", "ignore").decode()
    return "-".join([p for p in re.sub(r"[^a-z0-9]+", " ", t).split() if p not in PARADAS][:9])


def noticia(categoria, titulo):
    hoje = datetime.now(timezone(timedelta(hours=-3))).date().isoformat()
    return f"{hoje}-{slugify(titulo)}.json", {
        "slug": slugify(titulo), "data": hoje, "categoria": categoria, "status": "rascunho", "titulo": titulo,
        "lide": "", "corpo": [""], "fontes": [{"nome": "", "url": "https://", "data": "DD/MM/AAAA", "tipo": "primaria"}],
        "imagem": None, "crivo": {"escala": 100, "pontos": 0, "trilha": "quente", "abrangencia": "nacional",
                                    "criterios": {k: {"pontos": 0, "porque": ""} for k in ("impacto", "afinidade", "atualidade", "comprovacao", "originalidade")}}, "selo": "Informativo", "instituicao": "",
        "por_que_importa": "", "numeros": [["", "", ""], ["", "", ""]], "no_brasil": "",
        "critica": [{"fonte": "", "texto": "", "citacao": False}], "para_quem": [""], "nao_e_para": [], "veredito": "",
        "estudos": [], "ia": {"usada": True, "uso": ""}}


def estudo(titulo):
    return f"{slugify(titulo)}.json", {
        "slug": slugify(titulo), "status": "rascunho", "titulo": titulo, "passagem": "", "sigla": "", "livro": "",
        "testamento": "Novo Testamento", "genero": "Evangelho", "nivel": 1, "tempo_min": 20, "selo": "Ótimo para começar",
        "tagline": "", "lede": "", "descricao": "", "imagem": None,
        "versiculo_chave": {"texto": "", "referencia": "", "traducao": ""},
        "estrutura": [["", ""]], "estrutura_resumo": "", "questao": "",
        "posicoes": [{"lado": "", "resumo": "", "teologos": [{"autor": "", "quem": "", "obra": "", "url": "https://", "data": "", "texto": ""}]}],
        "convergencias": [""], "contexto": [""], "aplicacao": [""], "destaques": [["", ""]],
        "atencao": [["Moderada", "", ""]], "perfil": [["Contexto histórico", 3], ["Aplicação prática", 3]],
        "formatos": [["Sozinho", "", 2], ["Em família", "", 2], ["Em grupo", "", 2]], "para_quem": [""], "nao_e_para": [],
        "dica": "", "traducoes": "", "relacionadas": "", "comparacoes": [], "versiculos": [], "veredito": "",
        "ficha": [["Livro", ""], ["Autor", ""], ["Capítulos", ""]], "fontes": [["", "https://", ""]], "consulta": "",
        "legenda": "", "ia": {"usada": True, "uso": ""}}


def main(args):
    portal.iniciar()
    if len(args) == 3 and args[0] == "noticia":
        if not portal.editoria(args[1]):
            sys.exit(f"Categoria inexistente: {args[1]}. Opções: {', '.join(x['slug'] for x in portal.EDITORIAS)}")
        nome, dados, pasta = *noticia(args[1], args[2]), "noticias"
    elif len(args) == 2 and args[0] == "estudo":
        nome, dados, pasta = *estudo(args[1]), "estudos"
    else:
        sys.exit(__doc__)
    arq = portal.CONTEUDO / pasta / nome
    if arq.exists():
        sys.exit(f"Já existe: {arq.relative_to(portal.ROOT)}")
    arq.parent.mkdir(parents=True, exist_ok=True)
    arq.write_text(json.dumps(dados, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"ok rascunho criado: {arq.relative_to(portal.ROOT)}")


if __name__ == "__main__":
    main(sys.argv[1:])
