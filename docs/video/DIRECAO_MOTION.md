# Direção de motion: todo movimento tem função (pedido do editor, 25/11/2026)

> "Não se utiliza 3D para fazer um cenário sem que haja uma finalidade, tipo mostrar o mapa por cima, ampliar, tirar daqui
> e subir para uma imagem de mapa. Precisa ter uma utilidade. […] Você está ignorando os princípios de motion, os
> princípios de direção." (editor, depois do teste 3D de uma porteira no meio do nada)

Vale junto com `DIRECAO_ARTISTICA.md`:
- **Direção artística** cuida de como cada quadro é bonito.
- **Este arquivo** cuida de **por que algo se move, aparece ou é 3D**.

As fontes estão no fim do arquivo.

## 1. A regra-mãe: função antes da forma
Toda cena, todo movimento de câmera, todo 3D e todo letreiro animado tem **um trabalho que cabe numa frase**. O trabalho
sai desta lista:

| Função | O que faz | Exemplo no agro |
|---|---|---|
| **LOCALIZAR** | Diz onde a coisa acontece, do geral para o particular | Do mapa do Brasil ao estado, ao município e à divisa entre duas fazendas |
| **REVELAR** | Mostra algo que a narração acabou de dizer ou vai virar | Aproximação lenta da porteira quando a fala diz "fechou a estrada" |
| **COMPARAR** | Põe duas coisas lado a lado ou em antes e depois | A porteira trancada e a mesma porteira aberta, no mesmo enquadramento |
| **TRANSFORMAR** | Uma coisa vira outra e explica a mudança | A estrada pintada vira a linha amarela no mapa (corte por forma) |
| **MEDIR** | Faz número e prazo virarem tamanho ou tempo visível | Uma régua de 10 e de 20 anos crescendo sobre a estrada |
| **CAUSA E EFEITO** | Mostra a ação e a consequência em sequência | O cadeado fecha e o caminho no mapa fica vermelho |
| **ENFATIZAR** | Segura o olho na palavra-chave | O carimbo "SERVIDÃO" entrando no ponto exato da fala |

**Teste:** se ninguém consegue dizer a função em uma frase, a cena não se move, ou sai.
- Pintura de respiro pode existir, mas só com vida sutil (vento, luz, água), nunca com câmera fazendo "passeio".
- **Decoração não é função:** "fica bonito", "mostra que a gente sabe 3D" ou "dar movimento" não justificam nada.

## 2. Quando usar 3D (e quando não)
**3D só para espaço e geografia,** quando a relação entre lugares é a mensagem. Exemplos:
- o mapa visto de cima;
- a fazenda presa entre outras sem saída para a estrada;
- o caminho que atravessa a terra do vizinho;
- divisas, distâncias, área de preservação ao longo do rio;
- o sobrevoo que sai do mapa e desce até a propriedade.

Nesses casos, a câmera 3D faz o que a pintura não faz: **sobe, amplia, gira para mostrar a relação e desce de volta**.

**Proibido:** cenário 3D decorativo, como a porteira no meio do nada, árvores enfeitando ou "vitrine de capacidade". O
teste de 25/11/2026 ("teste-3d-porteira") é o exemplo do que não fazer: câmera girando sem motivo, sem informação nova.

O 3D do canal é **mapa e maquete com informação**:
- relevo simples e legível;
- divisas em linha;
- o caminho em cor de destaque;
- rótulos que aparecem na hora da fala.

## 3. Câmera motivada
Movimento motivado não chama atenção para si; movimento sem motivo chama.

- **Aproximação lenta (push-in):** quando a narração revela algo ou aponta o perigo. Começa **junto da palavra-chave**,
  não antes, porque, se começa cedo, entrega a revelação.
- **Afastamento (pull-out):** para dar contexto ("e não é só ele…") ou mostrar o tamanho da coisa.
- **Panorâmica e travelling:** seguem uma linha que existe na cena (estrada, rio, cerca), no sentido da leitura.
- **Câmera parada:** quando nada muda na informação. Parada não é erro; movimento à toa é.
- **Uma câmera por plano:** nada de zoom, giro e deslocamento ao mesmo tempo.

## 4. Contraste e afinidade: a curva de intensidade (Bruce Block)
Contraste visual (claro e escuro, cor quente e fria, diagonal e horizontal, ritmo rápido e lento) **sobe a intensidade**.
Afinidade (tudo parecido) **baixa**. Cada roteiro tem uma curva planejada:

| Batida | Intensidade | Como |
|---|---|---|
| Gancho (fala 1) | alta | contraste de valor e de cor, diagonal, o carimbo batendo, corte seco |
| Explicação (falas 2 a 5) | média-baixa | afinidade: paleta próxima, horizontais, câmera lenta, cortes por continuidade |
| Virada ("Agora, cuidado") | alta | muda a temperatura da cor (quente para fria, ou o inverso), entra a diagonal, ritmo mais curto |
| Fecho e pergunta | baixa | volta à afinidade e à luz quente, câmera parada |

