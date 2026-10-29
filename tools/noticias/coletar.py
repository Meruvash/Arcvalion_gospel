"""Coleta diária de notícias: feeds liberados, Bluesky e calendário de lançamentos da Ludopedia, com pré-crivo.

Uso: python3 tools/noticias/coletar.py [--dias 3]
Saída: .cache/noticias/<AAAA-MM-DD>.json (candidatas ordenadas pela pontuação prévia) e .md (relatório para ler),
e conteudo/lancamentos/<AAAA-MM>.json de todos os meses do ano e do próximo mês (precisa de LUDOPEDIA_TOKEN no ambiente).

O pré-crivo só ordena: a pontuação final, as fontes primárias e o texto seguem o padrão das notícias
(PADRAO_EDITORIAL.md) e passam por tools/noticias/checar_noticia.py. Os sites são lidos pelo cliente do robô
de imagens, que respeita o robots.txt e as pausas pedidas pelos servidores.
"""
import html
import json
import os
import re
import sys
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import requests

AQUI = Path(__file__).resolve().parent
ROOT = AQUI.parent.parent
sys.path.insert(0, str(AQUI.parent / "imagens"))
from robo import Bloqueado, Cliente  # noqa: E402

SAIDA = ROOT / ".cache" / "noticias"
BSKY = "https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed"
LUDO = "https://ludopedia.com.br/api/v1/lancamentos"

# Pré-crivo: os mesmos critérios de PLANO_NOTICIAS.md, detectados por palavra-chave.
PREMIOS = r"spiel des jahres|kennerspiel|kinderspiel|as d.or|golden geek|deutscher spiele preis|origins award|dice tower award|prêmio ludopedia"
BRASIL = r"\bbrasil|brasileir|galápagos|devir|grok|meeplebr|conclave|papergames|ludofun|mosaico|across the board|calamity|catarse|meeplestarter|diversão offline"
FINANC = r"kickstarter|gamefound|backerkit|catarse|meeplestarter|crowdfund|financiamento"
EVENTOS = r"\bessen\b|spiel ?\d{2,4}|gen con|diversão offline|cannes"
FORA = r"#publi|\bpubli\b|patrocinad|\brpg\b|d&d|dungeons & dragons|warhammer|magic: the gathering|pokémon tcg|videogame|video game|ps5|xbox|nintendo switch|steam"


def texto(t):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<!\[CDATA\[|\]\]>", "", t or "")))).strip()


def jogos_resenhados():
    """Nome do jogo (e o original) -> slug, das resenhas publicadas."""
    pauta = json.loads((ROOT / "pauta.json").read_text(encoding="utf-8"))
    mapa = {}
    for p in pauta["publicadas"]:
        slug = p["url"].rstrip("/").split("/")[-1]
        c = json.loads((ROOT / "conteudo" / f"{slug}.json").read_text(encoding="utf-8"))
        for nome in {c["jogo"], c.get("og_titulo", "").split(" Resenha")[0], p.get("jogo", "")}:
            nome = re.sub(r"\(.*?\)", "", nome).split(":")[0].strip()
            if len(nome) >= 4:
                mapa[nome.lower()] = slug
    return mapa


def ja_publicadas():
    links, titulos = set(), set()
    for p in (ROOT / "conteudo" / "noticias").glob("*.json"):
        n = json.loads(p.read_text(encoding="utf-8"))
        links |= {f["url"].rstrip("/") for f in n["fontes"]}
        titulos.add(n["titulo"].lower())
    return links, titulos


def feeds(cli, fontes, desde):
    itens, avisos = [], []
    filtro = re.compile(fontes["filtro_tabuleiro"], re.I)
    for f in fontes["feeds"]:
        try:
            _, b = cli.get(f["url"], usar_cache=False)
        except (Bloqueado, LookupError) as e:
            avisos.append(f"{f['nome']}: {e}")
            continue
        b = b if isinstance(b, str) else b.decode("utf-8", "ignore")
        novos = 0
        for it in re.findall(r"<item>(.*?)</item>", b, re.S):
            g = lambda t: (re.search(rf"<{t}>(.*?)</{t}>", it, re.S) or [None, ""])[1]
            try:
                quando = parsedate_to_datetime(texto(g("pubDate")))
            except (TypeError, ValueError):
                continue
            if quando < desde:
                continue
            cats = [texto(c) for c in re.findall(r"<category>(.*?)</category>", it, re.S)]
            item = {"fonte": f["nome"], "pais": f["pais"], "titulo": texto(g("title")), "link": texto(g("link")),
                    "data": quando.date().isoformat(), "resumo": texto(g("description"))[:400], "categorias": cats[:6]}
            if f.get("filtro") and not filtro.search(" ".join([item["titulo"], item["resumo"], *cats])):
                continue
            itens.append(item)
            novos += 1
        if not novos and not re.findall(r"<item>", b):
            avisos.append(f"{f['nome']}: feed sem itens")
    return itens, avisos


