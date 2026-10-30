"""Confere uma lição do Discipulado contra o padrão da coleção (docs/discipulado/padrao-editorial.md e padrao-de-escrita.md).

Uso: python3 tools/discipulado/checar_licao.py [conteudo/discipulado/<slug>/licao.json ...]   (sem argumentos, todas)
Cada lição é uma pasta conteudo/discipulado/<slug>/ com licao.json (dados de publicação), aluno.md (texto do aluno),
discipulador.md (guia) e dossie.md (pesquisa); auditoria.md só nas lições que tiveram auditoria (a Lição 1; o processo
simplificado de 30/10/2026 dispensa). O texto do aluno passa no medidor
de legibilidade (tools/discipulado/legibilidade.py) ou traz a justificativa num comentário <!-- justificativa: ... -->.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import portal  # noqa: E402
from discipulado.legibilidade import META_ALUNO, META_GUIA, analisar, falhas  # noqa: E402

# seções obrigatórias do texto do aluno, na ordem (padrao-editorial.md, seção 7); o título é o "# " do arquivo
# estrutura editorial do estudo (diretriz do editor, 30/10/2026); o título é o "# " do arquivo
SECOES_ALUNO = ["Questão central", "Introdução", "Fundamentação bíblica", "Desenvolvimento", "Aplicação prática",
                "Perguntas para reflexão", "Resumo", "Continue aprendendo", "Referências"]
CREDITO_NTLH = "Nova Tradução na Linguagem de Hoje"
TRAVESSOES = ("—", "–")
NOTA_MINIMA = 85


def palavras(t):
    return len(re.findall(r"[A-Za-zÀ-ÿ0-9]+", t))


def sem_comentarios(t):
    return re.sub(r"<!--.*?-->", "", t, flags=re.S)


def pasta_da(c):
    return portal.CONTEUDO / "discipulado" / c.get("slug", "")


def problemas(c, publicar=None, pasta=None):
    erros = []
    publicar = c.get("status") == "publicado" if publicar is None else publicar
    pasta = Path(pasta) if pasta else pasta_da(c)
    for campo in ("slug", "titulo", "descricao", "ideia_central"):
        if not c.get(campo):
            erros.append(f"falta {campo}")
    if "numero" in c:
        erros.append("numero: as lições não são numeradas (decisão do editor, 30/10/2026)")
    # tema escolhido pelo que as pessoas perguntam (decisão do editor, 30/10/2026); a primeira lição veio da lista antiga
    if (c.get("publicado_em") or "9999") >= "2026-10-31":
        rel = c.get("relevancia") or {}
        ev = rel.get("evidencias") or []
        if not rel.get("pergunta") or not ev or any(not str(x.get("url", "")).startswith("http") or not x.get("dado") for x in ev):
            erros.append("relevancia: {pergunta, evidencias: [{fonte, url, dado, data}]} com o que mostra que as pessoas perguntam isso")
    if not isinstance(c.get("tempo_min"), int):
        erros.append("tempo_min: minutos de leitura (número)")
    if c.get("titulo") and not c["titulo"].endswith("?"):
        erros.append("titulo: pergunta simples, terminada em '?'")
    # Biblioteca: categoria do catálogo e palavras-chave para a busca (pedido do editor, 30/10/2026)
    cats = {x["slug"] for x in catalogo()["categorias"]}
    if c.get("categoria") not in cats:
        erros.append("categoria: um slug de conteudo/discipulado/base/catalogo.json (" + ", ".join(sorted(cats)) + ")")
    if not 3 <= len(c.get("palavras_chave") or []) <= 12:
        erros.append("palavras_chave: 3 a 12 termos para a busca da Biblioteca")
    # elementos visuais (pedido do editor, 30/10/2026), no padrão das notícias e das resenhas
    rr = c.get("resumo_rapido") or {}
    if not rr.get("resposta") or len(rr.get("ideias") or []) != 3 or not rr.get("texto_central"):
        erros.append("resumo_rapido: {resposta (1 ou 2 frases), ideias (3), texto_central} para o Resumo em 1 minuto")
    vk = c.get("versiculo_chave") or {}
    if not vk.get("texto") or not vk.get("referencia"):
        erros.append("versiculo_chave: {texto (NTLH, lido na fonte), referencia}")
    if not 3 <= len(c.get("contexto") or []) <= 4 or any(len(x) != 3 for x in c.get("contexto") or []):
        erros.append("contexto: 3 a 4 blocos [rótulo, valor, detalhe] para Em poucas linhas")
    if not 2 <= len(c.get("equivocos") or []) <= 4 or any(len(x) != 3 or x[0] not in ("Leve", "Moderada", "Grave") for x in c.get("equivocos") or []):
        erros.append("equivocos: 2 a 4 [gravidade (Leve, Moderada, Grave), título, explicação] para Leituras equivocadas")
    textos = {}
    for nome in ("aluno.md", "discipulador.md", "dossie.md", "auditoria.md"):
        arq = pasta / nome
        if nome == "auditoria.md" and not c.get("auditoria"):
            continue
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
        if len(re.findall(r"^> \[!(chave|termo|atencao|citacao)\]", limpo, re.M)) < 3:
            erros.append("aluno.md: pelo menos 3 destaques no texto (> [!chave], > [!termo], > [!atencao], > [!citacao])")
        # pelo menos duas fontes além da Bíblia (pedido do editor, 30/10/2026: texto de uma fonte só fica suspeito)
        refs = limpo.split("## Referências", 1)[1] if "## Referências" in limpo else ""
        itens = [x for x in re.split(r"\n\s*\n", refs) if x.strip().startswith("- ")]
        fora_biblia = [x for x in itens if re.search(r"\]\(https?://", x) and not re.search(r"bibliaonline\.com\.br|biblegateway\.com|bible\.com", x)]
        if len(fora_biblia) < 2:
            erros.append("aluno.md: pelo menos 2 fontes além da Bíblia em Referências, de autores diferentes, cada uma com link (ideal: 3 ou 4, de tradições diferentes, com a Declaração de Fé das Assembleias de Deus)")
        if CREDITO_NTLH not in limpo:
            erros.append("aluno.md: texto bíblico na NTLH com a linha de crédito da SBB")
        if re.search(r"(?i)\b(lição|estudo) (anterior|seguinte)\b|na próxima lição|como vimos (na|no) (lição|estudo)", limpo):
            erros.append("aluno.md: o estudo é autossuficiente; nada de remeter a lição anterior ou seguinte")
        if re.search(r"\[(verificada|parcial|não verificada)\]", limpo):
            erros.append("aluno.md: marcas de verificação ficam no dossiê e no guia, não no texto do aluno")
        n = palavras(re.sub(r"^>.*$", "", limpo.split("## Referências")[0], flags=re.M))  # sem citação bíblica e sem a lista de referências
        if not 1200 <= n <= 2600:
            erros.append(f"aluno.md: {n} palavras fora das citações (padrão: 1.200 a 2.600)")
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
    if publicar and aud:
        if not isinstance(aud.get("nota"), int) or aud["nota"] < NOTA_MINIMA:
            erros.append(f"auditoria.nota: {NOTA_MINIMA} ou mais na auditoria independente (auditoria.md)")
        if aud.get("eliminatorios"):
            erros.append("auditoria: há problema eliminatório em aberto")
        if not isinstance(aud.get("rodadas"), int):
            erros.append("auditoria.rodadas: número de rodadas até a aprovação")
    if publicar:
        rev = c.get("revisao") or {}
        if not (portal.EQUIPE.get(rev.get("revisor", "")) or {}).get("revisor"):
            erros.append("revisão: revisor de config/equipe.json (tools/publicar.py)")
        if not isinstance((c.get("ia") or {}).get("usada"), bool):
            erros.append("ia: declare {\"usada\": true|false, \"uso\": \"...\"}")
        if not c.get("publicado_em"):
            erros.append("publicado_em ausente (tools/publicar.py)")
    return erros


def catalogo():
    return json.loads((portal.CONTEUDO / "discipulado" / "base" / "catalogo.json").read_text(encoding="utf-8"))


def problemas_catalogo():
    """Trilhas sem conteúdo duplicado: cada item é o slug de um estudo que existe ou {titulo} em preparação."""
    erros, slugs = [], {p.parent.name for p in licoes()}
    cat = catalogo()
    for t in cat["trilhas"]:
        vistos = set()
        for it in t["estudos"]:
            k = it if isinstance(it, str) else (it.get("titulo") if isinstance(it, dict) else None)
            if not k:
                erros.append(f"trilha {t['slug']}: item sem slug nem titulo")
            elif isinstance(it, str) and it not in slugs:
                erros.append(f"trilha {t['slug']}: estudo '{it}' não existe em conteudo/discipulado/")
            elif k in vistos:
                erros.append(f"trilha {t['slug']}: '{k}' repetido")
            vistos.add(k)
    if len({x["slug"] for x in cat["categorias"]}) != len(cat["categorias"]):
        erros.append("catalogo: categorias com slug repetido")
    return erros


def licoes():
    return sorted(p for p in (portal.CONTEUDO / "discipulado").glob("*/licao.json") if p.parent.name != "base")


if __name__ == "__main__":
    portal.iniciar()
    arqs = [Path(a) for a in sys.argv[1:]] or licoes()
    ruim = 0
    for e_ in problemas_catalogo():
        print("❌ catálogo: " + e_)
        ruim += 1
    for a in arqs:
        c = json.loads(a.read_text(encoding="utf-8"))
        e = problemas(c, pasta=a.parent)
        print(("✅ " if not e else "❌ ") + a.parent.name + ("" if not e else "\n   - " + "\n   - ".join(e)))
        ruim += bool(e) and c.get("status") in ("publicado", "revisao")
    sys.exit(1 if ruim else 0)