## 5. Hierarquia no tempo (encenação)
- **Uma coisa importante se move por vez.** O que se move é o que importa. Se tudo anima junto, o olho não acha nada.
- **Ordem de entrada:** primeiro o ambiente, depois o foco, depois o letreiro, nunca tudo junto.
- **Letreiro e carimbo** entram depois que o olho já achou o foco e nunca o cobrem (`DIRECAO_ARTISTICA.md`, A10).

## 6. Tempo e curvas (os 12 princípios, aplicados a motion)
- **Easing sempre:** aceleração e desaceleração suaves. Linear só em fumaça, água e nuvem.
- **Antecipação e assentamento:** o carimbo sobe um pouco antes de bater, o letreiro passa 2 a 4% do lugar e volta.
- **Ritmo pela narração:** cada fala é uma batida. Corte e entrada caem na sílaba tônica da palavra-chave, com a marca de
  tempo de `tempos.json`.
- **Continuidade:** quando a cena troca, algo continua: forma, cor, direção do movimento ou a linha da estrada. A transição
  com motivo (corte por forma, zoom que continua na próxima cena, mapa que vira pintura) vale mais que fusão genérica
  entre tudo.

## 7. Linguagem visual do vídeo (antes de produzir)
O fluxo dos estúdios de explicação:
1. **Referência:** o mestre ou os mestres, a paleta e a luz.
2. **2 ou 3 quadros de estilo (style frames)** perto do acabamento final.
3. **Aprovação junto com o roteiro.**
4. **Produção.**

Num vídeo: uma paleta, uma família de letreiro, uma lógica de luz. Uma linguagem nova (3D, mapa, colagem) só entra
quando a função da seção 1 pede, e com o mesmo acabamento.

## 8. O plano de imagem do roteiro (formato obrigatório)
Toda linha do plano diz a função e por que aquele movimento:

| Falas | Cena | Função | Movimento | Por que este movimento |
|---|---|---|---|---|
| 1 | Porteira trancada (Parreiras) | REVELAR | Aproximação lenta a partir de "fechou" | A notícia é a porteira fechada: o olho chega nela junto com a fala |

Linha sem função preenchida não entra.

## 9. Crivo de motion (M1 a M8, antes de mandar ao editor)
| # | Pergunta | Reprova se |
|---|---|---|
| M1 | Cada cena tem função da lista, escrita no plano? | Cena "bonita" sem trabalho |
| M2 | Todo 3D mostra espaço ou geografia com informação? | 3D decorativo |
| M3 | Todo movimento de câmera é motivado e começa na palavra certa? | Câmera passeando; revelação antes da fala |
| M4 | Uma coisa importante se move por vez? | Vários elementos animando juntos |
| M5 | A curva de intensidade segue o plano (gancho alto, explicação baixa, virada alta)? | Tudo no mesmo tom |
| M6 | Há easing, antecipação e assentamento nos letreiros e carimbos? | Movimento linear e duro |
| M7 | As transições têm continuidade (forma, cor, direção)? | Corte ou fusão sem relação entre as cenas |
| M8 | A linguagem visual é única no vídeo? | Estilos misturados sem motivo |

## Fontes (lidas em 25/11/2026)
- **Função como regra-mãe:** Made Good Designs, "Motion Design Principles"
  (https://madegooddesigns.com/motion-design-principles/); Clay, "Motion Design Principles"
  (https://clay.global/blog/web-design-guide/motion-design-principles); lista de funções (orientar, focar, expressar,
  ligar causa e efeito) em https://www.skillsdirectory.com/skills/intense-visions-design-motion-principles.
- **Contraste e afinidade, componentes visuais:** Bruce Block, *The Visual Story* (Routledge, capítulo em
  https://www.routledge.com/rsc/downloads/Chapter_9_from_The_Visual_Story_3e_9781315794839.pdf; resumo em
  http://filmbooknotes.blogspot.com/2013/05/the-visual-story-by-bruce-block.html).
- **Câmera motivada:** HowToFilmSchool (https://howtofilmschool.com/dictionary/motivated-camera-movement/); AeliaVision,
  "Motivated Movement Guide" (https://aeliavision.com/motivated-movement-guide/).
- **Mapa em explicação** (do geral ao local, de 8 a 20 s por batida de mapa): https://mapanimation.io/guide/camera-guide;
  https://github.com/iart-ai/map-animation-skills.
- **Quadros de estilo e linguagem visual:** Futur, "Motion Design Process – Art Direction & Style Frames"
  (https://www.classcentral.com/course/youtube-motion-design-process-art-direction-style-frames-109064);
  https://alchemybranding.studio/how-style-frames-can-help-you-meet-your-video-deadline;
  https://isla-studio.com/en/services/art-direction/.
- **12 princípios aplicados a motion:** Thomas e Johnston, *The Illusion of Life* (1981); Adobe
  (https://www.adobe.com/creativecloud/animation/discover/principles-of-animation.html); PremiumBeat
  (https://www.premiumbeat.com/blog/animation-easing-anticipation-follow-through/); Freepik
  (https://www.freepik.com/blog/animation-principles-in-motion-design).
