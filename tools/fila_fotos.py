"""Triagem de fotos da pauta: só entra em produção o jogo que tem foto oficial boa para o topo da página.

Uso:
  python3 tools/fila_fotos.py proximos [N]        os N próximos `na_fila` (padrão 6), com slug e situação das fotos
  python3 tools/fila_fotos.py aprovado "<jogo>" <slug>
                                                  registra o slug no jogo da pauta (fotos liberadas pelo crivo)
  python3 tools/fila_fotos.py sem-fotos "<jogo>" --obs "editoras consultadas"
                                                  tira o jogo da fila: status `sem_fotos`, com data e observação
  python3 tools/fila_fotos.py voltar "<jogo>"      devolve um jogo `sem_fotos` à fila (chegaram fotos, kit de imprensa)

O jogo `sem_fotos` mantém a prioridade: volta para o mesmo lugar da fila quando ganhar fotos.
"""
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from checar_roteiro import fotos_liberadas  # noqa: E402

PAUTA = ROOT / "pauta.json"


def slugificar(nome):
    s = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[:’'].*$", "", s) if len(s) > 30 else s  # subtítulo longo fica de fora
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def carregar():
    return json.loads(PAUTA.read_text(encoding="utf-8"))


def gravar(p):
    p["atualizado_em"] = date.today().isoformat()
    PAUTA.write_text(json.dumps(p, ensure_ascii=False, indent=1), encoding="utf-8")


def achar(p, nome):
    for j in p["jogos"]:
        if j["jogo"] == nome:
            return j
    sys.exit(f"{nome!r} não está na pauta")


def proximos(n):
    p = carregar()
    fila = sorted((j for j in p["jogos"] if j["status"] == "na_fila" and j.get("tipo") == "jogo"),
                  key=lambda j: j["prioridade"])
    for j in fila[:n]:
        slug = j.get("slug") or slugificar(j["jogo"])
        if fotos_liberadas(slug):
            situacao = "fotos ok"
        elif (ROOT / "triagem" / f"{slug}.json").exists() or (ROOT / "conteudo" / f"{slug}.json").exists():
            situacao = "em triagem, sem foto de topo"
        else:
            situacao = "fazer triagem"
        print(f'{j["prioridade"]:>4}  {slug:<32} {situacao:<30} {j["jogo"]}')


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    cmd, resto = args[0], args[1:]
    if cmd == "proximos":
        proximos(int(resto[0]) if resto else 6)
        return
    p = carregar()
    j = achar(p, resto[0])
    if cmd == "aprovado":
        if not fotos_liberadas(resto[1]):
            sys.exit(f"{resto[1]}: o crivo ainda não liberou foto para o topo (crivo.py --aplicar)")
        j["slug"] = resto[1]
        j.pop("fotos", None)
    elif cmd == "sem-fotos":
        obs = resto[resto.index("--obs") + 1] if "--obs" in resto else ""
        j["status"] = "sem_fotos"
        j["fotos"] = {"verificado_em": date.today().isoformat(), "obs": obs}
    elif cmd == "voltar":
        j["status"] = "na_fila"
        j.pop("fotos", None)
    else:
        sys.exit(__doc__)
    gravar(p)
    print(j["jogo"], "→", j["status"], j.get("slug", ""))


if __name__ == "__main__":
    main()
