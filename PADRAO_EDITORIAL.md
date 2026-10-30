# Padrão editorial dos infográficos (v2)

Vale para todo infográfico novo. O modelo é `modelos/referencia-1.jpg` (Código Secreto): cada bloco informa algo concreto sobre **este** jogo, e quem lê só a imagem já sabe como se joga, o que é bom, o que pesa e para quem é.

`tools/checar_roteiro.py` confere estas regras e `tools/lote_openai.py enviar` / `tools/gerar_infografico_openai.py` se recusam a gerar a imagem se o roteiro não passar.

## Formato

- **Quadrado 1:1** (2048×2048), o formato que funciona no nosso fluxo do Instagram. (O 4:5 foi testado com o Gloomhaven e descartado.)
- Texto pequeno, mas legível no celular: mesma hierarquia do modelo, comprimida no quadrado.
- No primeiro teste em quadrado com 12 linhas de ficha, 8 barras e veredito de 55 palavras, a faixa de baixo saiu espremida e com texto embaralhado; por isso a ficha e o veredito têm limites menores. No segundo teste a IA deixou de fora as barras de "compatibilidade com seu perfil", então esse bloco saiu do quadrado.

## Blocos do `roteiro` (em `conteudo/<slug>.json`)

| Campo | Regra |
|---|---|
| `titulo` | Nome do jogo como aparece na caixa nacional (ou original). |
| `chamada` | 12 a 22 palavras: o que o jogo é + o gancho. |
| `destaque` | 15 a 28 palavras de opinião na caixa do canto superior direito. |
| `lateral` | 10 linhas: jogadores, duração, complexidade (com rótulo), modo solo, dados, designer, editora original, editora no Brasil, ano, idioma. |
| `numeros` | 4 caixas `[rótulo, valor, contexto]`. O contexto explica o número ("106 mil avaliações", "pesado"). Só números com fonte. |
| `como_resumo` | Uma linha de 8 a 18 palavras que resume a partida. |
| `passos` | 5 passos `[título, texto]`: título de 2 a 4 palavras; texto de 15 a 30 palavras explicando a regra de verdade. |
| `fortes` | 6 a 7 itens de 4 a 10 palavras, específicos do jogo. |
| `atencao` | 6 a 7 itens de 4 a 10 palavras, específicos do jogo. |
| `ficha` | 8 a 10 linhas `Campo: valor`, incluindo componentes. |
| `premios` | 1 a 3 medalhas, das premiações confirmadas em `premiacoes`. |
| `extra` | `{titulo, texto}`: um bloco útil e verificável (experimente online, versão para iniciantes, expansões, preço de referência com data). Texto de 20 a 45 palavras. |
| `veredito` | Frase de 5 a 12 palavras. |
| `veredito_texto` | 25 a 40 palavras: o que entrega, o que pesa e um conselho claro de compra. |

## Regras de conteúdo

1. **Nada inventado.** Todo número vem de fonte listada em `fontes`. O que não foi confirmado fica fora das caixas de números e aparece como "não confirmado" na lateral ou na ficha.
2. **Específico, não genérico.** Proibido item que serviria para qualquer jogo: "arte marcante", "muito divertido", "tema fino", "sorte nas cartas" sem dizer onde. Diga o quê e por quê: "Arte de Maxime Morin faz cada região parecer um quadro".
3. **Como funciona ensina.** Os 5 passos, lidos em sequência, explicam uma rodada de verdade, com os termos do jogo.
4. **Consistência.** Lateral, números e ficha batem com a `ficha` da página.
5. **Bandeira do Brasil** só na linha "editora no Brasil", e só se houver edição nacional confirmada.
7. **Texto de gente, não de fórmula** (vale para resenhas e notícias). Sem muletas e adjetivos vazios ("vale a pena", "para quem gosta de", "ideal para", "jornada", "envolvente", "promete", "não é só X, é Y"): troque por um detalhe concreto (quanto tempo, quantas peças, qual jogo parecido, o que acontece na mesa). Varie a abertura das frases e dos itens de lista. Opinião com posição clara. A lista fica em `tools/vicios.py`; `checar_roteiro.py` e `checar_noticia.py` avisam (sem bloquear) e o aviso deve ser resolvido antes de publicar. Nunca use ferramenta de "humanizar" texto: ela troca palavras sem critério e cria erro.
6. **Revisão da imagem** (etapa 5 da skill): conferir bloco por bloco contra o roteiro. Duas falhas no mesmo bloco → gerar a arte sem texto e compor o texto por cima em HTML (Playwright).

