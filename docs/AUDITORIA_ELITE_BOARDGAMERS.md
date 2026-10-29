# Auditoria do projeto original: Elite Boardgamers

Data: 29/10/2026. Repositório auditado: `meruvash/golden-geek` (branch `main`, commit `4a8fb0e`, 93 commits).
Domínio: eliteboardgamers.com.br. A auditoria só leu arquivos: **nada foi alterado no repositório original**
(hash do commit e da árvore de arquivos registrados antes e conferidos no fim; ver `docs/ISOLAMENTO.md`).

## 1. Framework, linguagem, dependências e versões

| Item | Situação |
|---|---|
| Tipo de site | Estático (HTML + CSS + JS mínimo), **sem framework e sem build step no servidor** |
| Geração | ~40 scripts Python 3 em `tools/` que leem JSON de `conteudo/` e escrevem o HTML final no próprio repositório |
| Python | 3.x; dependências: **Pillow** (imagens; 12.3 no ambiente), `requests` (coleta), biblioteca padrão |
| Node | 22.x, só para ferramentas: **Playwright** (cartões de prévia 1200×630, auditorias de UX) |
| JS no navegador | Vanilla, sem bibliotecas: `busca.js`, `interacoes.js` e scripts inline curtos gerados por `tools/layout.py` |
| Serviço dinâmico | Cloudflare Worker (`worker/src/index.js`) + banco D1 (SQLite) para curtidas e comentários |
| Não há | `package.json`, `requirements.txt`, testes unitários, CI do GitHub Actions |

## 2. Estrutura de diretórios e arquitetura

```
conteudo/            fonte da verdade: JSON (resenhas, notícias, home.json, lançamentos, estados de sitemap/IndexNow)
tools/               geradores (build_*.py), checagens (checar_*.py, verificar_site.py), coleta, imagens, IndexNow
  layout.py          cabeçalho, menu, trilha, rodapé, compartilhar, barra de leitura, comentários (marcação única)
  seo.py             JSON-LD (Organization, WebSite, NewsArticle/Article, BreadcrumbList)
  noticias/          coleta (feeds, Bluesky, Ludopedia), validador do padrão das notícias, verificação de edição nacional
  imagens/           robô que respeita robots.txt para buscar fotos oficiais de editoras
  comentarios/       instalação do Worker e moderação
  ux/                auditorias Playwright (rolagem lateral, alvos de toque, foco visível)
<slug>/              uma pasta por resenha (index.html, capa, fotos, infográfico)
noticias/<slug>/     páginas de notícias geradas; noticias/capas/ imagens
worker/              Worker Cloudflare (curtidas/comentários), schema.sql, wrangler.toml
.claude/skills/      rotinas de IA: noticias, resenha, verificacao, comentarios, imagens + pacotes genéricos de design/SEO
docs/, seo/          relatórios de UX e de SEO
```

Arquitetura: **JSON → Python → HTML estático versionado → GitHub Pages**. `_config.yml` exclui do Pages os
arquivos de trabalho (tools, conteudo, docs etc.).

## 3. Componentes reutilizáveis

- `layout.py`: `cabecalho()` (marca + redes + busca + menu fixo com `aria-current`), `trilha()` (breadcrumb visível
  igual ao JSON-LD), `rodape()`, `botao_compartilhar()` (Web Share no celular, menu WhatsApp/Copiar no computador),
  `convite_compartilhar()`, `barra_leitura()` (barra fixa que aparece ao rolar), `interacoes()` (curtir + comentários).
- `build_home.py`: manchete, lista de últimas, cartões da grade do arquivo (`cartao_nota`), paginação, chips de
  categoria com estado na URL, páginas de categoria, página de notícia, "Leia também" (relacionadas), 404,
  política editorial.
- `imagens_resp.py` (srcset WebP com hash), `capas_grandes.py` (versão 1200×675 para o Discover), `og.py` +
  `og_cartoes.js` (cartão de prévia por página), `busca.py` + `busca.js` (busca local em diálogo acessível),
  `build_sitemap.py`, `indexnow.py`, `build_llms.py`, `checar_seo.py`, `verificar_site.py`, `vicios.py`.

## 4. Design system

