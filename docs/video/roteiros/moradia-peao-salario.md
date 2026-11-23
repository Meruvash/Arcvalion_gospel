# "A casa do peão vira salário?": moradia cedida ao trabalhador rural (roteiro v1, 23/11/2026, aguardando aprovação)

## Pesquisa de tendência (23/11/2026)
- **Autocomplete do Google:**
  - "trabalhador rural **que mora na propriedade**"
  - "trabalhador rural se aposenta com quantos anos"
  - "multa ambiental **prescreve**", "multa ambiental **por satélite**"
  - "produtor rural **tem que ter cnpj**"
  - "roubo de gado crime"
  - "funrural 2026"
- **Notícias da semana:**
  - Produtor pessoa física dispensado do CNPJ até 31/12/2028 (Agrolink, Canal Rural, FAEP).
  - Frente Parlamentar da Agropecuária entrega 32 pedidos sobre IBS e CBS à Receita (10/11).
  - Câmara aprovou em 20/05/2026 o PL 2.564/2025, que proíbe embargo só por satélite; o projeto está no Senado.

### Pautas candidatas (Crivo do Caseiro, 0 a 16)
| Eixo | Pauta | Nota | Observação |
|---|---|---|---|
| **G** | **A casa do peão vira salário?** (Lei 5.889/1973, art. 9º, § 5º) | **15** | Recomendada. Personagem próximo (o peão), dinheiro do dono em jogo, lei lida na fonte, cenas com gente para o Higgsfield. Perde 1 ponto: a busca é "que mora na propriedade", não "vira salário" |
| H | Multa ambiental prescreve? | 15 | Roteiro já escrito em 20/11 (22/23), à espera. Não tem personagem |
| G | Roubo de gado é crime de quê? | 12 | Lei ainda não lida (CP, art. 155, § 6º) |
| H | Embargo só por satélite | 9 | É projeto de lei, não lei; vence quando o Senado votar |
| C | Produtor tem que ter CNPJ? | 8 | Notícia da semana, mas tributária e datada (até 2028) e sem personagem |

**Rodízio:** os últimos vídeos foram do eixo F/B (arrendada) e B (CCIR). O eixo G só apareceu antes em 17/11.
**Gancho:** pergunta + resposta seca. O vídeo anterior usou suspense.

## Roteiro
| # | Fala |
|---|---|
| 1 | "O peão que mora de graça na sua fazenda está ganhando um favor? Pode estar ganhando salário, e a conta cai no seu bolso." |
| 2 | "A explicação está em duas palavras: contrato escrito." |
| 3 | "Pela lei do trabalho rural, a casa cedida ao peão só fica fora do salário se isso estiver num contrato escrito." |
| 4 | "A lei diz que esse contrato precisa de testemunhas e de aviso obrigatório ao sindicato dos trabalhadores rurais." |
| 5 | "Sem esse papel, a casa pode ser somada ao salário e entrar na conta das férias, do décimo terceiro e do fundo de garantia." |
| 6 | "E ele pode cobrar isso na Justiça até dois anos depois de sair da fazenda." |
| 7 | "Agora, cuidado: tem juiz que dispensa o contrato quando morar ali é indispensável pro trabalho, como quem vigia o gado de noite." |
| 8 | "Mas cada tribunal decide de um jeito, e só o papel assinado evita a briga antes que ela comece." |
| 9 | "Na sua fazenda, alguém mora na casa que você cedeu sem nada assinado?" |
| 10 | DR. PELICIONI: "Eu sou o Dr. Pelicioni, advogado. Na casa do peão, o que não está no papel vira conta. Me segue pra proteger a sua terra." |

## Auditoria de padrão ouro: 22/23
Única falta: A3 (um "estranho" em contraste), que não cabe neste tema. Tabela completa em
`tools/video/agro-arte/auditar_roteiro.py falas_exemplo_moradia_peao.json`.

## Fatos
- **Lei 5.889/1973, art. 9º** (texto atualizado da Câmara, lido em 23/11/2026,
  https://www2.camara.leg.br/legin/fed/lei/1970-1979/lei-5889-8-junho-1973-357971-normaatualizada-pl.html):
  - "a) até o limite de 20% (vinte por cento) pela ocupação da morada", calculado sobre o salário-mínimo;
  - § 1º: as deduções "deverão ser previamente autorizadas, sem o que serão nulas de pleno direito";
  - § 3º: findo o contrato, o empregado deve "desocupar a casa dentro de trinta dias";
  - § 5º: "A cessão pelo empregador, de moradia e de sua infra-estrutura básica, […] não integram o salário do trabalhador
    rural, desde que caracterizados como tais, em contrato escrito celebrado entre as partes, com testemunhas e notificação
    obrigatória ao respectivo sindicato de trabalhadores rurais." (incluído pela Lei 9.300/1996)
- **Reflexos (fala 5):** decisões do TRT-3 e do TRT-23 tratam a moradia sem contrato como salário in natura, com reflexos
  (Jusbrasil, notícia do TRT-3; CSJT, notícia do TRT-23, Súmula 22). São fontes secundárias, por isso a fala diz "pode".
- **Prazo (fala 6):** CF, art. 7º, XXIX: cinco anos para cobrar, "até o limite de dois anos após a extinção do contrato".
  **Conferir o texto literal antes do render.**
- **Divergência (fala 7):** TST, Súmula 367, I: a habitação "indispensável para a realização do trabalho" não tem natureza
  salarial. Há acórdão do TRT-3 que afastou o caráter salarial mesmo sem contrato. **Conferir a súmula no site do TST antes
  do render.**

## Cuidados
- A fala 1 diz "pode estar ganhando salário", não "está", porque depende do caso.
- A fala 7 é a virada honesta: a moradia que o trabalho exige pode não ser salário. A fala 8 explica por que o contrato
  continua sendo o caminho seguro.
- Nada de oferecer serviço: o fecho segue o padrão dos outros vídeos.

## Plano de imagem (código + Higgsfield nas cenas com gente)
- **Higgsfield (Seedance 2.0 Mini, cerca de 5 créditos por clipe de 5 s; 2.5 só se o Mini reprovar no crivo):** só planos
  abertos, sem close de rosto nem de mão. As 3 cenas somam uns 12 s:
  1. Abertura (fala 1): o peão de chapéu chega à casinha simples da fazenda no fim da tarde; a mulher na varanda.
  2. Fala 5: o casal na varanda, de longe, com a luz da cozinha acesa.
  3. Fala 7: o vaqueiro a cavalo, de costas, vigiando o gado à noite com lanterna.
- **Pinturas em código** (no mínimo 70% do tempo, sem gente):
  - falas 2 e 3: a mesa com o contrato e a caneta;
  - fala 4: a sede do sindicato rural numa praça de cidade pequena;
  - fala 6: a casa vazia, com a porta aberta e o caminho indo embora;
  - falas 8 e 9: o papel assinado e carimbado.
  Mestres ainda não usados nos vídeos anteriores.
- **Cartões:** Lei 5.889, art. 9º, § 5º; Súmula 367 do TST.
- **Capa:** "A CASA DO PEÃO VIRA SALÁRIO?" sobre a cena 1.
- **Crivo de qualidade em todas as cenas de gente** antes da montagem.
