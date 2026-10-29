---
name: resenha
description: Produz e publica sozinha a próxima resenha da Elite Boardgamers a partir da pauta de jogos premiados (pauta.json) — triagem de fotos oficiais, pesquisa com fontes, texto do site no padrão editorial (PADRAO_EDITORIAL.md), legenda e publicação no GitHub Pages, sem gerar imagem pela API e sem esperar aprovação. Use quando pedirem "/resenha", "próxima resenha", "resenha de <jogo>" ou "atualizar pauta".
---

# Resenha Elite Boardgamers

> **Regras desde 28/10/2026 (pedido do usuário):**
> 1. **Nenhuma imagem gerada pela API da OpenAI** (nem lote, nem refação): zero gasto. A resenha sai com as fotos oficiais da editora no topo e em "Como é jogar". `lote_openai.py enviar` e `gerar_infografico_openai.py` estão travados no código (`PERMITIR_IMAGEM_GPT=1` só com novo OK explícito do usuário). As etapas 3 a 5 (roteiro, geração e revisão do infográfico) não rodam mais; infográficos já publicados continuam nas páginas.
> 2. **Publicação automática**: a resenha que passa nas checagens (`checar_roteiro.py`, fotos liberadas, `publicar.py`) vai ao ar no mesmo dia, sem esperar aprovação. O usuário recebe só o resumo do que subiu.
> 3. **Verificação às 22h** (skill `verificacao`): confere o que foi publicado no dia e corrige sozinha o que estiver errado.

Só fazemos resenha de jogos premiados. **Quem escolhe o jogo é a pauta, não o usuário.**

- Argumento vazio ou "próxima": pegue os **4** jogos `na_fila` de menor `prioridade` em `pauta.json` **que passarem na triagem de fotos (etapa 1)** (uma série conta como um item). Jogo sem foto boa para o topo sai da fila (`sem_fotos`) e entra o próximo.
- Argumento com nome de jogo: só aceite se ele estiver em `pauta.json`; senão, avise que não está na pauta.
- Argumento "pauta": rode apenas a etapa 0.

Se o jogo tiver `serie` ou outros itens da mesma série na fila (versões, sequências, expansões), faça uma resenha comparativa única, como `nemesis/`, e marque todos como publicados ao final.

## Arquivos

- `conteudo/<slug>.json`: todo o conteúdo de uma resenha (ficha, prós, contras, fontes, o `roteiro` do infográfico e a `legenda` do Instagram). A página mostra os botões "Salvar na galeria" e "Legenda" (copia o campo `legenda`); sem esse campo o botão Legenda some.
- `tools/build_review.py conteudo/<slug>.json`: gera `<slug>/index.html` a partir do JSON. Não edite o HTML à mão.
- `tools/prompt_infografico.py conteudo/<slug>.json`: monta o prompt do infográfico a partir do `roteiro`.
- Ferramentas: busca na web funciona; Wikipedia abre via `curl`; Ludopedia e BoardGameGeek bloqueiam acesso automatizado (não contornar), então os números deles vêm da busca e são sinalizados na ficha.
- `modelos/referencia-*.jpg`: modelo visual dos infográficos antigos (geração desligada desde 28/10/2026).

- `pauta.json`: fila de jogos, regras e resenhas publicadas.
- `tools/fila_fotos.py`: triagem de fotos da pauta (`proximos`, `aprovado`, `sem-fotos`, `voltar`). Status `sem_fotos` = jogo fora da fila por falta de foto oficial boa para o topo, com data e editoras consultadas em `fotos`.
- `triagem/<slug>.json`: ficha mínima (nome e editoras) para buscar fotos antes de existir `conteudo/<slug>.json`.
- `resenhas/index.html`: lista de resenhas, gerada por `tools/build_lista.py` a partir de `pauta.json` (não editar à mão).
- Cada resenha mora em `<slug>/` com `index.html`, `infografico.webp` (até ~800 KB) e `capa.jpg` (800×800, até 250 KB, usada no og:image).

## Etapa 0: atualizar a pauta

