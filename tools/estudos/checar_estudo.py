"""Confere um estudo bíblico contra o padrão editorial (docs/PADRAO_EDITORIAL.md, "Estudos bíblicos").

Uso: python3 tools/estudos/checar_estudo.py [conteudo/estudos/<slug>.json ...]   (sem argumentos, todos)
O estudo é o equivalente da resenha do Elite Boardgamers e segue o mesmo esqueleto (resumo em 30 segundos, passos,
destaques e pontos de atenção, para quem é, veredito, ficha, fontes, perguntas frequentes). As regras de conteúdo:
toda passagem citada com a tradução; interpretação atribuída a quem a defende; nada de "a Bíblia diz" sem a referência.
O centro do estudo é "O que dizem os teólogos" (pedido de 30/10/2026). Estudo de debate (`tipo` "debate", padrão):
`posicoes`, os lados de uma questão disputada, cada um com pelo menos dois teólogos brasileiros de referência. Estudo
de passagem (`tipo` "passagem"): `vozes`, de 2 a 4 teólogos que comentam um texto que une os cristãos.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import portal  # noqa: E402
from editorial.vicios import avisos, sensacionalismo  # noqa: E402

TESTAMENTOS = {"Antigo Testamento", "Novo Testamento"}
GENEROS = {"Lei", "Narrativa", "Poesia e sabedoria", "Profecia", "Evangelho", "Epístola", "Apocalíptico", "Tema"}
NIVEIS = {1: "Iniciante", 2: "Intermediário", 3: "Aprofundado"}
SELOS = {"Ótimo para começar", "Ideal para grupos", "Para aprofundar"}
REFERENCIA = re.compile(r"\b\d?\s?[A-ZÁÉÍÓÚ][a-zçãéíóúê]+\.?\s\d+(:\d+(-\d+)?)?")


def palavras(t):
    return len(str(t).split())


def problemas_teologo(t):
    """Um teólogo citado: obra, link, data e paráfrase com o nome; citação literal só com o link da página."""
    erros = []
    nome = t.get("autor", "?")
    for campo in ("autor", "quem", "obra", "url", "data", "texto"):
        if not t.get(campo):
            erros.append(f"teólogo '{nome}': falta {campo}")
    if t.get("url") and not str(t["url"]).startswith("http"):
        erros.append(f"teólogo '{nome}': url com o link da obra ou do artigo")
    if t.get("texto") and not 25 <= palavras(t["texto"]) <= 110:
        erros.append(f"teólogo '{nome}': texto de 25 a 110 palavras")
    if t.get("citacao") and not str(t.get("citacao_url", t.get("url", ""))).startswith("http"):
        erros.append(f"teólogo '{nome}': citação literal só com o link da página onde a frase foi lida")
    return erros


def problemas_posicoes(c):
    """Estudo de debate: 2 a 4 lados com 2 a 4 teólogos cada. Estudo de passagem: 2 a 4 vozes que comentam o texto."""
    erros = []
    if c.get("tipo") == "passagem":
        vozes = c.get("vozes") or []
        if not 2 <= len(vozes) <= 4:
            erros.append("vozes (O que dizem os teólogos, estudo de passagem): 2 a 4 teólogos que comentam o texto")
        for t in vozes:
            erros += problemas_teologo(t)
    else:
        pos = c.get("posicoes") or []
        if not 2 <= len(pos) <= 4:
            return ["posicoes (O que dizem os teólogos): 2 a 4 lados {lado, resumo, teologos}"]
        for p in pos:
            lado = p.get("lado", "?")
            if not p.get("lado") or not 20 <= palavras(p.get("resumo", "")) <= 90:
                erros.append(f"posicoes '{lado}': lado e resumo de 20 a 90 palavras")
            ts = p.get("teologos") or []
            if not 2 <= len(ts) <= 4:
                erros.append(f"posicoes '{lado}': 2 a 4 teólogos")
            for t in ts:
                erros += problemas_teologo(t)
        if not 1 <= len(c.get("convergencias", [])) <= 5:
            erros.append("convergencias: 1 a 5 pontos em que os lados concordam")
    # linha editorial pentecostal (30/10/2026): todo estudo novo diz onde o portal está
    if c.get("nossa_posicao") or (c.get("publicado_em") or "9999") >= "2026-10-30":
        np_ = c.get("nossa_posicao") or []
        if not 1 <= len(np_) <= 4 or not 60 <= sum(palavras(x) for x in np_) <= 350:
            erros.append("nossa_posicao (Nossa posição ou O olhar pentecostal): 1 a 4 parágrafos, 60 a 350 palavras")
    if c.get("tipo", "debate") not in ("debate", "passagem"):
        erros.append("tipo: debate (questão disputada, com lados) ou passagem (texto que une os cristãos, com vozes)")
    return erros


def problemas(c, publicar=None):
    erros = []
    publicar = c.get("status") == "publicado" if publicar is None else publicar
    for campo in ("slug", "titulo", "passagem", "testamento", "genero", "tagline", "lede", "descricao", "veredito", "selo"):
        if not c.get(campo):
            erros.append(f"falta {campo}")
    erros += sensacionalismo(c.get("titulo", ""))
    if c.get("testamento") and c["testamento"] not in TESTAMENTOS:
        erros.append(f"testamento: {' ou '.join(sorted(TESTAMENTOS))}")
    if c.get("genero") and c["genero"] not in GENEROS:
        erros.append(f"genero: um de {', '.join(sorted(GENEROS))}")
    if c.get("nivel") not in NIVEIS:
        erros.append("nivel: 1 (Iniciante), 2 (Intermediário) ou 3 (Aprofundado)")
    if c.get("selo") and c["selo"] not in SELOS:
        erros.append(f"selo: um de {', '.join(sorted(SELOS))}")
    if not isinstance(c.get("tempo_min"), int):
        erros.append("tempo_min: minutos de leitura e estudo (número)")
    if not 12 <= palavras(c.get("tagline", "")) <= 30:
        erros.append("tagline: 12 a 30 palavras")
    if not 40 <= palavras(c.get("lede", "")) <= 90:
        erros.append("lede: 40 a 90 palavras")
    v = c.get("versiculo_chave") or {}
    if not v.get("texto") or not v.get("referencia") or not v.get("traducao"):
        erros.append("versiculo_chave: texto, referência e tradução (ex.: Almeida Revista e Corrigida)")
    if not 3 <= len(c.get("estrutura", [])) <= 7:
        erros.append("estrutura: 3 a 7 partes [título, texto com a referência]")
    for t, x in c.get("estrutura", []):
        if not REFERENCIA.search(x) and not REFERENCIA.search(t):
            erros.append(f"estrutura '{t}': indique a referência bíblica da parte")
    if not 3 <= len(c.get("destaques", [])) <= 7:
        erros.append("destaques (o que o texto ensina): 3 a 7 [título, explicação]")
    if not 2 <= len(c.get("atencao", [])) <= 6:
        erros.append("atencao (leituras equivocadas comuns): 2 a 6 [gravidade, título, explicação]")
    if not 1 <= len(c.get("contexto", [])) <= 5:
        erros.append("contexto: 1 a 5 parágrafos de contexto histórico e literário")
    if not 1 <= len(c.get("para_quem", [])) <= 4:
        erros.append("para_quem: 1 a 4 itens")
    if len(c.get("fontes", [])) < 3 or any(len(f) != 3 or not str(f[1]).startswith("http") for f in c.get("fontes", [])):
        erros.append("fontes: pelo menos 3 [nome, link, uso] (comentários, dicionários bíblicos, textos acadêmicos)")
    erros += problemas_posicoes(c)
    if c.get("comentaristas"):
        for x in c["comentaristas"]:
            if not x.get("autor") or not x.get("obra"):
                erros.append("comentaristas: toda interpretação citada tem autor e obra")
    im = c.get("imagem") or {}
    if publicar or c.get("status") == "revisao":
        if not im.get("arquivo") or not (portal.CONTEUDO / "imagens" / im["arquivo"]).is_file():
            erros.append("imagem: obra em domínio público, foto com licença livre ou própria (em conteudo/imagens/)")
        elif not im.get("credito") or not im.get("alt"):
            erros.append("imagem: crédito com a licença e texto alternativo")
        if im.get("gerada_por_ia"):
            erros.append("imagem gerada por IA não ilustra estudo")
    if publicar:
        rev = c.get("revisao") or {}
        if not (portal.EQUIPE.get(rev.get("revisor", "")) or {}).get("revisor"):
            erros.append("revisão humana: revisor de config/equipe.json (tools/publicar.py)")
        if not isinstance((c.get("ia") or {}).get("usada"), bool):
            erros.append("ia: declare {\"usada\": true|false, \"uso\": \"...\"}")
        if not c.get("publicado_em"):
            erros.append("publicado_em ausente (tools/publicar.py)")
    return erros


if __name__ == "__main__":
    portal.iniciar()
    arqs = [Path(a) for a in sys.argv[1:]] or sorted((portal.CONTEUDO / "estudos").glob("*.json"))
    ruim = 0
    for a in arqs:
        c = json.loads(a.read_text(encoding="utf-8"))
        e = problemas(c)
        print(("✅ " if not e else "❌ ") + a.name + ("" if not e else "\n   - " + "\n   - ".join(e)))
        for v in avisos(c):
            print("   ⚠️ vício de texto: " + v)
        ruim += bool(e) and c.get("status") in ("publicado", "revisao")
    sys.exit(1 if ruim else 0)
