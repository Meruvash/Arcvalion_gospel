# Entrega: Portal Cristão

## 1. Arquitetura reutilizada

A mesma do projeto de origem, sem trocar por algo inferior: **conteúdo em JSON versionado → geradores Python →
HTML estático** com CSS inline e JavaScript mínimo, mais um **Cloudflare Worker + D1** para o que é dinâmico.
Generalizações: identidade, editorias, equipe e anúncios em `config/` (nada de domínio repetido no código), saída
em `publico/` construída no CI em vez de HTML versionado, e deploy por GitHub Actions.

## 2. Funcionalidades preservadas

Moldura comum (cabeçalho, menu preso com altura medida, trilha visível = BreadcrumbList, rodapé); manchete,
últimas, grade de cartões 2/3/4 colunas, arquivo paginado com filtro por editoria e estado na URL; página de
matéria com quadro de análise separado, fontes com data, "Leia também"; compartilhar (menu do celular, WhatsApp,
Copiar; Telegram novo); barra de leitura; curtidas e comentários moderados por IA com fila de duvidosos e painel;
busca local em diálogo acessível (`/`, Ctrl+K); imagens WebP responsivas e versão 1200×675 para o Discover;
cartões de prévia 1200×630 por matéria; JSON-LD num `@graph` só com o que é visível; sitemap geral e de notícias
(48 h); robots.txt aberto a buscadores e IAs; llms.txt; IndexNow; validador editorial que bloqueia o build;
avisos de vícios de texto; checagem de SEO; validação de UX em 6 larguras (rolagem, alvos de toque WCAG 2.2, foco);
`prefers-reduced-motion`; skills de pauta, verificação e comentários.

## 3. Adaptações

- **Identidade**: fundo claro de jornal, azul-marinho e ouro velho, títulos em Source Serif 4 (OFL), símbolo
  próprio (livro aberto com cruz), cores por editoria sem paleta partidária; peças da marca geradas da configuração.
- **Editorias**: as 7 pedidas, configuráveis (criar, ocultar, reordenar sem mexer no código), com página própria,
  faixa na home e cor; vitrine de Opinião.
- **Tipos de conteúdo**: notícia, análise, opinião, explicativo e patrocinado, cada um rotulado e com o schema.org
  correspondente (NewsArticle, AnalysisNewsArticle, OpinionNewsArticle, Article).
- **Revisão humana obrigatória** (o original publicava sem aprovação): `publicar.py` com revisor real; quadro
  "Como esta matéria foi feita" com fontes, revisor, uso de IA e link de correção.
- **Correções** com data, aviso na assinatura e `dateModified`; atualização e despublicação registradas.
- **Bloqueios editoriais novos**: fonte anônima genérica, caça-clique no título, citação sem autor/fonte, imagem de
  IA, patrocínio em matéria jornalística ou como manchete.
- **Monetização**: espaços configuráveis por posição e editoria com altura reservada (CLS zero), anúncio da casa,
  AdSense só após consentimento, `ads.txt`, métricas agregadas de impressão visível e clique por espaço, conteúdo
  patrocinado, links de afiliado, página Anuncie, formulários comercial e de eventos, agenda com divulgação paga.
- **LGPD**: banner só quando há algo opcional (GA4/AdSense), recusar com o mesmo peso de aceitar, Consent Mode v2
  negado por padrão, preferências no rodapé, newsletter e formulários com consentimento registrado, política de
  privacidade e termos (modelos a revisar juridicamente).
- **SEO/E-E-A-T**: NewsMediaOrganization com `publishingPrinciples`, `correctionsPolicy`, `masthead`; páginas de
  autor (ProfilePage + Person) só para pessoas reais; RSS; Event para agenda confirmada; FAQPage só visível.
- **Coleta de pauta** com fontes primárias brasileiras (Senado, Câmara, Planalto, Banco Central, Agência Brasil) e
  religiosas, respeitando robots.txt.

Ficaram de fora, por serem do domínio de jogos: resenhas, infográficos por IA, pauta de premiados, consulta Golden
Geek, calendário da Ludopedia, guias e prêmios.

## 4. Estrutura do repositório

