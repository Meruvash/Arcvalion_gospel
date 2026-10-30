# Plano de fotos do Golden Geek

Como os sites de review conseguem fotos, o que já fazemos sozinhos e o que falta para cada resenha ter foto boa de mesa, caixa e partida.

## Como os sites de review fazem

1. **Cópia de review + foto própria.** O caminho principal. A editora manda o jogo (de graça ou só com frete), o site joga e fotografa. É por isso que Shut Up & Sit Down, Dicebreaker e Meeple Mountain têm fotos que ninguém mais tem. No Brasil, a prática é a mesma: editoras mandam lançamentos para criadores de conteúdo em troca de divulgação.
2. **Kit de imprensa da editora.** Fotos em alta, liberadas para imprensa, com crédito ("Imagem: Editora"). Muitas editoras deixam o kit público (Pandasaurus, Cocktail Games, Kosmos, Plaid Hat, Free League); outras mandam por e-mail.
3. **Fotos da comunidade com crédito.** Alguns sites usam fotos de leitores e fotógrafos de jogos com autorização.

O que **não** fazem com segurança: copiar fotos de usuários do BGG, da Ludopedia, do Pinterest ou do Instagram sem autorização. A foto é de quem fotografou, não do site onde ela está.

## Fontes, em ordem

| # | Fonte | Quem faz | Comando ou ação |
|---|---|---|---|
| 1 | Site da editora original | Robô | `robo.py buscar <slug>` |
| 2 | Editoras licenciadas em outros países | Robô | fixar página em `editoras.json` + `buscar` |
| 3 | Kit de imprensa público (ZIP) | Robô | `robo.py kit <slug> <link> --nome "Editora"` |
| 4 | Kit em Dropbox/Google Drive | Você baixa, robô processa | `robo.py kit <slug> ~/Downloads/kit.zip --nome "Editora"` |
| 5 | Fotos de usuários com licença livre (Wikimedia Commons) | Robô | `robo.py livres <slug>` (categorias em `livres.json`) |
| 6 | Bancos gratuitos (Pexels, Unsplash) | Você baixa (bloqueiam robôs) | buscar o nome do jogo; licença livre, crédito opcional |
| 7 | Pedido de kit ou cópia de review | Você envia | modelos abaixo |
| 8 | Comunidade (grupo do WhatsApp) | Você publica a chamada | modelo abaixo |
| 9 | Fotos próprias | Você | guia abaixo |

### Kits de imprensa já encontrados

- **Cocktail Games** (Bomb Busters e outros): página de downloads com um ZIP de "Visuels" por jogo. Já usado em Bomb Busters.
- **Pandasaurus** (The Mind, Mind Up!, The Mind: Soulmates): pasta no Dropbox em pandasaurusgames.com/pages/media-kits. O Dropbox proíbe robôs: baixe o ZIP e rode `kit`.
- **Kosmos**: página de Pressemappen.
- **Czech Games Edition**: páginas "for press" por jogo.

### Wikimedia Commons

Categorias com fotos de usuários em CC0 ou CC BY-SA: Terraforming Mars (8), Endeavor: Deep Sea (7), Azul (6), Codenames (6), Wingspan (5), Scythe (3), Nemesis (1). O crédito sai automático: "Foto: Autor · CC BY-SA 4.0 · Wikimedia Commons". O Wikimedia limita pedidos vindos de servidores na nuvem; se pedir pausa, o robô pula e avisa. Do seu computador costuma passar direto.

## Modelos

### Pedido de cópia de review (editoras brasileiras)

