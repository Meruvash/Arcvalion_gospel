# Novela curta do agro: análise do modelo e 3 propostas (22/11/2026)

Projeto novo, para o outro Instagram do editor. Nada aqui foi produzido ainda: aguarda a escolha do editor.

## 1. O modelo

- **Vídeo:** "【FULL】Married Into a Wealthy Family by Mistake — Now I'm Spoiled Rotten!", canal Whisper of Romantic,
  https://youtu.be/iqlSvK0sH60 (título e canal lidos no oEmbed do YouTube em 22/11/2026).
- **Como foi lido:** transcrição completa pelo Virlo (11.538 palavras, em inglês; mistura a fala dos atores com o texto
  da tela). O download do vídeo falhou: o YouTube respondeu 403 e exige PO Token (código 3 do `youtube_baixar`). Por
  isso não há quadros dos primeiros 3 minutos, só a capa. A transcrição fica fora do repositório (direito autoral).
- **Formato:** é a compilação "FULL" de um microdrama de estilo americano, desses de app de novela, com atores reais.
  Pela quantidade de palavras, tem entre 70 e 90 minutos (estimativa). A capa é horizontal e romântica: casal no centro,
  título em letra dourada, selo "FULL".

### Enredo resumido
Mia precisa de 100 mil dólares para a cirurgia da mãe e aceita um casamento pago. Na pressa, ela **casa com o homem
errado**: Alexander Kane, o presidente bilionário do grupo Kane. Depois disso, o vídeo é uma sequência de humilhações
seguidas de virada. A prima arrogante, a falsa noiva Sophie, o ex-namorado Tom e a "doutora de Yale" humilham Mia por
ser pobre. Logo depois, a verdade aparece. O anel "de prata" era o anel de poder do grupo. A velhinha catadora de
latinha era a presidente do conselho e avó dele. O "presidente" que se exibia era falso. No fim vem a revelação
afetiva: ele era o menino gordinho que ela protegeu aos 8 anos.

### O que faz o modelo prender
1. **Gancho em 30 segundos:** a dívida com prazo (a cirurgia da mãe), uma decisão desesperada e o erro irreversível
   ("I married the wrong man"). A pessoa já entra no conflito.
2. **Ciclo curto de humilhação e virada**, repetido a cada 2 ou 3 minutos:
   - o vilão arrogante expõe a vítima em público, com dinheiro e status ("você nasceu pra limpar");
   - a vítima diz uma verdade que ninguém acredita;
   - chega a prova ou o poderoso ("Quem ousa encostar nela?");
   - o vilão desaba e implora ("Me perdoa").
3. **Objeto-prova:** o anel. Todos acham que é barato e falso, mas é o que decide tudo. O espectador sabe antes dos
   personagens, e essa ironia dramática é o motor do vídeo.
4. **Identidade escondida:** o marido "pobre" é o dono, e a velhinha "pobre" é a presidente do conselho. O público espera
   a revelação.
5. **Números falados:** "100 mil", "um bilhão guardado", "100 milhões o anel". Dinheiro concreto dá peso.
6. **Fala curta e repetida:** a frase de impacto aparece duas ou três vezes, na fala e no texto da tela.
7. **Etiqueta na tela:** nome e papel do personagem na primeira aparição ("A melhor amiga da Mia", "A prima").
8. **Vilões sem nuance**, com bordões de desprezo ("caipira", "pobretona"). O público torce pela vítima sem esforço.

### O que não copiar
Atores, rostos, nomes, a trama em si, a capa e a marca. Fica só a estrutura dramática. Também não fazemos gente
animada por IA: a regra do editor é evitar humanos gerados.

## 2. Como adaptar sem gente deformada: "novela em prints"
O microdrama de app vive de rosto de ator. A adaptação troca o rosto pelo **celular**. A história é contada por telas de
WhatsApp feitas em HTML próprio, com nomes e números fictícios. Juntam-se a isso:

- **documentos-prova** (o objeto-prova do modelo vira o papel do cartório, a notificação, o contrato);
- **paisagens e objetos** da fazenda (porteira, chave, mesa com papel, caminhonete de longe);
- **áudios de WhatsApp** com voz ElevenLabs para cada personagem, com balão de onda na tela.

