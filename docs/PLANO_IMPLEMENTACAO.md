# Plano de implementação: Portal Cristão

Base: auditoria em `docs/AUDITORIA_ELITE_BOARDGAMERS.md`. Princípio: **mesma arquitetura** (JSON → Python →
HTML estático; Worker Cloudflare para o que é dinâmico), mesmos componentes e padrões de qualidade, nova identidade,
nova arquitetura editorial e isolamento total.

## Fase 1. Projeto independente (local)

- Repositório Git novo (`main`), sem o histórico do original, em pasta separada.
- Nada é copiado por cima do original; os módulos reaproveitados são portados para o novo repositório.
- Identidade e domínio em **um único arquivo** (`config/portal.json`); nenhum `SITE = "https://…"` espalhado.
- Saída do build em `publico/` (não versionada) e deploy por GitHub Actions (só manual até aprovação).

## Fase 2. Núcleo reaproveitado (portado e generalizado)

| Original | Novo | Mudança |
|---|---|---|
| `layout.py` | `tools/layout.py` | menu, redes e rodapé vindos da configuração; espaço para newsletter e preferências de privacidade |
| `build_home.py` | `tools/build.py` | home de portal com faixas por editoria, páginas de editoria sempre presentes, opinião, agenda |
| `seo.py` | `tools/seo.py` | NewsArticle / AnalysisNewsArticle / OpinionNewsArticle / Article, autor `Person` real, `publishingPrinciples` |
| `build_sitemap.py` | `tools/build_sitemap.py` | lastmod a partir de `atualizado_em` do conteúdo; patrocinado fora do sitemap de notícias |
| `busca.py`/`busca.js` | idem | grupos por editoria |
| `imagens_resp.py`, `capas_grandes.py` | `tools/imagens.py` | igual (srcset WebP, 1200×675 para o Discover) |
| `og.py` + `og_cartoes.js` | idem | novo visual de cartão |
| `checar_noticia.py` | `tools/editorial/checar.py` | regras do jornalismo cristão (fontes, atribuição, revisão humana, rotulagem) |
| `vicios.py` | `tools/editorial/vicios.py` | + sensacionalismo e caça-clique |
| `checar_seo.py`, `verificar_site.py`, `indexnow.py`, `build_llms.py` | idem | domínio e chaves próprios |
| `worker/` | `worker/` | + newsletter, contato comercial/eventos, métricas agregadas de anúncios; recursos novos |
| `tools/ux/validar.mjs` | idem | rotas do novo portal |

## Fase 3. Arquitetura editorial

- Editorias em `config/editorias.json` (nome, slug, descrição, cor, ordem, visível). Criar, ocultar ou reordenar
  editoria não exige mudar código.
- Tipos de conteúdo: notícia, análise, opinião, explicativo (evergreen), patrocinado. Cada tipo com rótulo visível,
  schema.org correspondente e regras próprias.
- Fluxo `rascunho → revisao → publicado`, com `tools/publicar.py --revisor` (humano cadastrado em `config/equipe.json`).

## Fase 4. SEO, Discover e IA

Sitemap geral, sitemap de notícias (48 h), RSS (`/feed.xml`, usado pelo "Seguir" do Discover), robots.txt
configurável, llms.txt, IndexNow com chave nova, páginas de autor, política editorial e de correções,
imagem 1200 px para o Discover, `max-image-preview:large`, um H1, breadcrumb visível + JSON-LD.

## Fase 5. Monetização e LGPD

Espaços de anúncio configuráveis por posição e editoria com altura reservada (sem CLS), AdSense só após
consentimento, anúncio da casa ("Anuncie conosco"), conteúdo patrocinado rotulado, links de afiliado com
`rel="sponsored"` e aviso, newsletter/cadastro com consentimento explícito, formulário comercial e de eventos,
métricas agregadas por espaço, banner de consentimento, política de privacidade e termos.

## Fase 6. Rotinas de IA (skills) adaptadas

`pauta` (coleta e rascunhos, nunca publica), `revisao` (checagem de fatos e relatório para o editor),
`comentarios` (moderação com o mesmo crivo de cautela).

## Fase 7. Testes, isolamento e entrega

Testes unitários (Python `unittest`), build de produção e de exemplo, checagem de SEO, validação Playwright em 6
larguras, auditoria automática de isolamento (`tools/checar_isolamento.py`), conferência de que o original não mudou.

## Ações externas que dependem de aprovação (não executadas sem ela)

1. Criar o repositório remoto no GitHub e enviar o código.
2. Registrar/configurar o domínio e o DNS.
3. Ativar o GitHub Pages (fonte: GitHub Actions) e rodar o primeiro deploy.
4. Criar a conta/zona Cloudflare, o banco D1, o Worker e o Turnstile do novo portal.
5. Criar as propriedades de analytics e Search Console do novo domínio.
