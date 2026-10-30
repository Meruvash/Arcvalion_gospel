"""Gera busca.json: o índice da busca do site (botão de lupa no cabeçalho, tools/layout.py + busca.js).

Uso: python3 tools/busca.py   (também roda no fim de build_home.py)
Um registro por estudo, notícia, livro da Bíblia e item da agenda do ano, só com nome, apelidos e uma linha
de contexto. Os apelidos (nome em português e em inglês) saem apenas dos dados do próprio site: nome da resenha,
nome da edição brasileira (og_titulo), série da pauta e os nomes entre parênteses das editoras na ficha.
O cruzamento entre estudos e notícias é pelo nome normalizado.
"""
import json
import re
import sys
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_review import ROOT, campo, nome_br  # noqa: E402

MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
# parênteses da "Editora no Brasil" que não são nome de jogo (datas, observações sobre a edição)
NAO_E_NOME = re.compile(r"\d{4}|lançad|edição|edições|segundo|português|/", re.I)


def chave(t):
    """Mesma normalização do busca.js: sem acento, minúsculas, pontuação vira espaço."""
    t = unicodedata.normalize("NFKD", t.lower()).encode("ascii", "ignore").decode()
    return " ".join(re.sub(r"[^a-z0-9]+", " ", t).split())


def apelidos(c, serie=()):
    """Todos os nomes de uma resenha que aparecem nos dados do site."""
    nomes = [c["jogo"], nome_br(c), *serie]
    br = campo(c["ficha"], "editora no brasil") or ""
    for p in re.findall(r"\(([^)]*)\)", br):
        p = re.sub(r",\s*\d{4}$", "", p).strip()
        if not NAO_E_NOME.search(p):
            nomes.append(p)
    orig = campo(c["ficha"], "editora original") or ""
    nomes += [m.group(1) for m in re.finditer(r"\(?([^();]+?), (?:em inglês|na Alemanha)\)?", orig)]
    vistos, saida = set(), []
    for n in nomes:
        if chave(n) not in vistos:
            vistos.add(chave(n))
            saida.append(n)
    return saida


def reg(tipo, nome, contexto, url, nomes=(), resenha=None):
    """Registro do índice. O busca.js procura em nome + contexto + "a" (apelidos que ainda não estão no texto)."""
    visto = chave(f"{nome} {contexto}")
    extra = [x for x in dict.fromkeys(nomes) if chave(x) not in visto]
    r = {"t": tipo, "n": nome, "s": contexto, "u": url}
    if extra:
        r["a"] = " ".join(extra)
    if resenha:
        r["r"] = f"{resenha}/"
    return r


def resenhas():
    """Resenhas publicadas, mais recentes primeiro: (slug, conteúdo, apelidos)."""
    pauta = json.loads((ROOT / "pauta.json").read_text(encoding="utf-8"))
    for pub in reversed(pauta["publicadas"]):
        slug = pub["url"].rstrip("/").split("/")[-1]
        c = json.loads((ROOT / "conteudo" / f"{slug}.json").read_text(encoding="utf-8"))
        yield slug, c, apelidos(c, pub.get("serie", []))


def resenhas_por_nome():
    """Chave normalizada de cada apelido -> (slug da resenha, todos os apelidos). Usado aqui e na Consulta."""
    return {chave(n): (slug, nomes) for slug, _, nomes in resenhas() for n in nomes}


def build():
    regs, por_nome = [], resenhas_por_nome()
    for slug, c, nomes in resenhas():
        outros = [n for n in nomes if n != nome_br(c)]
        regs.append(reg("r", nome_br(c), " · ".join(outros[:2]) or c["tagline"], f"{slug}/", nomes))

    def cruza(nome):
        """Resenha do mesmo jogo (nome igual a um apelido) e os apelidos dela, para achar pelo outro idioma."""
        return por_nome.get(chave(nome), (None, []))

    for p in sorted((ROOT / "conteudo" / "noticias").glob("*.json"), reverse=True):
        n = json.loads(p.read_text(encoding="utf-8"))
        if n.get("status", "publicado") != "publicado":  # nota em revisão não entra na busca
            continue
        extra = [a for j in n.get("jogos", []) for a in [j["nome"], *cruza(j["nome"])[1]]]
        d = datetime.fromisoformat(n["data"])
        regs.append(reg("n", n["titulo"], f'{d.day} de {MESES[d.month - 1]} · {n["categoria"]}', f'noticias/{n["slug"]}/', extra))

    # Livros da Bíblia (bloco RAW de consulta/): um registro por livro, com grupo, testamento e capítulos; o link abre o Versículo diário com um versículo do livro
    raw = re.search(r"const RAW = `(.*?)`", (ROOT / "consulta" / "index.html").read_text(encoding="utf-8"), re.S).group(1)
    for linha in raw.strip().split("\n"):
        y, cat, livros = linha.strip().split(" | ")
        for livro in livros.split("; "):
            nome, caps = livro.split("=")
            s = f'{cat} · {y} · {caps} {"capítulo" if caps == "1" else "capítulos"}'
            regs.append(reg("g", nome, s, "consulta/?livro=" + nome))

    # lançamentos do ano, como no calendário (mesmo jogo em dois meses fica no mais recente)
    from build_calendario import carregar, situacao, tipo
    hoje = datetime.now(timezone(timedelta(hours=-3))).date()
    por_id, _ = carregar(hoje.year)
    for j in sorted(por_id.values(), key=lambda j: (j["mes"], chave(j["nome"]))):
        nome = j["nome"].strip()
        slug, nomes = cruza(nome)
        ed = (j.get("editora") or {}).get("nome", "").strip()
        from build_home import NOME_EDITORA
        ed = NOME_EDITORA.get(ed, ed)
        mes = MESES[int(j["mes"][5:]) - 1]
        regs.append(reg("l", nome, " · ".join(x for x in (tipo(j)[1], ed, f"{mes} de {j['mes'][:4]}", situacao(j)[1]) if x),
                        f'lancamentos/#j{j["id_jogo"]}', nomes, slug))

    (ROOT / "busca.json").write_text(json.dumps(regs, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return len(regs)


if __name__ == "__main__":
    print("ok busca.json:", build(), "registros")
