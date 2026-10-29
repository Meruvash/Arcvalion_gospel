"""Aprovação humana: o único caminho para uma matéria ir ao ar, ser corrigida ou sair do ar.

Uso:
  python3 tools/publicar.py aprovar <arquivo.json> --revisor <slug> [--agendar AAAA-MM-DDTHH:MM]
      confere o padrão editorial e, se passar, grava status "publicado", revisao {revisor, data} e publicado_em.
  python3 tools/publicar.py corrigir <arquivo.json> --revisor <slug> --texto "O que mudou"
      registra a correção (data de hoje) e atualiza atualizado_em; o texto corrigido já deve estar no JSON.
  python3 tools/publicar.py atualizar <arquivo.json> --revisor <slug>
      marca atualização de conteúdo (fato novo) sem ser correção de erro.
  python3 tools/publicar.py despublicar <arquivo.json> --revisor <slug> --motivo "..."
      tira a matéria do site (status "despublicado"); o arquivo e o histórico ficam no repositório.

O revisor precisa estar em config/equipe.json com "revisor": true. Rotinas de IA não usam este script:
elas só escrevem rascunhos (premissa 6, revisão humana antes da publicação). Depois: python3 tools/build.py.
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
import portal  # noqa: E402
from noticias.checar_noticia import problemas as problemas_noticia  # noqa: E402
from estudos.checar_estudo import problemas as problemas_estudo  # noqa: E402


def _fuso():
    """Horário de Brasília; sem base de fusos no sistema (alguns servidores de build), usa -03:00 fixo (sem horário de verão desde 2019)."""
    try:
        return ZoneInfo("America/Sao_Paulo")
    except Exception:
        from datetime import timedelta, timezone as tz
        return tz(timedelta(hours=-3), "BRT")


FUSO = _fuso()


def agora():
    return datetime.now(FUSO).replace(microsecond=0).isoformat()


def main(argv=None):
    ap = argparse.ArgumentParser(description="Aprovação humana de matérias")
    ap.add_argument("acao", choices=["aprovar", "corrigir", "atualizar", "despublicar"])
    ap.add_argument("arquivo")
    ap.add_argument("--revisor", required=True)
    ap.add_argument("--texto")
    ap.add_argument("--motivo")
    ap.add_argument("--agendar")
    ap.add_argument("--exemplo", action="store_true", help=argparse.SUPPRESS)
    ar = ap.parse_args(argv)
    if ar.exemplo:
        portal.iniciar(conteudo=portal.ROOT / "exemplos" / "conteudo", config=portal.ROOT / "exemplos" / "config", exemplo=True)
    else:
        portal.iniciar()
    arq = Path(ar.arquivo)
    a = json.loads(arq.read_text(encoding="utf-8"))
    p = portal.EQUIPE.get(ar.revisor)
    if not p or not p.get("revisor"):
        sys.exit(f"{ar.revisor!r} não é pessoa revisora em config/equipe.json.")
    hora = agora()
    if ar.acao == "aprovar":
        a["status"] = "publicado"
        a["revisao"] = {"revisor": ar.revisor, "data": hora}
        a["publicado_em"] = datetime.fromisoformat(ar.agendar).replace(tzinfo=FUSO).isoformat() if ar.agendar else hora
        if "data" in a:
            a["data"] = a["publicado_em"][:10]
    elif ar.acao in ("corrigir", "atualizar"):
        if a.get("status") != "publicado":
            sys.exit("Só matéria publicada recebe correção ou atualização.")
        if ar.acao == "corrigir":
            if not ar.texto:
                sys.exit("Diga o que mudou: --texto \"...\"")
            a.setdefault("correcoes", []).append({"data": hora[:10], "texto": ar.texto})
        a["atualizado_em"] = hora
        a["revisao"] = {"revisor": ar.revisor, "data": hora}
    else:
        if not ar.motivo:
            sys.exit("Diga o motivo: --motivo \"...\"")
        a["status"] = "despublicado"
        a.setdefault("historico", []).append({"data": hora, "acao": "despublicado", "por": ar.revisor, "motivo": ar.motivo})
    if a["status"] == "publicado":
        erros = (problemas_estudo if "estudos" in arq.parts else problemas_noticia)(a, publicar=True)
        if erros:
            sys.exit("Não publicado; corrija antes:\n - " + "\n - ".join(erros))
    arq.write_text(json.dumps(a, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"ok {ar.acao}: {arq.name} (revisor: {p['nome']}). Agora rode python3 tools/build.py")


if __name__ == "__main__":
    main()