- **Cores** (CSS custom properties em `build_home.py`): moldura preta (`--ground #000`), cartões claros de leitura
  (`--paper #f4f5f7`), dourado da marca (`--gold #e3b23c`), link `#1f5fae`, WhatsApp `#157a43`; cores por categoria
  (prêmios, Brasil, mercado, financiamento) com par texto/fundo; "faixas" escuras coloridas alternando com blocos claros
  (referência declarada: The Verge).
- **Tipografia**: Public Sans (OFL, auto-hospedada, `font-display:swap`, preload), monoespaçada do sistema para
  linhas de data; títulos 800 com `text-wrap:balance` e `clamp()`.
- **Espaçamento**: contêiner `.in` de 1180 px com 16 px de margem; blocos com 16–20 px de respiro, raio 10 px.
- **Responsividade**: mobile-first; grade da home com `grid-template-areas` a partir de 900 px; grade do arquivo
  2/3/4 colunas (600/1000 px); no celular os blocos vão de ponta a ponta; `env(safe-area-inset-*)`.
- **Acessibilidade**: foco visível dourado de 3 px, alvos ≥ 44 px (mínimo 24 px, WCAG 2.2 2.5.8),
  `prefers-reduced-motion`, `aria-current`, diálogo de busca com combobox/listbox, um H1 por página.

## 5. Cabeçalho, menus, navegação, rodapé e páginas

Barra da marca (logo, Instagram, WhatsApp, lupa) + menu de seções preso no topo (rolagem horizontal no celular,
altura medida por JS para as barras presas abaixo). Rodapé com seções, guia, prêmios, política editorial e redes.
Páginas: home, arquivo `/noticias/` paginado (30/página), categorias, notícia, resenhas, lista de resenhas,
calendário de lançamentos, consulta Golden Geek, guias, prêmios, política editorial, 404.

## 6. Componentes de notícias, categorias e artigos

Notícia (`conteudo/noticias/<data>-<assunto>.json`): título, lide, "Por que importa" (análise assinada), "Em números"
(cada número com fonte), contexto, "No Brasil", "O que diz a crítica" (citações atribuídas, "tradução livre"),
"Interessa a você se…/Pense duas vezes se…", "Nossa opinião" com selo, compartilhar, comentários, jogos citados,
"Leia também", fontes com data de consulta, "Por que esta notícia entrou" (pontuação do crivo).
Categorias **fixas no código** (`CATEGORIAS` em `build_home.py`, cores em `og.py` e no CSS).

## 7. Sistema de publicação e gerenciamento de conteúdo

Não há CMS: o conteúdo é JSON versionado, editado por rotinas de IA (skills) ou à mão, e o HTML é regerado pelos
scripts e enviado com commit/push na `main`. `build_home.py` **se recusa a publicar** nota fora do padrão
(`checar_noticia.py`). `publicado_em` vem do commit que criou o arquivo e é gravado no JSON.

## 8. Banco de dados, autenticação, APIs e integrações

- D1 `elite-interacoes` (tabelas `curtidas`, `comentarios`), Worker em `api.eliteboardgamers.com.br`, CORS restrito
  ao domínio, Turnstile anti-robô, IP só como hash diário com sal, limite de 5 comentários/hora, painel de moderação
  com senha (Bearer token).
- APIs externas: Ludopedia (`LUDOPEDIA_TOKEN`), Bluesky público, feeds RSS, OpenAI (geração de infográfico, travada
  por `PERMITIR_IMAGEM_GPT=1`), Cloudflare GraphQL (resumo de visitas), IndexNow.
- Sem autenticação de usuários finais.

## 9. Hospedagem, build e deploy

GitHub Pages servindo a raiz da `main` (`CNAME` = eliteboardgamers.com.br), build local/na rotina e commit do HTML
gerado. Worker publicado com `wrangler` por `tools/comentarios/instalar.py`. Sem CI.

## 10. SEO técnico

URLs amigáveis em pastas (`/noticias/<slug>/`), canonical e `og:url` iguais à URL, `max-image-preview:large`,
Open Graph + Twitter Card com dimensões, cartões de prévia por página com `?v=` de versão, JSON-LD num único
`@graph` (Organization, WebSite, NewsArticle, BreadcrumbList), proibição explícita de Review/AggregateRating/Product
falsos, `datePublished` igual ao `<time>` visível, `dateModified` só quando o conteúdo muda (registro por hash em
`sitemap_estado.json`), sitemap geral + **sitemap de notícias com as últimas 48 h**, robots.txt aberto, 404 com
caminhos absolutos, `checar_seo.py` validando tudo.

