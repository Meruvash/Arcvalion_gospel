# Elenco fixo das novelas (proposta, 23/11/2026)

Pedido do editor: personagens fixos, para dar consistência e fazer o público querer acompanhar. Cada um se baseia num
arquétipo consolidado. Nome, voz e aparência foram escolhidos com critério.

**Regra de inspiração.** Das obras de sucesso tiramos só a **função** do personagem e o **código visual** (cor, objeto,
postura). Não tiramos o nome, a fala famosa, o rosto do ator nem o figurino idêntico, e nenhum personagem gerado pode
parecer um ator real.

## 1. O universo
- **Lugar:** uma cidade fictícia do interior, a **Vila do Jatobá**, que se repete em todos os episódios.
- **Elenco:** o mesmo, com uma família no centro (os irmãos Rosa e Valdir) e um vizinho.
- **Novos personagens:** cada episódio é um caso jurídico novo, mas quem traz o caso, sofre e trama é sempre alguém
  deste elenco. Personagens de fora entram só como figurante do caso: comprador, gerente, corretor.
- **Por que funciona:** o público volta para ver **o que a Cleide vai aprontar agora** e **como o doutor vai virar o
  jogo**, como nas novelas de vilã forte.

## 2. Os papéis (arquétipos de Vogler e Campbell, mais o que a teledramaturgia brasileira consagrou)

| Personagem | Arquétipo | Inspiração (só a função) | Função na série |
|---|---|---|---|
| **Dr. Pelicioni** | Mentor-herói | Vito Corleone, Joseph e Jonathan Joestar (`PERSONAGEM_DR_PELICIONI.md`) | Chega na virada, prevê o passo do vilão, resolve com a lei e protege |
| **Dona Rosa** | Heroína humilde, a "mãe-coragem" | Maria do Carmo (*Senhora do Destino*, 2004); Lurdes (*Amor de Mãe*, 2019) | Quem o público defende. Sofre, é desacreditada e vira o jogo com o doutor |
| **Valdir** | Sombra próxima: o irmão invejoso | Caim (Gn 4) e os irmãos de José (Gn 37). Combina com a linha do portal | Humilha, vende pelas costas e perde. Volta a tentar em outros episódios |
| **Cleide** | **Vilã-mor**, a que muda de cara (doce em público, venenosa no privado) | Carminha (*Avenida Brasil*, 2012), Nazaré Tedesco (*Senhora do Destino*, 2004), Odete Roitman (*Vale Tudo*, 1988) | Mulher do Valdir e cérebro das tramas. A personagem que o público "ama odiar", que segura a audiência |
| **Tavares** | Trapaceiro: o falso poderoso | Odorico Paraguaçu (*O Bem-Amado*, 1973): o falador engomado | Corretor e "doutor" de fachada que a Cleide contrata. É desmascarado sempre |
| **Seu Antônio** | Sábio humilde | O velho da roça que sabe das coisas, figura clássica das novelas rurais (*O Rei do Gado*, 1996; *Pantanal*, 1990) | Vizinho arrendatário. Dá conselho, prova que "o pequeno tem direito" e é vítima em episódios próprios |
| **Bruna** | Arauto e aliada jovem | A moça independente da roça, como a Juma Marruá (*Pantanal*, 1990) | Filha da Rosa. Grava tudo, chama o doutor e põe ele no grupo. É a jovem do público |
| **Zuleide** | Escudeira leal e alívio cômico | Tom Hagen (*O Poderoso Chefão*), o conselheiro discreto, com o calor de uma secretária do interior | Secretária do doutor. "O doutor já leu o seu caso." Faz a ponte entre um episódio e outro sem pedir contratação |

**O triângulo que segura a série:** Cleide e Valdir contra Rosa e Bruna, com o Dr. Pelicioni na virada. Seu Antônio,
Tavares e Zuleide giram em volta.

