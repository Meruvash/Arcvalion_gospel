# Auditoria de isolamento

Data: 29/10/2026. Automatizada em `tools/checar_isolamento.py` (roda no CI e no deploy).

## Projeto original intacto

| Verificação | Antes | Depois |
|---|---|---|
| Commit (`git rev-parse HEAD`) | `4a8fb0eac166…` | `4a8fb0eac166…` |
| Índice do Git (sha256 de `git ls-files -s`) | `aef12d497119387e` | `aef12d497119387e` |
| Todos os arquivos (sha256 do conjunto) | `dd4058b0cafc2ab2` | `dd4058b0cafc2ab2` |
| `git status --porcelain` | vazio | vazio |

Nenhum comando de escrita, commit, push, deploy ou chamada a serviço do original foi executado.
O novo projeto vive em outra pasta, com `git init` próprio (sem histórico nem remote do original).

## Itens verificados

| Item | Resultado |
|---|---|
| Banco de produção do original | não usado: o Worker do portal exige um D1 novo (`database_id` a preencher) e outro nome de banco |
| Credenciais compartilhadas | nenhuma: nenhum segredo copiado; não há `.env`; segredos novos via `wrangler secret` |
| Projeto de analytics | nenhum identificador do original; tokens de analytics vazios até criar os do portal |
| Sitemap e canonical | gerados do `url` de `config/portal.json`; nenhuma URL do domínio antigo no site |
| Publicação no original | impossível pelo código: o portal só escreve em `publico*/` dentro da própria pasta (trava em `limpar_saida`) |
| Arquivos do original | intactos (tabela acima) |
| Recursos de produção sem configuração explícita | nenhum: API, Turnstile, AdSense, GA4 e domínio vazios por padrão; o build de produção recusa domínio provisório |
| Deploys existentes | não tocados; o deploy do portal é um workflow novo, só manual |
| Marca antiga | ausente do site gerado, do JS, do CSS, das configurações e das skills; só aparece na documentação da migração e em comentários Python que dizem de onde o código foi portado |
| Buckets e armazenamento | nenhum compartilhado: imagens ficam no próprio repositório; o D1 é novo |
| Identificadores do original (Turnstile, D1, conta Cloudflare, IndexNow, verificação Google, grupo de WhatsApp) | nenhum encontrado; a chave IndexNow do portal foi gerada nova |
| Remote do Git | nenhum (será o repositório novo, depois de aprovado) |

## O que precisa ser configurado do zero (externo)

Repositório GitHub, GitHub Pages, domínio e DNS, conta/zona Cloudflare (Worker, D1, Turnstile, Web Analytics),
Search Console e Bing Webmaster, GA4 (opcional), AdSense (depois de aprovado), provedor de e-mail da newsletter.
Passo a passo em `docs/DEPLOY.md`.
