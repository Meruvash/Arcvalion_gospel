"""Gancho do Claude Code: percebe resenha ou notícia nova sem imagem e já põe a busca de fotos na fila.

Roda depois de cada Write, Edit ou Bash (configurado em .claude/settings.json) e olha o conteúdo mexido nas
últimas horas:
  - resenha `conteudo/<slug>.json` sem fotos aprovadas em `<slug>/fotos/fontes.json`;
  - notícia `conteudo/noticias/<data>-<assunto>.json` com `imagem` vazia ou apontando para arquivo que não existe.
Cada uma entra uma única vez numa fila (.cache/imagens/fila.txt). Um único trabalhador processa a fila, uma busca
por vez, para nunca bater em paralelo nos mesmos sites. Quando a busca termina (ou falha), a sessão é avisada uma
vez para revisar a folha de contato. Busca interrompida (trabalhador morto) volta para a fila sozinha.
O script nunca falha alto: qualquer erro sai em silêncio.

Uso manual: echo '{}' | python3 tools/imagens/gatilho.py      (o que o gancho faz)
            python3 tools/imagens/gatilho.py --trabalhar         (processa a fila; o gancho chama sozinho)
"""
import fcntl
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / ".cache" / "imagens"
FILA = CACHE / "fila.txt"
TRAVA = CACHE / "fila.lock"
JANELA_H = 6  # só conteúdo mexido nas últimas horas conta como novo


def recentes(arquivo_tocado):
    agora = time.time()
    for pasta in (ROOT / "conteudo", ROOT / "conteudo" / "noticias"):
        for f in sorted(pasta.glob("*.json")) if pasta.exists() else []:
            if agora - f.stat().st_mtime < JANELA_H * 3600 or (arquivo_tocado and f.resolve() == arquivo_tocado):
                yield str(f.relative_to(ROOT / "conteudo").with_suffix("")), f


def precisa_de_imagem(chave, c):
    if chave.startswith("noticias/"):
        im = c.get("imagem")
        return not (im and im.get("arquivo") and (ROOT / "noticias" / im["arquivo"]).exists())
    try:
        return not json.loads((ROOT / chave / "fotos" / "fontes.json").read_text(encoding="utf-8")).get("fotos")
    except (OSError, ValueError):
        return True


def tem_de_onde_buscar(c):
    """Editora na ficha (resenha); editora, jogos ou fontes (notícia). Sem isso a busca não teria por onde começar."""
    ficha = dict(c.get("ficha", []))
    return bool(ficha.get("Editora original") or ficha.get("Editora no Brasil") or c.get("editora") or c.get("fontes"))


def fila():
    return [l for l in FILA.read_text().splitlines() if l.strip()] if FILA.exists() else []


def trabalhador_ativo():
    TRAVA.parent.mkdir(parents=True, exist_ok=True)
    with open(TRAVA, "a") as t:
        try:
            fcntl.flock(t, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            return True
        fcntl.flock(t, fcntl.LOCK_UN)
        return False


def enfileirar(chave):
    pasta = CACHE / chave
    pasta.mkdir(parents=True, exist_ok=True)
    for marca in ("busca.fim", "busca.erro", "busca.avisado"):
        (pasta / marca).unlink(missing_ok=True)
    (pasta / "busca.iniciada").write_text(time.strftime("%Y-%m-%d %H:%M"))
    if chave not in fila():
        with open(FILA, "a") as f:
            f.write(chave + "\n")


def acordar_trabalhador():
    subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--trabalhar"], cwd=ROOT,
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     start_new_session=True)


