"""Auditoria de isolamento: o Portal Cristão não pode depender nem carregar nada do Elite Boardgamers.

Uso: python3 tools/checar_isolamento.py [--original /caminho/do/repo/original]
Falha (código 1) se encontrar, no código, na configuração, no conteúdo ou no site gerado:
- o domínio ou a marca antiga em qualquer arquivo publicado (publico/) ou de configuração/código (fora de docs/);
- identificadores de recursos do projeto original (analytics, Turnstile, banco D1, conta Cloudflare, IndexNow,
  verificação do Google), que provariam projeto de analytics, banco ou credencial compartilhados;
- arquivos de credencial (.env, chaves privadas) ou padrões de tokens no repositório;
- remote do Git apontando para o repositório original.
Com --original, confere também que o repositório original não tem alterações (git status limpo).
"""
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
# identificadores públicos do projeto original, levantados na auditoria (docs/AUDITORIA_ELITE_BOARDGAMERS.md)
ORIGINAIS = {
    "domínio antigo": r"eliteboardgamers\.com\.br",
    "marca antiga": r"elite ?boardgamers",
    "token do Cloudflare Web Analytics do original": r"b37421bd1ade44f1a59e46b96626bf03",
    "site key do Turnstile do original": r"0x4AAAAAAFrf_u5uh6OZZemp",
    "banco D1 do original": r"e117a6dc-26b6-49d7-a02e-7b57e8be4852",
    "conta Cloudflare do original": r"0b88cc2d6b58c936265686f078d9969f",
    "chave IndexNow do original": r"788e463403f2d9cfd5dffb7304088938",
    "verificação Google do original": r"google6eabfb67f89b80bc",
    "repositório original": r"golden-geek",
    "grupo de WhatsApp do original": r"IgQQkJdSkzHBaEq3UwFeAo",
}
SEGREDOS = r"(sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY|xox[bp]-[A-Za-z0-9-]+)"
IGNORAR = {".git", ".cache", "node_modules"}
# documentação pode citar o original (é o histórico da migração); este arquivo precisa listar os identificadores
LIVRES = {"docs", "tools/checar_isolamento.py"}
TEXTO = {".py", ".js", ".mjs", ".json", ".html", ".xml", ".txt", ".md", ".toml", ".sql", ".yml", ".yaml", ".css", ".svg"}


def arquivos():
    for p in RAIZ.rglob("*"):
        rel = p.relative_to(RAIZ)
        if p.is_file() and not IGNORAR & set(rel.parts):
            yield rel, p


def livre(rel):
    s = rel.as_posix()
    return any(s == x or s.startswith(x + "/") for x in LIVRES)


def checar(original=None):
    erros = []
    for rel, p in arquivos():
        if rel.name.startswith(".env") or rel.suffix in {".pem", ".key"}:
            erros.append(f"arquivo de credencial no repositório: {rel}")
        if p.suffix not in TEXTO:
            continue
        s = p.read_text(encoding="utf-8", errors="ignore")
        if re.search(SEGREDOS, s):
            erros.append(f"possível segredo em {rel}")
        publicado = rel.parts[0].startswith("publico")
        for nome, padrao in ORIGINAIS.items():
            # a marca antiga pode aparecer em comentários de código-fonte que documentam a origem ("Portado de ...");
            # no site publicado e nos identificadores de recurso, nunca
            if nome == "marca antiga" and not publicado and p.suffix == ".py":
                continue
            if not livre(rel) and re.search(padrao, s, re.I):
                erros.append(f"{nome} em {rel}")
    r = subprocess.run(["git", "remote", "-v"], cwd=RAIZ, capture_output=True, text=True)
    if re.search(ORIGINAIS["repositório original"], r.stdout, re.I):
        erros.append("o remote do Git aponta para o repositório original")
    if original:
        st = subprocess.run(["git", "status", "--porcelain"], cwd=original, capture_output=True, text=True)
        if st.returncode:
            erros.append(f"não consegui ler o repositório original em {original}")
        elif st.stdout.strip():
            erros.append("o repositório original tem alterações locais:\n" + st.stdout)
    return erros


def main(args):
    original = args[args.index("--original") + 1] if "--original" in args else None
    erros = checar(original)
    print("\n".join("❌ " + e for e in erros) if erros else
          "ok isolamento: nenhum domínio, marca, identificador de recurso ou credencial do projeto original" + (" e original intacto" if original else ""))
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
