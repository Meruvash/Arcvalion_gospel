"""Moldura comum a todas as páginas: cabeçalho, menu de editorias, trilha, rodapé, compartilhar e interações.

Portado de tools/layout.py do Elite Boardgamers: mesma marcação e mesmo comportamento (menu preso no topo com a
altura medida, busca baixada só no primeiro uso, um botão de compartilhar que usa o menu do celular, barra de
leitura que aparece ao rolar, curtidas e comentários moderados). O que era fixo (marca, redes, seções) agora vem de
config/ via portal.py. O CSS fica em estilo.py.
"""
import html
from urllib.parse import quote

import portal

e = html.escape

ICONES = {
    "casa": '<path d="M3 11.5 12 4l9 7.5"/><path d="M5.5 9.5V20h13V9.5"/><path d="M10 20v-5.5h4V20"/>',
    "busca": '<circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/>',
    "compartilhar": '<circle cx="18" cy="5" r="2.5"/><circle cx="6" cy="12" r="2.5"/><circle cx="18" cy="19" r="2.5"/><path d="M8.2 10.8l7.6-4.4M8.2 13.2l7.6 4.4"/>',
    "copiar": '<rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V6a2 2 0 0 1 2-2h8"/>',
    "zap": '<path d="M4 20l1.3-4A8 8 0 1 1 8.4 19l-4.4 1Z"/><path d="M9.2 8.6c.3-.5.8-.5 1-.1l.7 1.5c.1.3 0 .6-.2.8l-.4.4c.5 1.1 1.4 2 2.5 2.5l.4-.4c.2-.2.5-.3.8-.2l1.5.7c.4.2.4.7-.1 1-.7.5-1.6.6-2.4.3a7 7 0 0 1-4.2-4.2c-.3-.8-.2-1.7.4-2.3Z"/>',
    "insta": '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.3" cy="6.7" r=".6" fill="currentColor"/>',
    "youtube": '<rect x="2.5" y="5.5" width="19" height="13" rx="4"/><path d="M10 9.2v5.6l4.8-2.8Z" fill="currentColor"/>',
    "x": '<path d="M4 4l16 16M20 4 4 20"/>',
    "facebook": '<path d="M14.5 21v-7.5h2.6l.4-3h-3V8.6c0-.9.3-1.5 1.6-1.5h1.6V4.4A20 20 0 0 0 15.4 4c-2.3 0-3.9 1.4-3.9 4v2.5H9v3h2.5V21"/>',
    "telegram": '<path d="M21 4 3 11l6 2.5L19 7l-7.5 8 6 4.5Z"/>',
    "email": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m4 7 8 6 8-6"/>',
    "rss": '<path d="M5 19a1 1 0 1 0 0-.01M5 11a8 8 0 0 1 8 8M5 5a14 14 0 0 1 14 14"/>',
    "coracao": '<path d="M12 20s-7.5-4.6-9.3-9.2C1.4 7.4 3.6 4 7 4c2 0 3.6 1.1 5 3 1.4-1.9 3-3 5-3 3.4 0 5.6 3.4 4.3 6.8C19.5 15.4 12 20 12 20Z"/>',
    "balao": '<path d="M4 5h16v11H9l-5 4V5Z"/>',
    "livro": '<path d="M12 6.5C10 5 7 4.5 3.5 5v13c3.5-.5 6.5 0 8.5 1.5 2-1.5 5-2 8.5-1.5V5C17 4.5 14 5 12 6.5Z"/><path d="M12 6.5v13"/>',
    "calendario": '<rect x="3.5" y="5" width="17" height="15" rx="2"/><path d="M3.5 9.5h17M8 3v4M16 3v4"/>',
    "local": '<path d="M12 21s-6.5-6-6.5-11a6.5 6.5 0 0 1 13 0c0 5-6.5 11-6.5 11Z"/><circle cx="12" cy="10" r="2.3"/>',
    "aviso": '<path d="M12 3 2.5 20h19L12 3Z"/><path d="M12 10v4.5M12 17.2v.1"/>',
    "nao": '<path d="M6 6l12 12M18 6L6 18"/>',
}

REDES = [("instagram", "Instagram", "insta"), ("youtube", "YouTube", "youtube"), ("x", "X", "x"), ("facebook", "Facebook", "facebook"),
         ("telegram", "Telegram", "telegram"), ("whatsapp_canal", "Canal no WhatsApp", "zap")]


