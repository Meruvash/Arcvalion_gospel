"""Resumo de visitas do site (Cloudflare Web Analytics): hoje e ontem, no horário de Brasília.

Uso: python3 tools/resumo_visitas.py [--semana]   (--semana acrescenta as visitas por dia dos últimos 7 dias)
Precisa de duas variáveis de ambiente, configuradas no ambiente da nuvem (nunca no repositório):
  CLOUDFLARE_API_TOKEN   chave só de leitura com a permissão "Account Analytics: Read"
  CLOUDFLARE_ACCOUNT_ID  opcional: ID da conta (padrão: a conta onde está o domínio, em CONTA abaixo)
Visitas = entradas no site vindas de fora; visualizações = páginas abertas. Sem cookies, a Cloudflare não sabe se duas
visitas são da mesma pessoa, então "visitas" é o número mais próximo de "pessoas", não uma contagem exata.
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

HOST = "meruvash.github.io"
API = "https://api.cloudflare.com/client/v4/graphql"
BRT = timezone(timedelta(hours=-3))
CONTA = ""  # ID da conta Cloudflare: use a variável CLOUDFLARE_ACCOUNT_ID

# assistentes de IA que mandam visita com origem (ChatGPT, Perplexity, Claude, Gemini, Copilot)
IAS = ["chatgpt.com", "chat.openai.com", "perplexity.ai", "www.perplexity.ai", "claude.ai", "gemini.google.com", "copilot.microsoft.com"]

CONSULTA = """query($conta: String!, $ini: Time!, $fim: Time!, $host: String!, $ias: [String!]) {
  viewer { accounts(filter: {accountTag: $conta}) {
    total: rumPageloadEventsAdaptiveGroups(limit: 1, filter: {datetime_geq: $ini, datetime_lt: $fim, requestHost: $host}) {
      count sum { visits } }
    paginas: rumPageloadEventsAdaptiveGroups(limit: 5, orderBy: [count_DESC], filter: {datetime_geq: $ini, datetime_lt: $fim, requestHost: $host}) {
      count dimensions { requestPath } }
    origens: rumPageloadEventsAdaptiveGroups(limit: 5, orderBy: [sum_visits_DESC], filter: {datetime_geq: $ini, datetime_lt: $fim, requestHost: $host}) {
      sum { visits } dimensions { refererHost } }
    ia: rumPageloadEventsAdaptiveGroups(limit: 10, filter: {datetime_geq: $ini, datetime_lt: $fim, requestHost: $host, refererHost_in: $ias}) {
      sum { visits } dimensions { refererHost } }
    aparelhos: rumPageloadEventsAdaptiveGroups(limit: 5, orderBy: [count_DESC], filter: {datetime_geq: $ini, datetime_lt: $fim, requestHost: $host}) {
      count dimensions { deviceType } }
  } }
}"""


def consultar(token, conta, ini, fim):
    corpo = json.dumps({"query": CONSULTA, "variables": {"conta": conta, "ini": ini.isoformat(), "fim": fim.isoformat(), "host": HOST, "ias": IAS}}).encode()
    req = urllib.request.Request(API, data=corpo, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        dados = json.loads(r.read())
    if dados.get("errors"):
        sys.exit("A Cloudflare recusou a consulta: " + "; ".join(e.get("message", "") for e in dados["errors"]))
    return dados["data"]["viewer"]["accounts"][0]


def periodo(nome, d):
    total = d["total"][0] if d["total"] else {"count": 0, "sum": {"visits": 0}}
    linhas = [f"*{nome}*: {total['sum']['visits']} visitas, {total['count']} visualizações"]
    if d["paginas"]:
        linhas.append("  Páginas mais lidas: " + "; ".join(f"{p['dimensions']['requestPath']} ({p['count']})" for p in d["paginas"]))
    # navegação dentro do próprio site não é origem de visita
    origens = [o for o in d["origens"] if o["dimensions"]["refererHost"] != HOST]
    if origens:
        linhas.append("  De onde veio: " + "; ".join(f"{o['dimensions']['refererHost'] or 'direto/sem origem'} ({o['sum']['visits']})" for o in origens))
    ia = sum(o["sum"]["visits"] for o in d["ia"])
    linhas.append(f"  De assistentes de IA: {ia}" + (" (" + "; ".join(f"{o['dimensions']['refererHost']} ({o['sum']['visits']})" for o in d["ia"]) + ")" if ia else ""))
    if d["aparelhos"]:
        linhas.append("  Aparelhos: " + "; ".join(f"{a['dimensions']['deviceType']} ({a['count']})" for a in d["aparelhos"]))
    return "\n".join(linhas)


DIAS = ("seg", "ter", "qua", "qui", "sex", "sáb", "dom")
BUSCADORES = ("google", "bing", "duckduckgo", "yahoo", "ecosia", "yandex")


def tendencia(token, conta, hoje, dias=7):
    """Visitas por dia nos últimos dias fechados (horário de Brasília) e quantas vieram de buscadores."""
    linhas = ["*Últimos dias* (visitas no total · vindas do Google e outros buscadores)"]
    totais = []
    for i in range(dias, 0, -1):
        ini = hoje - timedelta(days=i)
        d = consultar(token, conta, ini, ini + timedelta(days=1))
        total = d["total"][0]["sum"]["visits"] if d["total"] else 0
        busca = sum(o["sum"]["visits"] for o in d["origens"] if any(b in (o["dimensions"]["refererHost"] or "") for b in BUSCADORES))
        totais.append((total, busca))
        if total or totais[:-1] and any(t for t, _ in totais[:-1]):
            linhas.append(f"  {ini:%d/%m} ({DIAS[ini.weekday()]}): {total} visitas · {busca} de buscador")
    com_dados = [t for t in totais if t[0]]
    if len(com_dados) >= 2:
        (a, ba), (b, bb) = com_dados[0], com_dados[-1]
        linhas.append(f"  Do primeiro ao último dia com dados: {a} → {b} visitas; buscadores {ba} → {bb}.")
    return "\n".join(linhas)


def main():
    token, conta = os.environ.get("CLOUDFLARE_API_TOKEN"), os.environ.get("CLOUDFLARE_ACCOUNT_ID") or CONTA
    if not token:
        sys.exit("Falta CLOUDFLARE_API_TOKEN no ambiente.")
    agora = datetime.now(BRT)
    hoje = agora.replace(hour=0, minute=0, second=0, microsecond=0)
    ontem = hoje - timedelta(days=1)
    print(f"Visitas em PREENCHER_DOMINIO (horário de Brasília, {agora:%d/%m %H:%M})")
    print(periodo(f"Hoje, até {agora:%H:%M}", consultar(token, conta, hoje, agora)))
    print(periodo(f"Ontem ({ontem:%d/%m})", consultar(token, conta, ontem, hoje)))
    if "--semana" in sys.argv:
        print(tendencia(token, conta, hoje))


if __name__ == "__main__":
    main()