O formato é 9:16, 1080×1920, de 60 a 90 s, com aviso "dramatização · história ilustrativa" no canto. O final traz a lei
com fonte (cartão com o artigo) e um gancho de "Parte 2".

## 3. As 3 propostas (fatos jurídicos já lidos na fonte nos roteiros do agro)

### A. "Vendeu a minha parte pelas costas" (herança)
- **Fonte:** Código Civil, arts. 1.794 e 1.795, em `roteiros/heranca-irmao-vendeu.md`.
- **Gancho (0–3 s):** print do grupo "Família 🌾" com a mensagem do irmão: "Vendi minha parte da fazenda. Já assinei.
  Não adianta chorar." Etiqueta: "O IRMÃO MAIS VELHO".
- **Humilhação:** áudio do irmão: "Você nunca teve dinheiro nem pra adubo. Quem comprou foi o Doutor Tavares, de
  Goiânia. Agora ele é teu sócio." O comprador manda foto da porteira: "Segunda eu chego com o trator."
- **Virada:** a irmã, quieta, abre a conversa com a filha advogada (ou com o Dr. Pelicioni). Cartão: art. 1.794, "não
  poderá ceder a sua quota a pessoa estranha… se outro co-herdeiro a quiser, tanto por tanto".
- **Golpe final:** "E como ninguém me avisou, a lei me dá 180 dias pra depositar o preço e ficar com a parte" (art.
  1.795). Print: o irmão "digitando…" e depois "apagou esta mensagem".
- **Gancho da parte 2:** "Mas o comprador tinha mais uma carta…"

### B. "O dono vendeu a terra que eu planto" (arrendamento)
- **Fonte:** Decreto 59.566/1966, arts. 45 e 47; Estatuto da Terra, art. 92, em `roteiros/terra-arrendada-preferencia.md`.
- **Gancho:** print do dono da terra: "Vendi a fazenda pro meu cunhado. Você tem até a colheita pra tirar tuas coisas."
- **Humilhação:** o cunhado novo dono manda áudio rindo ("arrendatário não manda em nada") e foto de uma placa de
  "Vende-se" já arrancada. A esposa do arrendatário, no grupo da família: "Vamos perder tudo que plantamos."
- **Virada:** o arrendatário responde só com a foto de um papel. A lei diz que o dono precisava notificá-lo e dar 30
  dias para ele decidir se comprava. Ninguém notificou.
- **Golpe final:** "Não me avisaram? Então eu deposito o preço e a terra é minha. Tenho 6 meses, contados do registro da
  escritura." Etiqueta no cunhado: "O NOVO DONO (por enquanto)".
- **Gancho:** "Só que o preço da escritura não era o preço verdadeiro…"

### C. "Vinte anos de caseiro" (usucapião, com virada contra a expectativa)
- **Fonte:** Código Civil, arts. 1.198, 1.238 e 1.239, em `roteiros/usucapiao-caseiro-vizinho.md`.
- **Gancho:** print do patrão rico, da cidade: "Vou vender o sítio. Você e sua família saem até sexta."
- **Humilhação:** o filho do patrão, no áudio: "Caseiro não tem direito a nada, é empregado." A família do caseiro
  acha que vai ganhar a terra por usucapião depois de 20 anos ali, e o vizinho "esperto" incentiva: "Entra com
  usucapião que é teu!"
- **Virada dupla (o diferencial):** a lei diz que quem cuida da terra cumprindo ordens do dono é **detentor**, não
  possuidor, e detentor não tem usucapião (art. 1.198). O vilão parece ter razão, e o público sente o baque.
- **Golpe final:** "Mas há 8 anos o patrão parou de pagar, sumiu, e eu passei a cuidar como dono." A partir daí pode
  correr a posse como dono (com o cuidado de dizer que depende de prova). Corta para o gancho.
- **Gancho:** "A prova estava numa mensagem antiga do próprio patrão…" Com isso, a parte 2 nasce sozinha.

## 4. Recomendação
**A (herança)** para o teste. É o tema que já passou de 5.000 visualizações no agro e tem o vilão mais claro (o irmão).
Também tem o objeto-prova mais visual (o grupo da família no WhatsApp) e o prazo concreto (180 dias), que faz o papel
dos "100 mil" do modelo.