def icone(nome, cls="ic"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{ICONES[nome]}</svg>'


# Símbolo da marca: livro aberto com uma cruz sobre a lombada. Desenho próprio e genérico, sem elemento de terceiros.
SIMBOLO = ('<svg class="simbolo" viewBox="0 0 32 32" aria-hidden="true"><rect width="32" height="32" rx="7" fill="#12294a"/>'
           '<path d="M16 12.2c-2.2-1.5-5.2-2-8.6-1.6v12.2c3.4-.4 6.4.1 8.6 1.6 2.2-1.5 5.2-2 8.6-1.6V10.6c-3.4-.4-6.4.1-8.6 1.6Z" fill="#fff"/>'
           '<path d="M16 12.2v12.2" stroke="#12294a" stroke-width="1.2"/><path d="M16 4.5v6M13.4 6.8h5.2" stroke="#d6b25e" stroke-width="2" stroke-linecap="round"/></svg>')


def secoes():
    """(caminho a partir da raiz, rótulo do menu, slug) das editorias visíveis, mais a vitrine de opinião."""
    return [(f"{x['slug']}/", x.get("menu") or x["nome"], x["slug"]) for x in portal.visiveis()] + [("opiniao/", "Opinião", "opiniao")]


# Disparador da busca (igual ao original): mostra a lupa e, no clique, em "/" ou em Ctrl+K, baixa busca.js na primeira vez.
DISPARADOR = ("(()=>{const b=document.querySelector('.busca-btn');let c;b.hidden=false;"
              "const a=()=>{c=c||new Promise((r,j)=>{const s=document.createElement('script');s.src='PREjs/busca.js';s.onload=r;"
              "s.onerror=()=>{c=null;j()};document.head.append(s)});c.then(()=>abrirBusca('PRE'),()=>{})};"
              "b.addEventListener('click',a);addEventListener('keydown',e=>{const t=e.target,ed=t.isContentEditable||/^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName);"
              "if((e.key==='/'&&!ed&&!e.ctrlKey&&!e.metaKey)||((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k')){e.preventDefault();a()}})})()")

# O menu fica preso no topo; o script mede a altura dele para as barras presas logo abaixo.
JS_MENU = ("(()=>{const n=document.querySelector('.nav'),h=()=>document.documentElement.style.setProperty('--nav-h',n.offsetHeight+'px');"
           "h();addEventListener('resize',h);addEventListener('load',h);const a=n.querySelector('[aria-current]');if(a)a.scrollIntoView({block:'nearest',inline:'center'})})()")


def faixa_exemplo():
    if not portal.EXEMPLO:
        return ""
    return ('<div class="exemplo" role="note"><b>Demonstração.</b> Esta é uma prévia com textos fictícios de exemplo, '
            'feita só para conferir o layout. Nada aqui é notícia real.</div>')


def cabecalho(pre, atual="", sub=False):
    """Barra da marca + menu. `atual` é o slug da seção (ou "inicio"); numa subpágina o link recebe aria-current="true"."""
    marca_atual = "page" if not sub else "true"
    redes = portal.CFG.get("redes", {})
    sociais = "".join(f'<a class="rede" href="{e(redes[k])}" target="_blank" rel="noopener" aria-label="{r}">{icone(ic)}</a>'
                      for k, r, ic in REDES if redes.get(k))
    casa = (f'<li><a class="casa" href="{pre or "./"}" aria-label="Página inicial"'
            f'{" aria-current=\"page\"" if atual == "inicio" else ""}>{icone("casa")}</a></li>')
    nav = casa + "".join(f'<li><a href="{pre}{h}"{f" aria-current=\"{marca_atual}\"" if s == atual else ""}>{e(t)}</a></li>'
                         for h, t, s in secoes())
    news = f'<a class="news-btn" href="{pre}newsletter/">{icone("email")}<span>Newsletter</span></a>'
    return f"""<a class="pular" href="#conteudo">Pular para o conteúdo</a>{faixa_exemplo()}
<header class="bar" id="topo"><div class="in">
 <a class="marca" href="{pre or './'}" aria-label="{e(portal.NOME)}: página inicial">{SIMBOLO}<span class="marca-t"><span class="marca-n">{e(portal.NOME)}</span><span class="marca-s">{e(portal.CFG.get('slogan', ''))}</span></span></a>
 <div class="bar-acoes">{sociais}{news}
 <button type="button" class="busca-btn" aria-label="Buscar no site" aria-haspopup="dialog" aria-keyshortcuts="/ Control+K" hidden>{icone("busca")}</button></div>
</div></header>
<script>{DISPARADOR.replace("PRE", pre)}</script>
<nav class="nav" aria-label="Editorias"><ul class="in">{nav}</ul></nav>
<script>{JS_MENU}</script>"""


def trilha(*itens):
    """Trilha visível a partir de pares (rótulo, href); o último item é a página atual. Igual ao BreadcrumbList."""
    *links, (atual, _) = itens
    lis = "".join(f'<li><a href="{h}">{r}</a></li>' for r, h in links)
    return f'<nav class="trilha" aria-label="Trilha de navegação"><ol>{lis}<li aria-current="page">{atual}</li></ol></nav>'


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
  m.querySelector('.tg-op').href='https://t.me/share/url?url='+encodeURIComponent(u)+'&text='+encodeURIComponent(t);
  const r=c.getBoundingClientRect();m.classList.toggle('sobe',!!c.closest('.barra-lt')||r.bottom>innerHeight-180);m.classList.toggle('dir',r.left>innerWidth-220);
  m.hidden=false;el.setAttribute('aria-expanded','true');m.querySelector('.cp-op').focus();return}
 if(el.tagName==='A'){fecha();return}
 fecha();let ok=false;try{await navigator.clipboard.writeText(u);ok=true}catch(e){
  const i=document.createElement('input');i.value=u;document.body.append(i);i.select();try{ok=document.execCommand('copy')}catch(e2){}i.remove()}
 st.textContent=ok?'Link copiado!':'Não deu para copiar o link.';clearTimeout(st._t);st._t=setTimeout(()=>st.textContent='',2500);
 c.querySelector('.cp').focus()})})()"""

JS_LEITURA = """(()=>{const l=document.querySelector('.barra-lt');if(!l)return;const vis=new Set();
const poe=()=>{const on=scrollY>500&&!vis.size;l.classList.toggle('fora',!on);l.inert=!on;document.body.classList.toggle('lt-on',on)};
const io=new IntersectionObserver(es=>{es.forEach(e=>e.isIntersecting?vis.add(e.target):vis.delete(e.target));poe()});
document.querySelectorAll('.convite,footer').forEach(x=>io.observe(x));addEventListener('scroll',poe,{passive:true});poe()})()"""


def botao_compartilhar(texto, url="", rotulo="Compartilhar", mini=False):
    """Botão único de compartilhar. Sem JavaScript é um link para o WhatsApp."""
    zap = f"https://wa.me/?text={quote(texto + ' ' + url, safe='')}" if url else "https://wa.me/"
    tg = f"https://t.me/share/url?url={quote(url, safe='')}&text={quote(texto, safe='')}" if url else "https://t.me/share/url"
    dados = (f' data-url="{e(url)}"' if url else "") + f' data-texto="{e(texto)}"'
    return (f'<div class="cpw{" mini" if mini else ""}"{dados}>'
            f'<a class="cp" href="{e(zap)}" target="_blank" rel="noopener">{icone("compartilhar")}<span>{e(rotulo)}</span></a>'
            f'<div class="cp-menu" hidden><a class="cp-op zap-op" href="{e(zap)}" target="_blank" rel="noopener">{icone("zap")}WhatsApp</a>'
            f'<a class="cp-op tg-op" href="{e(tg)}" target="_blank" rel="noopener">{icone("telegram")}Telegram</a>'
            f'<button type="button" class="cp-op">{icone("copiar")}Copiar link</button></div>'
            f'<p class="cp-st" role="status"></p></div><script>{JS_COMPARTILHAR}</script>')


def convite_compartilhar(texto, url, titulo, sub, classe="bloco"):
    return (f'<section class="{classe} convite" aria-label="Compartilhar"><div><p class="cv-t">{titulo}</p><p class="cv-s">{sub}</p></div>'
            f'{botao_compartilhar(texto, url)}</section>')


def api():
    return (portal.CFG.get("interacoes") or {}).get("api", "")


def barra_leitura(texto="", url="", interacao=True, pre=""):
    """Barra fixa no pé da tela: compartilhar sempre; curtir e comentários nas matérias (só com o serviço ligado)."""
    extras = ""
    if interacao and api():
        extras = (f'<button type="button" class="lt-b curtir" aria-pressed="false" aria-label="Curtir">{icone("coracao")}<b class="n">–</b></button>'
                  f'<a class="lt-b" href="#comentarios">{icone("balao")}<span>Comentários</span></a>')
    return (f'<div class="barra-lt fora" role="region" aria-label="Ações da página">{extras}{botao_compartilhar(texto, url)}'
            f'<a class="lt-news" href="{pre}newsletter/" aria-label="Receber a newsletter">{icone("email")}<span>Newsletter</span></a></div>'
            f'<script>{JS_LEITURA}</script>')


def interacoes(pre, caminho, classe="bloco"):
    """Curtir + comentários moderados (serviço em worker/). Vazio enquanto config/portal.json não tiver a API."""
    if not api():
        return ""
    ts = (portal.CFG.get("interacoes") or {}).get("turnstile", "")
    return f"""<section class="{classe} interacoes" id="comentarios" data-api="{e(api())}" data-p="{e(caminho)}" data-turnstile="{e(ts)}">
 <div class="curtir-l"><button type="button" class="curtir" aria-pressed="false">{icone("coracao")}<span class="rot">Curtir</span> <b class="n" aria-label="curtidas">–</b></button><span class="curtir-dica">Esta matéria foi útil? Deixe um coração.</span></div>
 <h2>Comentários <span class="coms-n"></span></h2>
 <ol class="coms"></ol><p class="coms-vazio">Ainda não há comentários.</p>
 <form class="com-form">
  <label>Nome<input name="nome" required minlength="2" maxlength="60" autocomplete="name"></label>
  <label>E-mail <small>(opcional, não é publicado)</small><input name="email" type="email" maxlength="120" autocomplete="email"></label>
  <label>Comentário<textarea name="texto" required minlength="3" maxlength="1500" rows="4"></textarea></label>
  <label class="isca" aria-hidden="true">Site<input name="site" tabindex="-1" autocomplete="off"></label>
  <div class="com-ts"></div>
  <button type="submit">Enviar comentário</button>
  <p class="com-aviso">Todo comentário passa por moderação antes de aparecer. Discordar com respeito é bem-vindo. <a href="{pre}politica-editorial/#comentarios">Como moderamos</a></p>
  <p class="com-st" role="status"></p>
 </form>
