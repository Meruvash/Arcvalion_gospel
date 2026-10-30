"""Confere uma notícia contra o padrão editorial das notícias (docs/PADRAO_EDITORIAL.md).

Uso: python3 tools/noticias/checar_noticia.py [conteudo/noticias/<arquivo>.json ...]  (sem argumentos, todas)
Sai com erro se alguma nota não passar; tools/build_home.py usa a mesma função e se recusa a publicar.
Cópia do checar_noticia.py do Elite Boardgamers (mesmas faixas de palavras, selos, crivo, foto obrigatória, regra da
manchete e vícios de texto), trocadas as regras de jogos (edição nacional, Ludopedia) pelas do jornalismo cristão:
fonte primária identificável, citação atribuída, nada de fonte anônima nem de caça-clique, revisão humana registrada.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import portal  # noqa: E402

if not portal.CFG:  # importado pelo build_home.py do Elite, que não inicia a configuração
    portal.iniciar()
from editorial.vicios import avisos, risco_juridico, sensacionalismo  # noqa: E402

# selo da nota (a "Nossa opinião"): no Elite eram Vale a compra, Vale acompanhar, Para fãs do jogo base, Com ressalvas, Informativo
SELOS = {"Boa notícia", "Vale acompanhar", "Para refletir", "Motivo de alerta", "Informativo"}
FAIXAS = {"titulo": (8, 16), "lide": (35, 70), "por_que_importa": (30, 70), "no_brasil": (25, 80), "veredito": (20, 60)}
STATUS = {"rascunho", "revisao", "publicado", "despublicado"}
# fonte anônima genérica não sustenta notícia
ANONIMO = re.compile(r"\b(segundo fontes|fontes (ouvidas|próximas|consultadas)|nos bastidores|comenta-se que|há rumores|circula nas redes que)\b", re.I)
# Loja de varejo não aparece no texto (regra herdada do Elite: seria publicidade de graça); só nas fontes.
LOJAS = re.compile(r"\b(Amazon|Mercado Livre|Magalu|Magazine Luiza|Shopee|Americanas|Submarino|Casas Bahia|AliExpress|Shein)\b", re.I)
FOTO_MIN = 500
MINIMO = 3   # notas por dia na fase de teste (o Elite usa 5)


def palavras(t):
    return len(t.split())


def textos(n):
    for campo in ("titulo", "lide", "por_que_importa", "no_brasil", "veredito"):
        yield n.get(campo) or ""
    yield from n.get("corpo", [])
    yield from n.get("para_quem", [])
    yield from n.get("nao_e_para", [])
    yield from (c.get("texto", "") for c in n.get("critica", []))


def checar_foto(n):
    im = n.get("imagem") or {}
    # como no Elite: noticias/capas/<arquivo>; o conteúdo fictício de exemplos/ guarda as fotos em exemplos/conteudo/imagens
    pasta = portal.CONTEUDO / "imagens" if portal.EXEMPLO else portal.ROOT / "noticias"
    arq = pasta / im["arquivo"] if im.get("arquivo") else None
    if not arq or not arq.is_file():
        return ["sem foto: notícia não sai sem foto (licença livre, divulgação oficial ou própria, com crédito)"]
    try:
        from PIL import Image
        with Image.open(arq) as f:
            lado = min(f.size)
    except ImportError:
        return []
    except Exception:
        return [f"foto ilegível ({im['arquivo']})"]
    if lado < FOTO_MIN:
        return [f"foto pequena ({lado} px no lado menor; mínimo {FOTO_MIN})"]
    if not im.get("credito"):
        return ["foto sem crédito"]
    if im.get("gerada_por_ia"):
        return ["imagem gerada por IA não ilustra notícia"]
    return []


def checar_revisao(n):
    """Revisão humana antes de publicar (premissa do portal): revisor real de config/equipe.json e uso de IA declarado."""
    erros = []
    rev = n.get("revisao") or {}
    p = portal.EQUIPE.get(rev.get("revisor", ""))
    if not p or not p.get("revisor"):
        erros.append("revisão humana: 'revisao.revisor' precisa ser pessoa revisora de config/equipe.json (tools/publicar.py)")
    ia = n.get("ia")
    if not isinstance(ia, dict) or not isinstance(ia.get("usada"), bool):
        erros.append("ia: declare {\"usada\": true|false, \"uso\": \"...\"}")
    return erros


def problemas(n, publicar=None):
    erros = []
    publicar = n.get("status", "publicado") in ("publicado",) if publicar is None else publicar
    if n.get("status", "rascunho") not in STATUS:
        erros.append(f"status inválido: {n.get('status')!r}")
    if not portal.editoria(n.get("categoria", "")) and not any(x["nome"] == n.get("categoria") for x in portal.EDITORIAS):
        erros.append(f"categoria inexistente: {n.get('categoria')!r} (use o nome de uma editoria de config/editorias.json)")
    for campo, (a, b) in FAIXAS.items():
        if not n.get(campo):
            erros.append(f"falta {campo}")
        elif not a <= palavras(n[campo]) <= b:
            erros.append(f"{campo} com {palavras(n[campo])} palavras (padrão: {a} a {b})")
    erros += sensacionalismo(n.get("titulo", ""))
    if n.get("selo") not in SELOS:
        erros.append(f"selo inválido: {n.get('selo')!r} ({', '.join(sorted(SELOS))})")
    corpo = sum(palavras(p) for p in n.get("corpo", []))
    if not 1 <= len(n.get("corpo", [])) <= 3 or not 40 <= corpo <= 200:
        erros.append(f"contexto com {len(n.get('corpo', []))} parágrafos e {corpo} palavras (padrão: 1 a 3, 40 a 200)")
    nums = n.get("numeros", [])
    if not 2 <= len(nums) <= 4 or any(len(x) != 3 or not x[2] for x in nums):
        erros.append("números: 2 a 4 itens [valor, rótulo, fonte], todos com fonte")
    crit = n.get("critica", [])
    if len(crit) > 3 or any(not c.get("fonte") or not c.get("texto") for c in crit) or (not crit and n.get("selo") != "Informativo"):
        erros.append("o que dizem: 1 a 3 posições com fonte e texto (só nota Informativo pode sair sem)")
    if not 1 <= len(n.get("para_quem", [])) <= 3 or not 1 <= len(n.get("nao_e_para", [])) <= 3:
        erros.append("para_quem (O que muda para você): 1 a 3 itens; nao_e_para (Pontos de atenção): 1 a 3 itens")
    fontes = n.get("fontes", [])
    if len(fontes) < 2 or any(not f.get("url") or not f.get("data") or not f.get("nome") for f in fontes):
        erros.append("fontes: pelo menos 2, com nome, link e data")
    if not any(f.get("tipo") == "primaria" for f in fontes):
        erros.append("fontes: pelo menos uma primária (documento, órgão oficial, nota da instituição, entrevista), marcada com \"tipo\": \"primaria\"")
    for t in textos(n):
        m = ANONIMO.search(t)
        if m:
            erros.append(f"fonte não identificável ({m.group(0)!r}): diga quem afirma e onde")
            break
    for t in list(textos(n)) + [x[1] for x in nums if len(x) > 1]:
        m = LOJAS.search(t)
        if m:
            erros.append(f"texto cita a loja {m.group(0)!r}: a loja fica só nas fontes")
            break
    for c in crit:
        if c.get("citacao") and not c.get("url"):
            erros.append(f"citação literal de {c.get('fonte')!r} sem 'url' da página onde a frase está")
    if publicar or n.get("status") == "revisao":
        erros += checar_foto(n)
    if not isinstance(n.get("crivo", {}).get("pontos"), int):
        erros.append("crivo sem pontos")
    # crivo jurídico (30/10/2026): opinião forte sem abrir espaço para processo
    erros += risco_juridico(n)[0]
    if (publicar or n.get("status") == "revisao") and len(str(n.get("checagem_juridica", "")).split()) < 12:
        erros.append("checagem_juridica: diga em uma ou duas frases o que foi conferido na leitura hostil "
                     "(nenhuma imputação de crime ou intenção sem fonte oficial, nenhuma frase que ofenda a honra de pessoa "
                     "ou discrimine grupo, ironia só sobre a decisão)")
    if publicar:
        erros += checar_revisao(n)
    return erros


def checar_dia(ns):
    """A manchete de cada dia precisa ser a nota de maior pontuação do dia (regra do Elite); a partir de 5 notas no dia,
    pelo menos 2 de cada 5 saem com Opinião Forte (docs/PADRAO_EDITORIAL.md, 30/10/2026)."""
    erros = []
    por_dia = {}
    for n in ns:
        por_dia.setdefault(n["data"], []).append(n)
    for dia, lista in por_dia.items():
        pts = [n["crivo"].get("pontos", 0) for n in lista]
        if any(n.get("manchete") and n["crivo"].get("pontos", 0) < max(pts) for n in lista):
            erros.append(f"{dia}: a manchete precisa ser a nota de maior pontuação do dia")
        fortes = sum(bool(n.get("opiniao_forte")) for n in lista)
        if len(lista) >= 5 and fortes < 2 * (len(lista) // 5):
            erros.append(f"{dia}: {fortes} de {len(lista)} notas com Opinião Forte; o padrão é 2 de cada 5")
    return erros


if __name__ == "__main__":
    portal.iniciar()
    arqs = [Path(a) for a in sys.argv[1:]] or sorted((portal.CONTEUDO / "noticias").glob("*.json"))
    ruim = 0
    todas = []
    for a in arqs:
        n = json.loads(a.read_text(encoding="utf-8"))
        todas.append(n)
        e = problemas(n, publicar=n.get("status") == "publicado")
        print(("✅ " if not e else "❌ ") + a.name + f" [{n.get('status', 'publicado')}]" + ("" if not e else "\n   - " + "\n   - ".join(e)))
        for v in risco_juridico(n)[1]:
            print("   ⚠️ " + v)
        for v in avisos(n):
            print("   ⚠️ vício de texto: " + v)
        ruim += bool(e) and n.get("status") in ("publicado", "revisao")
    for e in checar_dia([n for n in todas if n.get("status") == "publicado"]):
        print("❌ " + e)
        ruim += 1
    sys.exit(1 if ruim else 0)
