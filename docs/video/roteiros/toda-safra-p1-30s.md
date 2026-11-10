# "Toda safra deixa uma conta", Parte 1 (versão de 30 s): roteiro para aprovação (PORTÃO 1)

Gerado com `docs/video/PROMPT_SERIE_ALONGAMENTO.md`. Quadrado 1080x1080, 30 fps. Nenhuma voz foi gerada: espera aprovação.

**ENTRADA usada:** série "Toda safra deixa uma conta" · tema: prorrogação/alongamento de dívida rural · fatos F1, F2, F4
· personagens: você (produtor), o gerente da agência (antagonista que cumpre o manual), Seu Zé, vizinho de cerca
(aparece só no CTA nesta parte) · números fictícios: 50% da soja perdida, parcela de R$ 480.000, prazo de 30 dias,
cédula assinada em 12/3/2026 · Parte 1 · votação anterior: primeira parte · @: nenhum · duração-alvo: 30 s.

**Estética (vox-director em código):** arco `man_in_hole` · tema `newsprint-editorial` no azul do portal · recortes de
papel com borda rasgada, fita, retícula, sombra de papel · uma luz motivada por plano · acento mostarda #f0c24b ·
carimbo vermelho #b3202a. Painel de estado no topo: SAFRA · PARCELA · PRAZO · PEDIDO.