def bluesky(fontes, desde):
    itens, avisos = [], []
    for c in fontes["bluesky"]:
        try:
            r = requests.get(BSKY, params={"actor": c["handle"], "limit": 30, "filter": "posts_no_replies"}, timeout=20)
            r.raise_for_status()
        except requests.RequestException as e:
            avisos.append(f"Bluesky {c['handle']}: {e}")
            continue
        for x in r.json().get("feed", []):
            if x.get("reason"):  # repost de outra conta
                continue
            rec, post = x["post"]["record"], x["post"]
            quando = datetime.fromisoformat(rec["createdAt"].replace("Z", "+00:00"))
            if quando < desde:
                continue
            ext = (post.get("embed") or {}).get("external") or {}
            # o link do artigo pode vir no cartão (embed) ou só no texto do post (facets)
            no_texto = [f["uri"] for fc in rec.get("facets", []) for f in fc.get("features", []) if f.get("uri")]
            rkey = post["uri"].rsplit("/", 1)[-1]
            itens.append({"fonte": f"Bluesky: {c['nome']}", "pais": "", "titulo": texto(ext.get("title") or rec.get("text", ""))[:160],
                          "link": ext.get("uri") or (no_texto[0] if no_texto else f"https://bsky.app/profile/{c['handle']}/post/{rkey}"),
                          "data": quando.date().isoformat(), "resumo": texto(rec.get("text", ""))[:400], "categorias": []})
    return itens, avisos


def ludopedia(hoje):
    """Salva o calendário do mês atual e do próximo e devolve os lançamentos de tabuleiro do Brasil."""
    token = os.environ.get("LUDOPEDIA_TOKEN")
    if not token:
        return [], ["Ludopedia: falta LUDOPEDIA_TOKEN no ambiente; calendário de lançamentos não atualizado"]
    itens, avisos = [], []
    prox = (hoje.replace(day=1) + timedelta(days=32)).replace(day=1)
    pauta = {hoje.strftime("%Y-%m"), prox.strftime("%Y-%m")}
    # o ano inteiro alimenta o calendário (lancamentos/); só o mês atual e o próximo viram candidatas a nota
    for mes in sorted({f"{hoje.year}-{m:02d}" for m in range(1, 13)} | pauta):
        try:
            r = requests.get(LUDO, params={"mes": mes}, headers={"Authorization": f"Bearer {token}"}, timeout=30)
            r.raise_for_status()
        except requests.RequestException as e:
            avisos.append(f"Ludopedia {mes}: {e}")
            continue
        d = r.json()
        arq = ROOT / "conteudo" / "lancamentos" / f"{mes}.json"
        antigo = json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else {"lancados": [], "previstos": []}
        vistos = {(j["id_jogo"], j["status"]["slug"]) for g in ("lancados", "previstos") for j in antigo.get(g, [])}
        arq.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        if mes not in pauta:
            continue
        for g in ("lancados", "previstos"):
            for j in d[g]:
                if j.get("fl_tipo") != 1 or (j["id_jogo"], j["status"]["slug"]) in vistos:
                    continue  # só tabuleiro, e só o que é novo ou mudou de situação
                itens.append({"fonte": "Ludopedia: calendário de lançamentos", "pais": "Brasil",
                              "titulo": f"{j['nome'].strip()} ({(j.get('editora') or {}).get('nome', '')}): {j['status']['label']} em {d['label']}",
                              "link": j["url"], "data": hoje.isoformat(), "resumo": "", "categorias": ["lançamento"],
                              "id_ludopedia": j["id_jogo"], "base": j.get("fl_jogo_base")})
    return itens, avisos


