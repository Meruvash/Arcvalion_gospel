"""Base comum das páginas: o <head> (igual ao pagina() do build_home.py do Elite Boardgamers), datas e gravação.

O CSS de cada tipo de página vem de estilo_elite.py (copiado do Elite, com o preto trocado por azul). CSS_EXTRA cobre
só o que o Elite não tinha: formulários, avisos de prévia e pendências, tabela dos livros da Bíblia.
"""
import hashlib
import html
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import portal
import estilo_elite as est

e = html.escape
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
MES_CURTO = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
BRT = timezone(timedelta(hours=-3))
ESCRITOS = []

CSS_EXTRA = """
.marca{display:flex;align-items:center;gap:9px;color:#fff;text-decoration:none}.marca .simbolo{width:38px;height:38px;flex:none;border-radius:8px;box-shadow:0 0 0 1px rgba(255,255,255,.16)}
.marca .marca-n{font-weight:800;font-size:1.08rem;line-height:1.1;letter-spacing:-.01em;white-space:nowrap;color:#fff}
@media (max-width:420px){.marca .marca-n{font-size:.98rem}.marca .simbolo{width:34px;height:34px}}
.exemplo,.previa-aviso{background:#fff3cd;color:#5c4400;border-bottom:1px solid #e6cf85;padding:8px 16px;font-size:.9rem;text-align:center}
.previa-aviso{background:#ffe3e3;color:#7a1f1f;border-color:#f0a8a8}
.pend{background:#fff3cd;color:#5c4400;border-radius:4px;padding:1px 6px}
.form-pc{display:grid;gap:12px;margin-top:10px}
.form-pc label{display:grid;gap:4px;font-weight:700;font-size:.92rem}.form-pc small{font-weight:600;color:var(--paper-muted,#5a6270)}
.form-pc input,.form-pc textarea{font:inherit;font-size:16px;font-weight:400;padding:10px 12px;border:1px solid #c8cdd5;border-radius:8px;background:#fff;color:#14171c}
.form-pc textarea{resize:vertical;min-height:120px}
.form-pc fieldset{border:1px solid #dde1e7;border-radius:8px;padding:10px 12px;margin:0}.form-pc legend{font-weight:700;font-size:.92rem;padding:0 4px}
.form-pc .ops{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:2px 10px}
.form-pc .op,.form-pc .consent{display:flex;gap:10px;align-items:flex-start;font-weight:500;min-height:44px;padding:8px 0}
.form-pc .op input,.form-pc .consent input{width:24px;height:24px;margin:2px 0 0;flex:none}
.form-pc button{justify-self:start;min-height:44px;padding:10px 22px;border-radius:999px;border:0;background:#0a1a33;color:#fff;font:inherit;font-weight:800;cursor:pointer}
.f-st{font-weight:700;font-size:.93rem}.f-st:empty{display:none}.f-st.ok{color:#1b7a45}.f-st.erro{color:#a3223a}
.form-off a{color:var(--link,#1f5fae);font-weight:700}.isca{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}
.nota .corpo ul{list-style:disc;padding-left:22px;display:grid;gap:6px}.nota .corpo a{color:var(--link)}
.equipe li{border-top:1px solid var(--paper-line);padding:10px 0}.equipe li:first-child{border-top:0}
.transp{font-size:.85rem;color:var(--paper-muted)}.transp b{color:var(--paper-ink)}
"""


def css_editorias():
    """Cor de cada editoria nas etiquetas (.cat.ed-x, papel claro) e no filete dos cartões e faixas sobre o azul (--cat)."""
    return "".join(f".cat.ed-{x['slug']}{{color:{x['cor']};background:{x['fundo']}}}.ed-{x['slug']}{{--cat:{x['viva']};--acc:{x['viva']}}}"
                   f".card-n.ed-{x['slug']}{{--cat:{x['viva']}}}" for x in portal.EDITORIAS)


def quando(iso):
    d = datetime.fromisoformat(iso)
    return (d if d.tzinfo else d.replace(tzinfo=BRT)).astimezone(BRT)


def data_longa(iso):
    d = quando(iso) if "T" in iso else datetime.fromisoformat(iso[:10])
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


def data_curta(iso):
    d = quando(iso) if "T" in iso else datetime.fromisoformat(iso[:10])
    return f"{d.day:02d}/{d.month:02d}"


def hoje():
    return datetime.now(BRT).date()


def versao(arq):
    arq = Path(arq)
    return f"?v={hashlib.md5(arq.read_bytes()).hexdigest()[:8]}" if arq.exists() else ""


def escrever(rel, texto):
    alvo = portal.SAIDA / rel
    alvo.parent.mkdir(parents=True, exist_ok=True)
    alvo.write_text(texto, encoding="utf-8")
    ESCRITOS.append(rel)


def capa_secao():
    return f"{portal.SITE}/marca/capa.png"


def pagina(titulo, descricao, url, imagem, pre, corpo, tipo="website", head_extra="", jsonld="", css=None, indexavel=True, largura=None):
    """<head> do Elite. Sem `url` (404) ou fora do índice (prévias), sai noindex."""
    cfg = portal.CFG
    css = est.CSS_HOME % {"pre": pre} if css is None else css
    robots = '<meta name="robots" content="max-image-preview:large">' if indexavel and url and not portal.EXEMPLO else '<meta name="robots" content="noindex">'
    verif = "".join(f'\n<meta name="{n}" content="{e(cfg["verificacao"][k])}">' for k, n in (("google", "google-site-verification"), ("bing", "msvalidate.01"))
                    if (cfg.get("verificacao") or {}).get(k))
    tok = (cfg.get("analytics") or {}).get("cloudflare_token")
    medidor = (f"""<!-- Cloudflare Web Analytics --><script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "{e(tok)}"}}'></script>"""
               if tok and not portal.EXEMPLO else "")
    dim = f'\n<meta property="og:image:width" content="{largura[0]}">\n<meta property="og:image:height" content="{largura[1]}">' if largura else ""
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(titulo)}</title>
<meta name="description" content="{e(descricao)}">
{f'<link rel="canonical" href="{url}">' + chr(10) if url else ''}{robots}{verif}
<meta property="og:site_name" content="{e(portal.NOME)}">
<meta property="og:locale" content="pt_BR">
<meta property="og:title" content="{e(titulo)}">
<meta property="og:description" content="{e(descricao)}">
<meta property="og:type" content="{tipo}">
<meta property="og:url" content="{url or portal.SITE + '/'}">
<meta property="og:image" content="{imagem}">{dim}
<meta name="twitter:card" content="summary_large_image">{head_extra}
<meta name="theme-color" content="#0a1a33">
<link rel="icon" href="{pre}marca/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{pre}marca/logo-180.png">
<link rel="alternate" type="application/rss+xml" title="{e(portal.NOME)}" href="{portal.SITE}/feed.xml">
<link rel="preload" href="{pre}fontes/public-sans.woff2" as="font" type="font/woff2" crossorigin>
<style>{css}{est.CSS_TRILHA}{est.CSS_BUSCA}{CSS_EXTRA}{css_editorias()}</style>
{jsonld}
</head>
<body>
{corpo}
{medidor}
</body>
</html>
"""
