"""CSS do portal (inline em cada página, como no original: nenhuma requisição de CSS antes do conteúdo).

Estrutura herdada do Elite Boardgamers: contêiner de 1180 px, blocos de leitura com raio de 10 px, grade da home com
grid-template-areas a partir de 900 px, grade do arquivo 2/3/4 colunas, blocos de ponta a ponta no celular, alvos de
toque de 44 px, foco visível de 3 px e prefers-reduced-motion. A identidade é nova: fundo claro de jornal,
azul-marinho com ouro velho e títulos em serifa (Source Serif 4). As cores das editorias vêm de config/editorias.json.
"""
import portal

BASE = """
@font-face{font-family:"Public Sans";src:url(%(pre)sfontes/public-sans.woff2) format("woff2");font-weight:400 800;font-display:swap}
@font-face{font-family:"Source Serif 4";src:url(%(pre)sfontes/source-serif-4-700.woff2) format("woff2");font-weight:700;font-display:swap}
:root{color-scheme:light;--fundo:#f5f3ee;--papel:#fff;--tinta:#16202e;--texto:#2b3442;--suave:#5b6573;--linha:#e3e0d8;
--marinho:#12294a;--marinho2:#1b3a66;--ouro:#d6b25e;--ouro-esc:#8a6417;--link:#1d4f91;--foco:#8a6417;
--serif:"Source Serif 4",Georgia,"Times New Roman",serif;--sans:"Public Sans",system-ui,-apple-system,"Segoe UI",sans-serif;
--mono:ui-monospace,"SF Mono",SFMono-Regular,Menlo,Consolas,monospace;--c:var(--marinho);--f:#e8edf5}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%%}
body{margin:0;background:var(--fundo);color:var(--tinta);font:16px/1.6 var(--sans);padding-left:env(safe-area-inset-left,0px);padding-right:env(safe-area-inset-right,0px)}
h1,h2,h3,p,ul,ol,figure,blockquote,dl,dd{margin:0}ul,ol{padding:0;list-style:none}img{display:block;max-width:100%%;height:auto}a{color:inherit}
::selection{background:#f1dfae;color:#000}
:focus-visible{outline:3px solid var(--foco);outline-offset:2px;border-radius:3px}
.in{max-width:1180px;margin:0 auto;padding-left:16px;padding-right:16px}
.ic{width:20px;height:20px;fill:none;stroke:currentColor;stroke-width:1.75;stroke-linecap:round;stroke-linejoin:round;flex:none}
.pular{position:absolute;left:8px;top:-60px;z-index:50;background:var(--papel);color:var(--tinta);padding:10px 14px;border-radius:8px;font-weight:800}
.pular:focus{top:8px}
.exemplo{background:#fff3cd;color:#5c4400;border-bottom:1px solid #e6cf85;padding:8px 16px;font-size:.9rem;text-align:center}
/* barra da marca */
.bar{background:var(--marinho);color:#fff}
.bar .in{display:flex;align-items:center;gap:12px;padding-top:10px;padding-bottom:10px}
.bar :focus-visible{outline-color:var(--ouro)}
.marca{display:flex;align-items:center;gap:10px;text-decoration:none;min-width:0}
.simbolo{width:40px;height:40px;flex:none;border-radius:8px;box-shadow:0 0 0 1px rgba(255,255,255,.18)}
.marca-t{display:grid;min-width:0}
.marca-n{font-family:var(--serif);font-weight:700;font-size:1.5rem;line-height:1.05;letter-spacing:-.01em;white-space:nowrap}
.marca-s{font-size:.78rem;color:#c8d2e1;letter-spacing:.02em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bar-acoes{margin-left:auto;display:flex;align-items:center;gap:6px}
.rede{display:grid;place-items:center;width:40px;height:40px;border-radius:8px;color:#dfe6f0}.rede:hover{color:var(--ouro)}
.news-btn{display:flex;align-items:center;gap:6px;min-height:44px;padding:0 14px;border-radius:999px;background:var(--ouro);color:#1d1503;font-weight:800;font-size:.9rem;text-decoration:none}
.news-btn:hover{background:#e4c57a}
.busca-btn{display:grid;place-items:center;flex:none;width:44px;height:44px;padding:0;border:1px solid #3a557e;border-radius:8px;background:none;color:#fff;cursor:pointer}
.busca-btn:hover{border-color:var(--ouro);color:var(--ouro)}.busca-btn[hidden]{display:none}
@media (max-width:760px){.rede{display:none}.news-btn span{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%%)}.news-btn{padding:0;width:44px;justify-content:center}}
@media (max-width:420px){.marca-s{display:none}.marca-n{font-size:1.3rem}.simbolo{width:36px;height:36px}}
/* menu das editorias, preso no topo */
.nav{position:sticky;top:0;z-index:20;background:var(--papel);border-bottom:1px solid var(--linha);box-shadow:0 1px 0 rgba(0,0,0,.02)}
.nav ul{display:flex;gap:2px;overflow-x:auto;scrollbar-width:none}
.nav ul::-webkit-scrollbar{display:none}
.nav a{display:flex;align-items:center;min-height:48px;padding:0 12px;white-space:nowrap;text-decoration:none;font-weight:700;font-size:.93rem;color:var(--texto);border-bottom:3px solid transparent}
.nav a:hover{border-bottom-color:var(--ouro)}.nav a[aria-current]{color:var(--marinho);border-bottom-color:var(--marinho)}
.nav .casa{min-width:44px;justify-content:center}.nav .casa .ic{width:20px;height:20px}
:where(html){scroll-padding-top:calc(var(--nav-h,49px) + 12px)}
body .cats{top:var(--nav-h,49px)}
/* trilha */
.trilha{min-width:0;max-width:100%%}.trilha ol{display:flex;align-items:center;min-width:0;font-size:.85rem;color:var(--suave)}
.trilha li{display:flex;align-items:center;white-space:nowrap}
.trilha li+li::before{content:"›";content:"›" / "";margin:0 8px;color:var(--suave)}
.trilha a{color:var(--link);font-weight:700;text-decoration:none;padding:4px 0}.trilha a:hover{text-decoration:underline}
.trilha li:last-child{display:block;min-width:0;overflow:hidden;text-overflow:ellipsis}
/* blocos, etiquetas e títulos de seção */
.bloco{background:var(--papel);border:1px solid var(--linha);border-radius:10px;padding:16px;min-width:0}
.h-sec{display:flex;align-items:baseline;justify-content:space-between;gap:10px;margin-bottom:14px;padding-top:10px;border-top:3px solid var(--c);
 font-family:var(--serif);font-weight:700;font-size:1.3rem;line-height:1.2;color:var(--tinta)}
.h-sec a{flex:none;display:inline-flex;align-items:center;min-height:24px;font-family:var(--mono);font-size:.72rem;text-transform:uppercase;letter-spacing:.06em;color:var(--c);font-weight:700;text-decoration:none}
.h-sec a:hover{text-decoration:underline}
.cat{display:inline-block;font-size:.72rem;font-weight:800;letter-spacing:.04em;text-transform:uppercase;border-radius:4px;padding:2px 7px;color:var(--c);background:var(--f);text-decoration:none}
a.cat{display:inline-flex;align-items:center;min-height:24px}a.cat:hover{text-decoration:underline}
.tipo{display:inline-block;font-size:.72rem;font-weight:800;letter-spacing:.04em;text-transform:uppercase;border-radius:4px;padding:2px 7px;color:#fff;background:#3d4653}
.tipo.t-opiniao{background:var(--marinho)}.tipo.t-analise{background:#4a5b70}.tipo.t-explicativo{background:#7b5410}
.tipo.t-patrocinado{background:#fff4d6;color:#6b4a00;outline:1px solid #e0c27a}
.meta{font-family:var(--mono);font-size:.72rem;text-transform:uppercase;letter-spacing:.05em;color:var(--suave)}
.credito{font-size:.76rem;color:var(--suave)}
.titulo{font-family:var(--serif);font-weight:700;letter-spacing:-.01em;text-wrap:balance;color:var(--tinta)}
/* home */
.edicao{padding-top:14px;color:var(--ouro-esc)}
.grade{display:grid;gap:18px;padding-top:10px;padding-bottom:40px}
.lado{display:contents}
.manchete{order:1}.pub-topo{order:2}.ultimas{order:3}.destaques{order:4}.agenda{order:5}.faixas{order:6}.opinioes{order:7}.cta-news{order:8}
@media (min-width:900px){
 .grade{grid-template-columns:minmax(0,1fr) 340px;grid-template-areas:"manchete lado" "pubtopo lado" "ultimas lado" "faixas faixas" "opinioes cta" ;align-items:start}
 .lado{display:grid;gap:18px;grid-area:lado;align-content:start}
 .manchete{grid-area:manchete}.pub-topo{grid-area:pubtopo}.ultimas{grid-area:ultimas}.faixas{grid-area:faixas}.opinioes{grid-area:opinioes}.cta-news{grid-area:cta}
}
.manchete{padding:0;overflow:hidden;border-top:4px solid var(--c)}
.manchete a{display:grid;text-decoration:none}
.manchete figure{background:#e9e6df}
.manchete img{width:100%%;aspect-ratio:16/9;object-fit:cover}
.manchete .txt{padding:16px 18px 20px;display:grid;gap:10px;align-content:start}
.manchete .etq{display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.manchete .m-tit{font-size:clamp(1.6rem,4vw,2.35rem);line-height:1.12}
.manchete a:hover .m-tit{text-decoration:underline;text-decoration-thickness:2px;text-underline-offset:4px}
.manchete p.lf{color:var(--texto);font-size:1.05rem;max-width:62ch}
@media (min-width:640px){.manchete a{grid-template-columns:54%% 1fr}.manchete img{aspect-ratio:auto;height:100%%;min-height:320px}.manchete .txt{padding:22px 24px;align-content:center}}
.lista-n li{border-top:1px solid var(--linha)}.lista-n li:first-child{border-top:0}
.lista-n a{display:grid;grid-template-columns:96px 1fr;gap:14px;padding:14px 0;text-decoration:none}
.lista-n li:first-child a{padding-top:0}
.lista-n img,.lista-n .sem{width:96px;height:72px;border-radius:6px;object-fit:cover;background:var(--f)}
.lista-n .sem{display:grid;place-items:center;color:var(--c)}
.lista-n .l-tit{font-family:var(--serif);font-size:1.12rem;line-height:1.25;font-weight:700;margin:4px 0 3px;text-wrap:balance}
.lista-n a:hover .l-tit{text-decoration:underline}
.lista-n p{font-size:.9rem;color:var(--texto);display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.lista-n .sem-img{grid-template-columns:1fr}
.destaques ol{counter-reset:d}.destaques li{counter-increment:d;border-top:1px solid var(--linha)}.destaques li:first-child{border-top:0}
.destaques li a{display:grid;grid-template-columns:30px 1fr;gap:8px;padding:10px 0;text-decoration:none}
.destaques li a::before{content:counter(d);font-family:var(--serif);font-weight:700;font-size:1.5rem;line-height:1.1;color:var(--ouro-esc)}
.destaques b{display:block;font-size:.97rem;line-height:1.3}.destaques a:hover b{text-decoration:underline}
.agenda li{display:grid;grid-template-columns:62px 1fr;gap:12px;padding:10px 0;border-top:1px solid var(--linha);font-size:.92rem}
.agenda li:first-child{border-top:0;padding-top:0}
.agenda .q{display:grid;place-items:center;align-content:center;height:58px;border-radius:8px;background:var(--f);color:var(--c);font-weight:800;line-height:1.05;text-align:center}
.agenda .q b{font-size:1.35rem}.agenda .q small{font-size:.7rem;text-transform:uppercase;letter-spacing:.05em}
.agenda .d{display:block;color:var(--suave);font-size:.84rem}.agenda a{font-weight:800;text-decoration:none}.agenda a:hover{text-decoration:underline}
.agenda .prev{font-size:.72rem;font-weight:800;color:var(--ouro-esc);text-transform:uppercase;letter-spacing:.04em}
.vazio{color:var(--suave);font-size:.95rem}
.faixas{display:grid;gap:18px}
.faixa .cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
@media (min-width:760px){.faixa .cards{grid-template-columns:repeat(4,minmax(0,1fr))}}
.mini a{display:grid;gap:8px;text-decoration:none}
.mini .ci{position:relative;display:block;aspect-ratio:16/10;border-radius:6px;overflow:hidden;background:var(--f)}
.mini img{position:absolute;inset:0;width:100%%;height:100%%;object-fit:cover}
.mini .sem{position:absolute;inset:0;display:grid;place-items:center;color:var(--c)}.mini .sem .ic{width:34px;height:34px}
.mini .tipo{justify-self:start}.mini .t{font-family:var(--serif);font-weight:700;font-size:1.02rem;line-height:1.25;text-wrap:balance}.mini a:hover .t{text-decoration:underline}
.opinioes li{border-top:1px solid var(--linha);padding:12px 0}.opinioes li:first-child{border-top:0;padding-top:0}
.opinioes a{text-decoration:none;display:grid;gap:3px}.opinioes .t{font-family:var(--serif);font-weight:700;font-size:1.1rem;line-height:1.25}
.opinioes a:hover .t{text-decoration:underline}.opinioes .quem{font-size:.86rem;color:var(--suave)}
.cta-news{background:var(--marinho);color:#fff;border-color:var(--marinho);display:grid;gap:10px;align-content:start}
.cta-news .h-sec{color:#fff;border-top-color:var(--ouro)}.cta-news p{color:#d5dde9}
.cta-news a.btn{justify-self:start}
.btn{display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:10px 18px;border-radius:999px;background:var(--ouro);color:#1d1503;font-weight:800;text-decoration:none}
.btn:hover{background:#e4c57a}
.cta-news :focus-visible{outline-color:var(--ouro)}
/* arquivo e editorias */
.arq{display:grid;gap:16px;padding-top:16px;padding-bottom:40px}
.arq-topo{display:grid;gap:6px}.arq-topo h1{font-family:var(--serif);font-size:clamp(1.8rem,4.5vw,2.5rem);line-height:1.1;font-weight:700;border-top:4px solid var(--c);padding-top:12px}
.arq-topo p{color:var(--texto);max-width:70ch}
.cats{display:flex;flex-wrap:wrap;gap:8px}.cats[hidden]{display:none}
.cats button{font:inherit;font-size:.86rem;font-weight:700;min-height:40px;padding:4px 14px;border-radius:999px;border:1px solid var(--linha);background:var(--papel);color:var(--tinta);cursor:pointer}
.cats button small{margin-left:6px;font-weight:600;color:var(--suave);font-variant-numeric:tabular-nums}
.cats button:hover{border-color:var(--marinho)}.cats button[aria-pressed="true"]{background:var(--marinho);border-color:var(--marinho);color:#fff}.cats button[aria-pressed="true"] small{color:#c8d2e1}
.grade-n{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
@media (min-width:600px){.grade-n{grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}}
@media (min-width:1000px){.grade-n{grid-template-columns:repeat(4,minmax(0,1fr))}}
.card-n[hidden]{display:none}
.card-n a{display:flex;flex-direction:column;height:100%%;background:var(--papel);border-radius:10px;overflow:hidden;text-decoration:none;border:1px solid var(--linha);border-top:4px solid var(--c)}
.card-n a:hover{border-color:var(--c)}.card-n a:hover .t{text-decoration:underline}
.card-n .ci{position:relative;display:block;aspect-ratio:16/10;overflow:hidden;background:var(--f)}.card-n img{position:absolute;inset:0;width:100%%;height:100%%;object-fit:cover}
.card-n .sem{position:absolute;inset:0;display:grid;place-items:center;color:var(--c)}.card-n .sem .ic{width:40px;height:40px}
.card-n .cb{display:grid;gap:6px;align-content:start;padding:10px 12px 14px;flex:1}
.card-n .etq{display:flex;flex-wrap:wrap;gap:4px}
.card-n .t{font-family:var(--serif);font-size:1.05rem;line-height:1.25;font-weight:700;text-wrap:balance}
.card-n .resumo{font-size:.86rem;color:var(--texto);display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
@media (max-width:599px){.card-n .resumo{display:none}.card-n .t{font-size:.98rem}.card-n .cb{padding:9px 10px 12px}}
.paginas{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-top:8px;font-weight:700}.paginas a{color:var(--link)}.paginas span{color:var(--suave);font-size:.9rem}
/* matéria */
.materia{max-width:760px;margin:0 auto;padding-top:18px;padding-bottom:48px;display:grid;gap:16px}
.materia .cab{display:grid;gap:10px}
.materia .etq{display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.materia h1{font-family:var(--serif);font-size:clamp(1.85rem,5vw,2.7rem);line-height:1.12;font-weight:700;letter-spacing:-.015em;text-wrap:balance}
.materia .lf{font-size:1.15rem;line-height:1.5;color:var(--texto)}
.assinatura{display:flex;flex-wrap:wrap;gap:4px 14px;align-items:center;padding-top:10px;border-top:1px solid var(--linha);font-size:.9rem;color:var(--suave)}
.assinatura a{display:inline-flex;align-items:center;min-height:24px;color:var(--link);font-weight:700;text-decoration:none}.assinatura a:hover{text-decoration:underline}
.assinatura b{color:var(--tinta)}
.materia figure img{width:100%%;border-radius:8px;background:#e9e6df}
.materia figcaption{margin-top:6px}
.aviso-pat{display:grid;gap:4px;background:#fff8e6;border:1px solid #e9cf8c;border-left:4px solid #b98a1d;border-radius:8px;padding:12px 14px;font-size:.95rem;color:#4b3800}
.texto{display:grid;gap:16px;font-size:1.08rem;line-height:1.7;color:var(--texto)}
.texto .lide{font-weight:600;color:var(--tinta)}
.texto h2{font-family:var(--serif);font-size:1.45rem;line-height:1.25;color:var(--tinta);margin-top:8px}
.texto a{color:var(--link)}
.texto blockquote{border-left:4px solid var(--c);padding:4px 0 4px 16px}
.texto blockquote p{font-family:var(--serif);font-weight:700;font-size:1.22rem;line-height:1.4;color:var(--tinta)}
.texto blockquote footer{margin-top:6px;font-size:.88rem;color:var(--suave)}
.texto blockquote footer a{color:var(--link)}
.analise{background:#f3f6fa;border:1px solid #d9e2ee;border-left:4px solid var(--marinho2);border-radius:8px;padding:14px 16px;display:grid;gap:6px}
.analise .r{font-family:var(--mono);font-size:.72rem;text-transform:uppercase;letter-spacing:.06em;color:var(--marinho2);font-weight:700}
.analise p{color:var(--tinta)}
.biblia{background:#fbf6ea;border:1px solid #ecdcb5;border-radius:8px;padding:14px 16px;display:grid;gap:8px}
.biblia h2{font-family:var(--serif);font-size:1.1rem}.biblia li{padding-left:18px;position:relative}.biblia li::before{content:"";position:absolute;left:2px;top:.65em;width:7px;height:7px;border-radius:50%%;background:#b98a1d}
.biblia small{color:var(--suave)}
.faq details{border-top:1px solid var(--linha);padding:4px 0}.faq details:first-of-type{border-top:0}
.faq summary{cursor:pointer;min-height:44px;display:flex;align-items:center;font-weight:800;font-size:1.02rem}
.faq details p{padding:0 0 10px;color:var(--texto)}
.afiliados{font-size:.93rem}.afiliados p{color:var(--suave);margin-bottom:8px}.afiliados li{margin:6px 0}.afiliados a{color:var(--link);font-weight:700}
.transp{display:grid;gap:14px;background:#f8f7f3}
.transp h2,.relac h2,.faq h2,.afiliados h2,.correcoes h2{font-family:var(--serif);font-size:1.2rem;margin-bottom:6px}
.transp dl{display:grid;gap:10px;font-size:.93rem}.transp dt{font-weight:800}.transp dd{color:var(--texto)}
.fontes li{margin:6px 0;font-size:.93rem}.fontes a{color:var(--link)}.fontes span{color:var(--suave);font-size:.82rem}
.correcoes{border-left:4px solid #b3261e}.correcoes li{margin:6px 0;font-size:.95rem}.correcoes time{font-weight:800}
.tags{display:flex;flex-wrap:wrap;gap:6px}.tags li{font-size:.82rem;padding:3px 10px;border-radius:999px;background:#ece9e1;color:var(--texto)}
.relac li{border-top:1px solid var(--linha)}.relac li:first-child{border-top:0}
.relac a{display:block;padding:10px 0;color:var(--link);font-weight:700;text-decoration:none}.relac a:hover{text-decoration:underline}
/* autor e páginas institucionais */
.doc{max-width:760px;margin:0 auto;padding-top:18px;padding-bottom:48px;display:grid;gap:16px}
.doc h1{font-family:var(--serif);font-size:clamp(1.8rem,4.5vw,2.4rem);line-height:1.12;font-weight:700}
.doc .lf{font-size:1.1rem;color:var(--texto)}
.doc section h2{font-family:var(--serif);font-size:1.3rem;margin-bottom:8px}
.doc .corpo{display:grid;gap:12px;color:var(--texto)}.doc .corpo a{color:var(--link)}
.doc .corpo ul{list-style:disc;padding-left:22px;display:grid;gap:6px}
.equipe li{border-top:1px solid var(--linha);padding:12px 0}.equipe li:first-child{border-top:0}.equipe a{color:var(--link);font-weight:800}
.pend{background:#fff3cd;border:1px solid #e6cf85;color:#5c4400;border-radius:8px;padding:12px 14px}
/* formulários */
.form-pc{display:grid;gap:12px}
.form-pc label{display:grid;gap:4px;font-weight:700;font-size:.92rem}.form-pc small{font-weight:600;color:var(--suave)}
.form-pc input,.form-pc textarea{font:inherit;font-size:16px;font-weight:400;padding:10px 12px;border:1px solid #c9c5ba;border-radius:8px;background:#fff;color:var(--tinta)}
.form-pc textarea{resize:vertical;min-height:120px}
.form-pc fieldset{border:1px solid var(--linha);border-radius:8px;padding:10px 12px;margin:0}.form-pc legend{font-weight:700;font-size:.92rem;padding:0 4px}
.form-pc .ops{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:2px 10px}
.form-pc .op,.form-pc .consent{display:flex;gap:10px;align-items:flex-start;font-weight:500;min-height:44px;padding:8px 0}
.form-pc .op input,.form-pc .consent input{width:24px;height:24px;margin:2px 0 0;flex:none}
.form-pc .consent a{color:var(--link)}
.form-pc button{justify-self:start;min-height:44px;padding:10px 22px;border-radius:999px;border:0;background:var(--marinho);color:#fff;font:inherit;font-weight:800;cursor:pointer}
.form-pc button:disabled{opacity:.6}
.f-st{font-weight:700;font-size:.93rem}.f-st:empty{display:none}.f-st.ok{color:#1b6b3f}.f-st.erro{color:#a3223a}
.form-off{color:var(--texto)}.form-off a{color:var(--link);font-weight:700}
.isca{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}
.cta-news .form-pc label,.cta-news .form-pc legend{color:#fff}.cta-news .form-pc small{color:#c8d2e1}.cta-news .form-pc .consent a{color:var(--ouro)}
.cta-news .form-pc button{background:var(--ouro);color:#1d1503}.cta-news .f-st.ok{color:#9be0b8}.cta-news .f-st.erro{color:#ffb3c0}
.cta-news .form-pc fieldset{border-color:#3a557e}.cta-news .form-off{color:#d5dde9}
/* publicidade: altura reservada antes de carregar (CLS zero) */
.pub{display:grid;gap:4px;justify-items:center;min-width:0}
.pub-rot{font-family:var(--mono);font-size:.66rem;letter-spacing:.08em;text-transform:uppercase;color:var(--suave)}
.pub-in{width:100%%;min-height:var(--hm,0);display:grid;place-items:center;overflow:hidden}
@media (min-width:760px){.pub-in{min-height:var(--hd,0)}}
.pub.so-pc{display:none}@media (min-width:900px){.pub.so-pc{display:grid}}
.pub-casa{display:grid;gap:6px;justify-items:center;align-content:center;text-align:center;width:100%%;height:100%%;min-height:inherit;padding:14px;border:1px dashed #c9c5ba;border-radius:10px;background:#faf9f6;text-decoration:none}
.pub-casa b{font-family:var(--serif);font-size:1.05rem}.pub-casa span{font-size:.86rem;color:var(--suave)}.pub-casa i{font-style:normal;font-weight:800;color:var(--link);font-size:.9rem}
.pub-casa:hover{border-color:var(--marinho)}
/* rodapé */
footer{background:var(--marinho);color:#dfe6f0;margin-top:24px;font-size:.9rem}
footer .in{display:grid;gap:22px;padding-top:28px;padding-bottom:28px}
@media (min-width:760px){footer .in{grid-template-columns:1.4fr 1fr 1fr 1fr}}
footer .marca-n{font-size:1.35rem;color:#fff}.rod-marca p{margin-top:8px;color:#c8d2e1;max-width:40ch}
.rod-h{font-family:var(--mono);font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;color:var(--ouro);margin-bottom:8px}
footer li a,footer .pref-priv{display:inline-flex;align-items:center;min-height:32px;color:#dfe6f0;text-decoration:none}
footer li a:hover,footer .pref-priv:hover{color:#fff;text-decoration:underline}
footer .pref-priv{font:inherit;background:none;border:0;padding:0;cursor:pointer}.pref-priv[hidden]{display:none}
.rod-legal{grid-column:1/-1;border-top:1px solid #2b456d;padding-top:14px;color:#aebbd0;font-size:.82rem}
footer :focus-visible{outline-color:var(--ouro)}
/* compartilhar e barra de leitura (portados) */
.cpw{position:relative;display:inline-block}
.cp{display:inline-flex;align-items:center;justify-content:center;gap:8px;line-height:1.2;min-height:44px;margin:0;padding:10px 20px;border-radius:999px;border:0;background:var(--marinho);color:#fff;font:inherit;font-size:.95rem;font-weight:800;text-decoration:none;cursor:pointer}
.cp:hover{background:var(--marinho2);color:#fff}.cp .ic{width:19px;height:19px}
.cp-menu{position:absolute;z-index:30;top:calc(100%% + 8px);left:0;min-width:200px;display:grid;gap:2px;padding:6px;border-radius:12px;background:#fff;border:1px solid var(--linha);box-shadow:0 10px 30px rgba(0,0,0,.2)}
.cp-menu[hidden]{display:none}.cp-menu.sobe{top:auto;bottom:calc(100%% + 8px)}.cp-menu.dir{left:auto;right:0}
.cp-op{display:flex;align-items:center;gap:10px;min-height:44px;padding:8px 12px;border:0;border-radius:8px;background:none;color:var(--tinta);font:inherit;font-size:.95rem;font-weight:700;text-align:left;text-decoration:none;cursor:pointer}
.cp-op:hover,.cp-op:focus-visible{background:#f1efe9}.cp-op .ic{width:20px;height:20px}.cp-op.zap-op .ic{color:#157a43}.cp-op.tg-op .ic{color:#2481cc}
.cp-st{position:absolute;z-index:30;top:calc(100%% + 8px);left:0;white-space:nowrap;padding:6px 12px;border-radius:8px;background:var(--tinta);color:#fff;font-size:.85rem;font-weight:700}.cp-st:empty{display:none}
.barra-lt .cp-st{top:auto;bottom:calc(100%% + 8px)}
.convite{display:flex;align-items:center;justify-content:space-between;gap:12px 20px;flex-wrap:wrap}
.convite .cv-t{font-family:var(--serif);font-weight:700;font-size:1.15rem}.convite .cv-s{margin-top:2px;font-size:.92rem;color:var(--suave)}
.barra-lt{position:fixed;z-index:25;left:50%%;bottom:calc(12px + env(safe-area-inset-bottom));display:flex;align-items:center;gap:4px;padding:5px;border-radius:999px;background:var(--marinho);border:1px solid #2b456d;box-shadow:0 8px 24px rgba(0,0,0,.25);transform:translate(-50%%,0);transition:transform .25s ease,opacity .25s ease}
.barra-lt.fora{transform:translate(-50%%,calc(100%% + 24px));opacity:0;pointer-events:none}
.lt-b{display:inline-flex;align-items:center;gap:7px;min-height:44px;padding:8px 14px;border:0;border-radius:999px;background:none;color:#e9eef5;font:inherit;font-size:.9rem;font-weight:700;text-decoration:none;cursor:pointer}
.lt-b:hover{background:var(--marinho2);color:#fff}.lt-b .ic{width:20px;height:20px}
.barra-lt .lt-b.curtir{border:0;color:#e9eef5;background:none}.barra-lt .lt-b.curtir[aria-pressed=true]{color:#ff8fa3}.lt-b.curtir[aria-pressed=true] .ic{fill:currentColor}
.barra-lt .cp{min-height:44px;padding:8px 16px;font-size:.9rem;background:var(--marinho2)}
.lt-news{display:inline-flex;align-items:center;justify-content:center;gap:6px;min-width:44px;min-height:44px;padding:0 14px;border-radius:999px;background:var(--ouro);color:#1d1503;font-size:.9rem;font-weight:800;text-decoration:none}
.lt-news .ic{width:20px;height:20px}
.barra-lt :focus-visible{outline-color:var(--ouro)}
@media (max-width:479px){.lt-b span,.lt-news span{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%%);white-space:nowrap}.lt-news{padding:0}}
@media print{.barra-lt,.nav,.pub,.priv{display:none}}
/* curtidas e comentários (portados) */
.interacoes{display:grid;gap:14px}.interacoes[hidden]{display:none}.interacoes h2{font-family:var(--serif);font-size:1.2rem}
.curtir-l{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.curtir{display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:8px 18px;border-radius:999px;border:2px solid #a3223a;background:#fff;color:#a3223a;font:inherit;font-weight:800;cursor:pointer}
.curtir .ic{width:22px;height:22px}.curtir[aria-pressed=true]{background:#a3223a;color:#fff}.curtir[aria-pressed=true] .ic{fill:currentColor}
.curtir .n{font-variant-numeric:tabular-nums}.curtir-dica{font-size:.9rem;color:var(--suave)}
.coms{display:grid;gap:10px}.coms li{background:#faf9f6;border:1px solid var(--linha);border-radius:10px;padding:12px 14px}
.com-quem{font-size:.92rem}.com-quem time{color:var(--suave);font-size:.8rem;margin-left:6px}.com-txt{margin-top:4px;white-space:pre-wrap}.coms-vazio{color:var(--suave)}
.com-form{display:grid;gap:10px;border-top:1px solid var(--linha);padding-top:14px}
.com-form label{display:grid;gap:4px;font-weight:700;font-size:.9rem}.com-form small{font-weight:600;color:var(--suave)}
.com-form input,.com-form textarea{font:inherit;font-size:16px;font-weight:400;padding:10px 12px;border:1px solid #c9c5ba;border-radius:8px;background:#fff;color:var(--tinta)}
.com-form textarea{resize:vertical;min-height:110px}
.com-form button{justify-self:start;min-height:44px;padding:10px 20px;border-radius:999px;border:0;background:var(--marinho);color:#fff;font:inherit;font-weight:800;cursor:pointer}
.com-form button:disabled{opacity:.6}.com-aviso{font-size:.82rem;color:var(--suave)}.com-aviso a{color:var(--link)}
.com-st{font-weight:700;font-size:.92rem}.com-st:empty{display:none}.com-st.ok{color:#1b6b3f}.com-st.erro{color:#a3223a}
/* consentimento (LGPD) */
.priv{position:fixed;z-index:40;left:12px;right:12px;bottom:calc(12px + env(safe-area-inset-bottom));max-width:620px;margin:0 auto;background:#fff;color:var(--tinta);border:1px solid var(--linha);border-radius:14px;box-shadow:0 14px 40px rgba(0,0,0,.25);padding:16px;display:grid;gap:10px}
.priv[hidden]{display:none}.priv h2{font-family:var(--serif);font-size:1.15rem}.priv p{font-size:.92rem;color:var(--texto)}.priv a{color:var(--link)}
.priv .ops{display:grid;gap:6px}.priv .ops[hidden]{display:none}.priv label{display:flex;gap:10px;align-items:flex-start;font-size:.92rem;min-height:40px}.priv input{width:24px;height:24px;flex:none;margin-top:1px}
.priv .acoes{display:flex;flex-wrap:wrap;gap:8px}
.priv button{min-height:44px;padding:8px 16px;border-radius:999px;border:1px solid var(--marinho);background:#fff;color:var(--marinho);font:inherit;font-weight:800;cursor:pointer}
.priv button.pri{background:var(--marinho);color:#fff}
/* celular: blocos de ponta a ponta (como no original) */
@media (max-width:599px){
 .grade{gap:10px;padding-bottom:24px}.materia,.doc{gap:10px;padding-top:12px;padding-bottom:24px}
 .grade>.bloco,.lado>.bloco,.faixas>.bloco,.materia>.bloco,.doc>.bloco{margin-left:-16px;margin-right:-16px;border-radius:0;border-left:0;border-right:0}
 .manchete .txt{padding:14px 16px 18px}.manchete .m-tit{font-size:1.7rem}
 .lista-n a{grid-template-columns:84px 1fr;gap:12px}.lista-n img,.lista-n .sem{width:84px;height:64px}
 .texto{font-size:1.06rem}
 footer li a{min-height:36px}
}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important;scroll-behavior:auto!important}}
"""


def css_editorias():
    """Uma classe por editoria (.ed-<slug>) que troca as variáveis --c (texto e filete) e --f (fundo da etiqueta)."""
    return "".join(f".ed-{x['slug']}{{--c:{x['cor']};--f:{x['fundo']}}}" for x in portal.EDITORIAS)


def css(pre):
    return BASE % {"pre": pre} + css_editorias()