def pre_crivo(it, resenhados, publicadas):
    alvo = " ".join([it["titulo"], it["resumo"], *it["categorias"]]).lower()
    pontos, motivos = 0, []
    if re.search(FORA, alvo):
        return -1, ["eliminada: conteúdo pago ou fora do tabuleiro moderno"]
    if it["link"].rstrip("/") in publicadas[0] or it["titulo"].lower() in publicadas[1]:
        return -1, ["eliminada: já publicada"]
    if "lançamento" in it["categorias"] or re.search(BRASIL, alvo) or it["pais"] == "Brasil":
        pontos += 4; motivos.append("Brasil (4)")
    if re.search(PREMIOS, alvo):
        pontos += 4; motivos.append("prêmio (4)")
    nossos = sorted({s for nome, s in resenhados.items() if re.search(rf"\b{re.escape(nome)}\b", alvo)})
    if nossos:
        pontos += 3; motivos.append(f"jogo com resenha nossa: {', '.join(nossos)} (3)")
    if re.search(FINANC, alvo):
        pontos += 2; motivos.append("financiamento (2)")
    if re.search(EVENTOS, alvo):
        pontos += 2; motivos.append("evento grande (2)")
    if re.search(r"\breview\b|resenha|análise|\bopinião\b|top \d+|regras e gameplay|live ", alvo) and not motivos:
        motivos.append("crítica ou vídeo: serve de fonte, não de notícia")
    return pontos, motivos


def main():
    dias = int(sys.argv[sys.argv.index("--dias") + 1]) if "--dias" in sys.argv else 3
    hoje = date.today()
    desde = datetime.now(timezone.utc) - timedelta(days=dias)
    fontes = json.loads((AQUI / "fontes.json").read_text(encoding="utf-8"))
    cli = Cliente()
    todos, avisos = [], []
    for coleta in (lambda: feeds(cli, fontes, desde), lambda: bluesky(fontes, desde), lambda: ludopedia(hoje)):
        i, a = coleta()
        todos += i
        avisos += a
    resenhados, publicadas = jogos_resenhados(), ja_publicadas()
    unicos = {}
    for it in todos:  # o mesmo link chega pelo feed e pelo Bluesky: fica uma vez, com as duas fontes
        k = it["link"].split("?")[0].rstrip("/")
        if k in unicos:
            unicos[k]["fonte"] += f" + {it['fonte']}"
        else:
            unicos[k] = it
    for it in unicos.values():
        it["pre_pontos"], it["motivos"] = pre_crivo(it, resenhados, publicadas)
    cand = sorted(unicos.values(), key=lambda x: (-x["pre_pontos"], x["data"]))
    SAIDA.mkdir(parents=True, exist_ok=True)
    (SAIDA / f"{hoje}.json").write_text(json.dumps({"data": hoje.isoformat(), "avisos": avisos, "candidatas": cand}, ensure_ascii=False, indent=1), encoding="utf-8")
    linhas = [f"# Coleta de {hoje.strftime('%d/%m/%Y')}", "", f"{len(cand)} candidatas de {len(fontes['feeds'])} feeds, "
              f"{len(fontes['bluesky'])} perfis do Bluesky e a Ludopedia (últimos {dias} dias).", ""]
    if avisos:
        linhas += ["## Avisos", *[f"- {a}" for a in avisos], ""]
    for titulo, filtro in (("Passam no pré-crivo (5 ou mais)", lambda c: c["pre_pontos"] >= 5),
                           ("Abaixo de 5: conferir se a pesquisa sobe a pontuação", lambda c: 0 <= c["pre_pontos"] < 5),
                           ("Eliminadas", lambda c: c["pre_pontos"] < 0)):
        grupo = [c for c in cand if filtro(c)]
        linhas += [f"## {titulo} ({len(grupo)})", ""]
        linhas += [f"- **{c['pre_pontos']}** · {c['data']} · {c['fonte']} · [{c['titulo']}]({c['link']}) · {'; '.join(c['motivos'])}" for c in grupo]
        linhas.append("")
    linhas += ["## Leitura manual (sites que proíbem robôs)", *[f"- {m}" for m in fontes["manual"]]]
    (SAIDA / f"{hoje}.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"{len(cand)} candidatas, {sum(c['pre_pontos'] >= 5 for c in cand)} com 5 pontos ou mais; relatório em "
          f"{(SAIDA / f'{hoje}.md').relative_to(ROOT)}")
    for a in avisos:
        print("  ⚠️", a)


if __name__ == "__main__":
    main()
