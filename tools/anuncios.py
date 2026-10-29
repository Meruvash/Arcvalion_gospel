"""Espaços publicitários (config/anuncios.json). Não existia no Elite Boardgamers; segue as mesmas regras de performance.

espaco(posicao, pre, editoria) -> (html, tem_anuncio). O espaço:
- reserva a altura no CSS antes de qualquer script (sem empurrar o texto: CLS zero);
- sempre mostra o rótulo "Publicidade" (separação entre jornalismo e conteúdo comercial);
- sem anunciante, mostra o anúncio da casa (link para Anuncie conosco) ou nada;
- com AdSense configurado, js/anuncios.js só carrega o script do Google depois do consentimento de publicidade (LGPD);
- js/anuncios.js mede impressões visíveis e cliques por espaço, de forma agregada, se a API do Worker estiver ligada.
"""
import html

import portal

e = html.escape


def _vale(esp, editoria):
    if esp.get("editorias") and editoria not in esp["editorias"]:
        return False
    return not (editoria and editoria in (esp.get("fora_editorias") or []))


def espaco(posicao, pre, editoria=None, classe=""):
    cfg = portal.ANUNCIOS
    if not cfg.get("ativo"):
        return "", False
    esp = next((x for x in cfg.get("espacos", []) if x["posicao"] == posicao and _vale(x, editoria)), None)
    if not esp:
        return "", False
    casa = cfg.get("casa", {})
    adsense = bool(cfg.get("adsense_cliente") and esp.get("adsense_slot"))
    # o anúncio da casa só ocupa os espaços que aceitam ("casa": false no espaço reserva o lugar só para anunciante real)
    casa_ok = casa.get("ativo") and esp.get("casa", True)
    if not adsense and not casa_ok:
        return "", False
    so_pc = " so-pc" if not esp.get("altura_celular") else ""
    hm, hd = esp.get("altura_celular") or 0, esp.get("altura_computador") or 0
    conteudo = (f'<a class="pub-casa" href="{pre}anuncie/" data-casa="1"><b>{e(casa.get("titulo", ""))}</b>'
                f'<span>{e(casa.get("texto", ""))}</span><i>{e(casa.get("botao", "Anuncie conosco"))} →</i></a>') if casa_ok else ""
    api = (portal.CFG.get("interacoes") or {}).get("api", "")
    dados = (f' data-espaco="{e(esp["id"])}" data-slot="{e(esp.get("adsense_slot", ""))}" data-cliente="{e(cfg.get("adsense_cliente", ""))}"'
             f' data-api="{e(api)}" data-ed="{e(editoria or "")}"')
    return (f'<aside class="pub{so_pc} {classe}" aria-label="{e(cfg.get("rotulo", "Publicidade"))}"{dados}>'
            f'<span class="pub-rot">{e(cfg.get("rotulo", "Publicidade"))}</span>'
            f'<div class="pub-in" style="--hm:{hm}px;--hd:{hd}px">{conteudo}</div></aside>'), True
