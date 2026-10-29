"""Dados estruturados de cada resenha para os filtros da página /estudos/.

Os campos vêm do que a resenha já publica (ficha, "Com quantos jogar", etiquetas, prêmios e preço). Nada é inventado:
o que não dá para ler com segurança fica None, e o jogo simplesmente não aparece naquele filtro. Casos que o texto livre
não resolve vão em "filtros_ajuste" no JSON da resenha (ex.: duração por jogador).
Uso: python3 tools/filtros_resenha.py   (mostra a tabela de todos os jogos, para conferência)
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_review import ROOT, campo, numero  # noqa: E402

# perfil "Melhor para": um por resenha (campo "melhor_para"), com o critério que o define
PERFIS = {
    "entrada": ("Primeiro jogo moderno", "peso BGG abaixo de 2, regras em ~15 min, funciona com quem não joga"),
    "dupla": ("Jogar a dois", "2 jogadores é a melhor contagem"),
    "festa": ("Festa e grupos grandes", "melhor com 5 ou mais pessoas, partida de até ~30 min"),
    "cooperativo": ("Cooperativo", "todos juntos contra o jogo"),
    "solo": ("Ótimo sozinho", "modo solo oficial avaliado como ótimo"),
    "proximo": ("O próximo passo", "peso entre 2 e 3: para quem já passou dos jogos de entrada"),
    "estrategia": ("Estrategistas", "peso a partir de 3,2 ou partidas de 2 h"),
    "campanha": ("Campanha com grupo fixo", "história que continua por várias sessões"),
    "tema": ("Tema e história", "a narrativa e a imersão são o centro"),
}

MECANICAS = {
    "deck-building": "Construção de baralho", "construção de motor": "Construção de motor", "drafting": "Draft",
    "alocação de trabalhadores": "Alocação de trabalhadores", "trabalhadores": "Alocação de trabalhadores",
    "vazas": "Vazas", "dedução": "Dedução", "investigação": "Investigação", "peças": "Colocação de peças",
    "arriscar a sorte": "Arriscar a sorte", "programação": "Programação de ações", "palavras": "Palavras",
    "assimétrico": "Facções assimétricas", "dados": "Dados", "exploração": "Exploração", "legacy": "Legacy",
    "abstrato": "Abstrato",
}
PREMIOS = [("Kennerspiel", "Kennerspiel des Jahres"), ("Spiel des Jahres", "Spiel des Jahres"), ("Golden Geek", "Golden Geek"),
           ("As d'Or", "As d'Or"), ("Deutscher Spiele Preis", "Deutscher Spiele Preis")]


def faixa_numeros(texto):
    """'1 a 5 (…)' → (1, 5); '20 minutos' → (20, 20); '2 (exatamente)' → (2, 2)."""
    if not texto:
        return None
    m = re.search(r"(\d+)\s*(?:a|–|-)\s*(\d+)", texto)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.search(r"\d+", texto)
    return (int(m.group()), int(m.group())) if m else None


def melhores(c, maximo):
    """Contagens marcadas como ótimas (nível 3) em "Com quantos jogar"."""
    out = set()
    for rotulo, _texto, *nivel in c.get("jogadores", []):
        if not nivel or nivel[0] != 3:
            continue
        r = rotulo.lower()
        if "sozinho" in r:
            out.add(1)
        elif "casa" in r or "dupla" in r:
            out.add(2)
        elif "ou mais" in r:
            out.update(range(int(re.search(r"\d+", r).group()), (maximo or 8) + 1))
        else:
            a = faixa_numeros(r.replace(" ou ", " a "))
            if a:
                out.update(range(a[0], a[1] + 1))
    return sorted(out)


def derivar(c):
    f = c["ficha"]
    jog = faixa_numeros(campo(f, "jogadores"))
    dur = faixa_numeros(campo(f, "duração anunciada", "duração"))
    idade = re.search(r"(\d+)\s*\+", campo(f, "idade") or "")
    br = (campo(f, "editora no brasil", "edição nacional") or "").strip()
    tags = [t.lower() for t in c.get("tags", [])]
    perfil = c.get("melhor_para")
    estilos = set()
    if "cooperativo" in tags or perfil == "cooperativo" or any("cooperativo" in t for t in tags):
        estilos.add("Cooperativo")
    if not estilos or any("competitivo" in t for t in tags):
        estilos.add("Competitivo")
    if "equipes" in tags:
        estilos.add("Em equipes")
    if {"campanha", "legacy"} & set(tags):
        estilos.add("Campanha")
    preco = re.search(r"R\$\s*([\d.]+)", c.get("preco_ref", {}).get("faixa", ""))
    d = {
        "jogadores": list(jog) if jog else None,
        "melhor": melhores(c, jog[1] if jog else None),
        "duracao": list(dur) if dur else None,
        "peso": numero(campo(f, "peso bgg")),
        "idade": int(idade.group(1)) if idade else None,
        "solo": bool(jog and jog[0] == 1),
        "portugues": bool(br) and not br.lower().startswith(("não", "sem")),
        "estilos": sorted(estilos),
        "mecanicas": sorted({MECANICAS[t] for t in tags if t in MECANICAS}),
        "premios": sorted({nome for chave, nome in PREMIOS for a in c["premiacoes"]
                           if a.get("resultado") == "vencedor" and a.get("premio", "").lower().startswith(chave.lower())}),
        "preco": int(preco.group(1).replace(".", "")) if preco else None,
        "nota": numero(campo(f, "nota bgg")),
        "melhor_para": perfil,
    }
    d.update(c.get("filtros_ajuste", {}))
    return d


if __name__ == "__main__":
    pauta = json.loads((ROOT / "pauta.json").read_text(encoding="utf-8"))
    for p in pauta["publicadas"]:
        s = p["url"].rstrip("/").split("/")[-1]
        print(s.ljust(22), json.dumps(derivar(json.loads((ROOT / "conteudo" / f"{s}.json").read_text(encoding="utf-8"))), ensure_ascii=False))