| # | Batida | Tempo | Fala (quem fala) | Plano (cenário · luz · enquadramento · câmera · movimento dos recortes) | Painel de estado (muda?) | Texto na tela |
|---|---|---|---|---|---|---|
| 1 | 1 Gancho | 0,0–1,8 | NARRADOR: "Você perdeu 50% da soja." | Lavoura em recortes de papel verde sobre mesa azul · sol baixo de papel laranja atrás · WIDE · `push_in` · metade das plantas de papel murcha e cai em sequência, um recorte de nuvem seca passa voando (o único "voador" do vídeo), retícula pulsa | SAFRA 100% → **50%** (cai e pisca em mostarda) | Título no topo, recortado: "A SECA LEVOU **METADE**." · rótulo: HISTÓRIA FICTÍCIA · REGRAS REAIS |
| 2 | 1 Gancho | 1,8–4,0 | NARRADOR: "Parcela de 480 mil. Vence em 30 dias." | Boleto/cédula em papel creme preso com fita, sobre a mesa · luminária de mesa · CLOSE · `pan` lateral · fita tremula, o valor é "carimbado" letra a letra, um calendário de papel arranca a folha | PARCELA **R$ 480.000** e PRAZO **30 DIAS** entram | "R$ 480.000" no papel · rótulo: CASO FICTÍCIO |
| 3 | 2 Recap/premissa | 4,0–5,5 | NARRADOR: "Hoje, os comentários decidem." | Cartão escuro de papel carvão com recortes de balões de comentário colados · luz de tela de celular · MEDIUM · `tilt` para cima · balões caem e assentam (`drop`) | não muda | Cartão: "OS COMENTÁRIOS DECIDEM · PARTE 1" |
| 4 | 3 Ação | 5,5–7,0 | NARRADOR: "Você vai à agência." | Fachada de agência em recorte de jornal, você (boneco de papel, chapéu de palha) entra pela direita · poste de luz · EST_WIDE · `parallax` · camadas de papel deslizam em profundidades diferentes, porta de papel abre | não muda | rótulo: AGÊNCIA · 8:58 |
| 5 | 3 Ação | 7,0–8,6 | NARRADOR: "Pede mais prazo." | Balcão; sua mão de papel desliza um formulário · luminária do balcão · CLOSE · `push_in` · formulário entra com `slap`, carimbo PROTOCOLO bate · por um segundo, no canto da cédula, a data "ASSINADA EM 12/3/2026" fica legível (batida 4, sem fala) | PEDIDO — → **PROTOCOLADO** (pisca) | rótulo: SOLICITAÇÃO DO MUTUÁRIO |
| 6 | 6 Hora + fala | 8,6–10,6 | NARRADOR: "O gerente aponta uma linha." | Gerente (boneco de papel, gravata, sobrancelha que atua) abre um recorte de página do MCR · luminária da mesa dele · MEDIUM · `pull_out` · dedo de papel desliza até a linha, marca-texto mostarda passa | não muda | rótulo: AGÊNCIA · 9:02 · O GERENTE · recorte "MCR 2-6-4" |
| 7 | 6 Hora + fala | 10,6–12,4 | GERENTE: "'Conveniência e decisão.' Do banco." | DETAIL do recorte: "por sua conveniência e decisão" (texto literal de F1) · mesma luminária · `static` curto + tremor no "Do banco." · sobrancelha do gerente sobe | PEDIDO **EM ANÁLISE** (pisca devagar) | o trecho literal, realçado em mostarda |
| 8 | 7 O que você não sabe | 12,4–15,2 | NARRADOR: "E aqui vai o que você não sabe." | Você sozinho na caminhonete de papel à noite · luz do painel do carro · MEDIUM · `tilt` para baixo · recortes de chuva de papel caem, limpador de para-brisa de papel vai e volta | não muda | rótulo: 21:40 · ESTRADA |
| 9 | 7 + 8 Isso é real | 15,2–18,6 | NARRADOR: "Para o STJ, alongar é direito do devedor." | Papel creme preso com 4 fitas sobre fundo azul-escuro · luz de cima · CLOSE · `push_in` lento · o texto literal da Súmula 298 (F4) aparece por linhas; "direito do devedor" é realçado no ritmo da fala | não muda | "SÚMULA 298 · STJ · 2004" + texto literal |
| 10 | 8 Isso é real | 18,6–19,8 | (sem fala; trilha e som do carimbo) | Mesmo papel · `static` (recompensa) · carimbo vermelho "REAL" cai com `slap` e tremor | não muda | Carimbo: **REAL** · rodapé: "Súmula 298, STJ, DJ 22/11/2004" |
| 11 | 9 Escolha | 19,8–22,4 | NARRADOR: "Se acha que o banco cede, insiste." | Dois recortes de botão sobre a mesa, o primeiro entra · luminária · WIDE · `pan` · botão INSISTE cai com `pop_settle`, um relógio de papel gira ao lado | PRAZO 30 DIAS pisca | Botão **INSISTE** · subtítulo "aposta os 30 dias no banco" |
| 12 | 9 Escolha | 22,4–24,6 | NARRADOR: "Se acha que não, Justiça." | Mesma mesa · `parallax` · botão JUSTIÇA entra com `pop_settle`, um martelo de papel bate de leve | não muda | Botão **JUSTIÇA** · subtítulo "o banco vira parte contrária" |
| 13 | 10 CTA | 24,6–26,4 | NARRADOR: "Comenta INSISTE ou JUSTIÇA." | Os dois cartões lado a lado · luz de tela de celular · MEDIUM · `push_in` · balão de comentário de papel pulsa | não muda | "SEU VOTO: INSISTE ou JUSTIÇA (comenta aqui)" |
| 14 | 10 CTA | 26,4–28,2 | NARRADOR: "Manda pro vizinho de cerca." | Cerca de arame em recorte; do outro lado, Seu Zé (boneco de papel) recebe a notificação · fim de tarde · WIDE · `pan` · papel do celular acende | não muda | rótulo: SEU ZÉ · VIZINHO DE CERCA |
| 15 | 10 CTA | 28,2–30,2 | NARRADOR: "A maioria escreve a Parte 2." | Cartela: recortes de todos os planos se juntam num álbum (`mg_scrapbook`, cartas assentam) · luz geral suave · WIDE · `pull_out` | painel congela | "A MAIORIA ESCREVE A PARTE 2" · "TODA SAFRA DEIXA UMA CONTA" · opaladino.com.br · fontes: Res. CMN 5.314/2026 e Súmula 298/STJ |

Legenda palavra por palavra em todos os planos, no terço de baixo (acima de y 1000), em blocos de até 4 palavras.

## Contagem
- **77 palavras** escritas (cerca de 89 faladas, porque números viram várias palavras: "cinquenta por cento", "quatrocentos e oitenta mil").
- A ~2,7 palavras/s, isso daria ~29–33 s. A voz da Parte 0 (Adriano, velocidade 1,18) leu 80 palavras parecidas em 30,9 s, e a cartela de 2 s está somada. Fecha em **~30 s**; se passar, corto o plano 8 para "Aqui vai o que você não sabe" (7 palavras).
- **15 planos em 30 s**: um novo a cada 2,0 s em média.

