"""Confere uma lição do Discipulado contra o padrão da coleção (docs/discipulado/padrao-editorial.md e padrao-de-escrita.md).

Uso: python3 tools/discipulado/checar_licao.py [conteudo/discipulado/<NN-slug>/licao.json ...]   (sem argumentos, todas)
Cada lição é uma pasta conteudo/discipulado/<NN-slug>/ com licao.json (dados de publicação), aluno.md (texto do aluno),
discipulador.md (guia), dossie.md (pesquisa) e auditoria.md (auditoria independente). O texto do aluno passa no medidor
de legibilidade (tools/discipulado/legibilidade.py) ou traz a justificativa num comentário <!-- justificativa: ... -->.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import portal  # noqa: E402
from discipulado.legibilidade import META_ALUNO, META_GUIA, analisar, falhas  # noqa: E402

MODULOS = {1: "Conhecendo a fé cristã", 2: "Aprendendo a caminhar", 3: "Crescendo como discípulo"}
# seções obrigatórias do texto do aluno, na ordem (padrao-editorial.md, seção 7); o título é o "# " do arquivo
SECOES_ALUNO = ["O que vamos aprender?", "Para começar", "Texto bíblico principal", "Entendendo a Palavra", "Entendendo melhor",
                "A fé na vida real", "Vamos conversar?", "Desafio da semana", "Para guardar no coração", "Resumindo"]
CREDITO_NTLH = "Nova Tradução na Linguagem de Hoje"
TRAVESSOES = ("—", "–")
NOTA_MINIMA = 85


def palavras(t):
    return len(re.findall(r"[A-Za-zÀ-ÿ0-9]+", t))


def sem_comentarios(t):
    return re.sub(r"<!--.*?-->", "", t, flags=re.S)


def pasta_da(c):
    return portal.CONTEUDO / "discipulado" / f'{c.get("numero", 0):02d}-{c.get("slug", "")}'


def problemas(c, publicar=None, pasta=None):
    erros = []
    publicar = c.get("status") == "publicado" if publicar is None else publicar
    pasta = Path(pasta) if pasta else pasta_da(c)
    for campo in ("slug", "titulo", "descricao", "ideia_central"):
        if not c.get(campo):
            erros.append(f"falta {campo}")
    if c.get("numero") not in range(1, 13):
        erros.append("numero: 1 a 12 (arquitetura da coleção)")
    if c.get("modulo") not in MODULOS:
        erros.append("modulo: 1, 2 ou 3")
    if not isinstance(c.get("tempo_min"), int):
        erros.append("tempo_min: duração do encontro em minutos (número)")
    if c.get("titulo") and not c["titulo"].endswith("?"):
        erros.append("titulo: pergunta simples, terminada em '?'")
    textos = {}
    for nome in ("aluno.md", "discipulador.md", "dossie.md", "auditoria.md"):
        arq = pasta / nome
        if not arq.is_file():
            erros.append(f"falta {pasta.name}/{nome}")
        else:
            textos[nome] = arq.read_text(encoding="utf-8")
    for nome, t in textos.items():
        if any(x in t for x in TRAVESSOES):
            erros.append(f"{nome}: travessão (proibido em todo texto da coleção)")
    aluno = textos.get("aluno.md")
    if aluno:
        limpo = sem_comentarios(aluno)
        h1 = re.search(r"^# (.+)$", limpo, re.M)
        if not h1 or h1.group(1).strip() != c.get("titulo"):
            erros.append("aluno.md: o título '# ' precisa ser igual ao titulo do licao.json")
        achadas = [m.strip() for m in re.findall(r"^## (.+)$", limpo, re.M)]
        if achadas != SECOES_ALUNO:
            erros.append("aluno.md: seções '## ' na ordem do padrão: " + " | ".join(SECOES_ALUNO))
        if CREDITO_NTLH not in limpo:
            erros.append("aluno.md: texto bíblico na NTLH com a linha de crédito da SBB")
        if re.search(r"\[(verificada|parcial|não verificada)\]", limpo):
            erros.append("aluno.md: marcas de verificação ficam no dossiê e no guia, não no texto do aluno")
        n = palavras(re.sub(r"^>.*$", "", limpo, flags=re.M))  # sem o texto bíblico em citação
        if not 1000 <= n <= 1500:
            erros.append(f"aluno.md: {n} palavras fora das citações (padrão: 1.000 a 1.500)")
        f = falhas(analisar(aluno, META_ALUNO), META_ALUNO)
        if f and "justificativa:" not in aluno:
            erros.append("aluno.md reprovado no medidor de legibilidade: " + "; ".join(f))
    guia = textos.get("discipulador.md")
    if guia:
        f = falhas(analisar(guia, META_GUIA), META_GUIA)
        if f and "justificativa:" not in guia:
            erros.append("discipulador.md reprovado no medidor (metas do guia): " + "; ".join(f))
        if not re.search(r"\[(verificada|parcial)\]", guia):
            erros.append("discipulador.md: referências com a classificação [verificada] ou [parcial]")
    aud = c.get("auditoria") or {}
    if publicar:
        if not isinstance(aud.get("nota"), int) or aud["nota"] < NOTA_MINIMA:
            erros.append(f"auditoria.nota: {NOTA_MINIMA} ou mais na auditoria independente (auditoria.md)")
        if aud.get("eliminatorios"):
            erros.append("auditoria: há problema eliminatório em aberto")
        if not isinstance(aud.get("rodadas"), int):
            erros.append("auditoria.rodadas: número de rodadas até a aprovação")
        rev = c.get("revisao") or {}
        if not (portal.EQUIPE.get(rev.get("revisor", "")) or {}).get("revisor"):
            erros.append("revisão: revisor de config/equipe.json (tools/publicar.py)")
        if not isinstance((c.get("ia") or {}).get("usada"), bool):
            erros.append("ia: declare {\"usada\": true|false, \"uso\": \"...\"}")
        if not c.get("publicado_em"):
            erros.append("publicado_em ausente (tools/publicar.py)")
    return erros


def licoes():
    return sorted((portal.CONTEUDO / "discipulado").glob("[0-9][0-9]-*/licao.json"))


if __name__ == "__main__":
    portal.iniciar()
    arqs = [Path(a) for a in sys.argv[1:]] or licoes()
    ruim = 0
    for a in arqs:
        c = json.loads(a.read_text(encoding="utf-8"))
        e = problemas(c, pasta=a.parent)
        print(("✅ " if not e else "❌ ") + a.parent.name + ("" if not e else "\n   - " + "\n   - ".join(e)))
        ruim += bool(e) and c.get("status") in ("publicado", "revisao")
    sys.exit(1 if ruim else 0)
