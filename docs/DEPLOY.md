# Executar, publicar e configurar

## Rodar localmente

```bash
pip install -r requirements.txt          # Pillow
npm install && npx playwright install chromium   # opcional: cartões de prévia, peças da marca, testes de UX
python3 exemplos/gerar.py                # (re)gera o conteúdo FICTÍCIO da prévia
python3 tools/build.py --exemplo         # prévia com exemplos em publico-exemplo/ (noindex, faixa de aviso)
python3 -m http.server 8765 -d publico-exemplo   # abra http://localhost:8765
python3 tools/build.py                   # build real em publico/ (só matérias aprovadas)
```

Testes: `python3 -m unittest discover -s tests -v`, `node --test tests/worker.test.mjs`,
`python3 tools/checar_seo.py publico`, `python3 tools/checar_isolamento.py`,
`BASE=http://localhost:8765 node tools/ux/validar.mjs` e `node tools/ux/fluxos.mjs`.

## Antes do primeiro deploy (checklist)

1. `config/portal.json`: `url` (domínio real), `responsavel_editorial.nome`, `email_contato`, `email_comercial`,
   `email_correcoes`, `razao_social`, `cnpj`, redes. Trocar o nome do portal: `nome` e `slogan`, depois
   `python3 tools/gerar_marca.py` (logo e capa de compartilhamento).
2. `config/equipe.json`: pessoas reais, com pelo menos uma `"revisor": true`.
3. Revisão jurídica da Política de Privacidade e dos Termos (`conteudo/paginas/`), que são um modelo inicial.
4. `python3 tools/build.py --producao` precisa passar.

## Deploy do site (GitHub Pages)

1. Repositório próprio no GitHub → Settings → Pages → Source: **GitHub Actions**.
2. Actions → **Deploy** → Run workflow (é só manual; nenhum push publica sozinho). O workflow roda testes,
   isolamento, `build.py --producao`, `checar_seo.py` e grava o `CNAME` a partir de `config/portal.json`.
3. Depois de no ar: `python3 tools/indexnow.py` (Bing e outros) e envio do `sitemap.xml` no Search Console.

## Deploy do site (Cloudflare Pages, gratuito com repositório privado)

Escolhido em 29/10/2026: o repositório continua privado no GitHub e o Cloudflare Pages lê dele.

1. dash.cloudflare.com → Workers & Pages → Create → Pages → Connect to Git → autorize o GitHub só para o repositório do portal.
2. Configuração do build:
   - Production branch: `main`
   - Framework preset: None
   - Build command: `pip install -r requirements.txt && python3 tools/build.py --producao --sem-og`
   - Build output directory: `publico`
   - Variável de ambiente: `PYTHON_VERSION` = `3.12`
3. Para não publicar sem aprovação: em Settings → Builds & deployments, deixe **Automatic deployments** desligado
   até o lançamento e publique pelo botão "Retry deployment"/"Create deployment".
4. O build de produção falha de propósito enquanto faltarem domínio, responsável editorial, e-mail e revisor
   (`config/portal.json` e `config/equipe.json`).
5. Domínio: Custom domains → Set up a custom domain. Sem domínio próprio, o endereço `<projeto>.pages.dev`
   funciona: use-o como `url` em `config/portal.json`.

Os cartões de prévia (Playwright) não rodam no build da Cloudflare (`--sem-og`): a matéria usa a própria foto
como imagem de compartilhamento. O arquivo `CNAME` e o workflow Deploy do GitHub não são usados nesse caminho.

## Domínio

| Registro | Nome | Valor |
|---|---|---|
| A | @ | 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153 (GitHub Pages) |
| AAAA | @ | 2606:50c0:8000::153, 2606:50c0:8001::153, 2606:50c0:8002::153, 2606:50c0:8003::153 |
| CNAME | www | `<usuario>.github.io` |
| (Worker) | api | criado pela Cloudflare ao ligar `custom_domain` no `wrangler.toml` |

No GitHub: Settings → Pages → Custom domain → marque **Enforce HTTPS**. Confirme o domínio em
Settings → Pages → Verified domains (evita sequestro de subdomínio).

## Serviço de interações (comentários, newsletter, formulários, métricas de anúncio)

Tudo novo e separado: outra conta/zona Cloudflare (ou ao menos recursos novos), outro banco, outros segredos.

```bash
cd worker
npx wrangler d1 create portal-cristao-interacoes        # copie o database_id para wrangler.toml
npx wrangler d1 execute portal-cristao-interacoes --remote --file=schema.sql
npx wrangler secret put MODERACAO_TOKEN                  # senha longa (≥ 21 caracteres) do painel
npx wrangler secret put TURNSTILE_SECRET                 # do widget Turnstile criado para o novo domínio
# edite ORIGEM e a rota api.<domínio> em wrangler.toml, depois:
npx wrangler deploy
```

Depois, em `config/portal.json`: `interacoes.api` = `https://api.<domínio>` e `interacoes.turnstile` = site key.
Com a API vazia o site funciona igual, só sem comentários, curtidas e formulários online (viram link de e-mail).

Newsletter: o Worker guarda as inscrições com consentimento (data e texto aceito) e o link de descadastro
(`/v1/newsletter/sair?t=<token>`). O **envio** dos e-mails depende de um provedor (Brevo, Mailchimp, Amazon SES…):
exporte `GET /v1/admin/inscritos` ou integre o provedor; inclua o link de descadastro em cada mensagem.

## Variáveis e segredos (sem valores)

| Onde | Nome | Para quê |
|---|---|---|
| Worker (secret) | `MODERACAO_TOKEN` | painel e rotas administrativas |
| Worker (secret) | `TURNSTILE_SECRET` | anti-robô dos formulários |
| Worker (var) | `ORIGEM`, `NOME` | CORS e textos |
| Ambiente local (skill comentários) | `MODERACAO_SENHA` | mesma senha do `MODERACAO_TOKEN` |
| Ambiente local (deploy do Worker) | `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID` | wrangler, da conta do portal |
| `config/portal.json` (públicos) | `analytics.cloudflare_token`, `analytics.ga4_id`, `verificacao.google`, `verificacao.bing`, `interacoes.turnstile`, `indexnow_chave` | identificadores públicos por natureza |
| `config/anuncios.json` (público) | `adsense_cliente`, `adsense_slot` | AdSense, depois da aprovação da conta |

Nada disso vai para o repositório além dos identificadores públicos. `.env` e `.dev.vars` estão no `.gitignore`.

## Analytics, Search Console e AdSense

- Cloudflare Web Analytics (sem cookies): crie um site novo para o domínio e copie o token.
- Google Analytics 4 (opcional): propriedade nova; só carrega após consentimento (Consent Mode v2 com tudo negado por padrão).
- Search Console e Bing Webmaster: propriedade nova do domínio; código de verificação em `verificacao`.
- Google News / Discover: não há inscrição obrigatória; ajudam o sitemap de notícias, o RSS (`/feed.xml`),
  imagens de 1200 px, autoria clara e as páginas de política editorial. Nada garante indexação ou posição.
- AdSense: peça a aprovação com o site no ar e conteúdo real publicado; depois preencha `adsense_cliente` e os slots.