```
config/          portal.json (identidade), editorias.json, equipe.json, anuncios.json, fontes.json
conteudo/        artigos/*.json, imagens/, paginas/*.json (institucionais), agenda.json
tools/           build.py, portal.py, layout.py, estilo.py, seo.py, imagens.py, anuncios.py, og.py,
                 novo.py, publicar.py, checar_seo.py, checar_isolamento.py, indexnow.py, gerar_marca.py,
                 editorial/ (checar.py, vicios.py, coletar.py), ux/ (validar.mjs, fluxos.mjs)
assets/          fontes/ (OFL), marca/, js/ (busca, interações, formulários, privacidade, anúncios)
worker/          src/index.js, schema.sql, wrangler.toml
exemplos/        conteúdo FICTÍCIO para prévia e testes (gerar.py)
tests/           test_portal.py, worker.test.mjs
.claude/skills/  pauta, revisao, comentarios
.github/workflows/  ci.yml, deploy.yml (manual)
docs/            esta entrega, auditoria, padrão e fluxo editorial, deploy, isolamento
```

## 5–8. Execução local, deploy, variáveis e domínio

Em `docs/DEPLOY.md`.

## 9. Checklist de SEO

- [x] URLs amigáveis e estáveis (`/noticias/<slug>/`, `/<editoria>/`), independentes de troca de editoria
- [x] Sitemap XML dinâmico com lastmod do conteúdo; sitemap de notícias (48 h, sem patrocinado)
- [x] robots.txt com sitemaps; opção de bloquear só robôs de treino de IA
- [x] Canonical e `og:url` iguais à URL; `max-image-preview:large`; noindex em páginas vazias
- [x] Title/description por matéria (`titulo_seo` opcional); Open Graph, Twitter Card, `article:*`
- [x] NewsArticle/Analysis/Opinion/Article, NewsMediaOrganization, BreadcrumbList, ProfilePage, Event, FAQPage
- [x] Autoria (Person real ou Redação), `datePublished` = `<time>` visível, `dateModified` só com mudança real
- [x] Política editorial, correções, expediente, quem somos, contato
- [x] Imagens responsivas (srcset WebP), 1200 px para o Discover, `width/height`, lazy fora da dobra
- [x] Um H1 por página, intertítulos H2, trilha visível, links internos ("Leia também", editorias, autores)
- [x] RSS, llms.txt, IndexNow, busca interna
- [x] Acessibilidade: contraste, foco visível, alvos ≥ 24 px, pular para o conteúdo, reduced motion
- [ ] Enviar sitemap ao Search Console e Bing (depende do domínio)
- [ ] Medir Core Web Vitals de campo (depende de tráfego real)

Nada disso garante indexação ou posição; não há marcação enganosa nem metadado falso.

## 10. Checklist de segurança e isolamento

- [x] Nenhum segredo, `.env` ou dado de produção copiado; `.gitignore` bloqueia credenciais
- [x] Recursos externos todos novos (banco, Worker, Turnstile, analytics, IndexNow)
- [x] CORS do Worker restrito à origem; Turnstile; campo-isca; limite por hora; IP só como hash diário
- [x] Rotas administrativas com token; e-mail de comentarista nunca publicado; métricas sem dado pessoal
- [x] Build de produção recusa configuração provisória e falta de revisor humano
- [x] Projeto original intacto (`docs/ISOLAMENTO.md`); auditoria automática no CI
- [ ] Revisão jurídica da privacidade e dos termos; nomeação do encarregado de dados (LGPD)

## 11. Pendências

- Ações externas aguardando aprovação: repositório GitHub, domínio, Pages, Cloudflare (Worker, D1, Turnstile,
  Analytics), Search Console, AdSense.
- Preencher responsável editorial, equipe real, e-mails, razão social e CNPJ.
- Provedor de envio da newsletter (o cadastro já funciona; o envio não).
- Fontes evangélicas com feed confiável para a coleta (convenções, alianças, missões): a lista atual tem órgãos
  públicos, CNBB, Pew, Lifeway (só manual: robots.txt proíbe) e Christianity Today.
- Primeiras matérias reais (nenhuma foi criada: nada pode ser inventado e tudo passa por revisão humana).
- Paginação por autor e por tag (hoje autor lista todas na própria página; tags não têm página, para evitar páginas rasas).

## 12. Próximas etapas recomendadas

1. Aprovar a criação do repositório e do domínio; configurar `config/portal.json` e `config/equipe.json`.
2. Escrever 10 a 15 matérias reais (incluindo explicativos evergreen de Fé e Bíblia) antes de divulgar.
3. Ligar Worker, Turnstile e Web Analytics; rodar o Deploy; enviar sitemaps; IndexNow.
4. Pedir AdSense com conteúdo real no ar; definir tabela comercial e mídia kit com as métricas dos espaços.
5. Integrar o provedor de newsletter com confirmação por e-mail (dupla confirmação).
6. Agendar as skills `pauta` (manhã) e `revisao` (fim do dia) como apoio, sempre com aprovação humana.