> Assunto: Golden Geek – resenha de [JOGO]
>
> Olá, equipe [EDITORA]!
>
> Sou [NOME], do Golden Geek (https://meruvash.github.io/Arcvalion_gospel/), site de resenhas de jogos premiados ligado à comunidade O Paladino ([N] pessoas no grupo do WhatsApp, [perfil] no Instagram). Publicamos [N] resenhas por semana, com infográfico para o Instagram.
>
> Queremos resenhar [JOGO], que ganhou [PRÊMIO]. Vocês teriam uma cópia para review? Se preferirem, pagamos o frete. Também aceitamos o kit de imprensa com fotos oficiais, sempre com crédito à editora.
>
> A resenha é independente: dizemos o que funciona e o que pesa, e mandamos o link assim que publicar.
>
> Obrigado!

### Pedido de autorização a quem fotografou (Instagram, Ludopedia, BGG)

> Oi, [NOME]! Que foto bonita do [JOGO]. Sou do Golden Geek, site de resenhas de jogos premiados. Posso usar essa foto na nossa resenha, com crédito para você (@[PERFIL] e link)? Não é uso comercial e tiramos do ar quando você pedir.

Guarde o print da resposta e registre no `fontes.json` da foto: `"credito": "Foto: @perfil (autorizada em AAAA-MM-DD)"`.

### Chamada no grupo

> 📸 Chamada de fotos! A próxima resenha do Golden Geek é de [JOGO]. Tem foto da sua mesa? Manda aqui (de cima, com o jogo montado, sem gente na frente). A melhor vai para o site com o seu nome. Ao enviar, você autoriza o uso na resenha e no Instagram de O Paladino, com crédito.

## Guia rápido de foto própria

- **Luz:** perto de uma janela, de dia, sem flash. Nada de luz amarela de teto.
- **Mesa:** fundo liso (madeira clara, toalha neutra). Tire copos, celulares e caixas de outros jogos.
- **Quatro fotos por jogo:** caixa de frente (em pé, fundo limpo); mesa montada vista de cima (celular paralelo à mesa); partida no meio, em ângulo de 45°; detalhe de componentes bem de perto.
- **Celular:** modo normal (não retrato), lente principal, toque para focar, 2 ou 3 fotos de cada.
- **Sem pessoas no quadro** (a página não usa fotos com gente; mãos só se for o foco).
- Mande para o robô processar: `robo.py kit <slug> fotos.zip --nome "Golden Geek"` e o crédito sai "Imagem: Golden Geek".

## Escala: de onde os sites internacionais tiram as fotos

Pesquisa de 28/10/2026: 15 resenhas de 8 sites, com as imagens analisadas pelo crédito na legenda, pelo nome do arquivo e pelo servidor de origem (os metadados de câmera vêm apagados pelos CDNs).

| Site | Pista nas imagens | Fonte real |
|---|---|---|
| GamesRadar+ | "Image credit: Future/Matt Thrower" e "sample provided by the publisher" | cópia da editora + foto própria |
| Gaming Trend | `IMG_5866.jpeg` (iPhone) e "provided by the publisher" | cópia + foto de celular |
| Player Elimination | `pxl_2025…jpg` (Pixel) e `pic8662670.png` (padrão de nome do BGG) | foto de celular + 1 imagem do BGG |
| Board Game Quest | `Sky-Team-Gameplay.jpg` e "review copies provided by the publisher" | cópia + foto própria |
| Shut Up & Sit Down | `MVI_0202…Still001.jpg` | quadros dos próprios vídeos |
| Tabletop Gaming | capa tratada no Photoshop + foto de componentes | material da editora |
| Meeple Mountain | `m.media-amazon.com` | imagem de produto do programa de afiliados da Amazon |
| Zatu | fotos de produto | é loja: fotografa o próprio estoque |

**Conclusão: não existe um banco de imagens escondido.** Em 6 dos 8 sites, a fonte consistente é a mesma: a editora manda a cópia e o site fotografa. Material da editora, BGG e Amazon aparecem como complemento, quase sempre só para a caixa.

### Fontes de catálogo: o que dá e o que não dá

- **BGG (XML API):** desde 2025 exige registro do aplicativo; a licença gratuita é só para uso não comercial, com crédito "BoardGameGeek"; uso comercial (loja, por exemplo) pede licença paga. Os termos não falam das imagens, que pertencem a quem enviou. **Use para dados, não para fotos:** com o registro, nota, peso e número de avaliações viriam pela API oficial, em vez de busca na web.
- **Amazon (Product Advertising API):** só para afiliados; a imagem não pode ser guardada (só o link, por até 24 h) e precisa apontar para a Amazon com o link de afiliado. Não combina com o nosso fluxo (webp próprio, `capa.jpg`, crivo). Fica de fora.

### Arquitetura em camadas

| Camada | Fonte | Entrega | Escala |
|---|---|---|---|
| 1 | **Fotos próprias de cópias de review** | mesa, partida, componentes, caixa nacional | é a fonte dos grandes sites; precisa do programa de cópias e de uma sessão de fotos fixa |
| 2 | **Material oficial pelo robô** (editora, licenciadas, kits) | caixa e componentes; às vezes mesa | automática; já cobre 20 de 22 jogos com algo |
| 3 | **Ludoteca parceira** (board game café ou loja com biblioteca) | mesa e componentes de jogos que não temos | uma tarde por mês, cerca de 20 jogos por sessão a 10–15 min cada |
| 4 | **Comunidade** (grupo do WhatsApp, com termo) | fotos reais de partida | complementar; ótima para jogos raros |
| 5 | **Licença livre** (Commons) | fotos de usuários | baixa cobertura; só jogos famosos |

Como colocar a camada 1 e a 3 de pé:

1. **Kit de mídia do Golden Geek** (1 página): o que é o site, número de resenhas publicadas, alcance do grupo e do Instagram, exemplo de resenha e de infográfico, contato. É o que as editoras pedem antes de mandar cópia (Stonemaier pergunta "qual o tamanho do seu público?").
2. **Programa de cópias** com as editoras brasileiras: mandar o kit e pedir entrada na lista de imprensa (Galápagos/Asmodee Brasil, Devir, Grok, MeepleBR, Ludofy, Ludofun, Across the Board, PaperGames, Conclave). Oferecer pagar o frete. Cada cópia vira foto própria da edição nacional.
3. **Ludoteca parceira:** propor a um board game café uma sessão mensal de fotos em troca de crédito e link na resenha ("jogo fotografado no acervo do …"). Levar a lista de jogos da pauta sem foto de mesa.
4. **Padrão de estúdio:** o mesmo fundo, a mesma luz e as mesmas 4 fotos por jogo (guia acima), para o site ter cara de revista e o crivo aprovar de primeira.
5. **Lista de falta:** antes de cada sessão, listar os jogos da pauta (na fila e publicados) que não têm foto de mesa aprovada; essa lista é a pauta da sessão de fotos.

Meta de cobertura: toda resenha nova com pelo menos uma foto de mesa ou partida aprovada pelo crivo. Material oficial cobre caixa e componentes; mesa vem das camadas 1, 3 e 4.

## Próximos passos

1. Rodar `livres` nos 7 jogos com fotos no Commons e escolher as melhores.
2. Baixar o kit da Pandasaurus (The Mind) e rodar `kit`.
3. Enviar pedidos de cópia de review às editoras brasileiras (Galápagos, Devir, Grok, MeepleBR, Ludofy, Ludofun, Across the Board) para os próximos jogos da pauta.
4. Publicar a primeira chamada de fotos no grupo para MicroMacro, Sky Team e Detective, que não têm foto de mesa.
5. Montar o kit de mídia do Golden Geek e mandar com os pedidos de cópia.
6. Registrar o Golden Geek como aplicativo não comercial na XML API do BGG, para nota e peso oficiais (não para fotos).
7. Escolher e propor a parceria a uma ludoteca ou board game café para a sessão mensal de fotos.
