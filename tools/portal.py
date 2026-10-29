"""Configuração do portal num lugar só: identidade, editorias, equipe, anúncios e caminhos.

No Elite Boardgamers o domínio e o nome estavam repetidos em cada script (SITE = "https://..."). Aqui tudo sai de
config/*.json, carregado uma vez por iniciar(). Os outros módulos leem portal.CFG, portal.SITE etc. na hora do uso,
então trocar o nome ou o domínio é só editar config/portal.json e rodar o build de novo.

iniciar(conteudo=..., config=...) aceita outra pasta de conteúdo e uma pasta de configuração que sobrepõe a padrão
(arquivo a arquivo): é assim que o build de exemplo e os testes usam dados fictícios sem tocar nos reais.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# preenchidos por iniciar()
CFG = {}
EDITORIAS = []
EQUIPE = {}
ANUNCIOS = {}
SITE = ""
BASE = ""   # caminho do site no domínio: "" na raiz, "/Arcvalion" em meruvash.github.io/Arcvalion
NOME = ""
CONTEUDO = ROOT / "conteudo"
SAIDA = ROOT / "publico"
EXEMPLO = False

# endereços que não podem virar slug de editoria (páginas e pastas do próprio portal)
RESERVADOS = {"noticias", "autores", "sobre", "expediente", "politica-editorial", "privacidade", "termos", "contato", "anuncie",
              "newsletter", "opiniao", "img", "imagens", "fontes", "marca", "js", "busca", "feed", "sitemap", "pagina", "eventos-agenda"}

TIPOS = {
    # tipo: (rótulo visível, @type schema.org, entra no sitemap de notícias)
    "noticia": ("Notícia", "NewsArticle", True),
    "analise": ("Análise", "AnalysisNewsArticle", True),
    "opiniao": ("Opinião", "OpinionNewsArticle", True),
    "explicativo": ("Explica", "Article", False),
    "patrocinado": ("Conteúdo patrocinado", "Article", False),
}


def _ler(nome, sobre=None):
    """config/<nome>, com a versão da pasta `sobre` por cima: em portal.json as chaves se mesclam (um nível),
    nos outros arquivos a versão de `sobre` substitui a padrão."""
    dados = json.loads((ROOT / "config" / nome).read_text(encoding="utf-8"))
    extra = Path(sobre) / nome if sobre else None
    if extra and extra.exists():
        novo = json.loads(extra.read_text(encoding="utf-8"))
        if nome != "portal.json":
            return novo
        for k, v in novo.items():
            dados[k] = {**dados[k], **v} if isinstance(v, dict) and isinstance(dados.get(k), dict) else v
    return dados


def iniciar(conteudo=None, config=None, saida=None, exemplo=False):
    global CFG, EDITORIAS, EQUIPE, ANUNCIOS, SITE, BASE, NOME, CONTEUDO, SAIDA, EXEMPLO
    CFG = _ler("portal.json", config)
    EDITORIAS = _ler("editorias.json", config)["editorias"]
    EQUIPE = {p["slug"]: p for p in _ler("equipe.json", config)["pessoas"]}
    ANUNCIOS = _ler("anuncios.json", config)
    SITE = CFG["url"].rstrip("/")
    from urllib.parse import urlparse
    BASE = urlparse(SITE).path.rstrip("/")
    NOME = CFG["nome"]
    CONTEUDO = Path(conteudo) if conteudo else ROOT / "conteudo"
    SAIDA = Path(saida) if saida else ROOT / "publico"
    EXEMPLO = exemplo
    return CFG


def editoria(slug):
    return next((e for e in EDITORIAS if e["slug"] == slug), None)


def visiveis():
    return [e for e in EDITORIAS if e.get("visivel", True)]


def problemas_config(producao=False):
    """Erros de configuração. Em produção também recusa os valores provisórios."""
    erros = []
    slugs = [e["slug"] for e in EDITORIAS]
    if len(slugs) != len(set(slugs)):
        erros.append("editorias: slug repetido")
    for e in EDITORIAS:
        if e["slug"] in RESERVADOS:
            erros.append(f"editoria {e['slug']}: slug reservado para página do portal")
        if not all(e.get(k) for k in ("slug", "nome", "descricao", "cor", "fundo")):
            erros.append(f"editoria {e.get('slug')}: precisa de slug, nome, descricao, cor e fundo")
    if not SITE.startswith("https://"):
        erros.append("portal.json: url precisa começar com https://")
    if producao:
        if SITE.endswith(".example"):
            erros.append("portal.json: url ainda é o domínio provisório (.example); configure o domínio real")
        if not CFG.get("responsavel_editorial", {}).get("nome"):
            erros.append("portal.json: falta o nome do responsável editorial (exigido na política editorial e no expediente)")
        if not CFG.get("email_contato"):
            erros.append("portal.json: falta email_contato (canal de correções e de contato do leitor)")
        # sem revisor o site pode ir ao ar vazio; cada matéria continua exigindo revisor (editorial/checar.py)
    return erros


def url(caminho=""):
    """URL absoluta de um caminho relativo à raiz do site ("noticias/x/")."""
    return f"{SITE}/{caminho.lstrip('/')}"