</section>
<script src="{pre}js/interacoes.js" defer></script>"""


def formulario(tipo, pre, origem=""):
    """Formulário de newsletter/cadastro de leitores ou de contato (comercial, evento, correção, geral).

    Com a API configurada, envia para o Worker (com consentimento explícito e Turnstile). Sem ela, vira um link de
    e-mail para o endereço configurado, ou um aviso de que o canal ainda não está aberto. Nenhum dado é enviado a
    terceiros pelo navegador."""
    cfg = portal.CFG
    if not api():
        email = cfg.get("email_comercial") if tipo == "comercial" else cfg.get("email_correcoes") if tipo == "correcao" else cfg.get("email_contato")
        if tipo == "newsletter":
            return '<p class="form-off">As inscrições na newsletter abrem em breve.</p>'
        if email:
            return f'<p class="form-off">Escreva para <a href="mailto:{e(email)}">{e(email)}</a>.</p>'
        return '<p class="form-off">Este canal abre em breve.</p>'
    ts = (cfg.get("interacoes") or {}).get("turnstile", "")
    priv = f'<a href="{pre}privacidade/">Política de Privacidade</a>'
    if tipo == "newsletter":
        eds = "".join(f'<label class="op"><input type="checkbox" name="editorias" value="{x["slug"]}"> {e(x["nome"])}</label>' for x in portal.visiveis())
        campos = (f'<label>Nome <small>(opcional)</small><input name="nome" maxlength="80" autocomplete="name"></label>'
                  f'<label>E-mail<input name="email" type="email" required maxlength="120" autocomplete="email"></label>'
                  f'<fieldset><legend>Assuntos que você quer receber <small>(opcional)</small></legend><div class="ops">{eds}</div></fieldset>')
        consent = (f"Quero receber a newsletter do {e(portal.NOME)} por e-mail. Sei que posso cancelar a qualquer momento "
                   f"pelo link em cada mensagem, e li a {priv}.")
        botao = "Inscrever-me"
    else:
        extra = ""
        if tipo == "comercial":
            extra = '<label>Empresa ou igreja <small>(opcional)</small><input name="empresa" maxlength="120" autocomplete="organization"></label>'
        elif tipo == "evento":
            extra = ('<label>Nome do evento<input name="empresa" required maxlength="120"></label>'
                     '<label>Data e cidade<input name="detalhe" required maxlength="160" placeholder="Ex.: 12 a 14/03/2027, Curitiba (PR)"></label>')
        elif tipo == "correcao":
            extra = '<label>Endereço da matéria<input name="detalhe" type="url" required maxlength="300" placeholder="https://"></label>'
        campos = (f'<label>Nome<input name="nome" required minlength="2" maxlength="80" autocomplete="name"></label>'
                  f'<label>E-mail<input name="email" type="email" required maxlength="120" autocomplete="email"></label>{extra}'
                  f'<label>Mensagem<textarea name="mensagem" required minlength="10" maxlength="3000" rows="5"></textarea></label>')
        consent = f"Autorizo o uso destes dados só para responder a esta mensagem, conforme a {priv}."
        botao = "Enviar"
    return f"""<form class="form-pc" data-api="{e(api())}" data-tipo="{tipo}" data-origem="{e(origem)}" data-turnstile="{e(ts)}">
 {campos}
 <label class="isca" aria-hidden="true">Site<input name="site" tabindex="-1" autocomplete="off"></label>
 <label class="consent"><input type="checkbox" name="consentimento" required> <span>{consent}</span></label>
 <div class="f-ts"></div>
 <button type="submit">{botao}</button>
 <p class="f-st" role="status"></p>
