---
name: estudo
description: Produz e publica os estudos bíblicos do portal (o equivalente das resenhas do Elite Boardgamers) — tema da pauta (conteudo/pauta_estudos.json), pesquisa do que dizem teólogos brasileiros de referência de cada lado, texto no padrão dos estudos (docs/PADRAO_EDITORIAL.md), obra de arte em domínio público, build e publicação automática. Rotina diária: 5 estudos no ar antes das 9h. Use quando pedirem "/estudo", "próximo estudo", "estudo de <passagem>", "estudos do dia" ou quando a tarefa agendada disparar.
---

# Estudo bíblico

Mesma estrutura da resenha do Elite, com a passagem no lugar do jogo e, no centro, **"O que dizem os teólogos"**: uma questão em que teólogos brasileiros de referência divergem, cada lado com o seu melhor argumento. Modelo da linha pentecostal: `conteudo/estudos/batismo-de-criancas-atos-2.json` (ajustado a pedido em 30/10/2026). Os de 1 Coríntios 13 e 1 Tessalonicenses 4 mostram o esqueleto, mas são anteriores à linha pentecostal.

Publicação automática (ordem do responsável editorial, 29/10/2026): o que passa em `tools/estudos/checar_estudo.py` vai ao ar com `python3 tools/publicar.py aprovar conteudo/estudos/<slug>.json --revisor anderson-pelicioni-de-castro --automatica`. A conferência humana é diária (skill `verificacao`).

## Rotina diária (tarefa agendada, 05:13 de Brasília): 5 estudos no ar antes das 9h

1. `git pull origin main`. Pegue os **5 primeiros `na_fila`** de `conteudo/pauta_estudos.json` e marque-os `em_producao`.
2. **Pesquisa em paralelo**: um subagente (Agent, general-purpose) por tema, todos na mesma mensagem, com o briefing da seção "Pesquisa" abaixo. Enquanto pesquisam, busque as 5 imagens.
3. Para cada pesquisa que voltar com **2 ou mais teólogos brasileiros por lado, com fonte lida**: escreva o JSON, confira as citações (seção "Citações"), rode o validador. Tema sem fontes suficientes vira `sem_fontes` (com `obs`), e o próximo `na_fila` entra no lugar, até completar 5 ou até 08:30.
4. Publique os que passaram (`publicar.py aprovar ... --automatica`), marque `publicado` e o `slug` na pauta, rode `python3 tools/build_home.py` e as checagens do CLAUDE.md, confira 1 estudo no Playwright em 390 px.
5. Commit único em `main` e push (antes do push, `git pull --rebase origin main`: a rotina de notícias também publica de manhã). Se faltar algum para 5, publique os prontos mesmo assim: nunca publique texto com fonte faltando para cumprir a cota.
6. Resumo curto: estudos publicados com link, temas que viraram `sem_fontes` e por quê, e as legendas do Instagram.

Pedido avulso ("/estudo", "estudo de <passagem>"): mesmos passos para um tema; se a passagem não estiver na pauta, acrescente-a.

## Pesquisa (briefing do subagente)

Peça, em português: a passagem e a questão; **pelo menos 2, idealmente 3 teólogos brasileiros de referência por lado**, cada um com igreja ou instituição confirmada na fonte, posição, argumento em paráfrase fiel, 1 ou 2 citações literais com o URL onde a frase foi lida, obra, link e data; os argumentos exegéticos de cada lado; os pontos de concordância com fonte; um comentário clássico em domínio público (Calvino, Matthew Henry, Wesley) com link; a lista de fontes; e **o que não foi confirmado**. Regras para o subagente:
- Citação literal só de frase lida na página; dizer se conferiu baixando a página (curl + grep, grau A) ou só pelo WebFetch (grau B). Salvar as páginas em `<scratchpad>/web-<slug>/`.
- Não inventar títulos, datas, cargos nem posições. Teólogo sem texto lido não entra, mesmo que "todo mundo saiba" o que ele pensa.
- **Site que bloqueia robô (403, 406, desafio Cloudflare) não se contorna**: procure outra fonte ou uma reprodução fiel (ex.: as Lições Bíblicas da CPAD estão reproduzidas em estudantesdabiblia.com.br e em blogs; confira a mesma frase em duas reproduções). O mesmo vale para você: nada de trocar user-agent para passar por bloqueio.
- Fontes que funcionaram: blogs dos próprios autores (O Tempora, O Mores; Teologia Pentecostal; blog de Ciro Zibordi), colunas do Guiame, Fides Reformata (PDFs do CPAJ/Mackenzie), Monergismo, Lições Bíblicas reproduzidas, CCEL e biblestudytools para os clássicos. Bloqueados nas sessões de nuvem: hernandesdiaslopes.com.br, cpadnews.com.br, jmnoticia.com.br, web.archive.org.