Prêmios que contam (de `pauta.json > regras`): Golden Geek, Spiel des Jahres, Kennerspiel, Kinderspiel, As d'Or, Deutscher Spiele Preis e Prêmio Ludopedia. Entram vencedores e indicados que ficaram entre os 3 melhores da categoria. Excluir as categorias Aplicativo e Print & Play.

Para cada prêmio novo: colete de página oficial (Wikipedia só para conferir), registre `{premio, ano, categoria, colocacao, fonte}` e una com o jogo existente pelo nome oficial do BGG. Recalcule `prioridade`: vencedores antes de indicados; jogos-base antes de expansões; mais premiações primeiro; prêmio mais recente primeiro. Nunca inclua um jogo sem fonte do prêmio.

## Etapa 1: triagem de fotos (antes de pesquisar e escrever)

**Formato atual da resenha: foto oficial do jogo no topo** (modelo: `fate-of-the-fellowship/`, Sina da Sociedade; desde 28/10/2026 sem infográfico novo). Por isso a busca de fotos vem **antes** de qualquer pesquisa ou texto: só entra em produção o jogo que tem foto boa para o topo. Não gaste pesquisa, texto nem imagem com jogo que vai travar na publicação.

1. `python3 tools/fila_fotos.py proximos 8` lista os próximos da fila com slug e situação ("fotos ok", "fazer triagem"…).
2. Para cada candidato sem fotos, descubra a editora original e a nacional (busca rápida na web) e crie a ficha mínima: `python3 tools/imagens/robo.py triagem <slug> --jogo "<nome da pauta>" --editora "<Editora original>" --nacional "<Editora no Brasil>"` (grava `triagem/<slug>.json`).
3. Siga a skill `imagens`: `robo.py buscar <slug>`, revisão da folha de contato, `aprovar`, marcas `pessoas`/`texto` e `python3 tools/imagens/crivo.py --aplicar <slug>`. O resultado precisa ser **PUBLICA** (`"usar_na_pagina": true`), com uma foto de mesa, jogabilidade ou componentes no topo. Prefira no topo a foto mais aberta do jogo montado; ajuste `principal` e `jogar` no `fontes.json` se a escolha do crivo não for a melhor.
4. Se o crivo disser "FICA COM O INFOGRÁFICO", **não pare na primeira editora**: percorra todas as fontes da skill `imagens`, nesta ordem: editora original, **editoras licenciadas em outros países** (Santuário só ganhou foto de topo com a Capstone, a edição americana, porque a Feuerland só tinha foto de catálogo), editora nacional, premiações. Para cada site novo: `mapear <dominio>` e `buscar <slug> --url <página do jogo>`, depois `aprovar ... --forcar --nota "edição ..."`.
5. **Passou:** `python3 tools/fila_fotos.py aprovado "<jogo>" <slug>` grava o slug na pauta, e o jogo segue para a etapa 1b.
6. **Não passou em nenhuma fonte:** `python3 tools/fila_fotos.py sem-fotos "<jogo>" --obs "<editoras consultadas>"` tira o jogo da fila (mantém a prioridade) e **o próximo da fila entra no lugar**. Guarde o rascunho do pedido de kit de imprensa para a mensagem ao usuário. Quando chegarem fotos (kit de imprensa, `robo.py kit`), `fila_fotos.py voltar "<jogo>"` devolve o jogo ao mesmo lugar.

Faça commit de `triagem/`, `<slug>/fotos/`, `tools/imagens/editoras.json` e `pauta.json` (nunca `.cache/`). A trava confirma a regra: `publicar.py` recusa jogo sem fotos liberadas, e sem infográfico a foto é o topo da página. **Nunca use `--sem-fotos`**: jogo sem foto boa vira `sem_fotos` e o próximo da fila entra.

## Etapa 1b: pesquisa (só para quem passou na triagem)

Fontes, em ordem: página da editora; BoardGameGeek; Ludopedia (nota, nº de avaliações, peso, enquete de nº ideal, edição nacional); duas críticas especializadas (SU&SD, Dicebreaker, GamesRadar+, Tabletop Gaming, Ars Technica…); opiniões recorrentes de jogadores.

