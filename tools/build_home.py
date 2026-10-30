"""Gera a página inicial de notícias e a página de cada notícia.

Uso: python3 tools/build_home.py
Lê conteudo/noticias/*.json (uma nota por arquivo), conteudo/home.json (Destaques, chave em_alta; Financiamentos, Agenda),
conteudo/lancamentos/<AAAA-MM>.json (calendário da Ludopedia) e pauta.json (últimas resenhas).
Saída: index.html e noticias/<slug>/index.html. As regras das notas estão em PLANO_NOTICIAS.md.
"""
import json
import re
import subprocess
import sys
import unicodedata
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from PIL import Image  # noqa: E402
import seo  # noqa: E402
import capas_grandes  # noqa: E402
from imagens_resp import miniatura, srcset  # noqa: E402
from build_sitemap import lastmod_registrado  # noqa: E402
from build_review import INSTAGRAM, ROOT, SITE, WHATSAPP, e, icone, versao  # noqa: E402
from og import url_cartao  # noqa: E402
from layout import _config_interacoes, barra_leitura, botao_compartilhar, convite_compartilhar, interacoes  # noqa: E402
from layout import CSS_BUSCA, CSS_TRILHA, EMAIL, cabecalho, rodape, trilha  # noqa: E402
from noticias.checar_noticia import checar_dia, problemas  # noqa: E402
import portal  # noqa: E402  (iniciado pelo checar_noticia)

MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
SELO_CLASSE = {"Boa notícia": "compra", "Vale acompanhar": "acompanhar", "Para refletir": "fas", "Motivo de alerta": "ressalvas", "Informativo": "info"}
# categorias na ordem dos chips do arquivo de notícias, com o trecho de URL de cada uma
CATEGORIAS = {"Notícias Gospel": "noticias-gospel", "Política e Sociedade": "politica-e-sociedade", "Família e Valores": "familia-e-valores", "Fé e Bíblia": "fe-e-biblia",
              "Economia e Negócios": "economia-e-negocios", "Música e Cultura Cristã": "musica-e-cultura", "Eventos": "eventos"}
CAT_CLASSE = {"Notícias Gospel": "mercado", "Política e Sociedade": "financ", "Família e Valores": "brasil", "Fé e Bíblia": "premios",
              "Economia e Negócios": "mercado", "Música e Cultura Cristã": "financ", "Eventos": "premios"}


def norm(t):
    return unicodedata.normalize("NFKD", t.lower()).encode("ascii", "ignore").decode()


def data_longa(iso):
    d = date.fromisoformat(iso)
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


def data_curta(iso):
    d = date.fromisoformat(iso)
    return f"{d.day:02d}/{d.month:02d}"


def publicado_em(p):
    """Hora em que a nota entrou no site: o commit que criou o arquivo ou, se ainda não foi commitado, agora."""
    r = subprocess.run(["git", "log", "--diff-filter=A", "--format=%cI", "--", str(p.relative_to(ROOT))],
                       cwd=ROOT, capture_output=True, text=True)
    linhas = r.stdout.split()
    return linhas[-1] if r.returncode == 0 and linhas else datetime.now(timezone.utc).isoformat(timespec="seconds")


PREVIA = []