# Padrão editorial do texto do site (v2)

A página é a resenha completa: precisa ensinar o jogo, mostrar como é jogar, pesar o que é bom e o que pesa com o porquê, e terminar com um conselho de compra claro. Ela nunca pode ter menos informação que o infográfico. `tools/checar_roteiro.py` confere estas regras também, e `tools/lote_openai.py enviar` e `tools/publicar.py` se recusam a seguir se o texto não passar.

| Campo (em `conteudo/<slug>.json`) | Seção da página | Regra |
|---|---|---|
| `selo` | nível de recomendação | Um de: **Recomendado**; **Recomendado com ressalva** (obrigatório quando há ponto de atenção "Grave" ou preço mínimo acima de R$ 800); **Não recomendado**. |
| `ressalva` | junto do nível | Só com "Recomendado com ressalva": o obstáculo em 2 a 6 palavras, tirado da resenha ("joga-se uma vez só", "preço acima de R$ 1.000", "textos em inglês"). |
| `melhor_para` | balão do perfil | Um de: `entrada` (peso BGG abaixo de 2, regras em ~15 min), `dupla` (2 jogadores é a melhor contagem), `festa` (melhor com 5+, até ~30 min), `cooperativo`, `solo` (modo solo avaliado como ótimo), `proximo` (peso entre 2 e 3), `estrategia` (peso a partir de 3,2 ou partidas de 2 h), `campanha` (história em várias sessões), `tema` (narrativa e imersão no centro). Escolha o que melhor descreve quem deve comprar, sem repetir o perfil das últimas resenhas quando houver dúvida. |
| `titulo_busca` | título no Google e na prévia | Até 62 caracteres, com o nome do jogo e a palavra "resenha", e um ângulo tirado da própria resenha (a frase de destaque, o prêmio principal, a comparação ou a série). Exemplos: "Cascadia: resenha do quebra-cabeça de natureza em 30 min", "Santuário ou Ark Nova? Resenha do vencedor do DSP 2026". "Vale a pena?" só quando for a dúvida real (jogo caro) e sem repetir a fórmula das últimas resenhas. O subtítulo do veredito já traz "Veredito: <jogo> vale a pena?". |
| `lede` | abertura | 50 a 90 palavras: o que é, o prêmio principal, para quem é e uma pista do veredito. |
| `como_funciona` | Como funciona | 4 a 6 parágrafos, 200 a 350 palavras no total: objetivo, o turno, a mecânica central, a progressão e como acaba e pontua. Termos do jogo explicados na primeira vez. |
| `experiencia` | Como é jogar | 2 a 3 parágrafos, 120 a 220 palavras: ritmo, decisões típicas e um exemplo concreto de jogada. |
| `funciona` | O que funciona muito bem | 5 a 7 itens `[título, texto]`, texto de 30 a 70 palavras com o porquê; opinião sempre atribuída ("Para a Board Game Quest, …"). |
| `atencao` | Pontos de atenção | 5 a 7 itens `[gravidade, título, texto]`, mesma regra. |
| `jogadores` | Com quantos jogar | 2 a 5 itens `[número de jogadores, texto, nível]`, 10 a 45 palavras; nível 3 = ótimo, 2 = bom, 1 = fraco (vira os pontinhos da página). |
| `primeira_partida` | Primeira partida | 50 a 120 palavras: tempo de explicação, o que confunde e uma dica prática. |
| `edicao_nacional` | Edição nacional e preço | 40 a 100 palavras: editora, idioma, preço de referência com data e disponibilidade (ou a falta de edição nacional). |
| `versoes` | Expansões e versões | 30 a 100 palavras: expansões, versão digital, versões de entrada. |
| `comparacoes` | Se você gosta de… | 2 a 3 itens `[jogo, slug ou null, texto]`, 20 a 50 palavras; o slug liga para a nossa resenha. |
| `para_quem` / `nao_e_para` | É para você se… | 4 a 5 itens cada. |
| `veredito` | Veredito | 80 a 140 palavras: o que entrega, o que pesa, para quem é e se vale o preço. |
| `citacao` | destaque em Como é jogar | `{texto, fonte}`: uma frase curta de crítica especializada que resume a experiência ("tradução livre" quando traduzida). |
| `preco_ref` | resumo e cartão de preço | `{faixa, data, obs}`: faixa de preço das lojas consultadas, data da consulta e observação (estoque, importado, sem edição nacional). |
| `fontes` | Fontes | pelo menos 6, com link. |

