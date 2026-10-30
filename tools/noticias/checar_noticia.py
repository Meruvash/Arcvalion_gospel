"""Confere uma notícia contra o padrão editorial das notícias (docs/PADRAO_EDITORIAL.md).

Uso: python3 tools/noticias/checar_noticia.py [conteudo/noticias/<arquivo>.json ...]  (sem argumentos, todas)
Sai com erro se alguma nota não passar; tools/build_home.py usa a mesma função e se recusa a publicar.
Cópia do checar_noticia.py do Elite Boardgamers (mesmas faixas de palavras, selos, crivo, foto obrigatória, regra da
manchete e vícios de texto), trocadas as regras de jogos (edição nacional, Ludopedia) pelas do jornalismo cristão:
fonte primária identificável, citação atribuída, nada de fonte anônima nem de caça-clique, revisão humana registrada.
"""
import json
import re
from urllib.parse import urlparse
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
# referência bíblica ("Mateus 25.35", "2 Coríntios 8:21"): na Nossa opinião, o versículo vai no campo próprio, no fim
REF_BIBLICA = re.compile(r"\b(?:[1-3] ?)?[A-ZÁÉÍÓÚ][a-záéíóúâêôãõç]+ \d{1,3}[.:]\d{1,3}\b")
TRADUCOES = {"ARC", "ARA", "NVI", "NAA", "NVT", "ACF", "NTLH", "AS21", "KJA"}
FOTO_MIN = 500
MINIMO = 3   # notas por dia na fase de teste (o Elite usa 5)
# crivo editorial: motor de relevância de 0 a 100 (config/relevancia.json, pedido de 30/10/2026; substituiu o de 0 a 20)
TRILHAS = {"quente", "atemporal"}
ABRANGENCIAS = {"nacional", "rondonia", "porto-velho", "internacional"}


def faixa(pontos):
    """Nome da faixa de relevância (config/relevancia.json): prioridade máxima, alta, moderada, baixa."""
    return next(nome for minimo, nome in portal.RELEVANCIA["faixas"] if pontos >= minimo)


def checar_config(r):
    """Os pesos podem mudar na configuração, mas precisam somar 100."""
    soma = sum(c["peso"] for c in r["criterios"])
    return [] if soma == 100 else [f"config/relevancia.json: os pesos somam {soma}, precisam somar 100"]


def checar_tema(t, r):
    """Eliminatório 10 (30/10/2026): o fato precisa ser sobre um eixo do portal (config/relevancia.json, 'temas').
    Notícia de cidade sem esse eixo não entra, por mais local que seja; versículo na análise não vale como tema."""
    temas = [k for k in r.get("temas", {}) if not k.startswith("_")]
    if not isinstance(t, dict) or t.get("eixo") not in temas:
        return [f"crivo: 'tema' com o eixo do fato ({', '.join(temas)}) e o porquê; sem eixo temático a pauta não entra (eliminatório 10)"]
    if len(str(t.get("porque", "")).split()) < r["justificativa_min_palavras"]:
        return ["crivo: justifique o tema com o que, no próprio fato, é desse eixo ('tema.porque')"]
    return []


TETO_PUBLICO = {"valor": 8, "viral": 7, "cristao": 5}


def checar_publico(p):
    """Crivo público de até 20 pontos (docs/CRIVO_NOTICIAS.md, seção 4.1): é o que a página mostra em "Por que esta
    notícia entrou". Cada critério termina com os pontos entre parênteses, e a soma bate com o total e com os eixos."""
    if not isinstance(p, dict) or not isinstance(p.get("pontos"), int) or not isinstance(p.get("criterios"), list) or not p["criterios"]:
        return ["crivo: falta 'publico' {\"pontos\", \"eixos\", \"criterios\"}, o crivo de até 20 pontos que a página mostra (seção 4.1)"]
    pts = [re.search(r"\((\d+)\)\s*$", str(x)) for x in p["criterios"]]
    if not all(pts):
        return ["crivo.publico: cada critério termina com os pontos entre parênteses, como 'Proximidade: nacional (2)'"]
    erros = []
    if sum(int(m.group(1)) for m in pts) != p["pontos"]:
        erros.append(f"crivo.publico: os critérios somam {sum(int(m.group(1)) for m in pts)}, diferente de {p['pontos']}")
    eixos = p.get("eixos") if isinstance(p.get("eixos"), dict) else {}
    if set(eixos) != set(TETO_PUBLICO) or any(not isinstance(eixos[k], int) or not 0 <= eixos[k] <= t for k, t in TETO_PUBLICO.items()):
        erros.append("crivo.publico: 'eixos' {valor até 8, viral até 7, cristao até 5}")
    elif sum(eixos.values()) != p["pontos"]:
        erros.append("crivo.publico: a soma dos eixos difere do total")
    return erros