def notas():
    ns = []
    PREVIA.clear()
    for p in sorted((ROOT / "conteudo" / "noticias").glob("*.json")):
        n = json.loads(p.read_text(encoding="utf-8"))
        # a ordem das Últimas notícias depende da hora de publicação: nota sem ela ganha uma e o arquivo é salvo
        if not n.get("publicado_em"):
            n["publicado_em"] = publicado_em(p)
            p.write_text(json.dumps(n, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        if n.get("status") == "revisao":  # ainda não aprovada (tools/publicar.py, automática desde 29/10/2026): vai só para a prévia
            PREVIA.append(n)
            continue
        if n.get("status", "publicado") != "publicado":
            continue
        ns.append(n)
    ruins = {n["slug"]: problemas(n) for n in ns + PREVIA if problemas(n, publicar=n in ns)}
    if ruins:
        sys.exit("Notícias fora do padrão (rode tools/noticias/checar_noticia.py): " + ", ".join(ruins))
    if checar_dia(ns):
        sys.exit("Edição do dia: " + "; ".join(checar_dia(ns)))
    # mais recentes primeiro (dia e hora de publicação); empate, as mais pontuadas no crivo
    return sorted(ns, key=lambda n: (n["data"], datetime.fromisoformat(n["publicado_em"]).timestamp(), n["crivo"]["pontos"]), reverse=True)


def mes_chegando(hoje=None):
    """Mês do bloco Chegando ao Brasil: o atual até o dia 14, depois o próximo (se a coleta já salvou)."""
    hoje = hoje or date.today()
    prox = (hoje.replace(day=1) + timedelta(days=32)).replace(day=1).strftime("%Y-%m")
    if hoje.day >= 15 and (ROOT / "conteudo" / "lancamentos" / f"{prox}.json").exists():
        return prox
    meses = sorted(p.stem for p in (ROOT / "conteudo" / "lancamentos").glob("*.json"))
    atual = hoje.strftime("%Y-%m")
    return atual if atual in meses else max(m for m in meses)


def lancamentos(mes):
    d = json.loads((ROOT / "conteudo" / "lancamentos" / f"{mes}.json").read_text(encoding="utf-8"))
    jogos = [j for g in ("previstos", "lancados") for j in d[g] if j.get("fl_tipo") == 1]
    return d["label"], jogos


def capa_jogo(pre, id_jogo):
    return f"{pre}noticias/capas/{id_jogo}.jpg"


CSS = """
@font-face{font-family:"Public Sans";src:url(%(pre)sfontes/public-sans.woff2) format("woff2");font-weight:400 800;font-display:swap}
/* Moldura preta da marca com cartões claros de leitura; régua de densidade do BoardGameGeek */
:root{color-scheme:dark;--ground:#0a1a33;--bar:#0a1a33;--panel:#0f2242;--panel2:#142b52;--ink:#eceff3;--muted:#a1a9b5;--line:#1e3a64;
--paper:#f4f5f7;--paper-ink:#14171c;--paper-muted:#5a6270;--paper-line:#dde1e7;--gold:#e3b23c;--link:#1f5fae;--zap:#157a43;
--premios:#8a5f00;--premios-bg:#fff4d1;--brasil:#1b7a45;--brasil-bg:#e3f4ea;--mercado:#1f5fae;--mercado-bg:#e3ecf8;--financ:#6b4ea3;--financ-bg:#efe9f8}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%%}
body{margin:0;background:var(--ground);color:var(--ink);font:16px/1.55 "Public Sans",system-ui,sans-serif;padding-left:env(safe-area-inset-left,0px);padding-right:env(safe-area-inset-right,0px)}
h1,h2,h3,p,ul,ol,figure{margin:0}ul,ol{padding:0;list-style:none}img{display:block;max-width:100%%;height:auto}a{color:inherit}
::selection{background:var(--gold);color:#0a1a33}
:focus-visible{outline:3px solid var(--gold);outline-offset:2px;border-radius:3px}
.in{max-width:1180px;margin:0 auto;padding-left:16px;padding-right:16px}
.ic{width:20px;height:20px;fill:none;stroke:currentColor;stroke-width:1.75;stroke-linecap:round;stroke-linejoin:round;flex:none}
.bar{border-bottom:1px solid var(--line);background:var(--bar)}
.bar .in{display:flex;align-items:center;gap:12px;padding-top:8px;padding-bottom:8px}
.marca img{width:84px;border-radius:6px}
.bar a{text-decoration:none;font-weight:600;font-size:.95rem}
.bar .ig{margin-left:auto;display:flex;align-items:center;gap:6px;padding:6px 10px;border-radius:6px}.bar .ig:hover{color:var(--gold)}
.bar .zap-mini{display:flex;align-items:center;gap:6px;padding:6px 10px;border-radius:6px;background:var(--zap);color:#fff}
.nav{border-bottom:1px solid var(--line);background:var(--panel)}
.nav ul{display:flex;gap:2px;overflow-x:auto;scrollbar-width:none;padding-top:0;padding-bottom:0}
.nav a{display:block;padding:11px 12px;white-space:nowrap;text-decoration:none;font-weight:700;font-size:.92rem;border-bottom:3px solid transparent}
.nav a:hover{border-bottom-color:var(--gold)}.nav a[aria-current]{color:var(--gold);border-bottom-color:var(--gold)}
@media (max-width:700px){.bar .ig span,.bar .zap-mini span{display:none}}
.edicao{color:var(--muted);font-size:.85rem;padding-top:14px}
.grade{display:grid;gap:18px;padding-top:10px;padding-bottom:40px}
.lado{display:contents}
.manchete{order:1}.ultimas{order:2}.brasil{order:3}.alta{order:4}.financ{order:5}.agenda{order:6}.resenhas{order:7}.comunidade{order:8}
@media (min-width:900px){
 .grade{grid-template-columns:minmax(0,1fr) 340px;grid-template-areas:"manchete lado" "ultimas lado" "brasil brasil" "financ resenhas" "comunidade comunidade";align-items:start}
 .lado{display:grid;gap:18px;grid-area:lado;align-content:start}
 .manchete{grid-area:manchete}.ultimas{grid-area:ultimas}.brasil{grid-area:brasil}.financ{grid-area:financ}.resenhas{grid-area:resenhas}.comunidade{grid-area:comunidade}
}
.bloco{background:var(--paper);color:var(--paper-ink);border-radius:10px;padding:16px;min-width:0}
.bloco>h2,.bloco>.h-sec{display:flex;align-items:baseline;justify-content:space-between;gap:10px;font-size:.8rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--paper-muted);margin-bottom:12px;padding-bottom:8px;border-bottom:2px solid var(--paper-ink)}
.bloco>h2 a{display:inline-flex;align-items:center;min-height:24px;font-size:.8rem;letter-spacing:0;text-transform:none;color:var(--link);font-weight:700;text-decoration:none}
.bloco>h2 a:hover{text-decoration:underline}
.cat{display:inline-block;font-size:.72rem;font-weight:800;letter-spacing:.04em;text-transform:uppercase;border-radius:4px;padding:2px 7px}
.cat.premios{color:var(--premios);background:var(--premios-bg)}.cat.brasil{color:var(--brasil);background:var(--brasil-bg)}
.cat.mercado{color:var(--mercado);background:var(--mercado-bg)}.cat.financ{color:var(--financ);background:var(--financ-bg)}
.meta{font-size:.8rem;color:var(--paper-muted)}
/* manchete */
.manchete{padding:0;overflow:hidden;display:grid}
.manchete a{text-decoration:none;display:grid}
.manchete figure{background:#13284a}
.manchete img{width:100%%;aspect-ratio:16/10;object-fit:cover;object-position:center 30%%}
.manchete .txt{padding:16px;display:grid;gap:8px}
.manchete .kick{font-size:.75rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--premios)}
.manchete .m-tit{font-size:clamp(1.5rem,4.2vw,2.2rem);line-height:1.12;font-weight:800;letter-spacing:-.015em;text-wrap:balance}
.manchete a:hover .m-tit{text-decoration:underline;text-decoration-thickness:2px;text-underline-offset:4px}
.manchete p{color:#3a414c;max-width:62ch}
.credito{font-size:.72rem;color:var(--paper-muted)}
@media (min-width:640px){.manchete a{grid-template-columns:42%% 1fr}.manchete img{aspect-ratio:auto;height:100%%;min-height:300px}.manchete .txt{padding:20px 22px;align-content:center}}
/* últimas */
.lista-n li{border-top:1px solid var(--paper-line)}.lista-n li:first-child{border-top:0}
.lista-n a{display:grid;grid-template-columns:76px 1fr;gap:12px;padding:12px 0;text-decoration:none}
.lista-n li:first-child a{padding-top:0}
.lista-n img,.lista-n .sem{width:76px;height:76px;border-radius:6px;object-fit:cover;background:#e6e9ee}
.lista-n .sem{display:grid;place-items:center;color:var(--paper-muted)}
.lista-n h3,.nota .lista-n h2{font-size:1.02rem;line-height:1.25;font-weight:800;margin:3px 0 2px;text-wrap:balance;letter-spacing:0;text-transform:none;color:inherit}
.lista-n a:hover h3{text-decoration:underline}
.lista-n p{font-size:.88rem;color:#3a414c;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
/* destaques (chave em_alta): régua do "The Hotness" do BGG */
.alta .crit-h{font-size:.8rem;color:var(--paper-muted);margin:-4px 0 8px}
.hot li{counter-increment:h;border-top:1px solid var(--paper-line)}.hot li:first-child{border-top:0}
.hot{counter-reset:h}
.hot a{display:grid;grid-template-columns:22px 44px 1fr;gap:10px;align-items:center;padding:9px 0;text-decoration:none}
.hot a::before{content:counter(h);font-weight:800;font-size:1.05rem;color:var(--paper-muted);text-align:right;font-variant-numeric:tabular-nums}
.hot img{width:44px;height:44px;object-fit:cover;border-radius:4px}
.hot b{display:block;font-size:.93rem;line-height:1.25}.hot span{display:block;font-size:.8rem;color:var(--paper-muted)}
.hot a:hover b{text-decoration:underline}
/* agenda */
.agenda li{display:grid;grid-template-columns:104px 1fr;gap:10px;padding:9px 0;border-top:1px solid var(--paper-line);font-size:.9rem}
.agenda li:first-child{border-top:0;padding-top:0}
.agenda .q{font-weight:800;font-variant-numeric:tabular-nums}.agenda .q small{display:block;font-weight:600;font-size:.72rem;color:var(--paper-muted)}
.agenda .d{color:var(--paper-muted);font-size:.82rem}.agenda a{display:inline-block;padding:3px 0;text-decoration:none}.agenda a:hover{text-decoration:underline}
/* chegando ao Brasil */
.capas{display:flex;gap:12px;overflow-x:auto;scroll-snap-type:x mandatory;padding-bottom:6px}
.capas li{flex:0 0 132px;scroll-snap-align:start}
.capas a{display:grid;gap:6px;text-decoration:none}
.capas img{width:132px;height:140px;object-fit:cover;border-radius:6px;background:#e6e9ee}
.capas b{font-size:.86rem;line-height:1.2}.capas span{font-size:.75rem;color:var(--paper-muted)}
.capas .st{justify-self:start;font-size:.68rem;font-weight:800;border-radius:4px;padding:1px 6px;color:var(--brasil);background:var(--brasil-bg)}
.capas .st.lancado{color:#fff;background:var(--brasil)}
.capas a:hover b{text-decoration:underline}
.capas .todos a{height:100%%;min-height:140px;align-content:center;justify-items:center;text-align:center;border-radius:6px;background:var(--brasil-bg);color:var(--brasil);padding:12px}
.capas .todos .mais{font-size:.86rem;font-weight:800;line-height:1.25}.capas .todos .mais::after{content:" →";content:" →" / ""}
/* financiamentos */
.financ li{display:grid;gap:2px;padding:10px 0;border-top:1px solid var(--paper-line)}.financ li:first-child{border-top:0;padding-top:0}
.financ a{font-weight:800;text-decoration:none}.financ a:hover{text-decoration:underline}
.financ .onde{font-size:.72rem;font-weight:800;text-transform:uppercase;letter-spacing:.04em;color:var(--financ)}
.financ .s{font-size:.86rem;color:#3a414c}.financ .f{font-size:.75rem;color:var(--paper-muted)}
/* resenhas */
.res{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.res a{display:grid;gap:6px;text-decoration:none}
.res img{width:100%%;aspect-ratio:1;object-fit:cover;border-radius:6px}
.res b{font-size:.9rem;line-height:1.2}.res a:hover b{text-decoration:underline}
.comunidade{background:var(--panel2);color:var(--ink);border:1px solid var(--line);display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:space-between}
.comunidade p{max-width:60ch;color:#c9cfd8}
.comunidade .acoes{display:flex;flex-wrap:wrap;gap:10px}
.btn{display:flex;align-items:center;gap:8px;padding:12px 16px;border-radius:10px;text-decoration:none;font-weight:800}
.btn.zap{background:var(--zap);color:#fff}.btn.ig{border:1px solid #2e4d7a}.btn.ig:hover{border-color:var(--gold);color:var(--gold)}
footer{border-top:1px solid var(--line);font-size:.88rem}
footer .in{display:flex;flex-wrap:wrap;gap:10px 20px;padding-top:18px;padding-bottom:18px}
.selo{display:inline-block;font-size:.74rem;font-weight:800;border-radius:999px;padding:2px 10px;color:#fff;white-space:nowrap}
.selo.compra{background:#157a43}.selo.acompanhar{background:#1f5fae}.selo.fas{background:#6b4ea3}.selo.ressalvas{background:#8a5200}.selo.info{background:#5a6270}
.manchete .opina{font-size:.92rem;color:var(--paper-ink);border-left:3px solid var(--gold);padding-left:10px}
/* página da notícia */
.nota{max-width:760px;margin:0 auto;padding-top:20px;padding-bottom:48px;display:grid;gap:16px}
.nota .bloco{padding:20px}
.nota h1{font-size:clamp(1.6rem,5vw,2.4rem);line-height:1.12;font-weight:800;letter-spacing:-.015em;text-wrap:balance;margin:8px 0}
.nota .lide{font-size:1.08rem;font-weight:600;color:var(--paper-ink)}
.nota .corpo{display:grid;gap:12px;color:#3a414c;max-width:66ch}
.nota figure img{width:100%%;max-height:420px;object-fit:contain;background:#e6e9ee;border-radius:8px}
.nota figcaption{margin-top:6px}
.nota h2,.nota .h-sec{font-size:.8rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--paper-muted);margin-bottom:8px}
.nota .h-sec{margin:0 0 8px;line-height:inherit;text-wrap:wrap}
.leia li{padding:8px 0;border-top:1px solid var(--paper-line)}.leia li:first-child{border-top:0}.leia a{display:inline-block;padding:3px 0;color:var(--link);font-weight:700;text-decoration:none}.leia a:hover{text-decoration:underline}
/* arquivo de notícias: manchete em destaque e quadradinhos sobre a moldura preta */
.arq{display:grid;gap:16px;padding-top:16px;padding-bottom:40px}
.arq-topo{display:grid;gap:4px}.arq-topo h1{font-size:clamp(1.6rem,4.5vw,2.3rem);line-height:1.1;font-weight:800;letter-spacing:-.015em}.arq-topo p{color:var(--muted);font-size:.95rem}
.cats{display:flex;flex-wrap:wrap;gap:8px}.cats[hidden]{display:none}
.cats button{font:inherit;font-size:.86rem;font-weight:700;min-height:36px;padding:4px 12px;border-radius:999px;border:1px solid #2e4d7a;background:var(--panel2);color:var(--ink);cursor:pointer}
.cats button small{margin-left:6px;font-weight:600;color:var(--muted);font-variant-numeric:tabular-nums}
.cats button:hover{border-color:var(--gold)}.cats button[aria-pressed="true"]{background:var(--gold);border-color:var(--gold);color:#0a1a33}.cats button[aria-pressed="true"] small{color:#3a2a00}
.cat-nota{font-size:.9rem;color:var(--muted)}.cat-nota a{color:var(--gold);font-weight:700}
.arq .manchete[hidden],.card-n[hidden]{display:none}
/* .brasil, .financ e .manchete também são nomes de blocos da home (ordem e área de grade): no arquivo não valem */
.arq .manchete,.arq .brasil,.arq .financ,.arq .mercado,.arq .premios{grid-area:auto;order:0}
.grade-n{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
@media (min-width:600px){.grade-n{grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}}
@media (min-width:1000px){.grade-n{grid-template-columns:repeat(4,minmax(0,1fr))}}
.card-n a{display:flex;flex-direction:column;height:100%%;background:var(--paper);color:var(--paper-ink);border-radius:10px;overflow:hidden;text-decoration:none;border:2px solid transparent}
.card-n a:hover{border-color:var(--gold)}.card-n a:hover h2{text-decoration:underline}
.card-n .ci{position:relative;display:block;aspect-ratio:1;overflow:hidden;background:#e6e9ee}.card-n img{position:absolute;inset:0;width:100%%;height:100%%;object-fit:cover}
.card-n .sem{position:absolute;inset:0;display:grid;place-items:center;width:100%%;height:100%%}.card-n .sem .ic{width:40px;height:40px}
.card-n .sem.premios{background:var(--premios-bg);color:var(--premios)}.card-n .sem.brasil{background:var(--brasil-bg);color:var(--brasil)}.card-n .sem.mercado{background:var(--mercado-bg);color:var(--mercado)}.card-n .sem.financ{background:var(--financ-bg);color:var(--financ)}
.card-n .cb{display:grid;gap:6px;align-content:start;padding:10px 12px 14px;flex:1}
.card-n .cat{justify-self:start}.card-n .selo{justify-self:start}
.card-n h2{font-size:1rem;line-height:1.25;font-weight:800;text-wrap:balance}
.card-n .resumo{font-size:.86rem;color:#3a414c;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
@media (max-width:599px){.card-n .resumo{display:none}.card-n h2{font-size:.95rem}.card-n .cb{padding:9px 10px 12px}.card-n .cat{font-size:.66rem}}
.arq .paginas{margin:0;color:var(--ink)}.arq .paginas a{color:var(--gold)}.arq .paginas span{color:var(--muted)}
.paginas{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-top:16px;font-weight:700}.paginas a{color:var(--link)}.paginas span{color:var(--paper-muted);font-size:.9rem}
.nota .fontes li{margin:6px 0;font-size:.92rem}.nota .fontes a{color:var(--link)}.nota .fontes span{color:var(--paper-muted);font-size:.82rem}
.nota .jogos{display:flex;flex-wrap:wrap;gap:8px}.nota .jogos a{display:inline-block;padding:6px 10px;border-radius:6px;background:#e6e9ee;text-decoration:none;font-weight:700;font-size:.9rem}
.nota .crivo{font-size:.85rem;color:var(--paper-muted)}.nota .crivo b{color:var(--paper-ink)}
.volta{color:var(--gold);font-weight:700;text-decoration:none}
.nota .abre{display:grid;gap:14px}
.nota .importa{border-left:4px solid var(--gold)}.nota .importa p{font-size:1.02rem;color:var(--paper-ink)}.nota .assina{font-size:.78rem!important;color:var(--paper-muted)!important;margin-top:8px}
.nums{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px}
.nums li{background:#fff;border:1px solid var(--paper-line);border-radius:8px;padding:12px;display:grid;gap:2px}
.nums b{font-size:1.35rem;line-height:1.15;font-weight:800;font-variant-numeric:tabular-nums}.nums span{font-size:.86rem;color:#3a414c}.nums small{font-size:.72rem;color:var(--paper-muted)}
.nota .brasil-n{border-left:4px solid var(--brasil)}.nota .brasil-n p{color:#3a414c}
.crit{display:grid;gap:12px}.crit p{color:#3a414c}
.crit .cit q{display:block;font-size:1.15rem;font-weight:700;line-height:1.3;color:var(--paper-ink);quotes:"“" "”"}
.crit cite{display:block;margin-top:4px;font-style:normal;font-size:.82rem;color:var(--paper-muted)}
.nota .quem{display:grid;gap:16px}@media (min-width:640px){.nota .quem{grid-template-columns:1fr 1fr}}
.quem li{position:relative;padding-left:16px;margin:6px 0;color:#3a414c}.quem li::before{content:"";position:absolute;left:0;top:.6em;width:7px;height:7px;border-radius:50%%;background:#1b7a45}
.quem .no li::before{background:#b3263e}
.nota .veredito{background:var(--panel2);color:var(--ink);border:1px solid var(--gold)}.nota .veredito h2{color:var(--gold)}
.nota .veredito p{font-size:1.08rem;font-weight:600;margin-top:10px;max-width:62ch}
.nota .veredito p.versiculo{font-size:.92rem;font-weight:400;font-style:italic;color:var(--muted);margin-top:14px;padding-top:10px;border-top:1px solid var(--line)}
.nota .veredito .versiculo cite{font-style:normal;font-size:.82rem;white-space:nowrap}
/* celular: blocos de ponta a ponta, lista enxuta e textos miúdos um pouco maiores */
@media (max-width:599px){
 .marca img{width:68px}
 .grade{gap:8px;padding-bottom:24px}.nota{gap:8px;padding-top:14px;padding-bottom:24px}
 .grade .bloco,.nota .bloco{margin-left:-16px;margin-right:-16px;border-radius:0}
 .nota .bloco{padding:18px 16px}
 .nota .abre figure{margin:-18px -16px 0}.nota .abre figure img{border-radius:0;max-height:440px;object-fit:contain}
 .nota .abre figcaption{padding:0 16px}
 .manchete img{aspect-ratio:4/3;object-position:center top}.manchete .txt{padding:16px 16px 18px}.manchete .m-tit{font-size:1.65rem}.manchete p{font-size:1rem}
 .meta{font-size:.84rem}.cat{font-size:.74rem}.credito{font-size:.76rem}
 .lista-n a{grid-template-columns:68px 1fr;gap:12px;padding:14px 0}
 .lista-n img{width:68px;height:68px}
 .lista-n .sem-img{grid-template-columns:1fr}.lista-n .sem{display:none}
 .lista-n .meta{display:inline}
 .lista-n div>.cat+.meta{white-space:normal}
 .lista-n h3,.nota .lista-n h2{font-size:1.06rem;margin:5px 0 6px}
 .lista-n p{display:block;-webkit-line-clamp:unset;overflow:visible;font-size:.92rem}
 .lista-n .resumo{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;margin-top:5px;color:#3a414c}
 .hot span,.financ .f,.capas span{font-size:.82rem}
 .agenda li{grid-template-columns:92px 1fr}
 .nota .fontes li{margin:10px 0}
 footer .in{gap:4px 20px;align-items:center}footer a{display:inline-block;padding:6px 0}
}
@media (prefers-reduced-motion:reduce){*{scroll-behavior:auto}}
/* compartilhar */
.comunidade .cp{background:none;border:1px solid #2e4d7a;color:var(--ink)}.comunidade .cp:hover{border-color:var(--gold);background:none}
/* ===== Paleta de seções (referência: The Verge) =====
   Filete colorido em cima de cada seção, título em caixa normal, etiquetas preenchidas, linha de data em
   monoespaçada e faixas de cor alternando com os blocos claros de leitura. As faixas trocam as variáveis
   --paper-*: o conteúdo de dentro (que usa essas variáveis) muda de cor sem regra nova. */
:root{--mono:ui-monospace,"SF Mono",SFMono-Regular,Menlo,Consolas,monospace;
--faixa-escura:#0f2244;--faixa-verde:#0b2a1b;--faixa-roxa:#21173a;--faixa-ouro:#1d1606}
.bloco>h2,.bloco>.h-sec{border-bottom:0;border-top:3px solid var(--acc,var(--gold));padding:10px 0 0;margin-bottom:14px;
 font-size:1.12rem;letter-spacing:-.01em;text-transform:none;color:var(--paper-ink)}
.bloco>h2 a{font-family:var(--mono);font-size:.72rem;text-transform:uppercase;letter-spacing:.06em}
.meta,.credito,.card-n .meta,.edicao{font-family:var(--mono);font-size:.7rem;text-transform:uppercase;letter-spacing:.05em}
.edicao{color:var(--gold)}
/* manchete: etiqueta preenchida, como o "FIRST LOOK" */
.manchete .kick{justify-self:start;background:var(--gold);color:#0a1a33;border-radius:3px;padding:3px 8px;font-size:.7rem}
.manchete{border-top:4px solid var(--gold)}
/* faixas escuras e coloridas */
.bloco.alta,.bloco.agenda,.bloco.financ,.bloco.brasil,.bloco.resenhas{--paper-ink:#eceff3;--paper-muted:#a7afbb;--paper-line:#24426e;color:var(--paper-ink)}
.bloco.alta{background:var(--faixa-escura);border:1px solid #1e3a64}
.alta .hot a::before{font-size:1.6rem;color:var(--gold);font-weight:800}
.alta .hot a{grid-template-columns:28px 44px 1fr}
.bloco.agenda{background:var(--faixa-ouro);border:1px solid #3a2e10;--acc:#f0c24b}
.agenda .q{color:#f0c24b}
.bloco.brasil{background:var(--faixa-verde);border:1px solid #17432c;--acc:#3ddc84}
.brasil h2 a,.alta h2 a,.agenda h2 a,.financ h2 a,.resenhas h2 a{color:var(--acc,var(--gold))}
.brasil .capas img{background:#1a3d2b}
.brasil .capas .todos a{background:#123824;color:#7ff0b0}
.bloco.financ{background:var(--faixa-roxa);border:1px solid #3b2a66;--acc:#b493ff}
.financ .onde{color:#c9b3ff}.financ .s{color:#d4cce8}
.bloco.resenhas{background:var(--faixa-escura);border:1px solid #1e3a64}
.res img{outline:1px solid #1e3a64}
.ultimas{--acc:var(--gold)}
/* arquivo /noticias/: quadradinhos escuros com a cor da categoria no topo */
.card-n{--cat:var(--gold)}
.card-n:has(.cat.brasil){--cat:#3ddc84}.card-n:has(.cat.financ){--cat:#b493ff}.card-n:has(.cat.mercado){--cat:#6ea8ff}.card-n:has(.cat.premios){--cat:#f0c24b}
.card-n a{background:var(--faixa-escura);color:var(--ink);border:1px solid #1e3a64;border-top:4px solid var(--cat)}
.card-n a:hover{border-color:var(--cat)}
.card-n .resumo{color:#b9c0cb}.card-n .meta{color:#8d96a3}
.card-n .ci{background:#13284a}
.arq-topo h1{border-top:3px solid var(--gold);padding-top:12px}
/* página da notícia: blocos de análise em faixas, texto corrido nos blocos claros */
.nota .importa{background:var(--faixa-ouro);border:1px solid #3a2e10;border-left:4px solid var(--gold);--paper-ink:#eceff3;--paper-muted:#bfae84}
.nota .importa p{color:#f1ead6}
.nota .brasil-n{background:var(--faixa-verde);border:1px solid #17432c;border-left:4px solid #3ddc84;--paper-ink:#eceff3;--paper-muted:#8fd3ae;--acc:#3ddc84}
.nota .brasil-n p{color:#dcefe4}
.nota .crivo{background:var(--faixa-escura);border:1px solid #1e3a64;--paper-ink:#eceff3;--paper-muted:#a7afbb}
.nota .crivo p,.nota .crivo li{color:#c9cfd8}.nota .crivo ul{margin-top:8px;display:grid;gap:4px;padding-left:18px;font-size:.85rem}
"""


def og_dim(imagem):
    """og:image:width/height lidos do arquivo, quando a imagem é do próprio site."""
    arq = ROOT / imagem.removeprefix(SITE + "/").split("?")[0]
    if not imagem.startswith(SITE + "/") or not arq.is_file():
        return ""
    try:
        im = Image.open(arq)
    except Exception:
        return ""
    with im:
        return f'\n<meta property="og:image:width" content="{im.width}">\n<meta property="og:image:height" content="{im.height}">'


JS_CATEGORIAS = """(()=>{const g=document.querySelector('.cats');if(!g)return;
const lis=[...document.querySelectorAll('.arq [data-cat]')],nota=document.querySelector('.cat-nota');
const aplica=v=>{lis.forEach(li=>{li.hidden=!!v&&li.dataset.cat!==v});
g.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.c===v)));
const u=new URL(location.href);if(v)u.searchParams.set('categoria',v);else u.searchParams.delete('categoria');history.replaceState(null,'',u);
if(nota){const b=g.querySelector('[data-c="'+v+'"]'),a=nota.querySelector('a');nota.hidden=!v;if(v){a.href=b.dataset.pag;a.textContent='Ver todas as notícias de '+b.dataset.t}}};
g.addEventListener('click',ev=>{const b=ev.target.closest('button');if(b)aplica(b.dataset.c)});
const c=new URLSearchParams(location.search).get('categoria');g.hidden=false;aplica(c&&g.querySelector('[data-c="'+c+'"]')?c:'')})()"""


def capa_secao(secao):
    """Prévia 1200×630 da seção (tools/capa_secoes.js), com ?v= para o WhatsApp buscar a nova quando mudar."""
    return f"{SITE}/{secao}/capa.jpg{versao(ROOT / secao / 'capa.jpg')}"


def pagina(titulo, descricao, url, imagem, pre, corpo, tipo="website", head_extra="", jsonld=""):
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(titulo)}</title>
<meta name="description" content="{e(descricao)}">
{f'<link rel="canonical" href="{url}">' + chr(10) + '<meta name="robots" content="max-image-preview:large">' if url else '<meta name="robots" content="noindex">'}
<meta property="og:site_name" content="O Paladino">
<meta property="og:locale" content="pt_BR">
<meta property="og:title" content="{e(titulo)}">
<meta property="og:description" content="{e(descricao)}">
<meta property="og:type" content="{tipo}">
<meta property="og:url" content="{url or SITE + '/'}">
<meta property="og:image" content="{imagem}">{og_dim(imagem)}
<meta name="twitter:card" content="summary_large_image">{head_extra}
<meta name="theme-color" content="#0a1a33">
<link rel="icon" href="{pre}favicon.svg" type="image/svg+xml">
<link rel="preload" href="{pre}fontes/public-sans.woff2" as="font" type="font/woff2" crossorigin>
<style>{CSS % {"pre": pre}}{CSS_TRILHA}{CSS_BUSCA}</style>
{jsonld}
</head>
<body>
{corpo}
{seo.ANALYTICS}
</body>
</html>
"""


# entra na política editorial quando o serviço de curtidas e comentários estiver instalado
SECAO_COMENTARIOS = """ <section class="bloco" id="comentarios"><h2>Comentários e curtidas</h2><div class="corpo">
  <p>Todo comentário passa por moderação antes de aparecer. Uma ferramenta de inteligência artificial faz a primeira leitura com regras públicas: publica os comentários respeitosos sobre jogos, descarta propaganda, golpe, ofensa, discurso de ódio e dados pessoais de outras pessoas, e manda para o responsável editorial tudo o que não for claro. Discordar do site, de uma resenha ou de uma editora, com educação, é bem-vindo.</p>
  <p>Para comentar pedimos só um nome. O e-mail é opcional, nunca é publicado e só serve para respondermos ou excluirmos o comentário a pedido. Não guardamos o endereço IP: usamos apenas uma assinatura dele, que muda todo dia, para limitar abusos. A curtida é contada uma vez por aparelho, com um identificador aleatório guardado no seu navegador, sem cookies de rastreamento. Quer apagar um comentário seu? Peça pelo Instagram.</p>
 </div></section>"""


def build_politica():
    """Página de política editorial: quem responde pelo site e como notícias e resenhas são feitas."""
    pre = "../"
    url = f"{SITE}/politica-editorial/"
    corpo = f"""{cabecalho(pre, "")}
<main id="conteudo" class="in"><div class="nota">
 <article class="bloco">
  <h1>Política editorial</h1>
  <p class="lide">Como O Paladino escolhe, escreve, confere e corrige o que publica.</p>
 </article>
 <section class="bloco"><h2>Quem responde pelo site</h2><div class="corpo">
  <p><b>Anderson Pelicioni de Castro</b>, advogado, é o responsável editorial de O Paladino. Ele responde pelo que é publicado e confere o site todos os dias.</p>
 </div></section>
 <section class="bloco"><h2>Como o conteúdo é produzido</h2><div class="corpo">
  <p>Notícias e estudos bíblicos são redigidos com apoio de ferramentas de inteligência artificial, sempre a partir das fontes citadas em cada página. Nenhum texto vai ao ar sem fontes, e todo número, nome ou data precisa estar numa delas. O texto só é publicado depois de passar pela checagem automática do padrão editorial (fontes, foto com licença, separação entre fato e opinião). O responsável editorial confere o site todos os dias e corrige o que for preciso.</p>
  <p>Todos os dias, à noite, o que foi publicado é conferido de novo contra as fontes. Dado que não se confirma sai do texto ou passa a constar como "não confirmado nas fontes consultadas".</p>
 </div></section>
 <section class="bloco"><h2>Como escolhemos as notícias</h2><div class="corpo">
  <p>Toda notícia passa por um crivo editorial. Fica de fora o que não tem fonte primária (boato, vazamento ou "fontes dizem"), conteúdo pago ou release sem fato novo, notícia atrasada e assunto sem relação com fé, família, igreja e sociedade.</p>
  <p>O que passa recebe pontos por relevância para o leitor cristão no Brasil, como fonte primária oficial, efeito concreto na vida das famílias e das igrejas ou confirmação por duas fontes independentes. A de maior pontuação vira a manchete, e cada notícia mostra no fim por que entrou.</p>
 </div></section>
 <section class="bloco" id="destaques"><h2>Destaques da página inicial</h2><div class="corpo">
  <p>O bloco Destaques reúne os temas mais citados nas nossas notícias dos últimos 7 dias, cada um com o link de uma notícia sobre ele. Não é um ranking de acessos nem de vendas: o site não usa dados de visitas para montar essa lista.</p>
 </div></section>
 <section class="bloco"><h2>Fato e opinião</h2><div class="corpo">
  <p>Os fatos vêm com fonte e data de consulta. A nossa opinião aparece separada, nas seções "Por que importa" e "Nossa opinião". A opinião de outros veículos aparece sempre com o nome de quem a deu.</p>
  <p>Os estudos bíblicos indicam sempre a passagem e a tradução da Bíblia citada. Interpretações aparecem com o nome de quem as defende, e divergências entre tradições cristãs aparecem como divergências.</p>
 </div></section>
 <section class="bloco"><h2>Imagens</h2><div class="corpo">
  <p>Usamos fotos oficiais de órgãos públicos e de divulgação, imagens de licença livre ou fotos nossas, sempre com crédito. Não usamos imagens geradas por inteligência artificial nas matérias.</p>
 </div></section>
{''' <section class="bloco"><h2>Medição de visitas</h2><div class="corpo">
  <p>Contamos as visitas com o Cloudflare Web Analytics, que não usa cookies e não identifica quem visita o site. Os números servem só para saber quais páginas são lidas e melhorar o conteúdo.</p>
 </div></section>''' if seo.ANALYTICS else ""}
{SECAO_COMENTARIOS if _config_interacoes().get("api") else ""}
 <section class="bloco"><h2>Correções</h2><div class="corpo">
  <p>Encontrou um erro? {f'Mande uma mensagem no <a href="{INSTAGRAM}" target="_blank" rel="noopener">Instagram</a>' if INSTAGRAM else (f'Escreva para <a href="mailto:{EMAIL}">{EMAIL}</a>' if EMAIL else 'Avise o responsável editorial')}, com o link da página e a fonte da informação correta. Erros confirmados são corrigidos na própria página.</p>
 </div></section>
</div></main>
{rodape(pre)}"""
    ld = seo.script({"@type": "WebPage", "@id": url, "url": url, "name": "Política editorial", "inLanguage": "pt-BR", "publisher": {"@id": seo.ORG_ID}},
                    seo.trilha(("Início", f"{SITE}/"), ("Política editorial", url)))
    out = ROOT / "politica-editorial" / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(pagina("Política editorial | O Paladino", "Quem responde por O Paladino e como notícias e resenhas são escolhidas, escritas, conferidas e corrigidas.",
                          url, capa_secao("noticias"), pre, corpo, jsonld=ld), encoding="utf-8")


def img_nota(n, pre):
    return f"{pre}noticias/{n['imagem']['arquivo']}" if n.get("imagem") else None


_EDITORAS_LANC = None
# como o calendário grafa algumas editoras -> nome atual da editora.
# A Galápagos hoje opera como Asmodee: galapagosjogos.com.br redireciona para asmodee.com.br (conferido em 29/10/2026).
NOME_EDITORA = {"Asmodee (Galápagos)": "Asmodee", "Galápagos": "Asmodee", "Galápagos Jogos": "Asmodee"}


def editora_nota(n):
    """Quem publica o jogo da notícia, para a linha de data (no lugar do site de onde veio a informação).

    Ordem: o campo "editora" da nota (tirado do próprio texto); senão as editoras do calendário de lançamentos
    para os ids_ludopedia da nota (duas aparecem juntas, três ou mais viram "Várias editoras"); senão nada
    (notícia de evento ou prêmio sem editora). As fontes continuam listadas dentro de cada notícia."""
    global _EDITORAS_LANC
    if n.get("editora"):
        return NOME_EDITORA.get(n["editora"], n["editora"])
    if _EDITORAS_LANC is None:
        _EDITORAS_LANC = {}
        for arq in (ROOT / "conteudo" / "lancamentos").glob("*.json"):
            d = json.loads(arq.read_text(encoding="utf-8"))
            for j in d["previstos"] + d["lancados"]:
                if (j.get("editora") or {}).get("nome"):
                    nome = j["editora"]["nome"].strip()
                    _EDITORAS_LANC[j["id_jogo"]] = NOME_EDITORA.get(nome, nome)
    eds = list(dict.fromkeys(_EDITORAS_LANC[i] for i in n.get("ids_ludopedia", []) if i in _EDITORAS_LANC))
    return "" if not eds else eds[0] if len(eds) == 1 else " e ".join(eds) if len(eds) == 2 else "Várias editoras"


def linha_data(n, data):
    ed = editora_nota(n)
    return f"{data} · {e(ed)}" if ed else data


def bloco_manchete(m, pre, titulo="h1"):
    """A notícia principal, com foto grande, lide e a nossa opinião: no topo da home (h1) e do arquivo /noticias/ (h2)."""
    try:
        with Image.open(ROOT / "noticias" / m["imagem"]["arquivo"]) as im:
            lw, lh = im.size
    except Exception:  # imagem com problema não segura a manchete
        lw, lh = 1200, 675
    return f"""<article class="bloco manchete" data-cat="{CATEGORIAS.get(m['categoria'], 'outras')}"><a href="{pre}noticias/{m['slug']}/">
  <figure><img src="{img_nota(m, pre)}" srcset="{srcset(ROOT / "noticias" / m["imagem"]["arquivo"], pre)}" sizes="(min-width: 640px) 340px, 100vw" width="{lw}" height="{lh}" alt="{e(m['titulo'])}" fetchpriority="high"></figure>
  <div class="txt"><span class="kick">Manchete · {e(m['categoria'])}</span><{titulo} class="m-tit">{e(m['titulo'])}</{titulo}><p>{e(m['lide'])}</p>
  <p class="opina"><span class="selo {SELO_CLASSE[m['selo']]}">{e(m['selo'])}</span> {e(m['veredito'])}</p>
  <span class="meta">{linha_data(m, data_longa(m['data']))}</span><span class="credito">{e(m['imagem']['credito'])}</span></div>
 </a></article>"""


def cartao_nota(n, pre):
    """Quadradinho da grade do arquivo: imagem, categoria, título, selo de opinião e data, levando à notícia."""
    if n.get("imagem"):
        arq = ROOT / "noticias" / n["imagem"]["arquivo"]
        img = (f'<img src="{img_nota(n, pre)}" srcset="{srcset(arq, pre, (480,))}" sizes="(min-width: 1000px) 270px, (min-width: 600px) 31vw, 46vw" '
               f'alt="" loading="lazy" decoding="async">')
    else:
        img = f'<span class="sem {CAT_CLASSE.get(n["categoria"], "mercado")}" aria-hidden="true">{icone("dica")}</span>'
    return (f'<li class="card-n" data-cat="{CATEGORIAS.get(n["categoria"], "outras")}"><a href="{pre}noticias/{n["slug"]}/">'
            f'<span class="ci">{img}</span><span class="cb"><span class="cat {CAT_CLASSE.get(n["categoria"], "mercado")}">{e(n["categoria"])}</span>'
            f'<h2>{e(n["titulo"])}</h2><span class="selo {SELO_CLASSE[n["selo"]]}">{e(n["selo"])}</span>'
            f'<span class="resumo">{e(n["por_que_importa"])}</span>'
            f'<span class="meta">{linha_data(n, data_curta(n["data"]))}</span></span></a></li>')


def build_home():
    ns = notas()
    home = json.loads((ROOT / "conteudo" / "home.json").read_text(encoding="utf-8"))
    pre = ""
    # manchete: a mais recente aprovada; a proposta da rotina diária espera "manchete_aprovada": true
    m = max((n for n in ns if n.get("manchete") and n.get("manchete_aprovada", True)), key=lambda n: n["data"], default=None) or (ns[0] if ns else None)
    resto = [n for n in ns if n is not m]
    # sem notícia publicada ainda (tudo em revisão): no lugar da manchete, a apresentação do portal
    manchete = bloco_manchete(m, pre) if m else ('<article class="bloco manchete"><div class="txt"><span class="kick">O Paladino</span>'
                                                  '<h1 class="m-tit">Jornalismo com princípios</h1><p>As primeiras notícias entram aqui assim que forem publicadas.</p></div></article>')
    def item(n, pre):
        return f"""<li data-cat="{CATEGORIAS.get(n['categoria'], 'outras')}"><a href="noticias/{n['slug']}/"{'' if n.get("imagem") else ' class="sem-img"'}>{f'<img src="{miniatura(ROOT / "noticias" / n["imagem"]["arquivo"], pre)}" width="76" height="76" alt="" loading="lazy">' if n.get("imagem") else f'<span class="sem">{icone("dica")}</span>'}
   <div><span class="cat {CAT_CLASSE.get(n['categoria'], 'mercado')}">{e(n['categoria'])}</span> <span class="meta">{linha_data(n, data_curta(n['data']))}</span>
   <h3>{e(n['titulo'])}</h3><p><span class="selo {SELO_CLASSE[n['selo']]}">{e(n['selo'])}</span> <span class="resumo">{e(n['por_que_importa'])}</span></p></div></a></li>"""
    ultimas = resto[:8]
    # trava: nenhuma nota fora da lista pode ser mais nova que uma que está nela
    if len(resto) > 8 and any(datetime.fromisoformat(f["publicado_em"]) > datetime.fromisoformat(u["publicado_em"])
                              for f in resto[8:] for u in ultimas if f["data"] >= u["data"]):
        sys.exit("Últimas notícias fora de ordem: há nota mais nova fora da lista")
    itens = "".join(item(n, pre) for n in ultimas)
    # arquivo de notícias: 30 por página; a 1ª é /noticias/, as outras /noticias/pagina/<n>/
    POR_PAGINA = 30
    paginas = [ns[i:i + POR_PAGINA] for i in range(0, len(ns), POR_PAGINA)] or [[]]
    for velha in (ROOT / "noticias" / "pagina").glob("*/index.html"):
        if not velha.parent.name.isdigit() or int(velha.parent.name) > len(paginas):
            velha.unlink()
            velha.parent.rmdir()
    # Com mais de uma página, cada categoria ganha também uma página estática e indexável (/noticias/categoria/<nome>/),
    # porque o filtro no navegador só enxerga as notas da página aberta. Com uma página só, elas não existem.
    paginado = len(paginas) > 1
    por_cat = {c: [n for n in ns if n["categoria"] == c] for c in CATEGORIAS}
    pasta_cat = ROOT / "noticias" / "categoria"
    for velha in pasta_cat.glob("*/index.html"):
        if not paginado or velha.parent.name not in CATEGORIAS.values() or not por_cat[next(c for c, v in CATEGORIAS.items() if v == velha.parent.name)]:
            velha.unlink()
            velha.parent.rmdir()
    if paginado:
        for cat, lista in por_cat.items():
            if not lista:
                continue
            c_pre, url_c = "../../../", f"{SITE}/noticias/categoria/{CATEGORIAS[cat]}/"
            itens_c = "".join(cartao_nota(n, c_pre) for n in lista)
            corpo_c = f"""{cabecalho(c_pre, "Notícias", sub=True)}
<main id="conteudo" class="in arq">{trilha(("Início", c_pre), ("Notícias", f"{c_pre}noticias/"), (e(cat), ""))}
 <div class="arq-topo"><h1>{e(cat)}</h1><p>{len(lista)} notícia{"s" if len(lista) > 1 else ""} nesta categoria.</p></div>
 <ul class="grade-n">{itens_c}</ul>
</main>
{rodape(c_pre)}"""
            destino_c = pasta_cat / CATEGORIAS[cat] / "index.html"
            destino_c.parent.mkdir(parents=True, exist_ok=True)
            destino_c.write_text(pagina(f"{cat}: notícias | O Paladino", f"Notícias da editoria {cat}, com fonte, data e opinião.", url_c,
                                        capa_secao("noticias"), c_pre, corpo_c,
                                        jsonld=seo.script(seo.trilha(("Início", f"{SITE}/"), ("Notícias", f"{SITE}/noticias/"), (cat, url_c))))
                                 , encoding="utf-8")

    def chips_cat(lote, p_pre):
        """Chips de categoria do arquivo: filtram as notas da página no navegador (estado em ?categoria=)."""
        conta = {c: sum(1 for n in lote if n["categoria"] == c) for c in CATEGORIAS}
        bts = "".join(f'<button type="button" data-c="{v}" data-t="{e(c)}" data-pag="{p_pre}noticias/categoria/{v}/" aria-pressed="false">{e(c)}<small>{conta[c]}</small></button>'
                      for c, v in CATEGORIAS.items() if conta[c])
        nota = '<p class="cat-nota" hidden>Esta página mostra só parte do arquivo. <a href="#">Ver todas</a></p>' if paginado else ""
        return (f'<div class="cats" role="group" aria-label="Filtrar por categoria" hidden><button type="button" data-c="" aria-pressed="true">Todas<small>{len(lote)}</small></button>{bts}</div>{nota}')

    for num, lote in enumerate(paginas, 1):
        p_pre = "../" if num == 1 else "../../../"
        url = f"{SITE}/noticias/" if num == 1 else f"{SITE}/noticias/pagina/{num}/"
        # 1ª página: a manchete em destaque no topo e as demais em quadradinhos; páginas seguintes só a grade
        destaque = bloco_manchete(m, p_pre, "h2") if num == 1 and m else ""
        arquivo = "".join(cartao_nota(n, p_pre) for n in lote if not (num == 1 and n is m))
        ant = "" if num == 1 else f'<a href="{p_pre}noticias/{"" if num == 2 else f"pagina/{num - 1}/"}" rel="prev">← Mais recentes</a>'
        prox = f'<a href="{p_pre}noticias/pagina/{num + 1}/" rel="next">Mais antigas →</a>' if num < len(paginas) else ""
        nav = f'<nav class="paginas" aria-label="Páginas de notícias">{ant}<span>Página {num} de {len(paginas)}</span>{prox}</nav>' if len(paginas) > 1 else ""
        sufixo = "" if num == 1 else f" (página {num})"
        corpo_arq = f"""{cabecalho(p_pre, "Notícias", sub=num > 1)}
<main id="conteudo" class="in arq">
 <div class="arq-topo"><h1>Notícias{sufixo}</h1><p>Com fonte, data e a nossa opinião separada do fato. {len(ns)} notícias publicadas.</p></div>
 {chips_cat(lote, p_pre)}
 {destaque}
 <ul class="grade-n">{arquivo}</ul>
 {nav}
 <script>{JS_CATEGORIAS}</script>
</main>
{rodape(p_pre)}"""
        trilha_ld = [("Início", f"{SITE}/"), ("Notícias", f"{SITE}/noticias/")] + ([] if num == 1 else [(f"Página {num}", url)])
        destino = ROOT / "noticias" / ("index.html" if num == 1 else f"pagina/{num}/index.html")
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(pagina(f"Notícias{sufixo} | O Paladino", f"Notícias de O Paladino, com fonte, data e opinião{sufixo}.", url,
                                  capa_secao("noticias"), p_pre, corpo_arq, jsonld=seo.script(seo.trilha(*trilha_ld))), encoding="utf-8")
    # cada item dos Destaques tem de levar a uma nota que trate do jogo já no título
    for j in home["em_alta"]:
        slug = j["link"].strip("/").split("/")[-1]
        alvo_n = next((n for n in ns if n["slug"] == slug), None)
        base = norm(re.split(r" [–-] |:", j["nome"])[0])
        if not alvo_n or base not in norm(alvo_n["titulo"]):
            sys.exit(f"Destaques: '{j['nome']}' leva a {slug}, que não trata do jogo no título")
    alta = "".join(
        f'<li><a href="{j["link"]}"><img src="{miniatura(ROOT / "noticias" / "capas" / f'{j["id_ludopedia"]}.jpg', pre, 96)}" width="44" height="44" alt="" loading="lazy"><div><b>{e(j["nome"])}</b><span>{e(j["motivo"])}</span></div></a></li>'
        for j in home["em_alta"]
    )
    def alvo(item):
        # notícia nossa quando existe; senão o link de fora (ou âncora) do próprio item
        return (f'noticias/{item["noticia"]}/', "") if item.get("noticia") else (item.get("link", ""), ' target="_blank" rel="noopener"' if item.get("link", "").startswith("http") else "")
    agenda = ""
    for a in home["agenda"]:
        href, ext = alvo(a)
        tit = f'<a href="{e(href)}"{ext}>{e(a["titulo"])}</a>' if href else e(a["titulo"])
        agenda += f'<li><span class="q">{e(a["quando"])}{"<small>previsto</small>" if a["previsto"] else ""}</span><span><b>{tit}</b><br><span class="d">{e(a["detalhe"])}</span></span></li>'
    por_jogo = {i: n["slug"] for n in ns for i in n.get("ids_ludopedia", [])}
    mes = mes_chegando()
    rotulo, jogos = lancamentos(mes)
    capas = "".join(
        f'<li><a href="lancamentos/#j{j["id_jogo"]}"><img src="{miniatura(ROOT / "noticias" / "capas" / f'{j["id_jogo"]}.jpg', pre, 280)}" width="132" height="140" alt="" loading="lazy">'
        f'<span class="st {j["status"]["slug"]}">{e(j["status"]["label"])}</span><b>{e(j["nome"].strip())}</b><span>{e((j.get("editora") or {}).get("nome", ""))}</span></a></li>'
        for j in jogos
    ) + f'<li class="todos"><a href="lancamentos/#{mes}"><span class="mais">Ver os {len(jogos)} de {e(rotulo.split(" de ")[0].lower())} e todo o calendário</span></a></li>'
    financ = "".join(
        f'<li><span class="onde">{e(f["onde"])}</span><a href="{e(alvo(f)[0])}"{alvo(f)[1]}>{e(f["nome"])}</a>'
        f'<span class="s">{e(f["editora"])} · {e(f["situacao"])}</span><span class="f">Fonte: {e(f["fonte"])}</span></li>'
        for f in home["financiamentos"]
    )
    pauta = json.loads((ROOT / "pauta.json").read_text(encoding="utf-8"))
    slugs = [p["url"].rstrip("/").split("/")[-1] for p in reversed(pauta["publicadas"])][:4]
    res = ""
    import build_estudo
    for c in build_estudo.publicados()[:4]:
        res += f'<li><a href="estudos/{c["slug"]}/"><img src="estudos/{c["slug"]}/foto.jpg" width="800" height="800" alt="" loading="lazy"><b>{e(c["titulo"])}</b></a></li>'
    for s in slugs[:4 - res.count("<li>")]:
        c = json.loads((ROOT / "conteudo" / f"{s}.json").read_text(encoding="utf-8"))
        res += f'<li><a href="{s}/"><img src="{s}/capa.jpg{versao(ROOT / s / "capa.jpg")}" srcset="{srcset(ROOT / s / "capa.jpg", pre, (400,))}" sizes="(min-width: 640px) 160px, 45vw" width="800" height="800" alt="" loading="lazy"><b>{e(c["jogo"])}</b></a></li>'
    corpo = f"""{cabecalho(pre, "Início")}
<main id="conteudo" class="in">
 {f'<p class="edicao">Edição de {data_longa(max(n["data"] for n in ns))}</p>' if ns else ''}
 <div class="grade">
  {manchete}
  <section class="bloco ultimas"><h2>Últimas notícias <a href="noticias/">Ver todas ({len(ns)})</a></h2><ul class="lista-n">{itens}</ul></section>
  {f'''<aside class="lado">{f'<section class="bloco alta"><h2>Destaques <a href="politica-editorial/#destaques" aria-label="Critério dos destaques">Critério</a></h2><p class="crit-h">Os temas mais citados nas nossas notícias dos últimos 7 dias.</p><ol class="hot">{alta}</ol></section>' if alta else ''}
  {f'<section class="bloco agenda"><h2>Agenda</h2><ul>{agenda}</ul></section>' if agenda else ''}</aside>''' if alta or agenda else ''}
  {f'<section class="bloco brasil" id="chegando"><h2>Lançamentos gospel · {e(rotulo.lower())} <a href="lancamentos/#{mes}">Agenda completa</a></h2><ul class="capas">{capas}</ul></section>' if jogos else ''}
  {f'<section class="bloco financ"><h2>Missões e campanhas</h2><ul>{financ}</ul></section>' if financ else ''}
  {f'<section class="bloco resenhas"><h2>Últimos estudos bíblicos <a href="estudos/">Ver todos</a></h2><ul class="res">{res}</ul></section>' if res else ''}
  <section class="bloco comunidade"><p>Notícias com fonte e data e estudos bíblicos, todos os dias. Entre no grupo para receber as novidades.</p>
   <div class="acoes">{f'<a class="btn zap" href="{WHATSAPP}" target="_blank" rel="noopener">{icone("zap")}Entrar no grupo do WhatsApp</a>' if WHATSAPP else ''}{f'<a class="btn ig" href="{INSTAGRAM}" target="_blank" rel="noopener">{icone("insta")}Instagram</a>' if INSTAGRAM else ''}{botao_compartilhar("O Paladino: jornalismo com princípios. Notícias com fonte e estudos bíblicos.", f"{SITE}/", "Compartilhar o site")}</div></section>
 </div>
</main>
{rodape(pre)}"""
    titulo = "O Paladino: jornalismo com princípios"
    descr = f"{m['titulo'] if m else 'O Paladino'}. Notícias com fonte e data, estudos bíblicos e a agenda cristã, com uma perspectiva cristã sobre o Brasil e o mundo."
    # 404: servida pelo GitHub Pages em qualquer profundidade, por isso os caminhos são absolutos ("/")
    RAIZ = urlparse(SITE).path.rstrip("/") + "/"  # o site mora em /Arcvalion_gospel/ no GitHub Pages
    corpo_404 = f"""{cabecalho(RAIZ, "")}
<main id="conteudo" class="in"><div class="nota"><section class="bloco">
 <h1>Página não encontrada</h1>
 <p class="lide">O endereço pode ter mudado ou sido digitado errado. Veja o que há de novo:</p>
 <div class="jogos"><a href="{RAIZ}">Notícias de hoje</a><a href="{RAIZ}estudos/">Estudos bíblicos</a><a href="{RAIZ}consulta/">Versículo diário</a></div>
</section></div></main>
{rodape(RAIZ, "")}"""
    (ROOT / "404.html").write_text(pagina("Página não encontrada | O Paladino", "Página não encontrada.", "", capa_secao("noticias"), RAIZ, corpo_404), encoding="utf-8")
    build_politica()
    (ROOT / "index.html").write_text(pagina(titulo, descr, f"{SITE}/", (url_cartao(f"noticia-{m['slug']}") or f"{SITE}/{img_nota(m, '')}") if m else capa_secao("noticias"), pre, corpo, jsonld=seo.script(seo.site())), encoding="utf-8")
    return ns


def relacionadas(n, limite=3):
    """Notas para o "Leia também": primeiro as que citam o mesmo jogo, depois as da mesma categoria; mais recentes antes."""
    jogos = {j.get("resenha") or j["nome"] for j in n.get("jogos", [])}
    cands = []
    for p in (ROOT / "conteudo" / "noticias").glob("*.json"):
        o = json.loads(p.read_text(encoding="utf-8"))
        if o["slug"] == n["slug"] or o.get("status", "publicado") != "publicado":  # nota em revisão não aparece
            continue
        comum = len(jogos & {j.get("resenha") or j["nome"] for j in o.get("jogos", [])})
        if comum or o["categoria"] == n["categoria"]:
            cands.append((comum, o["data"], o.get("publicado_em", ""), o))
    cands.sort(key=lambda x: x[:3], reverse=True)
    return [o for *_, o in cands[:limite]]


def por_que_entrou(n):
    """Seção "Por que esta notícia entrou": mostra o crivo de até 20 pontos, com a lista de critérios (pedido do
    responsável editorial, 30/10/2026). A escolha interna usa o motor de 0 a 100, que não vai para a página; as notas
    do motor guardam a versão pública em crivo.publico, e as de antes do motor já têm o crivo antigo na raiz."""
    c = n["crivo"]
    pub = c.get("publico") if c.get("escala") == 100 else c
    pub = pub or {"pontos": 0, "criterios": []}
    return (f'<section class="bloco crivo"><h2>Por que esta notícia entrou</h2><p><b>{pub["pontos"]} pontos no crivo editorial</b>'
            f'{":" if pub.get("criterios") else ""} {e("; ".join(pub.get("criterios") or []) or "(nenhum critério de pontuação)")}.</p></section>')


def versiculo(n):
    """Versículo opcional da Nossa opinião: sai embaixo do posicionamento, nunca no meio dele (pedido de 30/10/2026)."""
    v = n.get("versiculo")
    if not v:
        return ""
    return f'<p class="versiculo">“{e(v["texto"])}” <cite>{e(v["referencia"])}, {e(v["traducao"])}</cite></p>'


def build_nota(n, previa=False):
    """previa=True: nota em revisão, gerada em previa/noticias/<slug>/ fora do índice, com aviso no topo."""
    pre = "../../../" if previa else "../../"
    url = f"{SITE}/noticias/{n['slug']}/"
    texto_cp = f"{n['titulo']} (via O Paladino)"
    # prévia: só a foto original, sem gerar variantes em img/ (a pasta é pública e não pode antecipar nota em revisão)
    resp = "" if previa else f' srcset="{srcset(ROOT / "noticias" / n["imagem"]["arquivo"], pre)}" sizes="(min-width: 760px) 720px, 100vw"' if n.get("imagem") else ""
    fig = (f'<figure><img src="{pre}noticias/{n["imagem"]["arquivo"]}"{resp} alt="{e(n["titulo"])}"><figcaption class="credito">{e(n["imagem"]["credito"])}</figcaption></figure>'
           if n.get("imagem") else "")
    jogos = "".join(f'<a href="{pre}{j["resenha"]}/">Resenha: {e(j["nome"])}</a>' for j in n.get("jogos", []))
    fontes = "".join(f'<li><a href="{e(f["url"])}" target="_blank" rel="noopener">{e(f["nome"])}</a> <span>consulta em {e(f["data"])}</span></li>' for f in n["fontes"])
    numeros = "".join(f'<li><b>{e(v)}</b><span>{e(r)}</span><small>{e(f)}</small></li>' for v, r, f in n["numeros"])
    critica = "".join(
        (f'<li class="cit"><q>{e(c["texto"])}</q><cite>{e(c["fonte"])}{" (tradução livre)" if c.get("traducao") else ""}</cite></li>' if c.get("citacao")
         else f'<li><p>{e(c["texto"])}</p></li>') for c in n["critica"])
    sim = "".join(f"<li>{e(x)}</li>" for x in n["para_quem"])
    nao = "".join(f"<li>{e(x)}</li>" for x in n.get("nao_e_para", []))
    sc = SELO_CLASSE[n["selo"]]
    leia = "".join(f'<li><a href="{pre}noticias/{o["slug"]}/">{e(o["titulo"])}</a></li>' for o in relacionadas(n))
    aviso = ('<div style="background:#ffe3e3;color:#7a1f1f;padding:8px 16px;text-align:center;font-size:.9rem"><b>Prévia em revisão.</b> '
             'Esta notícia ainda não foi publicada: espera a checagem do padrão editorial. Não compartilhe.</div>') if previa else ""
    corpo = f"""{aviso}{cabecalho(pre, "Notícias", sub=True)}
<main id="conteudo" class="in"><div class="nota">
 {trilha(("Início", pre), ("Notícias", f"{pre}noticias/"), (e(n["titulo"]), ""))}
 <article class="bloco">
  <span class="cat {CAT_CLASSE.get(n['categoria'], 'mercado')}">{e(n['categoria'])}</span> <span class="selo {sc}">{e(n['selo'])}</span>
  <h1>{e(n['titulo'])}</h1>
  <p class="meta"><time datetime="{n['publicado_em']}">{data_longa(n['data'])}</time> · Redação O Paladino</p>
 </article>
 <div class="bloco abre">{fig}<p class="lide">{e(n['lide'])}</p></div>
 <section class="bloco importa"><h2>Por que importa</h2><p>{e(n['por_que_importa'])}</p><p class="assina">Análise O Paladino</p></section>
 <section class="bloco"><h2>Em números</h2><ul class="nums">{numeros}</ul></section>
 <section class="bloco"><h2>Contexto</h2><div class="corpo">{"".join(f"<p>{e(p)}</p>" for p in n['corpo'])}</div></section>
 <section class="bloco brasil-n"><h2>No Brasil</h2><p>{e(n['no_brasil'])}</p></section>
 {f'<section class="bloco"><h2>O que dizem</h2><ul class="crit">{critica}</ul></section>' if critica else ''}
 <section class="bloco quem"><div><h2>O que muda para você</h2><ul class="ok">{sim}</ul></div>{f'<div><h2>Pontos de atenção</h2><ul class="no">{nao}</ul></div>' if nao else ""}</section>
 <section class="bloco veredito {sc}"><h2>Nossa opinião</h2><span class="selo {sc}">{e(n['selo'])}</span><p>{e(n['veredito'])}</p>{versiculo(n)}</section>
 {convite_compartilhar(texto_cp, url, "Conhece alguém que vai gostar?", "Mande esta notícia para a turma.")}
 {interacoes(pre, f"/noticias/{n['slug']}/")}
 {f'<section class="bloco"><h2>Jogos citados</h2><div class="jogos">{jogos}</div></section>' if jogos else ""}
 {f'<section class="bloco leia"><h2>Leia também</h2><ul>{leia}</ul></section>' if leia else ""}
 <section class="bloco fontes"><h2>Fontes</h2><ul>{fontes}</ul></section>
 {por_que_entrou(n)}
</div></main>
{rodape(pre, barra_leitura(texto_cp, url))}"""
    out = ROOT / ("previa" if previa else "") / "noticias" / n["slug"] / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    img = f"{SITE}/noticias/{n['imagem']['arquivo']}" if n.get("imagem") else capa_secao("noticias")
    url = f"{SITE}/noticias/{n['slug']}/"
    modificado = lastmod_registrado(url, {k: v for k, v in n.items() if k != "publicado_em"})
    # imagem para o Google: versão 16:9 com 1200 px (Discover) antes da capa original
    # é preferência, não regra: qualquer problema com a imagem só deixa de fora a versão larga
    imagens = [img]
    if n.get("imagem") and not previa:
        try:
            larga = capas_grandes.larga(ROOT / "noticias" / n["imagem"]["arquivo"])
            if larga != ROOT / "noticias" / n["imagem"]["arquivo"]:
                imagens.insert(0, f"{SITE}/{larga.relative_to(ROOT).as_posix()}")
        except Exception as ex:
            print(f"  aviso: sem versão larga para {n['slug']} ({ex.__class__.__name__}); a nota sai normalmente")
    ld = seo.script(seo.artigo("NewsArticle", url, n["titulo"], n["lide"], imagens, n["publicado_em"], modificado),
                    seo.trilha(("Início", f"{SITE}/"), ("Notícias", f"{SITE}/noticias/"), (n["titulo"], url)))
    # título da busca: titulo_seo (opcional, aprovado pela edição) ou o título; o sufixo da marca só cabe em título curto
    t_busca = n.get("titulo_seo") or n["titulo"]
    t_busca = t_busca if len(t_busca) > 42 else f"{t_busca} | O Paladino"
    # prévia do WhatsApp: o cartão largo de tools/og.py; o JSON-LD continua com a foto da nota
    out.write_text(pagina(t_busca, n["lide"], "" if previa else url, url_cartao(f"noticia-{n['slug']}") or img, pre, corpo, "article",
                          f'\n<meta property="article:published_time" content="{n["publicado_em"]}">', ld), encoding="utf-8")


if __name__ == "__main__":
    # capa da Ludopedia em versão média vira a versão cheia (melhor na página e no Google)
    try:
        print("ok capas trocadas pela versão cheia:", capas_grandes.atualizar())
    except Exception as ex:  # sem rede: segue com as capas atuais
        print("⚠️ capas não atualizadas:", ex.__class__.__name__)
    import og
    print("ok cartões de prévia: %d refeitos de %d" % og.gerar())
    for n in build_home():
        build_nota(n)
    for n in PREVIA:
        build_nota(n, previa=True)
    print("ok index.html e", len(notas()), "notícias")
    # guias "Melhores jogos para…" antes das resenhas: o balão do perfil só liga para guia que existe
    import build_llms
    print("ok", build_llms.build())
    # resenhas mostram "Notícias sobre este jogo": regera as publicadas para incluir notas novas
    import build_review
    for pub in json.loads((ROOT / "pauta.json").read_text(encoding="utf-8"))["publicadas"]:
        slug = pub["url"].rstrip("/").split("/")[-1]
        (ROOT / slug / "index.html").write_text(build_review.build(json.loads((ROOT / "conteudo" / f"{slug}.json").read_text(encoding="utf-8"))), encoding="utf-8")
    import build_lista
    (ROOT / "estudos").mkdir(exist_ok=True)
    (ROOT / "estudos" / "index.html").write_text(build_lista.build(), encoding="utf-8")
    print("ok estudos/index.html")
    import build_paginas
    print("ok páginas institucionais:", ", ".join(f.parent.name for f in build_paginas.todas()))
    import build_estudo
    print("ok páginas de estudo:", len(build_estudo.todos()))
    if build_estudo.publicados() or not json.loads((ROOT / "pauta.json").read_text(encoding="utf-8"))["publicadas"]:
        (ROOT / "estudos" / "index.html").write_text(build_estudo.pagina_lista(), encoding="utf-8")
        print("ok estudos/index.html com", len(build_estudo.publicados()), "estudos")
    if (ROOT / "consulta" / "index.html").exists():
        import build_consulta
        print("ok consulta/index.html:", build_consulta.build())
    import build_calendario
    print("ok lancamentos/index.html: %d lançamentos, %d sem capa" % build_calendario.build())
    import busca
    print("ok busca.json:", busca.build(), "registros")
    import build_sitemap
    print("ok sitemap.xml (%d URLs), sitemap-noticias.xml (%d), robots.txt" % build_sitemap.atualizar()[:2])