Resenhas antigas, cujo infográfico é anterior ao padrão v2, levam `passos`, `perfil` e `como_resumo` próprios no nível do site (mesmas regras do roteiro), sem mexer na imagem.

Layout (gerado por `build_review.py` quando a resenha tem `experiencia`): resumo de 30 segundos no topo, passos numerados (vêm do `roteiro.passos`), faixa escura com a citação, prós e contras em cartões que abrem com um toque, barras de perfil (`roteiro.perfil`), blocos de número de jogadores, dica de primeira partida, cartão de preço, comparações com capa, e no celular ficha, prêmios, versões e fontes começam fechados.

Regras de texto:

1. **Nada inventado**, como no infográfico. Regra do jogo é fato; elogio e crítica são opinião e sempre têm dono.
2. **Escreva para quem nunca jogou.** Frases diretas, sem jargão solto ("construção de baralho", não "deck-building" sem explicar).
3. **Atribuição natural.** "Para a Tabletop Gaming, …" e não "A IGN, citada pela Wikipedia, elogia…".
4. **Exemplo concreto** em Como é jogar e em pelo menos dois pontos fortes ou de atenção.
5. **Sem frase genérica** ("muito divertido", "arte marcante", "tema fino") sem dizer o quê e por quê.

## Opinião forte (29/10/2026)

Pedido do usuário: a resenha precisa gerar reação e compartilhamento. O tom das partes de opinião é **inteligente, sarcástico, ácido e engraçado**, com a estrutura de stand-up de Ricky Gervais (mapa abaixo). Modelo aprovado: `conteudo/vantage.json` ("um jogo para seis pessoas que querem ficar sozinhas"). Referências: Berger e Milkman (emoção de alta ativação se compartilha), *Contágio* (STEPPS), *Ideias que colam* (o inesperado), *Breakthrough Advertising* (ângulo novo para um público que já viu tudo), *Save the Cat* (logline).

**Onde vai o tom:** `titulo_html`, `tagline`, `lede` (a partir da segunda frase), `experiencia`, títulos e textos de `atencao`, `para_quem` / `nao_e_para`, `veredito` e `legenda`. **Onde não vai:** `como_funciona`, `passos`, ficha, prêmios, edição nacional e fontes, que continuam neutros e exatos.

1. **Uma tese por resenha.** Uma frase que o leitor possa repetir ou contestar, de preferência contra o consenso ("superestimado", "solo que finge ser para seis"). Ela aparece no título ou na tagline, abre o veredito e a legenda.
2. **O sarcasmo nasce do fato.** A graça vem do contraste entre o que a caixa promete e o que a crítica e as regras mostram (até seis jogadores × "não passe de três"; oito anos de desenvolvimento × recomeçar do zero). Todo número e toda crítica citada continuam com fonte.
3. **Alvo certo.** Ironia contra o jogo, o preço, o marketing, a edição e as decisões da editora. Nunca contra pessoas, autores, editoras como empresa, lojistas ou quem gosta do jogo.
4. **Justiça na mesma página.** A resenha ácida reconhece o que o jogo faz bem em `funciona`, com o mesmo cuidado. O selo segue as regras de sempre: o tom não muda o selo, e opinião forte não é desculpa para "Não recomendado".
5. **Frase pronta para compartilhar.** Pelo menos uma frase curta e citável no veredito (capital social: o leitor compartilha para parecer entendido), e a legenda fecha com uma pergunta que provoque resposta.
6. **Inteligente, não grosseiro.** Nada de palavrão, xingamento ou deboche fácil. Comparações concretas e inesperadas ("reunião de condomínio", "peça de ficção") funcionam melhor que adjetivos.
7. **Nada inventado para causar.** Se a pesquisa não sustenta a polêmica, o tom fica firme mas sem a tese contrária. A opinião é de O Paladino e precisa ser defensável.
8. **Voz: "a gente".** Tom de conversa, mas a voz é do site: "a gente", nunca "eu". Nunca cite o nome de Gervais nem de outro humorista no texto; é só a estrutura.
9. **Nada de muleta.** A mesma piada no máximo uma vez por resenha; o preço entra no máximo três vezes nas partes de opinião (além do item de preço). Bordões de uma resenha não se repetem na seguinte: "Olha", "Isso não é uma crítica. Bom, é um pouco", "Ou outros amigos" e similares valem uma vez e depois saem do repertório. Repita as técnicas, não as frases.
10. **Sem palavrão e sem alvo vulnerável.** Gervais xinga e às vezes mira em grupos de pessoas; aqui não. Nada de piada com doença, deficiência, aparência, origem ou religião.

