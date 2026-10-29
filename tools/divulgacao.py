"""Pacote de divulgação do dia: textos prontos para copiar e colar no Instagram e nos grupos de WhatsApp/Telegram.

Uso: python3 tools/divulgacao.py [AAAA-MM-DD]   (sem data: hoje, no horário de Brasília)
Grava divulgacao/<data>.md (fica no repositório, fora do site) e imprime o resumo para os grupos.
Os textos saem só do que já está publicado (título, lide, opinião, legenda da resenha): nada é inventado aqui.
Cópia do tools/divulgacao.py do Elite Boardgamers: notícias publicadas no dia e estudos bíblicos (no lugar das resenhas).
"""
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import portal  # noqa: E402

portal.iniciar()
ROOT = portal.ROOT
SITE = portal.SITE
BRT = timezone(timedelta(hours=-3))
GERAIS = "#NoticiasGospel #FeCrista #Biblia #" + portal.NOME.replace(" ", "")
CHAMADAS = ROOT / "conteudo" / "chamadas.json"  # chamada e pergunta de cada nota/resenha (fora da página)


def chamadas():
    return json.loads(CHAMADAS.read_text(encoding="utf-8")) if CHAMADAS.exists() else {}


def primeira_frase(t):
    return re.split(r"(?<=[.!?])\s+", (t or "").strip())[0]


def hashtag(t):
    t = re.sub(r"[^\w\s]", "", t or "")
    return "#" + "".join(p[:1].upper() + p[1:] for p in t.split()) if t.strip() else ""


def dia_brt(iso):
    return datetime.fromisoformat(iso).astimezone(BRT).date().isoformat() if iso else None


def noticias(dia):
    ns = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((ROOT / "conteudo" / "noticias").glob("*.json"))]
    ns = [n for n in ns if n.get("status", "publicado") == "publicado" and (dia_brt(n.get("publicado_em")) == dia or (not n.get("publicado_em") and n.get("data") == dia))]
    # manchete primeiro, depois a pontuação
    return sorted(ns, key=lambda n: (not n.get("manchete"), -(n.get("crivo", {}).get("pontos") or 0)))


def resenhas(dia):
    # estudos bíblicos publicados no dia (as resenhas do Elite)
    res = []
    for p in sorted((ROOT / "conteudo" / "estudos").glob("*.json")):
        c = json.loads(p.read_text(encoding="utf-8"))
        if c.get("status") == "publicado" and dia_brt(c.get("publicado_em")) == dia:
            res.append({**c, "jogo": c["titulo"]})
    return res


def bloco_noticia(n, ch):
    url = f"{SITE}/noticias/{n['slug']}/"
    c = ch.get(n["slug"], {})
    gancho, pergunta = c.get("chamada") or n["titulo"], c.get("pergunta")
    tags = " ".join(t for t in [hashtag(portal.editoria(n["categoria"])["nome"]), hashtag(n.get("instituicao"))] if t)
    insta = (f"{gancho}\n\n{primeira_frase(n['lide'])}\n\n"
             f"Nossa opinião: {primeira_frase(n['veredito'])}\n\n"
             + (f"💬 {pergunta}\n\n" if pergunta else "")
             + f"Notícia completa no link da bio.\n\n{tags} {GERAIS}".replace("  ", " "))
    zap = f"*{gancho}*\n\n{n['titulo']}\n{url}" + (f"\n\n💬 {pergunta}" if pergunta else "")
    return (f"### {n['titulo']}\n\n"
            f"Link: {url}\n"
            f"Imagem para o post: {SITE}/img/og/noticia-{n['slug']}.jpg\n\n"
            f"**WhatsApp / Telegram**\n\n```\n{zap}\n```\n\n"
            f"**Instagram (legenda)**\n\n```\n{insta}\n```\n")


def bloco_resenha(c, ch):
    url = f"{SITE}/estudos/{c['slug']}/"
    titulo = f"Estudo bíblico: {c['jogo']} ({c['passagem']})"
    x = ch.get(c["slug"], {})
    gancho, pergunta = x.get("chamada"), x.get("pergunta")
    insta = (f"{gancho}\n\n" if gancho else "") + (c.get("legenda") or (f"{titulo}\n\n{c.get('tagline', '')}\n\nEstudo completo no link da bio.\n\n"
                                 f"{hashtag(c['jogo'])} {GERAIS}"))
    zap = (f"*{gancho}*\n\nEstudo bíblico: {c['jogo']}\n{url}" if gancho else f"*Estudo bíblico: {c['jogo']}*\n{c.get('tagline', '')}\n{url}") \
        + (f"\n\n💬 {pergunta}" if pergunta else "")
    return (f"### Estudo bíblico: {c['jogo']}\n\n"
            f"Link: {url}\n"
            f"Imagem para o post: {SITE}/img/og/estudo-{c['slug']}.jpg\n\n"
            f"**WhatsApp / Telegram**\n\n```\n{zap}\n```\n\n"
            f"**Instagram (legenda)**\n\n```\n{insta}\n```\n")


def resumo_grupos(dia, ns, rs, ch):
    d = datetime.fromisoformat(dia).strftime("%d/%m")
    linhas = [f"✝️ *As notícias de hoje ({d})*", ""]
    linhas += [f"👉 {ch.get(n['slug'], {}).get('chamada') or n['titulo']}\n{SITE}/noticias/{n['slug']}/\n" for n in ns]
    linhas += [f"📖 Estudo bíblico: {c['jogo']}: {ch.get(c['slug'], {}).get('chamada') or c.get('tagline', '')}\n{SITE}/estudos/{c['slug']}/\n" for c in rs]
    # a pergunta da manchete (ou do primeiro item) puxa a conversa no grupo
    pergunta = next((ch[x["slug"]]["pergunta"] for x in ns + rs if ch.get(x["slug"], {}).get("pergunta")), None)
    if pergunta:
        linhas += [f"💬 *{pergunta}*", ""]
    linhas += [f"Tudo em {SITE.removeprefix('https://')}"]
    return "\n".join(linhas)


def gerar(dia):
    ns, rs, ch = noticias(dia), resenhas(dia), chamadas()
    if not ns and not rs:
        return None, ""
    resumo = resumo_grupos(dia, ns, rs, ch)
    md = (f"# Divulgação de {datetime.fromisoformat(dia).strftime('%d/%m/%Y')}\n\n"
          "Textos prontos para copiar e colar. Os do Instagram dizem \"link na bio\"; nos Stories, use a figurinha de link "
          "com o endereço da notícia. Poste em horários diferentes ao longo do dia, não tudo de uma vez.\n\n"
          f"## Resumo do dia para grupos de WhatsApp e Telegram\n\n```\n{resumo}\n```\n\n"
          + (f"## Notícias ({len(ns)})\n\n" + "\n".join(bloco_noticia(n, ch) for n in ns) if ns else "")
          + (f"\n## Estudos bíblicos ({len(rs)})\n\n" + "\n".join(bloco_resenha(c, ch) for c in rs) if rs else ""))
    destino = ROOT / "divulgacao" / f"{dia}.md"
    destino.parent.mkdir(exist_ok=True)
    destino.write_text(md, encoding="utf-8")
    return destino, resumo


if __name__ == "__main__":
    dia = sys.argv[1] if len(sys.argv) > 1 else datetime.now(BRT).date().isoformat()
    destino, resumo = gerar(dia)
    if not destino:
        sys.exit(f"Nada publicado em {dia}.")
    print(f"ok {destino.relative_to(ROOT)}\n\n{resumo}")