## 11. Otimização para buscadores e sistemas de IA

`llms.txt` gerado, robots.txt liberando robôs de IA, perguntas frequentes visíveis nas resenhas e guias,
IndexNow para Bing/Yandex, contagem de visitas vindas de assistentes de IA no resumo de visitas.

## 12. Analytics, Search Console e monitoramento

Cloudflare Web Analytics (sem cookies) em todas as páginas; arquivo de verificação do Google Search Console
(`google6eabfb67f89b80bc.html`); chave do IndexNow na raiz; `resumo_visitas.py` (API da Cloudflare);
`verificar_site.py --online` como monitor diário. Não usa Google Analytics.

## 13. Performance e Core Web Vitals

CSS inline por página (sem requisição de CSS), uma fonte com preload, imagens responsivas WebP com `srcset/sizes`,
`width/height` para evitar CLS, `fetchpriority="high"` na imagem da manchete, `loading="lazy"` no resto, busca
carregada só no primeiro uso, Turnstile só quando a pessoa começa a comentar, nenhum framework JS.

## 14. Automação editorial e uso de IA

Skills `.claude/skills/`: `noticias` (coleta em 3 rodadas, crivo por pontos, mínimo de 5 notas/dia, escrita no
padrão, publicação), `resenha`, `imagens` (robô respeitando robots.txt), `verificacao` (conferência noturna contra
as fontes, corrige sozinha), `comentarios` (IA aprova/reprova/encaminha duvidosos ao editor). Hook `PostToolUse`
dispara a busca de fotos. Validador de "vícios de texto" para evitar texto com cara de série.

## 15. Segurança e variáveis de ambiente

Nenhum segredo encontrado no repositório (varredura por padrões de chaves de API, tokens do GitHub, AWS, Slack e
chaves privadas). Estão versionados apenas identificadores públicos por natureza: token do Cloudflare Web Analytics,
site key do Turnstile, chave do IndexNow, ID da conta Cloudflare e `database_id` do D1. Segredos ficam no ambiente:
`LUDOPEDIA_TOKEN`, `OPENAI_API_KEY`, `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_API_TOKEN_COMENTARIOS`, `MODERACAO_SENHA`
(e, no Worker, `MODERACAO_TOKEN` e `TURNSTILE_SECRET` como secrets). Não há `.env` no repositório.

## Premissas editoriais implementadas no código e na documentação

1. **Nada inventado**: todo número precisa de fonte; o que não se confirma vira "não confirmado nas fontes consultadas".
2. Fontes com link **e data de consulta**, no mínimo duas por notícia (`checar_noticia.py`).
3. **Fato separado de opinião**: análise só em blocos rotulados ("Por que importa", "Nossa opinião"); opinião de
   terceiros sempre atribuída; citação literal só de frase lida na fonte.
4. Crivo editorial com eliminatórias (sem fonte primária, conteúdo pago, atraso, fora do tema) e pontuação pública.
5. Afirmações de ausência ("não saiu no Brasil") exigem verificação registrada; frases categóricas são bloqueadas.
6. Proibição de citar lojas de varejo no texto (evitar publicidade não declarada).
7. Foto obrigatória (≥ 500 px, com crédito), nunca imagem gerada por IA para notícia.
8. Lista de vícios de texto (adjetivos vazios, fórmulas) com avisos automáticos.
9. Dados estruturados só com o que está visível e é verdade.
10. Correções na própria página com linha "Correção em <data>".
11. **Desde 28/10/2026 a publicação é automática, sem aprovação humana**, com revisão noturna por IA.

> A premissa 11 é incompatível com a regra do novo portal ("conteúdo produzido com apoio de IA deve passar por
> revisão humana antes da publicação"). No Portal Cristão o fluxo foi invertido: a IA só cria rascunhos, e o
> build se recusa a publicar sem revisor humano registrado (ver `docs/FLUXO_EDITORIAL.md`).

## O que é específico do domínio de jogos (não migra)

Resenhas, infográficos e geração por OpenAI, pauta de jogos premiados, consulta Golden Geek, calendário da
Ludopedia, guias "melhores jogos para…", prêmios, verificação de edição nacional, robô de fotos de editoras,
critérios do crivo ligados a tabuleiro, selos "Vale a compra" etc.