**Mapa do estilo (Ricky Gervais: monólogos do Globo de Ouro e especiais *Humanity*, *SuperNature* e *Armageddon*)**

1. **A verdade que ninguém fala em voz alta.** O que todo mundo pensa e o marketing esconde ("a caixa diz seis, a crítica diz três").
2. **Abertura de confissão.** "Vamos ser honestos", "olha": tom de conversa antes da faca.
3. **Frases curtas, em sequência.** Uma ideia por frase. A piada vem na última.
4. **O recuo que não recua.** Finge pedir desculpa e reforça o ataque ("Isso não é uma crítica. Bom, é um pouco.").
5. **Lógica até o absurdo.** Seguir o raciocínio com cara séria até o ridículo ("oito anos fazendo um jogo para uma pessoa e depois imprimiu seis na caixa").
6. **Ataque para cima.** O alvo é o poderoso: o jogo premiado, a editora, o marketing, o preço. Nunca o leitor.
7. **Elogio sincero no meio do ataque.** Reconhecer o mérito deixa a crítica mais crível e mais cruel.
8. **A vida real como contraponto.** "São onze e meia da noite e você trabalha amanhã"; "você já faz isso de graça no grupo da família".
9. **Final que vira de lado.** Parece conselho e termina em soco.
10. **Autoironia do próprio público.** Nós, que pagamos caro por papelão, também entramos na piada.

Outras referências de tom, para variar a técnica: Roger Ebert (a demolição elegante), A. A. Gill e Jay Rayner (o detalhe concreto e a comparação absurda), Charlie Brooker (o exagero que escala), Jeremy Clarkson (a comparação doméstica e o deadpan), Ben "Yahtzee" Croshaw e Quinns, do Shut Up & Sit Down (humor sobre o próprio hobby), Dorothy Parker (a frase curta e letal), José Simão, Stanislaw Ponte Preta e Millôr Fernandes (o humor brasileiro).

## Fotos oficiais na página

Quando a resenha tem fotos aprovadas em `<slug>/fotos/fontes.json` (skill `imagens`) e o jogo foi liberado com `"usar_na_pagina": true` nesse arquivo (depois da revisão das fotos), `build_review.py` monta a página assim (modelo aprovado com Terraforming Mars):

- **Topo:** uma foto oficial do jogo no lugar do infográfico. Vale a foto marcada com `"principal": true`; sem marca, a ordem é mesa, componentes, jogabilidade, caixa.
- **Como é jogar:** a foto marcada com `"jogar": true`; sem marca, a próxima disponível (componentes, jogabilidade ou mesa), logo depois da citação.
- **Edição nacional e preço:** a caixa (`capa`), pequena, ao lado do texto.
- **Infográfico:** desce para o meio, na seção "Infográfico para o Instagram" depois de Prós e contras, com os botões Salvar na galeria e Legenda.
- Toda foto leva o crédito da editora embaixo ("Imagem: …").
- **Sem rosto de frente:** foto com mãos, braços ou rosto de perfil pode entrar (29/10/2026). Só a foto em que aparece o rosto de alguém de frente leva `"pessoas": true` no `fontes.json` e não entra na página.
- **Miniatura:** a `capa.jpg` (cartão na lista de resenhas e prévia do link no WhatsApp) é refeita a partir da foto do topo, recortada no centro em 800×800, sempre que a página é gerada. O `og:image` leva `?v=` com a versão da imagem, para o WhatsApp buscar a nova.
- Só a caixa não basta: sem foto de mesa, componentes ou jogabilidade, a página continua com o infográfico no topo e a miniatura do infográfico.

## Crivo de qualidade das fotos

`python3 tools/imagens/crivo.py <slug>` avalia cada foto aprovada pelo robô e escolhe o lugar dela na página; `--aplicar` grava a escolha no `fontes.json` (`principal`, `jogar`, `fora`) e libera a página (`usar_na_pagina`). A página só ganha fotos se alguma passar para o topo; senão fica com o infográfico até chegarem fotos melhores. Os limites foram calibrados com as fotos já aprovadas.

**Eliminatórios (a foto não entra em lugar nenhum)** — marcados na revisão visual da folha de contato:
- rosto de alguém de frente (`"pessoas": true`); mãos e perfil podem;
- texto por cima da foto (faixa de loja, selo, ícones de idade) ou texto em outra língua que domina a imagem (`"texto": true`);
- medidos pelo crivo: brilho médio fora de 40–235 (escura ou estourada) e nitidez abaixo de 6.