def trabalhar():
    """Processa a fila, uma busca por vez. Só um trabalhador roda: os outros saem na hora."""
    TRAVA.parent.mkdir(parents=True, exist_ok=True)
    with open(TRAVA, "a") as t:
        try:
            fcntl.flock(t, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            return
        while True:
            itens = fila()
            if not itens:
                break
            chave = itens[0]
            pasta = CACHE / chave
            pasta.mkdir(parents=True, exist_ok=True)
            with open(pasta / "busca.log", "w") as log:
                rc = subprocess.call([sys.executable, str(ROOT / "tools/imagens/robo.py"), "buscar", chave],
                                     cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
            (pasta / ("busca.fim" if rc == 0 else "busca.erro")).write_text(f"{time.strftime('%Y-%m-%d %H:%M')} rc={rc}")
            FILA.write_text("".join(l + "\n" for l in fila() if l != chave))


def candidatas(chave):
    try:
        return len(json.loads((CACHE / chave / "candidatas.json").read_text(encoding="utf-8")))
    except (OSError, ValueError):
        return 0


def instrucao(chave):
    if chave.startswith("noticias/"):
        return (f"escolha uma imagem na folha .cache/imagens/{chave}/folha.jpg (foto de divulgação, sem texto por cima) "
                f"e grave com `python3 tools/imagens/robo.py imagem-noticia {chave} <n>`")
    return (f"abra .cache/imagens/{chave}/folha.jpg e siga a skill imagens (etapas 3 e 4: escolher, aprovar, "
            f"marcar pessoas/texto e rodar o crivo)")


def main():
    try:
        evento = json.load(sys.stdin)
    except ValueError:
        evento = {}
    caminho = (evento.get("tool_input") or {}).get("file_path")
    tocado = Path(caminho).resolve() if caminho else None
    avisos, novos = [], []
    ativo = trabalhador_ativo()
    for chave, f in recentes(tocado):
        try:
            c = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue  # arquivo pela metade: tenta de novo no próximo gancho
        if not precisa_de_imagem(chave, c):
            continue
        pasta = CACHE / chave
        tipo = "notícia" if chave.startswith("noticias/") else "resenha"
        reservadas = ROOT / chave / "fotos" / "reservadas"
        extra = (f" Há fotos próprias guardadas em {reservadas.relative_to(ROOT)}/ (reservadas.json): "
                 "considere-as antes das da editora.") if reservadas.exists() else ""
        iniciada = (pasta / "busca.iniciada").exists()
        fim, erro = (pasta / "busca.fim").exists(), (pasta / "busca.erro").exists()
        if not iniciada:
            if tem_de_onde_buscar(c):
                enfileirar(chave)
                novos.append(f"{tipo} {chave}")
        elif not fim and not erro and not ativo and chave not in fila():
            enfileirar(chave)  # o trabalhador morreu no meio: volta para a fila
            novos.append(f"{tipo} {chave} (retomada)")
        elif (fim or erro) and not (pasta / "busca.avisado").exists():
            (pasta / "busca.avisado").write_text(time.strftime("%Y-%m-%d %H:%M"))
            n = candidatas(chave)
            if erro:
                avisos.append(f"A busca de fotos de {chave} falhou (veja .cache/imagens/{chave}/busca.log).{extra}")
            elif n:
                avisos.append(f"A busca de fotos de {chave} terminou com {n} candidatas: {instrucao(chave)}.{extra}")
            else:
                avisos.append(f"A busca de fotos de {chave} terminou sem candidatas (log em .cache/imagens/{chave}/"
                              f"busca.log). Siga a ordem das fontes da skill imagens.{extra}")
    if novos:
        acordar_trabalhador()
        avisos.insert(0, f"Conteúdo novo sem imagem: {', '.join(novos)}. Busca de fotos na fila, uma por vez, em "
                         f"segundo plano ({len(fila())} na fila); aviso quando cada uma terminar.")
    if avisos:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": evento.get("hook_event_name", "PostToolUse"),
                                                 "additionalContext": " ".join(avisos)}}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        trabalhar() if "--trabalhar" in sys.argv else main()
    except Exception:  # um gancho nunca pode atrapalhar a sessão
        pass