Regras inegociáveis:
- Todo número tem fonte e data da consulta. O que não for encontrado fica **"não confirmado nas fontes consultadas"**. Nunca estime.
- Separe FATO de OPINIÃO e atribua cada opinião à crítica que a fez.
- Guarde o link de cada fonte (a seção Fontes da página tem links).

A pesquisa precisa render também os campos do site que antes vinham do roteiro: `perfil` (6 barras), `passos` (5 passos de 15–30 palavras) e `como_resumo`, gravados direto no `conteudo/<slug>.json`.

Saída da pesquisa: FICHA (ano, autor, editora, jogadores, duração anunciada e relatada, nota Ludopedia com nº de votos, peso, melhor com, edição nacional, **premiações da pauta**); COMO FUNCIONA; DIFERENCIAIS entre versões; ELOGIOS com fonte; CRÍTICAS com fonte e gravidade (leve/moderada/grave); PARA QUEM É / NÃO É; FONTES.

## Etapa 2: texto da resenha

**Nome da editora:** a Galápagos hoje é a Asmodee (galapagosjogos.com.br redireciona para asmodee.com.br). No texto, escreva sempre "Asmodee", mesmo quando a fonte ainda disser Galápagos; os nomes das fontes ficam como a página citada os escreve.


O texto do site segue a segunda parte do **`PADRAO_EDITORIAL.md`** (exemplo completo: `conteudo/gloomhaven.json`). Seções: abertura (`lede`), Como funciona (4–6 parágrafos), Como é jogar (`experiencia`), O que funciona muito bem e Pontos de atenção (5–7 itens de 30–70 palavras, com gravidade), Com quantos jogar (`jogadores`), Primeira partida, Edição nacional e preço, Expansões e versões (`versoes`), Se você gosta de… (`comparacoes`, ligando para as nossas resenhas), Para quem é / não é (4–5 cada), Veredito com selo (nível `selo` + `ressalva` quando houver, e perfil `melhor_para`; regras no PADRAO_EDITORIAL.md) e tagline, Prêmios, Ficha e Fontes (pelo menos 6). Tom direto e honesto, escrito para quem nunca jogou; opinião sempre com dono; nada além do que está na pesquisa. **Nas partes de opinião, siga "Opinião forte" do PADRAO_EDITORIAL.md** (desde 29/10/2026): tom inteligente, sarcástico, ácido e engraçado, com a estrutura de stand-up de Ricky Gervais mapeada lá; voz "a gente", uma tese por resenha, sarcasmo nascido do fato, nunca contra pessoas, e sem repetir bordões de uma resenha para outra (leia as 3 últimas publicadas antes de escrever); modelo: `conteudo/vantage.json`.

`python3 tools/checar_roteiro.py` confere o texto (e o roteiro, nas resenhas antigas que têm um); `publicar.py` se recusa a seguir se ele não passar. Ele também mostra `⚠️ vício de texto` (regra 7 do PADRAO_EDITORIAL.md): reescreva cada trecho apontado com um detalhe concreto do jogo antes de publicar.

## Etapas 3 a 6: desligadas (28/10/2026)

Roteiro do infográfico, geração pela OpenAI (lote ou síncrona), revisão do texto da imagem e aprovação em lote **não rodam mais**. Se existir `lotes/pendente.json` de antes da mudança (já pago), `lote_openai.py buscar` pode baixar as imagens: use o infográfico só se o texto dele bater com o `conteudo/<slug>.json` atual bloco por bloco; na dúvida, descarte (`rm <slug>/variacao-*.png`) e publique só com as fotos.

## Rotina das fotos (14:51 de Brasília, sessão agendada)

Na véspera, a tarefa "Fotos oficiais das resenhas do dia seguinte (15h)" faz a triagem de fotos (etapa 1) dos próximos da fila, até deixar **4 jogos com "fotos ok"** prontos para a rotina das 8h; quem não tiver foto boa vira `sem_fotos` e o seguinte é testado. Ela não pesquisa nem escreve resenha, só faz commit de `triagem/`, `<slug>/fotos/`, `tools/imagens/editoras.json` e `pauta.json` e avisa o usuário dos jogos que saíram da fila, com o pedido de kit de imprensa pronto.

