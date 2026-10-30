"""Moldura comum a todas as páginas: cabeçalho, menu de seções e rodapé, num lugar só.

Usado por build_home.py (home, notícias, política, 404), build_calendario.py, build_review.py, build_lista.py
e build_consulta.py (que reescreve a moldura dentro de consulta/index.html). O CSS de cada página continua no
próprio gerador; aqui fica só a marcação, para que links, rótulos e aria-current sejam iguais no site inteiro.
"""
INSTAGRAM = ""  # Instagram do portal: preencher
WHATSAPP = ""  # grupo do WhatsApp do portal: preencher
# e-mail da redação (config/portal.json): rodapé e pedidos de correção; vazio, o link não aparece
EMAIL = __import__("json").loads((__import__("pathlib").Path(__file__).resolve().parent.parent / "config" / "portal.json").read_text(encoding="utf-8")).get("email_contato", "")

# Editor responsável (primeiro revisor de config/equipe.json) e o Instagram dele, se estiver em "redes": aparece no
# rodapé, no "Fale com o editor" do fim das notícias e dos estudos e em Quem somos. É o perfil pessoal do editor,
# não o do portal (esse é INSTAGRAM, acima).
EDITOR = next((p for p in __import__("json").loads((__import__("pathlib").Path(__file__).resolve().parent.parent / "config" / "equipe.json")
                                                    .read_text(encoding="utf-8"))["pessoas"] if p.get("revisor")), {})
EDITOR_IG = next((r for r in EDITOR.get("redes", []) if "instagram.com/" in r), "")
EDITOR_ARROBA = "@" + EDITOR_IG.rstrip("/").rsplit("/", 1)[-1] if EDITOR_IG else ""

ICONES = {
    "jogadores": '<path d="M8 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7Zm8 1a3 3 0 1 0 0-6M2 20c0-3.3 2.7-6 6-6s6 2.7 6 6M15.5 14.2c3 .4 5.5 2.8 5.5 5.8"/>',
    "duracao": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>',
    "idade": '<path d="M12 21a9 9 0 1 1 0-18 9 9 0 0 1 0 18Z"/><path d="M9 10h.01M15 10h.01M8.5 14.5c1.9 2 5.1 2 7 0"/>',
    "peso": '<path d="M6 9h12l2 11H4L6 9Z"/><path d="M9 9a3 3 0 1 1 6 0"/>',
    "ok": '<path d="M4.5 12.5l4.5 4.5L19.5 6.5"/>',
    "insta": '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.3" cy="6.7" r=".6" fill="currentColor"/>',
    "zap": '<path d="M4 20l1.3-4A8 8 0 1 1 8.4 19l-4.4 1Z"/><path d="M9.2 8.6c.3-.5.8-.5 1-.1l.7 1.5c.1.3 0 .6-.2.8l-.4.4c.5 1.1 1.4 2 2.5 2.5l.4-.4c.2-.2.5-.3.8-.2l1.5.7c.4.2.4.7-.1 1-.7.5-1.6.6-2.4.3a7 7 0 0 1-4.2-4.2c-.3-.8-.2-1.7.4-2.3Z"/>',
    "nao": '<path d="M6 6l12 12M18 6L6 18"/>',
    "salvar": '<rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="9" cy="9" r="1.8"/><path d="M21 15.5l-5-5L5 21"/>',
    "copiar": '<rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V6a2 2 0 0 1 2-2h8"/>',
    "dica": '<path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0 0 12 3Z"/>',
    "preco": '<path d="M3 12V4h8l10 10-8 8L3 12Z"/><circle cx="7.5" cy="8.5" r="1.5"/>',
    "voltar": '<path d="M15 18l-6-6 6-6"/>',
    "topo": '<path d="M12 19V5M5 12l7-7 7 7"/>',
    "casa": '<path d="M3 11.5 12 4l9 7.5"/><path d="M5.5 9.5V20h13V9.5"/><path d="M10 20v-5.5h4V20"/>',
    "coracao": '<path d="M12 20s-7.5-4.6-9.3-9.2C1.4 7.4 3.6 4 7 4c2 0 3.6 1.1 5 3 1.4-1.9 3-3 5-3 3.4 0 5.6 3.4 4.3 6.8C19.5 15.4 12 20 12 20Z"/>',
    "busca": '<circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/>',
    "balao": '<path d="M4 5h16v11H9l-5 4V5Z"/>',
    "compartilhar": '<circle cx="18" cy="5" r="2.5"/><circle cx="6" cy="12" r="2.5"/><circle cx="18" cy="19" r="2.5"/><path d="M8.2 10.8l7.6-4.4M8.2 13.2l7.6 4.4"/>',
}