Foto de outra edição não reprova: entra com o aviso no crédito (`"Imagem: … · foto da 2ª edição; a resenha trata da edição original de 2017"`).

**Topo (foto principal)** — mesa, jogabilidade ou componentes, nessa ordem de preferência:
- lado menor de pelo menos 800 px;
- proporção até 1,8 (16:9); mais comprida vira uma faixa fina no celular;
- sem cara de catálogo: menos de 35% da foto em branco recortado e menos de 45% em fundo liso de estúdio;
- a caixa sozinha nunca vai para o topo.

**Como é jogar** — outra foto de mesa, jogabilidade ou componentes, com lado menor de pelo menos 600 px e proporção até 2,4. Prefere uma que também passaria no topo; foto de catálogo é aceita aqui.

**Preço** — a caixa, com lado menor de pelo menos 400 px.

# Padrão editorial das notícias (v1)

A notícia de O Paladino não repete o release: diz o que aconteceu, por que importa para quem joga no Brasil, o que a crítica acha e o que a gente recomenda. Herda do padrão das resenhas a regra de ouro: **fato tem fonte, opinião tem dono**. Conferido por `tools/noticias/checar_noticia.py`; `tools/build_home.py` não publica nota que não passa.

| Campo (em `conteudo/noticias/<data>-<assunto>.json`) | Seção da página | Regra |
|---|---|---|
| `titulo` | título | 8 a 16 palavras: o fato e quem, sem caça-clique. |
| `selo` | selo da nota | Um de: **Vale a compra**, **Vale acompanhar**, **Para fãs do jogo base**, **Com ressalvas**, **Informativo**. |
| `lide` | abertura | 35 a 70 palavras: o fato, quando, onde e a ligação com o Brasil. |
| `por_que_importa` | Por que importa | 30 a 70 palavras de **análise nossa**, assinada por O Paladino: o que a notícia muda para o leitor. |
| `numeros` | Em números | 2 a 4 itens `[valor, rótulo, fonte]`. Só número com fonte; preço sempre com data. |
| `corpo` | Contexto | 1 a 3 parágrafos, 40 a 200 palavras: o que o leitor precisa saber para entender. |
| `no_brasil` | No Brasil | 25 a 80 palavras: editora nacional, preço com data, disponibilidade, ou a falta de edição nacional. |
| `critica` | O que diz a crítica | 1 a 3 itens `{fonte, texto, citacao}`; vazio só em nota **Informativo** sem resenha publicada, e a página avisa isso. `citacao: true` só para frase literal traduzida ("tradução livre"); senão é paráfrase atribuída ("Para a Board Game Quest, …"). |
| `para_quem` / `nao_e_para` | Interessa a você se… / Pense duas vezes se… | 1 a 3 itens cada (`nao_e_para` pode ficar vazio em nota informativa). |
| `veredito` | Nossa opinião | 20 a 60 palavras: conselho claro (comprar, esperar, acompanhar) e o porquê. |
| `fontes` | Fontes | pelo menos 2, com link e data da consulta. |
| `crivo` | Por que esta notícia entrou | pontos e critérios do crivo (PLANO_NOTICIAS.md). No mínimo 5 notas por dia e sem máximo; a pontuação ordena as notas e escolhe a manchete (PLANO_NOTICIAS.md, "Edição diária"). |
| `publicado_em` | (ordem das Últimas notícias) | Hora de publicação, ISO 8601. Preenchido por `tools/build_home.py` (commit que criou o arquivo ou a hora da geração); não se escreve à mão. A lista da página inicial segue esta hora, e a geração para se uma nota mais nova ficar fora dela. |
| `verificacao_nacional` | (não aparece na página) | Obrigatório quando a nota diz que um jogo não tem edição nacional, e recomendado para todo jogo citado: `[{jogo, resultado, data, fontes, obs}]`, com `resultado` "edição nacional" ou "não encontrada" e pelo menos 2 fontes com link, uma brasileira. "Não encontrada" exige o link do ComparaJogos. Ver regra 6. |

Regras de texto:

