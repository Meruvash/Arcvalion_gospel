# Novela "Herança do Pai" — Parte 1: "Vendeu a minha parte pelas costas" (roteiro v1, 22/11/2026)

- **Para onde vai:** o outro Instagram do editor. É o primeiro teste do formato "novela em prints" (ver
  `../ANALISE_MODELO.md`).
- **Formato:** 9:16, 1080×1920, cerca de 70 s. A história corre em telas de WhatsApp feitas em HTML próprio, sem logotipo,
  com nomes e números fictícios. As vozes são áudios de WhatsApp na ElevenLabs. Cenas de IA só **sem gente**: porteira,
  mesa da cozinha, retrato antigo virado.
- **Aviso fixo no canto:** "DRAMATIZAÇÃO · história ilustrativa". O cartão da lei leva a fonte real.
- **Estrutura do modelo:** gancho com erro sem volta, humilhação, verdade que ninguém acredita, prova, vilão desaba, e
  gancho para a parte 2.

## Personagens (fictícios)
| Personagem | Papel | Etiqueta na 1ª aparição |
|---|---|---|
| **Rosa** | irmã do meio, cuida da fazenda, 50 anos | "ROSA · ficou com o pai até o fim" |
| **Valdir** | irmão mais velho, mora na cidade, arrogante | "VALDIR · o irmão mais velho" |
| **Zé** | caçula, assustado | "ZÉ · o caçula" |
| **Dr. Tavares** | comprador de Goiânia, frio e educado | "O COMPRADOR" |

## Roteiro

| # | Tempo | Tela | Voz / texto |
|---|---|---|---|
| 1 | 0–3 s | Grupo **"Herança do Pai 🌾"**. A mensagem chega com o "plim". Etiqueta VALDIR | Texto do Valdir: "Vendi minha parte da fazenda. Já assinei no cartório. Não adianta chorar." |
| 2 | 3–9 s | Rosa digitando, depois a resposta | Rosa (texto): "Vendeu?? Sem falar com a gente?" · **Áudio do Valdir:** "Falar o quê, Rosa? Você nunca teve dinheiro nem pra adubo. Agora quem manda lá é o doutor Tavares." |
| 3 | 9–17 s | Conversa nova, de número desconhecido: "Dr. Tavares (Goiânia)". Ele manda uma foto da porteira da fazenda (IA, sem gente) | **Áudio do Tavares:** "Dona Rosa, boa tarde. Segunda-feira eu chego com o trator. A senhora vai ter que se acostumar com o sócio novo." |
| 4 | 17–23 s | Mesa da cozinha: café frio e retrato antigo do pai em moldura (IA, sem gente). Por cima, a conversa com o Zé | Rosa → Zé: "O Valdir vendeu pra um estranho. A terra do pai, Zé." · Zé: "E agora, Rosa? A gente não tem esse dinheiro…" |
| 5 | 23–29 s | De volta ao grupo. Valdir manda figurinha rindo (desenho nosso) | Valdir (texto): "Quem tem dinheiro compra. Quem não tem, chora 😂" — **pico da humilhação** |
| 6 | 29–39 s | Rosa manda **foto de uma página do Código Civil** com o artigo grifado em amarelo (cartão 1) | Rosa (texto): "Lê isso, Valdir." · **Áudio da Rosa:** "Tanto por tanto, Valdir. Pelo mesmo preço que o doutor pagou, a tua parte fica comigo." |
| 7 | 39–49 s | Valdir digitando… Resposta seca. Cartão 2 com o art. 1.795 | Valdir: "E quem te avisou? Ninguém. Já era." · **Áudio da Rosa:** "Justamente. Ninguém me avisou. Então a lei me dá cento e oitenta dias pra depositar o preço e ficar com a parte." |
| 8 | 49–55 s | Valdir "digitando…" três vezes, depois **"🚫 Esta mensagem foi apagada"**. O Zé manda 🙌. Na conversa do Tavares: "Dona Rosa, podemos conversar?" | (só som de notificação) |
| 9 | 55–63 s | Cartela de fundo escuro com as duas regras e a fonte | **Dr. Pelicioni** (clone, S neutro): "Herança ainda não dividida: irmão tem preferência sobre comprador de fora. E o prazo é de cento e oitenta dias. Perdeu, não volta." |
| 10 | 63–70 s | Gancho: chega mensagem do Tavares. Tela congela. Letreiro **"PARTE 2"** | Tavares (texto): "A senhora tem os dois milhões, dona Rosa? Porque eu paguei à vista." |

**Legenda na tela:** amarela, palavra por palavra, só nos áudios. As mensagens de texto aparecem e o público lê.

## Fatos jurídicos (lidos na fonte em 16/11/2026, em `../../roteiros/heranca-irmao-vendeu.md`)
Código Civil (Lei 10.406/2002), texto publicado pelo Senado Federal:
https://legis.senado.leg.br/norma/552282/publicacao/15676634
- **Art. 1.794:** "O co-herdeiro não poderá ceder a sua quota hereditária a pessoa estranha à sucessão, se outro
  co-herdeiro a quiser, tanto por tanto." É o cartão 1.
- **Art. 1.795:** "O co-herdeiro, a quem não se der conhecimento da cessão, poderá, depositado o preço, haver para si a
  quota cedida a estranho, se o requerer até cento e oitenta dias após a transmissão." É o cartão 2.
- **Art. 1.791, parágrafo único:** até a partilha, a herança é indivisível e segue as regras do condomínio. Por isso a
  fala 9 diz "herança ainda não dividida".

**Ficção (não é fato):** os nomes, o valor de "dois milhões", a porteira, o trator e o cartório.

## Vozes (amostras em `voz/amostras/`, para o editor escolher)
| Personagem | Candidatas (ElevenLabs, PT-BR) |
|---|---|
| Rosa | Scheila (sério, direto) · Carla Rural · Fernanda (formal) |
| Valdir | Adriano (grave, rústico) · Otto (intimidador) · David (grave) |
| Dr. Tavares | Cassio Cruz (confiante, formal) · Rafael Valente (suave) |
| Dr. Pelicioni | clone, só por `voz_editor_s_neutro.py` |