# (caminho a partir da raiz, rótulo) das seções do menu
SECOES = [("noticias/", "Notícias"), ("estudos/", "Estudos bíblicos"), ("discipulado/", "Discipulado"), ("consulta/", "Versículo diário")]


def icone(nome, cls="ic"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{ICONES[nome]}</svg>'


# Disparador da busca: mostra a lupa e, no clique, em "/" ou em Ctrl+K, baixa busca.js (e o índice) pela primeira vez.
# É o único JavaScript de busca na carga da página.
DISPARADOR = ("(()=>{const b=document.querySelector('.busca-btn');let c;b.hidden=false;"
              "const a=()=>{c=c||new Promise((r,j)=>{const s=document.createElement('script');s.src='PREbusca.js';s.onload=r;"
              "s.onerror=()=>{c=null;j()};document.head.append(s)});c.then(()=>abrirBusca('PRE'),()=>{})};"
              "b.addEventListener('click',a);addEventListener('keydown',e=>{const t=e.target,ed=t.isContentEditable||/^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName);"
              "if((e.key==='/'&&!ed&&!e.ctrlKey&&!e.metaKey)||((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k')){e.preventDefault();a()}})})()")

# Compartilhar: um botão só. No celular abre o menu do próprio aparelho (WhatsApp, Instagram, Telegram...);
# no computador abre uma janelinha com WhatsApp e Copiar link.
CSS_COMPARTILHAR = (".cpw{position:relative;display:inline-block}"
                    ".cp{display:inline-flex;align-items:center;justify-content:center;gap:8px;box-sizing:border-box;line-height:1.2;min-height:44px;margin:0;padding:10px 20px;"
                    "border-radius:999px;border:0;background:#157a43;color:#fff;font:inherit;font-size:.95rem;font-weight:800;text-decoration:none;cursor:pointer}"
                    ".cp:hover{background:#11683a;color:#fff}.cp .ic{width:19px;height:19px}.cp[hidden]{display:none}"
                    ".cpw.mini .cp{min-height:40px;padding:8px 14px;font-size:.88rem}"
                    ".cp-menu{position:absolute;z-index:30;top:calc(100% + 8px);left:0;min-width:200px;display:grid;gap:2px;padding:6px;border-radius:12px;"
                    "background:#fff;border:1px solid #dde1e7;box-shadow:0 10px 30px rgba(0,0,0,.25)}.cp-menu[hidden]{display:none}"
                    ".cp-menu.sobe{top:auto;bottom:calc(100% + 8px)}.cp-menu.dir{left:auto;right:0}"
                    ".cp-op{display:flex;align-items:center;gap:10px;min-height:44px;padding:8px 12px;border:0;border-radius:8px;background:none;"
                    "color:#14171c;font:inherit;font-size:.95rem;font-weight:700;text-align:left;text-decoration:none;cursor:pointer}"
                    ".cp-op:hover,.cp-op:focus-visible{background:#eef1f4;color:#14171c}.cp-op .ic{width:20px;height:20px}.cp-op.zap-op .ic{color:#157a43}"
                    ".cp-st{position:absolute;z-index:30;top:calc(100% + 8px);left:0;white-space:nowrap;margin:0;padding:6px 12px;border-radius:8px;"
                    "background:#0a1a33;color:#fff;font-size:.85rem;font-weight:700}.cp-st:empty{display:none}.barra-lt .cp-st{top:auto;bottom:calc(100% + 8px)}"
                    # convite no fim do conteúdo
                    ".convite{display:flex;align-items:center;justify-content:space-between;gap:12px 20px;flex-wrap:wrap}"
                    ".convite .cv-t{margin:0;font-weight:800;font-size:1.1rem}.convite .cv-s{margin:2px 0 0;font-size:.92rem;opacity:.8}"
                    # "Fale com o editor": botão no magenta do Instagram (contraste AA com o branco)
                    ".ig-cv{display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:10px 20px;border-radius:999px;background:#c13584;color:#fff;"
                    "font-size:.95rem;font-weight:800;text-decoration:none}.ig-cv:hover{background:#a42b70;color:#fff}.ig-cv .ic{width:20px;height:20px}"
                    "footer .rod-ig{gap:6px}footer .rod-ig .ic{width:18px;height:18px}"
                    # barra de leitura: aparece depois de rolar e some perto do fim
                    ".barra-lt{position:fixed;z-index:25;left:50%;bottom:calc(12px + env(safe-area-inset-bottom));display:flex;align-items:center;gap:4px;padding:5px;"
                    "border-radius:999px;background:#0a1a33;border:1px solid #2e4d7a;box-shadow:0 8px 24px rgba(0,0,0,.35);"
                    "transform:translate(-50%,0);transition:transform .25s ease,opacity .25s ease}"
                    ".barra-lt.fora{transform:translate(-50%,calc(100% + 24px));opacity:0;pointer-events:none}"
                    ".lt-b{display:inline-flex;align-items:center;gap:7px;min-height:44px;padding:8px 14px;border:0;border-radius:999px;background:none;"
                    "color:#e9ecf1;font:inherit;font-size:.9rem;font-weight:700;text-decoration:none;cursor:pointer}"
                    ".lt-b:hover{background:#262a31;color:#fff}.lt-b .ic{width:20px;height:20px}"
                    ".barra-lt .lt-b.curtir{background:none;border:0;color:#e9ecf1;padding:8px 14px}.barra-lt .lt-b.curtir[aria-pressed=true]{color:#ff6b81;background:none}"
                    "@media (max-width:479px){.lt-b span{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%);white-space:nowrap}}.lt-b.curtir[aria-pressed=true] .ic{fill:currentColor}"
                    # botão do grupo do WhatsApp: dourado da marca, só o ícone no celular
                    ".lt-grupo{display:inline-flex;align-items:center;justify-content:center;gap:6px;min-width:44px;min-height:44px;padding:0 12px;border-radius:999px;"
                    "background:#e3b23c;color:#14171c;font-size:.9rem;font-weight:800;text-decoration:none}.lt-grupo:hover{background:#f0c44f;color:#14171c}"
                    ".lt-grupo .ic{width:22px;height:22px}@media (max-width:479px){.lt-grupo{padding:0}.lt-grupo span{display:none}}"
                    ".barra-lt .cp{min-height:44px;padding:8px 16px;font-size:.9rem}"
                    "body.lt-on .voltar-topo,body.lt-on button.sobe{bottom:calc(76px + env(safe-area-inset-bottom))}"
                    "@media print{.barra-lt{display:none}}")

CSS_INTERACOES = (".interacoes{display:grid;gap:14px}.interacoes[hidden]{display:none}"
                  ".curtir-l{display:flex;align-items:center;gap:12px;flex-wrap:wrap}"
                  ".curtir{display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:8px 18px;border-radius:999px;border:2px solid #b3263e;"
                  "background:#fff;color:#b3263e;font:inherit;font-weight:800;cursor:pointer}.curtir .ic{width:22px;height:22px}"
                  ".curtir[aria-pressed=true]{background:#b3263e;color:#fff}.curtir[aria-pressed=true] .ic{fill:currentColor}"
                  ".curtir .n{font-variant-numeric:tabular-nums}.curtir-dica{font-size:.9rem;color:#5a6270}"
                  ".interacoes h2{margin:4px 0 0}.coms{list-style:none;margin:0;padding:0;display:grid;gap:10px}"
                  ".coms li{background:#fff;border:1px solid #dde1e7;border-radius:10px;padding:12px 14px}"
                  ".com-quem{margin:0;font-size:.92rem}.com-quem time{color:#5a6270;font-size:.8rem;margin-left:6px}"
                  ".com-txt{margin:4px 0 0;white-space:pre-wrap;color:#14171c}.coms-vazio{margin:0;color:#5a6270}"
                  ".com-form{display:grid;gap:10px;border-top:1px solid #dde1e7;padding-top:14px}"
                  ".com-form label{display:grid;gap:4px;font-weight:700;font-size:.9rem;color:#14171c}.com-form small{font-weight:600;color:#5a6270}"
                  ".com-form input,.com-form textarea{font:inherit;font-size:16px;font-weight:400;padding:10px 12px;border:1px solid #c8cdd5;border-radius:8px;background:#fff;color:#14171c}"
                  ".com-form textarea{resize:vertical;min-height:110px}"
                  ".com-form .isca{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}"
                  ".com-form button{justify-self:start;min-height:44px;padding:10px 20px;border-radius:999px;border:0;background:#0a1a33;color:#fff;font:inherit;font-weight:800;cursor:pointer}"
                  ".com-form button:disabled{opacity:.6}.com-aviso{margin:0;font-size:.82rem;color:#5a6270}.com-aviso a{color:#1f5fae}"
                  ".com-st{margin:0;font-weight:700;font-size:.92rem}.com-st:empty{display:none}.com-st.ok{color:#1b7a45}.com-st.erro{color:#a3223a}")

BANNER_LARGURAS = (640, 960, 1280, 1920)

# Cabeçalho com o banner: a arte ocupa a largura toda no celular e fica centrada, com as bordas esfumadas no fundo
# da própria arte, na tela grande. width/height no <img> reservam o espaço (sem salto de layout). A lupa (e o
# Instagram/WhatsApp, quando preenchidos) fica por cima do canto do banner, em vidro escuro, para não roubar altura.
CSS_FAIXA = (".bar.faixa{position:relative;background:#021628;border-bottom:1px solid var(--line,#1e3a64)}"
             ".bar.faixa .in{display:block;max-width:640px;margin:0 auto;padding:0}.bar.faixa.grande .in{max-width:960px}"
             ".bar.faixa .marca{display:block;border-radius:0}"
             ".bar.faixa .marca .banner{display:block;width:100%;height:auto;border-radius:0;aspect-ratio:2048/634}"
             "@media (min-width:641px){.bar.faixa .marca .banner{-webkit-mask-image:linear-gradient(90deg,transparent,#000 7%,#000 93%,transparent);"
             "mask-image:linear-gradient(90deg,transparent,#000 7%,#000 93%,transparent)}}"
             ".bar.faixa .acoes{position:absolute;top:8px;right:max(8px,calc((100% - 1120px)/2 + 16px));display:flex;align-items:center;gap:8px}"
             ".bar.faixa .acoes .ig{margin-left:0}"
             ".bar.faixa .busca-btn,.bar.faixa .acoes .ig{background:rgba(2,22,40,.55);border-color:rgba(255,255,255,.28);color:#fff;"
             "-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px)}"
             ".bar.faixa .busca-btn:hover{border-color:#e3b23c;color:#e3b23c}")

# CSS comum a todas as páginas: botão de busca e respeito a prefers-reduced-motion (sem transições, animações,
# rolagem suave nem os deslocamentos de hover/toque dos cartões e botões)
CSS_BUSCA = (".busca-btn{display:grid;place-items:center;flex:none;width:44px;height:44px;padding:0;border:1px solid #2e4d7a;border-radius:8px;"
             "background:none;color:#e9ecf1;cursor:pointer}.busca-btn:hover{border-color:#e3b23c;color:#e3b23c}.busca-btn[hidden]{display:none}"
             # alvo de toque mínimo de 24 px (WCAG 2.2, 2.5.8) nos links do rodapé comum
             "footer .in a{display:inline-flex;align-items:center;min-height:24px}"
             + CSS_FAIXA + CSS_COMPARTILHAR + CSS_INTERACOES +
             # menu das seções sempre preso no topo; as outras barras presas ficam logo abaixo dele
             ":where(html){scroll-padding-top:calc(var(--nav-h,49px) + 12px)}"
             ".nav{position:sticky;top:0;z-index:20}body .abas,body .barra-f,body .ctrl{top:var(--nav-h,49px)}"
             ".nav .casa{display:flex;align-items:center;justify-content:center;min-width:44px}.nav .casa .ic{width:20px;height:20px}"
             "@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms!important;animation-iteration-count:1!important;"
             "transition-duration:.01ms!important;scroll-behavior:auto!important}"
             ".card:hover,.jogo:hover .capa img,.jogo:active .capa,.zap:active,.post-btn:active,.btn-filtro:hover,.btn-filtro:active,.ver:active{transform:none!important}}")


# O menu fica sempre preso no topo; barras que também ficam presas (abas da resenha, filtros) param logo abaixo dele.
# O script só mede a altura do menu (que muda se o texto quebrar ou a fonte for maior).
JS_MENU = ("(()=>{const n=document.querySelector('.nav'),h=()=>document.documentElement.style.setProperty('--nav-h',n.offsetHeight+'px');"
           "h();addEventListener('resize',h);addEventListener('load',h)})()")


def cabecalho(pre, atual="", sub=False):
    """Barra da marca + menu de seções.

    `atual` é o rótulo da seção da página. Na página-índice da seção o link recebe aria-current="page";
    numa subpágina (uma resenha, uma notícia) recebe aria-current="true", que marca a seção sem dizer
    que o link leva à própria página. O visual é o mesmo nos dois casos ([aria-current] no CSS)."""
    marca = "page" if not sub else "true"
    # primeiro item: a casinha, que volta à página inicial (marcada como página atual na própria home)
    casa = f'<li><a class="casa" href="{pre or './'}" aria-label="Página inicial"{" aria-current=\"page\"" if atual == "Início" else ""}>{icone("casa")}</a></li>'
    nav = casa + "".join(f'<li><a href="{pre}{h}"{f" aria-current=\"{marca}\"" if t == atual else ""}>{t}</a></li>' for h, t in SECOES)
    # banner da marca (tools/gerar_banner.py): grande na página inicial, contido nas demais para o conteúdo subir
    home = atual == "Início"
    larg = 960 if home else 640
    srcset = ", ".join(f"{pre}marca/banner-{w}.webp {w}w" for w in BANNER_LARGURAS)
    return f"""<header class="bar faixa{' grande' if home else ''}" id="topo"><div class="in">
 <a class="marca" href="{pre or './'}"><img class="banner" src="{pre}marca/banner-960.webp" srcset="{srcset}" sizes="(min-width:{larg}px) {larg}px, 100vw" width="2048" height="634"{' fetchpriority="high"' if home else ''} alt="O Paladino: jornalismo com princípios. Fé, cultura, sociedade. Página inicial"></a>
 <div class="acoes">{f'<a class="ig" href="{INSTAGRAM}" target="_blank" rel="noopener" aria-label="Instagram">{icone("insta")}<span>Instagram</span></a>' if INSTAGRAM else ''}
 {f'<a class="zap-mini" href="{WHATSAPP}" target="_blank" rel="noopener" aria-label="Grupo do WhatsApp">{icone("zap")}<span>Grupo do WhatsApp</span></a>' if WHATSAPP else ''}
 <button type="button" class="busca-btn" aria-label="Buscar no site" aria-haspopup="dialog" aria-keyshortcuts="/ Control+K" hidden>{icone("busca")}</button></div>
</div></header>
<script>{DISPARADOR.replace("PRE", pre)}</script>
<nav class="nav" aria-label="Seções do site"><ul class="in">{nav}</ul></nav>
<script>{JS_MENU}</script>"""


def trilha(*itens):
    """Trilha visível (breadcrumb) a partir de pares (rótulo, href); o último item é a página atual, sem link.

    Os rótulos são os mesmos do BreadcrumbList em JSON-LD (seo.trilha), que já existe nessas páginas."""
    *links, (atual, _) = itens
    lis = "".join(f'<li><a href="{h}">{r}</a></li>' for r, h in links)
    return f'<nav class="trilha" aria-label="Trilha de navegação"><ol>{lis}<li aria-current="page">{atual}</li></ol></nav>'


# CSS da trilha, igual nas páginas escuras (resenha, notícia)
CSS_TRILHA = (".trilha{min-width:0;max-width:100%}.trilha ol{display:flex;align-items:center;min-width:0;margin:0;padding:0;list-style:none;font-size:.85rem;color:var(--muted)}"
              ".trilha li{display:flex;align-items:center;white-space:nowrap}"
              ".trilha li+li::before{content:\"›\";content:\"›\" / \"\";margin:0 8px;color:var(--muted)}"
              ".trilha a{color:var(--gold);font-weight:700;text-decoration:none;padding:4px 0}.trilha a:hover{text-decoration:underline}"
              ".trilha li:last-child{display:block;min-width:0;overflow:hidden;text-overflow:ellipsis}"
              ".trilha li:last-child::before{display:inline}")


from endereco import SITE  # noqa: E402  (config/portal.json)

# Sem JavaScript, o botão é um link para o WhatsApp; o script troca pelo menu do celular ou pela janelinha.
JS_COMPARTILHAR = """(()=>{const pega=c=>({u:c.dataset.url||location.href,t:c.dataset.texto||document.title});
document.querySelectorAll('.cpw:not(.ok)').forEach(c=>{c.classList.add('ok');const b=c.querySelector('.cp');
 const n=document.createElement('button');n.type='button';n.className=b.className;n.innerHTML=b.innerHTML;n.setAttribute('aria-expanded','false');b.replaceWith(n)});
if(window.__cp)return;window.__cp=1;
const celular=()=>navigator.share&&matchMedia('(pointer:coarse)').matches;
const fecha=()=>document.querySelectorAll('.cp-menu:not([hidden])').forEach(m=>{m.hidden=true;m.parentNode.querySelector('.cp').setAttribute('aria-expanded','false')});
document.addEventListener('keydown',e=>{if(e.key==='Escape')fecha()});
document.addEventListener('click',async ev=>{const c=ev.target.closest('.cpw');if(!c){fecha();return}
 const {u,t}=pega(c),m=c.querySelector('.cp-menu'),st=c.querySelector('.cp-st'),el=ev.target.closest('.cp,.cp-op');if(!el)return;
 if(el.classList.contains('cp')){
  if(celular()){try{await navigator.share({title:document.title,text:t,url:u})}catch(e){}return}
  const abre=m.hidden;fecha();if(!abre)return;
  m.querySelector('.zap-op').href='https://wa.me/?text='+encodeURIComponent(t+' '+u);
  const r=c.getBoundingClientRect();m.classList.toggle('sobe',!!c.closest('.barra-lt')||r.bottom>innerHeight-140);m.classList.toggle('dir',r.left>innerWidth-220);
  m.hidden=false;el.setAttribute('aria-expanded','true');m.querySelector('.cp-op').focus();return}
 if(el.classList.contains('zap-op')){fecha();return}
 fecha();let ok=false;try{await navigator.clipboard.writeText(u);ok=true}catch(e){
  const i=document.createElement('input');i.value=u;document.body.append(i);i.select();try{ok=document.execCommand('copy')}catch(e2){}i.remove()}
 st.textContent=ok?'Link copiado!':'Não deu para copiar o link.';clearTimeout(st._t);st._t=setTimeout(()=>st.textContent='',2500);
 c.querySelector('.cp').focus()})})()"""

# Barra de leitura: aparece depois que a pessoa rola um pouco e some quando o convite do fim ou o rodapé aparecem.
JS_LEITURA = """(()=>{const l=document.querySelector('.barra-lt');if(!l)return;const vis=new Set();
const poe=()=>{const on=scrollY>500&&!vis.size;l.classList.toggle('fora',!on);l.inert=!on;document.body.classList.toggle('lt-on',on)};
const io=new IntersectionObserver(es=>{es.forEach(e=>e.isIntersecting?vis.add(e.target):vis.delete(e.target));poe()});
document.querySelectorAll('.convite,footer').forEach(x=>io.observe(x));addEventListener('scroll',poe,{passive:true});poe()})()"""


def botao_compartilhar(texto, url="", rotulo="Compartilhar", mini=False):
    """Botão único de compartilhar. Sem `url`, usa o endereço atual (páginas cujo endereço muda com os filtros)."""
    import html
    from urllib.parse import quote
    zap = f"https://wa.me/?text={quote(texto + ' ' + url, safe='')}" if url else "https://wa.me/"
    dados = (f' data-url="{html.escape(url)}"' if url else "") + f' data-texto="{html.escape(texto)}"'
    return (f'<div class="cpw{" mini" if mini else ""}"{dados}>'
            f'<a class="cp" href="{html.escape(zap)}" target="_blank" rel="noopener">{icone("compartilhar")}<span>{html.escape(rotulo)}</span></a>'
            f'<div class="cp-menu" hidden><a class="cp-op zap-op" href="{html.escape(zap)}" target="_blank" rel="noopener">{icone("zap")}WhatsApp</a>'
            f'<button type="button" class="cp-op">{icone("copiar")}Copiar link</button></div>'
            f'<p class="cp-st" role="status"></p></div><script>{JS_COMPARTILHAR}</script>')


def convite_compartilhar(texto, url, titulo, sub, classe="bloco"):
    """O convite único no fim do conteúdo (depois de "Nossa opinião" ou do veredito), seguido do "Fale com o editor"."""
    return (f'<section class="{classe} convite" aria-label="Compartilhar"><div><p class="cv-t">{titulo}</p><p class="cv-s">{sub}</p></div>'
            f'{botao_compartilhar(texto, url)}</section>{fale_com_editor(classe)}')


def fale_com_editor(classe="bloco"):
    """Bloco de contato com o editor responsável: seguir e mandar mensagem no Instagram dele (vazio sem Instagram)."""
    if not EDITOR_IG:
        return ""
    return (f'<section class="{classe} convite editor-cv" aria-label="Fale com o editor"><div><p class="cv-t">Fale com o editor</p>'
            f'<p class="cv-s">{EDITOR["nome"]}, {EDITOR.get("cargo", "editor").lower()}. Sugestão de pauta, correção ou conversa: '
            f'mande mensagem no Instagram.</p></div>'
            f'<a class="ig-cv" href="{EDITOR_IG}" target="_blank" rel="noopener me">{icone("insta")}<span>Seguir {EDITOR_ARROBA}</span></a></section>')


def barra_leitura(texto="", url="", interacao=True):
    """Barra fixa no pé da tela: Compartilhar em todas as páginas; nas notícias e resenhas também Curtir e Comentários
    (só com o serviço ligado). Sem `texto` e `url`, compartilha o título e o endereço da própria página."""
    extras = ""
    if interacao and _config_interacoes().get("api"):
        extras = (f'<button type="button" class="lt-b curtir" aria-pressed="false" aria-label="Curtir">{icone("coracao")}<b class="n">–</b></button>'
                  f'<a class="lt-b" href="#comentarios">{icone("balao")}<span>Comentários</span></a>')
    return (f'<div class="barra-lt fora" role="region" aria-label="Ações da página">{extras}{botao_compartilhar(texto, url)}'
            + (f'<a class="lt-grupo" href="{WHATSAPP}" target="_blank" rel="noopener" aria-label="Entrar no grupo do WhatsApp">{icone("zap")}<span>Grupo</span></a>' if WHATSAPP else '') + '</div>'
            f'<script>{JS_LEITURA}</script>')


def _config_interacoes():
    import json
    from pathlib import Path
    arq = Path(__file__).resolve().parent.parent / "conteudo" / "interacoes.json"
    return json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else {}


def interacoes(pre, caminho, classe="bloco"):
    """Curtir + comentários moderados (serviço em worker/). Vazio enquanto conteudo/interacoes.json não tiver a API,
    ou seja, nada aparece no site antes de o serviço estar instalado."""
    import html
    cfg = _config_interacoes()
    if not cfg.get("api"):
        return ""
    return f"""<section class="{classe} interacoes" id="comentarios" data-api="{html.escape(cfg['api'])}" data-p="{html.escape(caminho)}" data-turnstile="{html.escape(cfg.get('turnstile', ''))}">
 <div class="curtir-l"><button type="button" class="curtir" aria-pressed="false">{icone("coracao")}<span class="rot">Curtir</span> <b class="n" aria-label="curtidas">–</b></button><span class="curtir-dica">Gostou? Deixe um coração.</span></div>
 <h2>Comentários <span class="coms-n"></span></h2>
 <ol class="coms"></ol><p class="coms-vazio">Ainda não há comentários. Seja a primeira pessoa a comentar.</p>
 <form class="com-form">
  <label>Nome<input name="nome" required minlength="2" maxlength="60" autocomplete="name"></label>
  <label>E-mail <small>(opcional, não é publicado)</small><input name="email" type="email" maxlength="120" autocomplete="email"></label>
  <label>Comentário<textarea name="texto" required minlength="3" maxlength="1500" rows="4"></textarea></label>
  <label class="isca" aria-hidden="true">Site<input name="site" tabindex="-1" autocomplete="off"></label>
  <div class="com-ts"></div>
  <button type="submit">Enviar comentário</button>
  <p class="com-aviso">Todo comentário passa por moderação antes de aparecer. O e-mail não é publicado. <a href="{pre}politica-editorial/#comentarios">Como moderamos</a></p>
  <p class="com-st" role="status"></p>
 </form>
</section>
<script src="{pre}interacoes.js" defer></script>"""


def rodape(pre, barra=None):
    """Rodapé comum. `barra` é a barra fixa do pé da tela: por padrão, só Compartilhar; "" para nenhuma."""
    if barra is None:
        barra = barra_leitura(interacao=False)
    return f"""<footer><div class="in">
 <span>O Paladino</span><a href="{pre}noticias/">Notícias</a><a href="{pre}estudos/">Estudos bíblicos</a><a href="{pre}discipulado/">Discipulado</a><a href="{pre}consulta/">Versículo diário</a><a href="{pre}sobre/">Quem somos</a><a href="{pre}politica-editorial/">Política editorial</a>
 {f'<a href="{INSTAGRAM}" target="_blank" rel="noopener">Instagram</a>' if INSTAGRAM else ''}{f'<a class="rod-ig" href="{EDITOR_IG}" target="_blank" rel="noopener me" aria-label="Instagram do editor, {EDITOR_ARROBA}">{icone("insta")}{EDITOR_ARROBA}</a>' if EDITOR_IG else ''}{f'<a href="{WHATSAPP}" target="_blank" rel="noopener">Grupo do WhatsApp</a>' if WHATSAPP else ''}{f'<a href="mailto:{EMAIL}">Contato</a>' if EMAIL else ''}
</div></footer>
{barra}"""