def checar_crivo(c, data=""):
    """Motor de relevância: cada critério de 0 até o peso, com justificativa em fatos concretos; o total decide se a nota
    sai (publicar_se_faltar), e a comprovação tem piso próprio, porque pontuação alta não substitui verificação.
    Notas de antes da vigência só precisam da estrutura: o corte não é aplicado a quem já estava no ar."""
    r = portal.RELEVANCIA
    erros = checar_config(r)
    if c.get("escala") != 100 and data < r["vigencia"]:  # crivo antigo (0 a 20) de nota que já estava no ar
        return erros + ([] if isinstance(c.get("pontos"), int) else ["crivo sem pontos"])
    if c.get("escala") != 100 or not isinstance(c.get("pontos"), int):
        return erros + ["crivo: use o motor de 0 a 100 ({\"escala\": 100, \"pontos\", \"criterios\": {...}}), docs/CRIVO_NOTICIAS.md"]
    crit = c.get("criterios") if isinstance(c.get("criterios"), dict) else {}
    soma = 0
    for k in r["criterios"]:
        item = crit.get(k["chave"]) if isinstance(crit.get(k["chave"]), dict) else {}
        v = item.get("pontos")
        if not isinstance(v, int) or not 0 <= v <= k["peso"]:
            erros.append(f"crivo: {k['nome']} ({k['chave']}) precisa ser inteiro de 0 a {k['peso']}")
            continue
        soma += v
        if len(str(item.get("porque", "")).split()) < r["justificativa_min_palavras"]:
            erros.append(f"crivo: justifique {k['nome']} com os elementos concretos da pauta ('porque')")
    if not erros and soma != c["pontos"]:
        erros.append(f"crivo: pontos ({c['pontos']}) diferente da soma dos critérios ({soma})")
    if not erros and data >= r["vigencia"]:
        if c["pontos"] < r["publicar_se_faltar"]:
            erros.append(f"crivo: {c['pontos']} pontos ({faixa(c['pontos'])}), abaixo do corte de {r['publicar_se_faltar']}")
        if crit["comprovacao"]["pontos"] < r["comprovacao_minima"]:
            erros.append(f"crivo: comprovação {crit['comprovacao']['pontos']}, abaixo do mínimo de {r['comprovacao_minima']}: "
                         "volte à apuração (fonte oficial, documento ou segunda reportagem independente)")
    erros += checar_tema(c.get("tema"), r)
    erros += checar_publico(c.get("publico"))
    if c.get("trilha") not in TRILHAS:
        erros.append("crivo: 'trilha' precisa ser quente ou atemporal")
    if c.get("abrangencia") not in ABRANGENCIAS:
        erros.append("crivo: 'abrangencia' precisa ser nacional, rondonia, porto-velho ou internacional")
    o = c.get("origem")
    if o is not None and (not isinstance(o, dict) or not o.get("nome") or not o.get("url")):
        erros.append("crivo: 'origem' (portal onde a pauta nasceu) precisa de nome e url")
    return erros


def checar_versiculo(n):
    """Nossa opinião é posicionamento concreto sobre o fato; o versículo, se houver, fica embaixo (pedido de 30/10/2026)."""
    erros = []
    if REF_BIBLICA.search(n.get("veredito", "")):
        erros.append("veredito com versículo: a Nossa opinião diz o posicionamento do portal sobre o fato; "
                     "o versículo, se couber, vai no campo 'versiculo' {texto, referencia, traducao}, exibido no fim")
    v = n.get("versiculo")
    if v is not None:
        if not isinstance(v, dict) or not v.get("texto") or not REF_BIBLICA.fullmatch(v.get("referencia", "")):
            erros.append("versiculo: {\"texto\": \"...\", \"referencia\": \"Mateus 25.35\", \"traducao\": \"ARC\"}")
        elif v.get("traducao") not in TRADUCOES:
            erros.append(f"versiculo: tradução {v.get('traducao')!r} fora da lista ({', '.join(sorted(TRADUCOES))})")
    return erros


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
    if n.get("descricao_seo") and not 70 <= len(n["descricao_seo"]) <= 155:
        erros.append(f"descricao_seo com {len(n['descricao_seo'])} caracteres (padrão: 70 a 155)")
    for x in n.get("estudos", []):
        slug = x.get("estudo") if isinstance(x, dict) else x
        if not (portal.CONTEUDO / "estudos" / f"{slug}.json").exists():
            erros.append(f"estudos: {slug!r} não é um estudo de conteudo/estudos/ (use o slug do estudo)")
    erros += checar_versiculo(n)
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
    # regra local (docs/CRIVO_NOTICIAS.md, 30/10/2026): em Rondônia e Porto Velho, reportagem própria de veículo local
    # confiável vale como base se houver confirmação de outro veículo independente ou de fonte oficial
    locais = {re.sub(r"^www\.", "", urlparse(f.get("url", "")).netloc) for f in fontes if f.get("tipo") == "reportagem_local"}
    oficiais = [f for f in fontes if f.get("tipo") == "primaria"]
    local_ok = n.get("crivo", {}).get("abrangencia") in ("rondonia", "porto-velho") and locais and (len(locais) >= 2 or oficiais)
    if not oficiais and not local_ok:
        erros.append("fontes: pelo menos uma primária (documento, órgão oficial, nota da instituição, entrevista), marcada com \"tipo\": \"primaria\"; "
                     "em Rondônia e Porto Velho, ou duas reportagens próprias de veículos locais diferentes (\"tipo\": \"reportagem_local\")")
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
    erros += checar_crivo(n.get("crivo") or {}, n.get("data", ""))
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
        # as notas de antes da vigência têm crivo de 0 a 20: a manchete se compara com as notas da mesma escala
        escala = lambda x: x["crivo"].get("escala", 20)  # noqa: E731
        if any(n.get("manchete") and n["crivo"].get("pontos", 0) < max(o["crivo"].get("pontos", 0) for o in lista if escala(o) == escala(n))
               for n in lista):
            erros.append(f"{dia}: a manchete precisa ser a nota de maior pontuação do dia")
        piso = portal.RELEVANCIA.get("manchete", 0)
        if dia >= portal.RELEVANCIA.get("vigencia", "") and any(n.get("manchete") and n["crivo"].get("pontos", 0) < piso for n in lista):
            erros.append(f"{dia}: manchete precisa de {piso} pontos ou mais no crivo de 0 a 100")
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