## Fatos usados
- **F1** (Res. CMN 5.314/2026, MCR 2-6-4): o banco prorroga "por sua conveniência e decisão" (plano 7, trecho literal); "mediante solicitação do mutuário" (plano 5, rótulo "SOLICITAÇÃO DO MUTUÁRIO" e PEDIDO PROTOCOLADO).
- **F2** (frustração de safras por fatores adversos): é o motivo da história (plano 1). Não é narrado como regra nesta parte; guardado para a Parte 2.
- **F4** (Súmula 298 do STJ): plano 9, paráfrase falada ("alongar é direito do devedor") e texto literal no papel.
- **Números fictícios** (rotulados "caso fictício"): 50% da soja, R$ 480.000, 30 dias, cédula de 12/3/2026, horários 8:58, 9:02 e 21:40.

## As 2 opções e o preço
- **INSISTE** (se você acha que o banco cede): você aposta os 30 dias de prazo na boa vontade da agência. Se ela disser não perto do vencimento, a parcela vence.
- **JUSTIÇA** (se você acha que não cede): o banco que financia a sua próxima safra vira parte contrária, e quem decide é um juiz, não a agência.
- Nenhuma das duas é apresentada como a certa: F1 dá ao banco a decisão, F4 chama de direito do devedor, e a Parte 2 mostra o que cada caminho custa.

## Fio solto para a Parte 2
A data que aparece "por um segundo" no plano 5: **cédula assinada em 12/3/2026, antes de a regra nova entrar em vigor (1º/7/2026)**. A pergunta da Parte 2: "A regra de julho vale para um contrato de março?". O tema está em disputa, e a Parte 2 mostra os dois lados sem resolver por conta própria.

## Autochecagem
| Item | Situação |
|---|---|
| Batida 1, Gancho | Presente (planos 1–2): "você" + 50% + R$ 480.000 + 30 dias; título em 2 cores. |
| Batida 2, Recap pelo voto | Presente como premissa da Parte 1 (plano 3): "Hoje, os comentários decidem." Sem %, porque não houve votação anterior. |
| Batida 3, Ação | Presente (planos 4–5), com a regra "mediante solicitação" virando ação (o formulário e o carimbo). |
| Batida 4, Semente de mistério | **Só imagem** (plano 5): a data da cédula aparece por um segundo, sem fala. Narrar custaria ~4 s que a versão de 30 s não tem. |
| Batida 5, Silêncio e escolha forçada | **Cortada.** Exige 3 ou mais frases de tentativas que falham (~10 s). Volta na versão de 100 s. |
| Batida 6, Hora + fala citada | Presente (planos 6–7): "AGÊNCIA · 9:02" e a fala do gerente com trecho literal de F1. |
| Batida 7, "O que você não sabe" | Presente (planos 8–9), com frase fixa e uma regra real (F4). |
| Batida 8, "Isso é real" | Presente (planos 9–10): papel creme com fita, texto literal, carimbo REAL. Sem "PESSOAS DE INTERESSE", porque não há @ para creditar. |
| Batida 9, Escolha com preço | Presente (planos 11–12), no formato "Se acha que…, …", duas opções de uma palavra, preço escrito. |
| Batida 10, CTA | Presente (planos 13–15): "Comenta INSISTE ou JUSTIÇA", compartilhamento ligado à história e "A maioria escreve a Parte 2." |
| Frases até 8 palavras | Todas. As maiores têm exatamente 8: "E aqui vai o que você não sabe." e "Para o STJ, alongar é direito do devedor.". |
| Pelo menos 3 números concretos | 50%, R$ 480.000, 30 dias, 298, 2004, 9:02. |
| Nenhum fato fora da lista F | Ok. Os números da história estão rotulados como fictícios. |
| Citação inalterada | "conveniência e decisão" é trecho contínuo de F1. O texto da súmula vai na tela letra por letra. |
| Sem serviço jurídico | Ok. "Justiça" é uma opção da história, sem indicação de advogado nem contato. |
| CTA termina em "A maioria escreve a Parte N+1." | Sim: "A maioria escreve a Parte 2." |