- **Ludopedia só nas fontes** (29/10/2026): o texto da nota não cita a Ludopedia. Lançamento, pré-venda e data prevista se atribuem ao **nosso calendário de lançamentos** (/lancamentos/, que usa os dados dela), e a Ludopedia aparece só na lista de fontes, no campo `fonte` dos números e no crédito da capa ("Capa via Ludopedia"). `checar_noticia.py` recusa a nota que citar a Ludopedia no texto.
- **Loja não aparece no texto** (29/10/2026): nome de loja de varejo (TabuleRIO, Amazon etc.) seria publicidade de graça. No texto, escreva "em loja parceira", "em lojas brasileiras" ou "a partir de R$ X, segundo o ComparaJogos"; a loja vai só nas `fontes` e na fonte dos números. A loja da própria editora pode ser citada ("loja oficial da Ludofun"). `checar_noticia.py` recusa as lojas da lista `LOJAS`.
- **Opinião forte nas notícias** (29/10/2026): o tom da seção "Opinião forte" (inteligente, sarcástico, ácido e engraçado, voz "a gente") vale só em `por_que_importa`, `para_quem`, `nao_e_para` e `veredito`. Título, lide, números, contexto, no Brasil (no máximo uma frase seca no fim) e crítica continuam informativos e neutros: notícia é fato. O título pode ter graça, desde que tudo nele seja fato e diga o que aconteceu, com quem (nada de caça-clique). As mesmas regras da resenha valem aqui: sarcasmo nascido do fato, alvo no jogo, no preço e nas decisões, nunca em pessoas, e sem repetir os bordões da resenha do mesmo jogo. Modelo: `conteudo/noticias/2026-10-28-vantage-chega-ao-brasil.json`.

1. **Opinião ancorada.** O veredito se apoia nas nossas resenhas (quando o jogo tem) e na crítica citada; nunca em impressão solta.
2. **Brasil primeiro.** Toda nota responde: dá para comprar aqui, por quanto e de quem? Se não dá, diz isso.
3. **Sem citação inventada.** Frase entre aspas só se a frase original existe; o resto é paráfrase com dono.
4. **Previsão é previsão.** Data de lançamento é "prevista" até o jogo chegar às lojas.
5. **Crítica dividida aparece dividida.** Se as resenhas discordam, mostre os dois lados.
6. **Edição nacional: verificação obrigatória.** Ausência de notícia de lançamento não prova que o jogo não saiu no Brasil; foi assim que erramos Galactic Cruise (Jelly Monster, nov/2025), Rebirth e Hot Streak. Antes de escrever que um jogo não tem edição nacional, faça os três passos e registre em `verificacao_nacional`:
   1. `python3 tools/noticias/edicao_nacional.py "<nome do jogo>"`: consulta o ComparaJogos. Oferta de jogo novo em loja brasileira (fora Amazon e marketplaces) é sinal forte de edição nacional: abra a página da loja e confira editora e idioma.
   2. Página do jogo na Ludopedia (campo de edição nacional e "No Brasil").
   3. Busca na web em modo estendido, em português e pensando em loja: "<nome> jogo português loja brasileira", "<nome> editora nacional". A busca comum não alcança lojas brasileiras.

   Só então, e só se nada aparecer, escreva o que foi verificado e até quando: "não encontramos edição nacional até <data>". Nunca "não há", "não tem", "ainda não há" ou "sem edição nacional": o verificador recusa essas frases. Se um jogo tem edição nacional, diga a editora, o mês de lançamento e a fonte.

# Chamadas para redes (WhatsApp, Telegram, Instagram)

Pedido do usuário em 29/10/2026: chamada com emoção, que faça clicar e comentar. Ficam em `conteudo/chamadas.json`
(`{"<slug>": {"chamada": "...", "pergunta": "..."}}`), fora da página, e `tools/divulgacao.py` usa no pacote do dia.

- **Chamada** (até 120 caracteres, 1 emoji no fim): pode usar curiosidade ("mas um deles já atrasou"), contraste ("R$ 118 ou R$ 422,99?"), opinião forte, a dor do leitor ("a caixa assusta?"), número ou prêmio real e urgência real (pré-venda aberta, prazo de campanha).
- **Pergunta** para puxar comentário: fácil de responder em uma palavra ou escolha ("Looot ou Through the Desert?", "pé embaixo ou freio?"), sobre o gosto do leitor, nunca prova de conhecimento.
- **A regra que não se quebra:** a página precisa entregar o que a chamada promete. Todo número, prêmio, preço ou data da chamada está no texto publicado. Proibido: fato inventado, urgência falsa, "você não vai acreditar", "chocante", CAIXA ALTA, mistério sobre algo que o texto não revela. Clickbait enganoso derruba a distribuição no Google Discover e no Facebook e queima a confiança do grupo.