## Rotina diária (07:55 de Brasília, sessão agendada): 4 resenhas no ar, sem aprovação

1. `git pull origin main`. Pegue os 4 próximos `na_fila` com "fotos ok" em `fila_fotos.py proximos` (faltando, faça a triagem da etapa 1; quem não passar vira `sem_fotos` e entra o seguinte).
2. Para cada um: etapa 1b (pesquisa) e etapa 2 (texto), com `perfil`, `passos`, `como_resumo` e `legenda` no JSON. Não escreva `roteiro`: sem ele, `python3 tools/checar_roteiro.py conteudo/<slug>.json` confere só o texto do site, e precisa passar.
3. Publique na hora (etapa 7) todos os que passaram, num único commit em `main` com push.
4. Resumo curto ao usuário: jogos publicados com link, selo e prêmio, os que saíram da fila (`sem_fotos`) com o pedido de kit de imprensa pronto, e as legendas do Instagram. Não peça aprovação.

Jogo que não fechar no dia (fonte faltando, checagem não passou) fica `em_producao` e é o primeiro do dia seguinte; nunca publique texto com número sem fonte para cumprir a cota.

## Etapa 7: publicação

1. Só se houver infográfico antigo aproveitável (`<slug>/variacao-1.png`): `python3 tools/salvar_imagem.py <slug>`. Sem ele, pule.
2. `python3 tools/build_review.py conteudo/<slug>.json` gera `<slug>/index.html` com a foto oficial no topo e refaz a `<slug>/capa.jpg` a partir dela (ver "Fotos oficiais na página" em `PADRAO_EDITORIAL.md`).
3. `python3 tools/publicar.py conteudo/<slug>.json` confere se há fotos oficiais liberadas (`usar_na_pagina`; ver etapa 1), marca o jogo como `publicado` em `pauta.json` e regera `resenhas/index.html` inteira (`tools/build_lista.py`) e todas as páginas de resenha, para o bloco "Continue lendo" incluir a nova, e a página inicial (bloco Últimas resenhas, via `tools/build_home.py`). Depois, `node tools/capa_resenhas.js` refaz `resenhas/capa.jpg` (prévia do WhatsApp da página de resenhas) com o mosaico das capas.
4. Teste no Playwright em 390 px e 1200 px: sem erros de JS, sem rolagem horizontal e com a foto no topo.
5. Commit em `main` e push (sem esperar aprovação). Inclua no commit `sitemap.xml`, `sitemap-noticias.xml`, `robots.txt`, `llms.txt`, `404.html`, `img/`, `jogos-de-tabuleiro/`, `premios/` e `conteudo/sitemap_estado.json`, que os scripts regeram sozinhos. Depois que as páginas estiverem no ar (o GitHub Pages leva alguns minutos), rode `python3 tools/indexnow.py` para avisar Bing e outros buscadores; página que ainda não subiu fica para a próxima rodada. Se ele gravar `conteudo/indexnow_estado.json`, faça commit e push só desse arquivo (`IndexNow de <dd/mm/aaaa>`).
6. Grave a legenda do Instagram no campo `legenda` de `conteudo/<slug>.json` antes do passo 2 (é o texto que o botão "Legenda" copia) e entregue-a também na resposta: gancho de até 125 caracteres na 1ª linha, 3–4 linhas de resumo com o veredito e o prêmio, uma pergunta para comentários, "Resenha completa no link da bio" e 8–12 hashtags em PT e EN.
7. Escreva em `conteudo/chamadas.json` a `chamada` e a `pergunta` da resenha (PADRAO_EDITORIAL.md, "Chamadas para redes"). Depois da publicação, `python3 tools/divulgacao.py` atualiza o pacote de divulgação do dia (`divulgacao/<AAAA-MM-DD>.md`, com a resenha nova junto das notícias); commit e push dele, e mande ao usuário o link `https://github.com/Meruvash/Golden-Geek/blob/main/divulgacao/<AAAA-MM-DD>.md`.