## 3. Nomes (com o critério e a fonte)
Fonte: IBGE, Censo 2010, frequência de nascimentos por década
(https://servicodados.ibge.gov.br/api/v2/censos/nomes/{nome}, consultado em 23/11/2026).

| Nome | Pico de nascimentos | Idade que o nome "passa" | Idade do personagem |
|---|---|---|---|
| Rosa | 1960–69 (71.023) | 55 a 65 anos | 56 ✔ |
| Valdir | 1960–69 (57.888) | 55 a 65 anos | 59 ✔ |
| Cleide | 1970–79 (33.284) | 45 a 55 anos | 50 ✔ |
| Antônio | 1960–69 (531.596) | qualquer idade, e é o mais comum | 72 ✔ |
| Bruna | 1990–99 (243.948) | 25 a 35 anos | 27 ✔ |
| Zuleide | 1960–69 (6.361), raro | 55 a 65 anos, e é fácil de lembrar | 60 ✔ |
| Tavares | sobrenome (só 83 nascimentos de 1960 a 1969 com esse primeiro nome) | chamado pelo sobrenome, como corretor | 45 ✔ |

**Critérios:**
- **Iniciais diferentes** (P, R, V, C, T, A, B, Z), para o público não confundir os nomes na legenda.
- **Nomes de 2 a 3 sílabas.**
- **Nome que combina com a idade**, pelo IBGE.
- **Sem nome de pessoa famosa** nem de personagem de novela.

## 4. Voz (ElevenLabs, amostras em `elenco/voz/`)
Todas as amostras foram geradas com eleven_multilingual_v2, style 0, e conferidas por transcrição (scribe_v1): o texto
saiu certo em todas. O editor escolhe uma de cada par.

| Personagem | Opção A | Opção B | O que a voz precisa ter |
|---|---|---|---|
| Dr. Pelicioni | voz clonada do editor (`voz_editor_s_neutro.py`) | — | calma, grave, sem "S" chiado |
| Rosa | `rosa_edna` (Edna: calorosa, maternal) | `rosa_lucinda` (Lucinda: terrosa, rouca) | humilde e firme, que dá pena e depois dá orgulho |
| Valdir | `valdir_adriano` (Adriano: grave, áspero) | `valdir_sergio` (Sergio: grave, decidido) | arrogante, de quem "tem dinheiro" |
| Cleide | `cleide_bianca` (Bianca: rouca, com malícia) | `cleide_elena` (Elena: elegante, falsa doçura) | doce na superfície e veneno embaixo |
| Tavares | `tavares_diego` (Diego: locutor de comercial) | `tavares_cassio` (Cassio Cruz) | voz de vendedor, segura demais |
| Seu Antônio | `antonio_manoel` (Manoel Lopes: idoso, caloroso) | `antonio_jairo` (Jairo Moraes: 60 anos, sotaque do interior) | voz de roça, lenta e sábia |
| Bruna | `bruna_raquel` (Raquel: jovem, enérgica) | `bruna_roberta` (Roberta: jovem, segura) | rápida, de quem resolve |
| Zuleide | `zuleide_lucinda` (Lucinda) | `zuleide_amandoca` (Amandoca: divertida) | simpática, cômica sem ser boba |

Depois da escolha, cada personagem fica com **uma voz e um ajuste fixos para sempre**. Isso é registrado aqui.

## 5. Aparência (código visual)
Inspiração: o **código de cor** das novelas de sucesso. A vilã se veste de cor forte, estampa animal e dourado; a
heroína, de cor suave e estampa simples; o poderoso, de azul-escuro e sobriedade. Cada personagem tem **um objeto de
marca**, para ser reconhecido em 1 segundo, mesmo pela foto de perfil do WhatsApp.

| Personagem | Rosto e corpo | Figurino fixo | Objeto de marca | Cor dele |
|---|---|---|---|---|
| Dr. Pelicioni | foto e vídeo reais do editor | blazer azul-marinho, lenço de bolso com bolinhas, camisa azul-clara | o lenço de bolso | azul-marinho |
| Rosa | 56 anos, pele morena de sol, cabelo escuro com fios brancos, preso | blusa de algodão florida, avental às vezes | o livro do pai | rosa-claro e verde |
| Valdir | 59 anos, barriga, bigode grisalho, pele vermelha de sol | camisa xadrez para dentro da calça, cinto de fivela grande, chapéu branco | corrente de ouro e chave de caminhonete | marrom e dourado |
| Cleide | 50 anos, cabelo loiro tingido e escovado, unhas longas vermelhas | blusa de oncinha ou vermelha, brincos grandes dourados | o celular sempre filmando | vermelho e oncinha |
| Tavares | 45 anos, cabelo com gel para trás, bronzeado de academia | terno brilhante um número menor, sem gravata | óculos espelhados e pasta de couro | cinza brilhante |
| Seu Antônio | 72 anos, barba branca rala, rosto marcado | camisa de botão gasta, chapéu de palha | o chapéu de palha | bege e azul desbotado |
| Bruna | 27 anos, cabelo cacheado solto, sardas | camiseta lisa e jaqueta jeans | celular com capinha rachada | amarelo |
| Zuleide | 60 anos, cabelo curto grisalho, batom discreto | cardigã, óculos de leitura na correntinha | a xícara de cafezinho | lilás |

**Como manter o rosto igual em todos os episódios:**
1. Gerar **uma folha de personagem por pessoa**, uma vez só: 5 poses (frente, três-quartos dos dois lados, perfil e
   close), fundo neutro. O editor aprova cada folha.
2. Usar essa folha como **imagem de referência em todo plano**, com o mesmo texto de descrição sempre.
3. Na decupagem:
   - 1 ou 2 personagens por plano;
   - plano médio ou close de rosto;
   - pouca mão em ação;
   - cortes de 2 a 8 s.

**Regras:**
- **Gente gerada por IA:** a regra do projeto contra gente gerada por IA vale para o agro. Nesta série o editor pediu
  personagens humanos. O Dr. Pelicioni continua só com imagem real.
- **Rótulo:** todo post leva o rótulo de IA do Instagram e o aviso "dramatização".

## 6. O que muda nos roteiros V1 a V3
- **V1, "O livro do pai":** já usa Rosa, Valdir e Tavares. Entra a Cleide no grupo, como quem ri e manda "joga no
  lixo", e a Bruna, que adiciona o doutor.
- **V2, "O doutor falso":** o Tavares é o falso doutor, e quem o contratou é a Cleide.
- **V3, "O arrendatário":** o Marcos sai. O comprador que quer tirar Seu Antônio é o Valdir, com a Cleide por trás.
- **Gancho fixo de série:** a Cleide nunca é presa nem some. Ela perde e jura voltar, como nas novelas de vilã forte.