</form>
<script src="{pre}js/formularios.js" defer></script>"""


def rodape(pre, barra=None):
    """Rodapé comum. `barra` é a barra fixa do pé da tela: por padrão só compartilhar e newsletter; "" para nenhuma."""
    if barra is None:
        barra = barra_leitura(interacao=False, pre=pre)
    cfg = portal.CFG
    eds = "".join(f'<li><a href="{pre}{x["slug"]}/">{e(x["nome"])}</a></li>' for x in portal.visiveis())
    inst = [("sobre/", "Quem somos"), ("expediente/", "Expediente"), ("politica-editorial/", "Política editorial"),
            ("politica-editorial/#correcoes", "Correções"), ("contato/", "Fale conosco"), ("anuncie/", "Anuncie conosco"),
            ("newsletter/", "Newsletter"), ("privacidade/", "Privacidade"), ("termos/", "Termos de uso")]
    links = "".join(f'<li><a href="{pre}{h}">{t}</a></li>' for h, t in inst)
    redes = cfg.get("redes", {})
    sociais = "".join(f'<li><a href="{e(redes[k])}" target="_blank" rel="noopener">{r}</a></li>' for k, r, _ in REDES if redes.get(k))
    sociais += f'<li><a href="{pre}feed.xml">RSS</a></li>'
    pref = ('<li><button type="button" class="pref-priv" hidden>Preferências de privacidade</button></li>')
    legal = " · ".join(x for x in (cfg.get("razao_social"), f"CNPJ {cfg['cnpj']}" if cfg.get("cnpj") else "") if x)
    return f"""<footer><div class="in">
 <div class="rod-marca"><span class="marca-n">{e(portal.NOME)}</span><p>{e(cfg.get('descricao', ''))}</p></div>
 <nav aria-label="Editorias no rodapé"><p class="rod-h">Editorias</p><ul>{eds}<li><a href="{pre}opiniao/">Opinião</a></li><li><a href="{pre}noticias/">Todas as notícias</a></li></ul></nav>
 <nav aria-label="Institucional"><p class="rod-h">Institucional</p><ul>{links}{pref}</ul></nav>
 <nav aria-label="Redes"><p class="rod-h">Acompanhe</p><ul>{sociais}</ul></nav>
 <p class="rod-legal">© {e(cfg.get('fundacao', ''))} {e(portal.NOME)}{(' · ' + e(legal)) if legal else ''}. Publicidade e conteúdo patrocinado são sempre identificados.</p>
</div></footer>
{barra}"""