## Citações

Antes de escrever, confira cada citação nas páginas salvas (`grep -F "<trecho>"`). Frase que só aparece reproduzida por terceiros (ex.: post de rede social citado num blog) entra como **paráfrase**, com a obra dizendo onde foi reproduzida. Se o autor recusa um rótulo (Augustus Nicodemus não se diz cessacionista), o texto diz isso. Se a fonte não trata da passagem do estudo, o texto diz isso.

## Texto

`conteudo/estudos/<slug>.json` (docs/PADRAO_EDITORIAL.md, "Estudos bíblicos" e "O que dizem os teólogos"). Campos: `titulo`, `passagem`, `sigla`, `livro`, `testamento`, `genero`, `nivel` (1 a 3), `tempo_min`, `selo`, `tagline`, `lede`, `descricao`, `imagem`, `versiculo_chave` (texto, referência, tradução; a Almeida Corrigida Fiel do bibliaonline.com.br entra como citação curta com crédito à SBTB), `estrutura` (3 a 7 partes com referência), `estrutura_resumo`, `questao`, `posicoes` (2 a 4 lados, 2 a 4 teólogos cada), `convergencias`, `contexto`, `aplicacao`, `destaques`, `atencao` (com gravidade), `perfil`, `formatos`, `para_quem`, `nao_e_para`, `dica`, `traducoes`, `relacionadas`, `comparacoes`, `versiculos`, `veredito`, `ficha`, `fontes`, `consulta`, `legenda`, `cor`, `ia`, `status: "revisao"`.

**Linha pentecostal (30/10/2026, obrigatória):** o portal é pentecostal e diz onde está. Leia "Linha editorial pentecostal" em docs/PADRAO_EDITORIAL.md e a **Declaração de Fé das Assembleias de Deus** (https://cgadb.org.br/wp-content/uploads/2021/01/declaracao_de_fe.pdf; peça ao subagente o que ela diz sobre o tema, com a frase conferida). Todo estudo tem `nossa_posicao` (Nossa posição, 1 a 4 parágrafos, tese pentecostal firme e fundamentada), o lado pentecostal primeiro em `posicoes`, e título, tagline, lede, destaques, atenção, aplicação, veredito e legenda escritos a partir dessa cosmovisão. O outro lado continua relatado com fidelidade e respeito, sem caricatura e sem chamar ninguém de herege. Modelo: `conteudo/estudos/batismo-de-criancas-atos-2.json`.

Tom: o relato dos lados é fiel e no melhor argumento de cada um; a voz do portal ("a gente") fica nas partes de opinião. Varie as aberturas, os vereditos e as legendas entre os estudos do dia (leia os últimos publicados): nada de repetir "A gente fica com..." em todos.

## Imagem

Obra de arte em domínio público, ligada ao texto, sem nudez. O Wikimedia Commons limita pedidos vindos da nuvem (429); o acervo aberto do Metropolitan Museum funciona:
- busca: `https://collectionapi.metmuseum.org/public/collection/v1.1/search?hasImages=true&isPublicDomain=true&limit=20&q=<termo em inglês>`
- detalhes (título, artista, data, `constituents` com "After ..." quando é gravura segundo outro pintor): `.../public/collection/v1/objects/<id>`
- veja a miniatura (`/web-large/`) antes de escolher, baixe com `python3 tools/imagens/baixar.py <primaryImage> estudo-<slug>.jpg --credito "Artista, Título (técnica, ano). The Metropolitan Museum of Art, Nova York (domínio público, Open Access CC0)" --pagina <objectURL>` e reduza para até 1600 px e ~300 KB.
Nunca imagem gerada por IA.

## Checagens antes do push

`python3 tools/estudos/checar_estudo.py`, `python3 tools/noticias/checar_noticia.py`, `python3 -m unittest discover -s tests`, `python3 tools/checar_isolamento.py`, `python3 tools/build_home.py` e `python3 tools/checar_seo.py`. Não versione `previa/` (o deploy gera).
