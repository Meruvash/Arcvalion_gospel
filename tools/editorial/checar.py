"""Confere uma matéria contra o padrão editorial (docs/PADRAO_EDITORIAL.md). Portado de tools/noticias/checar_noticia.py.

Uso: python3 tools/editorial/checar.py [--exemplo] [conteudo/artigos/<arquivo>.json ...]   (sem arquivos, todas)
Sai com erro se alguma matéria publicada (ou pronta para revisão) não passar; tools/build.py usa a mesma função e se
recusa a publicar. Rascunhos são conferidos só como aviso.

As regras traduzem as premissas do portal em checagens automáticas:
- notícia com fontes identificáveis e verificáveis (link + data de consulta, pelo menos uma fonte primária);
- citação sempre atribuída (quem disse, cargo e a fonte onde a frase está);
- fato separado de opinião (opinião só no tipo "opiniao", com autor identificado; análise da redação só no bloco rotulado);
- revisão humana obrigatória antes de publicar (revisor real de config/equipe.json), com o uso de IA declarado;
- conteúdo patrocinado e links de afiliado sempre identificados;
- correções registradas com data;
- título sem caça-clique; nada de fonte anônima genérica ("segundo fontes").
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import portal  # noqa: E402
from vicios import avisos, sensacionalismo  # noqa: E402

STATUS = {"rascunho", "revisao", "publicado", "despublicado"}
FAIXAS = {"titulo": (5, 20), "linha_fina": (8, 40)}
FAIXA_LIDE = (20, 75)
# fonte anônima genérica não sustenta notícia (premissa 2); a exceção, quando houver, é decisão do editor em texto próprio
ANONIMO = re.compile(r"\b(segundo fontes|fontes (ouvidas|próximas|consultadas pel[oa] reportagem)|nos bastidores|comenta-se que|"
                     r"há rumores|circula nas redes que|dizem que)\b", re.I)
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def palavras(t):
    return len(str(t).split())


def iso_ok(v):
    try:
        datetime.fromisoformat(v)
        return True
    except (TypeError, ValueError):
        return False


def textos(a):
    for campo in ("titulo", "linha_fina", "lide", "analise"):
        if a.get(campo):
            yield a[campo]
    for b in a.get("corpo", []):
        if isinstance(b, str):
            yield b
        elif isinstance(b, dict):
            yield from (v for k, v in b.items() if isinstance(v, str) and k in ("citacao", "intertitulo", "texto"))


def checar_corpo(a, erros):
    corpo = a.get("corpo") or []
    if not corpo:
        erros.append("corpo vazio")
        return
    n_fontes = len(a.get("fontes") or [])
    total = 0
    for i, b in enumerate(corpo):
        if isinstance(b, str):
            total += palavras(b)
            continue
        if not isinstance(b, dict):
            erros.append(f"corpo[{i}]: bloco inválido")
        elif "citacao" in b:
            # premissa 5: declaração atribuída corretamente
            if not b.get("autor"):
                erros.append(f"corpo[{i}]: citação sem autor")
            if not isinstance(b.get("fonte"), int) or not 0 <= b["fonte"] < n_fontes:
                erros.append(f"corpo[{i}]: citação precisa apontar a fonte onde a frase está (índice em 'fontes')")
            total += palavras(b["citacao"])
        elif "intertitulo" in b:
            if not 2 <= palavras(b["intertitulo"]) <= 12:
                erros.append(f"corpo[{i}]: intertítulo com {palavras(b['intertitulo'])} palavras (2 a 12)")
        else:
            erros.append(f"corpo[{i}]: bloco desconhecido (use texto, {{\"intertitulo\"}} ou {{\"citacao\", \"autor\", \"fonte\"}})")
    minimo = 120 if a.get("tipo") in ("noticia", "analise", "opiniao", "patrocinado") else 250
    if total < minimo:
        erros.append(f"corpo com {total} palavras (mínimo {minimo} para {a.get('tipo')})")


def checar_fontes(a, erros):
    fontes = a.get("fontes") or []
    tipo = a.get("tipo")
    for i, f in enumerate(fontes):
        if not f.get("nome") or not str(f.get("url", "")).startswith(("https://", "http://")) or not f.get("data"):
            erros.append(f"fontes[{i}]: precisa de nome, link (http/https) e data de consulta")
        if f.get("tipo") not in ("primaria", "secundaria"):
            erros.append(f"fontes[{i}]: tipo precisa ser 'primaria' (documento, órgão, pessoa envolvida) ou 'secundaria' (outro veículo)")
    minimo = {"noticia": 2, "analise": 2, "explicativo": 1, "opiniao": 1, "patrocinado": 0}.get(tipo, 2)
    if len(fontes) < minimo:
        erros.append(f"fontes: {tipo} precisa de pelo menos {minimo} fonte(s) com link e data")
    if tipo in ("noticia", "analise") and not any(f.get("tipo") == "primaria" for f in fontes):
        erros.append("fontes: notícia precisa de pelo menos uma fonte primária (documento oficial, nota da instituição, entrevista)")


def checar_revisao(a, erros):
    """Premissa 6: nada vai ao ar sem revisão humana; o uso de IA fica declarado."""
    rev = a.get("revisao") or {}
    pessoa = portal.EQUIPE.get(rev.get("revisor", ""))
    if not pessoa or not pessoa.get("revisor"):
        erros.append("revisão humana: 'revisao.revisor' precisa ser uma pessoa revisora de config/equipe.json (use tools/publicar.py)")
    if not iso_ok(rev.get("data")):
        erros.append("revisão humana: falta 'revisao.data' (ISO 8601)")
    ia = a.get("ia")
    if not isinstance(ia, dict) or not isinstance(ia.get("usada"), bool):
        erros.append("ia: declare {\"usada\": true|false, \"uso\": \"...\"} (aparece no quadro de transparência)")
    elif ia["usada"] and not ia.get("uso"):
        erros.append("ia: diga em que a IA ajudou (pesquisa, organização, primeira versão do texto...)")
    if not iso_ok(a.get("publicado_em")):
        erros.append("publicado_em ausente ou fora do formato ISO 8601")
    if a.get("atualizado_em") and (not iso_ok(a["atualizado_em"]) or (iso_ok(a.get("publicado_em")) and a["atualizado_em"] < a["publicado_em"])):
        erros.append("atualizado_em inválido ou anterior a publicado_em")
    if rev.get("revisor") and rev.get("revisor") == a.get("autor") and a.get("tipo") in ("noticia", "analise"):
        erros.append("revisão humana: quem revisa não pode ser quem assina a notícia")


def problemas(a, publicar=None):
    """Erros que impedem a matéria de ir ao ar. publicar=None decide pelo status (publicado/revisao)."""
    erros = []
    publicar = a.get("status") in ("publicado", "revisao") if publicar is None else publicar
    if not SLUG.match(a.get("slug", "")):
        erros.append("slug inválido (letras minúsculas, números e hífens)")
    if a.get("status") not in STATUS:
        erros.append(f"status inválido: {a.get('status')!r} ({', '.join(sorted(STATUS))})")
    if a.get("tipo") not in portal.TIPOS:
        erros.append(f"tipo inválido: {a.get('tipo')!r} ({', '.join(portal.TIPOS)})")
    if not portal.editoria(a.get("editoria", "")):
        erros.append(f"editoria inexistente: {a.get('editoria')!r} (veja config/editorias.json)")
    for campo, (lo, hi) in FAIXAS.items():
        if not a.get(campo):
            erros.append(f"falta {campo}")
        elif not lo <= palavras(a[campo]) <= hi:
            erros.append(f"{campo} com {palavras(a[campo])} palavras (padrão: {lo} a {hi})")
    if a.get("titulo"):
        erros += sensacionalismo(a["titulo"])
        if a.get("titulo_seo"):
            erros += sensacionalismo(a["titulo_seo"])
    if a.get("tipo") in ("noticia", "analise"):
        if not a.get("lide"):
            erros.append("notícia precisa de lide (o quê, quem, quando, onde, como e por quê)")
        elif not FAIXA_LIDE[0] <= palavras(a["lide"]) <= FAIXA_LIDE[1]:
            erros.append(f"lide com {palavras(a['lide'])} palavras (padrão: {FAIXA_LIDE[0]} a {FAIXA_LIDE[1]})")
    if a.get("analise") and a.get("tipo") not in ("noticia", "explicativo"):
        erros.append("'analise' (quadro de análise da redação) só existe em notícia e explicativo; opinião vai no tipo 'opiniao'")
    if a.get("analise") and not 15 <= palavras(a["analise"]) <= 90:
        erros.append(f"analise com {palavras(a['analise'])} palavras (15 a 90)")
    if a.get("tipo") == "opiniao":
        p = portal.EQUIPE.get(a.get("autor", "")) or (a.get("colaborador") or {})
        if not p.get("nome"):
            erros.append("opinião precisa de autor identificado (pessoa de config/equipe.json ou 'colaborador' com nome e descrição)")
        if a.get("colaborador") and not a["colaborador"].get("descricao"):
            erros.append("colaborador de opinião precisa de descrição (quem é, de onde fala)")
    if a.get("tipo") == "patrocinado":
        pat = a.get("patrocinador") or {}
        if not pat.get("nome"):
            erros.append("conteúdo patrocinado precisa do nome do patrocinador (aparece no topo e no rótulo)")
        if a.get("manchete") or a.get("destaque"):
            erros.append("conteúdo patrocinado não pode ser manchete nem destaque editorial")
    elif a.get("patrocinador"):
        erros.append("'patrocinador' só existe no tipo 'patrocinado': matéria jornalística não tem patrocinador")
    for i, l in enumerate(a.get("afiliados") or []):
        if not l.get("texto") or not str(l.get("url", "")).startswith("https://") or not l.get("loja"):
            erros.append(f"afiliados[{i}]: precisa de texto, link https e nome da loja (o aviso de afiliado sai automático)")
    if a.get("tipo") in ("noticia", "analise"):
        for t in textos(a):
            m = ANONIMO.search(t)
            if m:
                erros.append(f"fonte não identificável ({m.group(0)!r}): diga quem afirma e onde; boato não é notícia")
                break
    checar_corpo(a, erros)
    checar_fontes(a, erros)
    for i, q in enumerate(a.get("faq") or []):
        if not q.get("pergunta", "").strip().endswith("?") or palavras(q.get("resposta", "")) < 15:
            erros.append(f"faq[{i}]: pergunta terminando em '?' e resposta com pelo menos 15 palavras")
    for i, c in enumerate(a.get("correcoes") or []):
        if not iso_ok(c.get("data")) or not c.get("texto"):
            erros.append(f"correcoes[{i}]: precisa de data (ISO) e texto dizendo o que mudou")
        elif not a.get("atualizado_em") or a["atualizado_em"][:10] < c["data"][:10]:
            erros.append(f"correcoes[{i}]: atualizado_em precisa ser igual ou posterior à correção")
    im = a.get("imagem")
    if im:
        if not im.get("arquivo") or not im.get("credito") or not im.get("alt"):
            erros.append("imagem: precisa de arquivo, crédito e texto alternativo (alt)")
        elif not (portal.CONTEUDO / "imagens" / im["arquivo"]).is_file():
            erros.append(f"imagem: arquivo {im['arquivo']} não está em conteudo/imagens/")
        else:
            try:
                from PIL import Image
                with Image.open(portal.CONTEUDO / "imagens" / im["arquivo"]) as f:
                    if f.width < 800:
                        erros.append(f"imagem com {f.width} px de largura (mínimo 800; o Google Discover recomenda 1200)")
            except Exception:
                erros.append(f"imagem ilegível: {im['arquivo']}")
        if im.get("gerada_por_ia"):
            erros.append("imagem gerada por IA não ilustra notícia (pode induzir o leitor a erro); use foto com crédito")
    elif publicar and a.get("tipo") in ("noticia", "analise"):
        erros.append("notícia sem foto: o Discover e as redes dependem dela (foto real, com crédito)")
    if len(a.get("tags") or []) > 8:
        erros.append("tags: no máximo 8")
    if publicar:
        checar_revisao(a, erros)
    return erros


def carregar_todos():
    return [(p, json.loads(p.read_text(encoding="utf-8"))) for p in sorted((portal.CONTEUDO / "artigos").glob("*.json"))]


def checar_conjunto(artigos):
    """Regras entre matérias: slug único, uma manchete por vez entre as publicadas."""
    erros = []
    slugs = [a["slug"] for a in artigos if a.get("slug")]
    for s in {s for s in slugs if slugs.count(s) > 1}:
        erros.append(f"slug repetido: {s}")
    return erros


def main(args):
    exemplo = "--exemplo" in args
    args = [x for x in args if x != "--exemplo"]
    if exemplo:
        portal.iniciar(conteudo=portal.ROOT / "exemplos" / "conteudo", config=portal.ROOT / "exemplos" / "config", exemplo=True)
    elif not portal.CFG:
        portal.iniciar()
    arqs = [Path(x) for x in args] or [p for p, _ in carregar_todos()]
    ruim = 0
    todos = []
    for arq in arqs:
        a = json.loads(arq.read_text(encoding="utf-8"))
        todos.append(a)
        publicar = a.get("status") in ("publicado", "revisao")
        es = problemas(a)
        if es and publicar:
            ruim += 1
        marca = "✅" if not es else ("❌" if publicar else "📝")
        print(f"{marca} {arq.name} [{a.get('status')}]" + ("" if not es else "\n   - " + "\n   - ".join(es)))
        for v in avisos(a):
            print("   ⚠️ vício de texto: " + v)
    for e in checar_conjunto(todos):
        print("❌ " + e)
        ruim += 1
    return 1 if ruim else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
