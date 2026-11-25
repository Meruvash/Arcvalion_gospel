# Parte 2 · «Barulho de fazenda»: roteiro alternativo à v3 «O vídeo inteiro» (para aprovação, 25/11/2026)

**Nenhum crédito gasto.** Fonte do roteiro: `v3b_barulho_de_fazenda.json` (auditor e renderizador leem o JSON).
Formato: Drama do Higgsfield, Seedance 2.5 em 720p e 9:16, cerca de 89 s.

## 1. O que eu extraí do repositório (o padrão que este vídeo segue)

| Camada | Regra | Onde está |
|---|---|---|
| Produto | novelinha do outro Instagram, Reels vertical de 60 a 90 s em cena atuada, elenco fixo da Vila do Jatobá | `.claude/skills/novela/SKILL.md` |
| Protagonista | o Dr. Pelicioni só aparece na virada, faz uma **previsão inteligente** (4 testes), resolve com a lei lida na fonte e protege a vítima. Fala de Corleone: curta, baixa, sem ponto de exclamação | `PERSONAGEM_DR_PELICIONI.md` |
| Limites da OAB | nada de "garanto", promessa de resultado, "contrate" ou "honorários" (O9); o editor confere o Provimento 205/2021 | idem |
| Elenco | Rosa (heroína), Cleide (vilã-mor, doce em público), Valdir (irmão invejoso), Bruna (aliada que grava e chama o doutor), com figurino, objeto de marca e voz fixos | `ELENCO_FIXO.md`, `drama_prompt.py` |
| Fórmula | gancho de 0 a 3 s, 2 ou mais humilhações diante de testemunhas, descrença, objeto desprezado que decide, virada entre 48% e 81%, queda, proteção, dinheiro dito, gancho final; nota de 0,85 ou mais | `FORMULAS_NOVELA.md`, `auditar_novela.py` |
| Padrão ouro | assinatura sensorial, bordão, riso de 2 a 4 s, ruptura, confissão entre 70% e 88%, gancho congelado, redenção sem fechar a história | `PADRAO_OURO_NOVELA.md` (avisos A5 a A8) |
| Teste da história | 3 frases, a prova prova, o público viu antes, o Dr. muda a situação com um gesto, o final responde ao começo | `REGRAS_ROTEIRO.md` §10 (lição da V2c) |
| Aura do Dr. | entrada, previsão, lei, dedução, fecho, com alguém dando razão a ele | pedido do editor, 25/11 |
| Plano | um falante por plano, até 10 palavras, fala começando entre 0,6 e 0,8 s, 1 s ou mais de silêncio no fim, rosto em três quartos, "No music, no subtitles" | `AUDITORIA_V2C.md` §7 |
| Pronúncia | não se falam: renúncia, calúnia, anca, novilha, roça, mamadeira. Guia no prompt: herança, março, Rosinha, Cleide | `producao_v3/LEIA_PRIMEIRO.md` |
| Áudio errado | primeiro se conserta só o áudio; o plano só se regera com a boca errada e com o OK do editor | skill, passo 7 |
| Voz do Dr. | o Seedance não clona: `voice_change` com o clone `95b656d3…` só no trecho do Dr. (1 crédito) | `AUDITORIA_V2C.md` §3 |
| Ordem das referências | placa do quadro, depois o lugar, os personagens, os objetos e as vozes ("@AudioN is the voice of @ImageM") | `drama_prompt.py` |
| Montagem | cortes de 0,25 s antes a 0,4 s depois da fala, -19 LUFS, legenda amarela, cartão da lei como inserto, aviso "DRAMATIZAÇÃO · PERSONAGENS FICTÍCIOS" | `montar_cena.py` |
| Entrega | original mais uma cópia de 15 MB, créditos gastos, legenda do Instagram sem entregar a trama, rótulo de IA | `AUDITORIA_V2C.md` §10 |
| Série | a parte 2 abre repetindo a última batida (`reprise`), retoma o estado de passagem e paga contas abertas | `REGRAS_ROTEIRO.md` §5, O10 |

Estado de passagem herdado:
- **V1:** o Valdir disse que vendeu a parte dele por "dois milhões, à vista"; a Rosa tem preferência e 180 dias para depositar o preço.
- **V2c:** a Estrela foi vendida por 12 mil; a Cleide, expulsa, ergueu o celular: "Doze mil não apaga o que eu gravei."

## 2. Auditoria da v3 aprovada («O vídeo inteiro»)

A v3 só existia em Markdown e nunca tinha passado pelo `auditar_novela.py`. Convertida fala por fala, sem mudar nada,
ela **reprova: nota 0,61 e obrigatórias falhando**.

| Item | Problema na v3 | Como a alternativa resolve |
|---|---|---|
| O2 | gancho de 5 s (o máximo é 3 s) | reprise de 3 s do plano n3 da V2c, já pago |
| O10 | não repete a última batida da parte anterior | a 1ª batida é a reprise do celular erguido no portão |
| F4 | o Dr. entra aos 26% (a faixa é de 48% a 81%): sobra pouco sofrimento antes e o meio arrasta | entra aos 48%, depois de 4 degraus de pressão |
| F1 | só uma humilhação antes da virada | três: escritura empurrada, vídeo tocado, "Coitada, já esqueceu" |
| F3 | o recibo cai do céu: o público não viu nada antes (§10, item 3) | o **ronco do trator** toca no vídeo, o Valdir despreza ("Barulho de fazenda") e a Marta lê a data em voz alta, tudo antes da virada |
| F7 | nenhum número em dinheiro | "Dois milhões, à vista" (eco da V1) e "Doze mil" |
| A1, A5 a A7 | 34 s sem tensão, sem ruptura, sem riso e sem confissão | celular vibrando, chapéu do Valdir, confissão "Errei" |
| Lógica | uma escrevente que "vamos ouvir" um vídeo como renúncia parece incompetente; e por que a Cleide estaria no cartório? | a cena tem motivo legal: o Valdir quer passar a escritura da parte dele (art. 1.793), a Marta pergunta da preferência da irmã (arts. 1.794 e 1.795), e o vídeo é a resposta da Cleide |
| Lógica | por que o Valdir deixou a mulher passar vergonha? | ele tinha vendido o trator escondido dela; a confissão explica e abre a conta da parte 3 |
| Gancho | "Em casa a gente conversa" é piada, não abre conta (§5.1) | a Marta acha no livro um testamento do pai, e só a Cleide sorri (ver §4-A) |

**Mantido da v3** (o editor já tinha aprovado): o cartório, a Marta, a previsão, a fala da lei, o recibo do trator, o
Valdir debochando, a Marta dando razão ao Dr., "grave o vídeo inteiro" e "A senhora não está sozinha".

## 3. A história em 3 frases (teste da história)
1. **Começo:** no cartório, o Valdir quer passar a escritura da parte dele por dois milhões. A Marta pergunta se a irmã,
   que tem preferência, foi avisada. A Cleide toca um vídeo da Rosa: "Pode vender, Valdir. Eu assino.", com um motor
   roncando ao fundo, que o Valdir despreza.
2. **Meio:** o Dr. entra e prevê que a Cleide vai dizer que o vídeo vale como assinatura. Ela diz, ele responde com o art.
   1.806 e a Marta fecha o livro: a escritura não sai.
3. **Fim:** ele vai além e limpa o nome da Rosa. O barulho era de trator, e a data do vídeo é a da venda do trator do pai.
   O Valdir confessa que sabia e o Dr. protege a Rosa. Mas, ao arquivar a ficha, a Marta acha no livro um testamento do
   pai, e a única que sorri é a Cleide.

## 4. Roteiro (plano a plano)

| # | Tempo | Plano | Fala exata | Modelo e créditos |
|---|---|---|---|---|
| 1 | 0:00–0:03 | **Reprise** (plano n3 da V2c): a Cleide no portão ergue o celular. Selo "PARTE 2" | CLEIDE: "Doze mil não apaga o que eu gravei." | já pago · 0 |
| 2 | 0:03–0:08 | Cartório. Valdir no balcão, empurra a pasta da escritura; a chave tilinta | VALDIR: "Faz a escritura, dona Marta. Dois milhões, à vista." | 2.5 · 5 s · 35 |
| 3 | 0:08–0:12 | Marta olha por cima dos óculos, sem tocar nos papéis | MARTA: "A irmã foi avisada? Ela tem preferência." | 2.5 · 4 s · 28 |
| 4 | 0:12–0:17 | Cleide bate o celular de tela para baixo no vidro; a Rosa desfocada ao fundo | CLEIDE: "Ela abriu mão da herança. Tá gravado." | 2.5 · 5 s · 35 |
| 5 | 0:17–0:21 | Inserto: celular no balcão, tela virada para longe; **ronco alto de trator** por baixo da voz | ROSA (no celular, só voz): "Pode vender, Valdir. Eu assino." | Mini · 4 s · 4 + 0,2 |
| 6 | 0:21–0:25 | Marta olha a tela (longe da câmera) e anota a data na ficha | MARTA: "Gravado em doze de março." | 2.5 · 4 s · 28 |
| 7 | 0:25–0:30 | Rosa junto ao banco, envelope pardo nas mãos, balança a cabeça | ROSA: "Eu nunca abri mão da terra do meu pai." | 2.5 · 5 s · 35 |
| 8 | 0:30–0:35 | Valdir ri de lado e abana a mão como quem espanta o barulho | VALDIR: "Barulho de fazenda. A voz é sua, Rosinha." | 2.5 · 5 s · 35 |
| 9 | 0:35–0:40 | Cleide, doce de igreja, ajeita o brinco com a unha vermelha | CLEIDE: "Coitada, já esqueceu. Deus é mais, né, amor?" | 2.5 · 5 s · 35 |
| 10 | 0:40–0:43 | **Ruptura:** o celular da Bruna vibra no banco; ela digita e olha a porta; passos lá fora | — | Mini · 4 s · 4 |
| 11 | 0:43–0:46 | **AURA 1:** a porta abre, câmera baixa, o Dr. atravessa sem pressa e ajeita o lenço. A trilha entra | — | 2.5 · plano de 8 s · 56 |
| 12 | 0:46–0:47,5 | **Riso:** o Valdir tira o chapéu sem perceber, leva um olhar da Cleide e põe de volta | — | Mini · 4 s · 4 |
| 13 | 0:47,5–0:52,5 | **AURA 2** (volta ao plano 11): ele para ao lado da Rosa e diz baixo, olhando a Cleide | DR.: "Ela vai dizer que o vídeo vale como assinatura." | (no plano 11) |
| 14 | 0:52,5–0:56,5 | Cleide ergue o queixo e aperta o celular contra o peito | CLEIDE: "Vale sim. Falou, tá falado." | 2.5 · 4 s · 28 |
| 15 | 0:56,5–1:02,5 | **AURA 3:** o Dr. calmo, mãos juntas. **Cartão CC art. 1.806** | DR.: "Abrir mão de herança, só em escritura ou com juiz." | 2.5 · 6 s · 42 |
| 16 | 1:02,5–1:04,5 | A Marta concorda com a cabeça, tira os óculos e **fecha o livro** | — | Mini · 4 s · 4 |
| 17 | 1:04,5–1:10 | **AURA 4:** em silêncio, ele põe o recibo dobrado no balcão (desfocado) e ergue os olhos para o Valdir | DR.: "Barulho de trator, seu Valdir. Vendido em doze de março." | 2.5 · 5,5 s · 42 |
| 18 | 1:10–1:16 | Valdir calado sob a voz da Rosa; depois abaixa os olhos e tira o chapéu, agora de propósito | ROSA (fora, só voz): "O trator do pai." · VALDIR: "Eu sabia que era o trator. Errei." | 2.5 · 6 s · 42 + 0,2 |
| 19 | 1:16–1:23 | **AURA 5:** o Dr. à Cleide; pausa de 1 s; depois baixo, à Rosa | DR.: "Da próxima vez, grave o vídeo inteiro." … "A senhora não está sozinha." | 2.5 · 7 s · 49 |
| 20 | 1:23–1:27,5 | **Gancho:** todos se viram para sair; a Marta reabre o livro preto para arquivar a ficha, o dedo para numa página e ela ergue os olhos | MARTA: "Dona Rosa, seu pai deixou testamento." | 2.5 · 5 s · 35 |
| 21 | 1:27,5–1:29 | **Congela:** na porta, todos chocados, menos a Cleide, que abre um sorriso lento e verdadeiro. O quadro para no sorriso. "CONTINUA" | — | Mini · 4 s · 4 |

Posições fixas (as da v3):
- balcão ao fundo, com a Marta atrás;
- Cleide e Valdir à direita do quadro;
- Rosa e Bruna junto ao banco, à esquerda;
- porta de vidro à direita;
- o Dr. para à esquerda da Rosa.

**A lei** (lida em planalto.gov.br em 25/11/2026, `l10406compilada.htm`):
- **Art. 1.806 (cartão):** "A renúncia da herança deve constar expressamente de instrumento público ou termo judicial."
- **Base da cena, sem cartão:**
  - art. 1.793: a cessão do quinhão se faz por escritura pública;
  - art. 1.794: a irmã tem preferência, tanto por tanto;
  - art. 1.795: depósito do preço em até 180 dias.

## 4-A. O gancho final (segunda versão, 25/11/2026)

**Por que as duas tentativas anteriores falharam:**
- "Em casa você me conta do dinheiro" era uma briga de casal.
- "A parte custa dois milhões" era conta de matemática dita por quem perdeu.

As duas são **falas**, não **acontecimentos**, e nenhuma muda a pergunta da série.

**O gancho novo é um acontecimento:**
1. **Plano 20.** Todos já se viram para sair. A Marta reabre o livro preto para arquivar a ficha da Rosa, e o dedo para
   numa página. Ela ergue os olhos e diz, baixo: **"Dona Rosa, seu pai deixou testamento."** A sala para.
2. **Plano 21.** Corte para a porta. Todo mundo está chocado, menos a Cleide, que abre um sorriso lento, o primeiro
   sorriso verdadeiro dela no episódio. **Congela no sorriso.** "CONTINUA".

**Por que agora prende:**
- **Muda a pergunta da série.** Deixa de ser "a Rosa ganha?" e passa a ser "o que o pai fez, e por que a Cleide já
  sabia?". Mistério de família puxa mais que conta de dinheiro.
- **É o segredo-mestre previsto no padrão ouro** (`PADRAO_OURO_NOVELA.md`, segredos em três camadas): o testamento do
  pai, plantado cedo e aberto só no fim da temporada. Aqui só aparece que ele existe; o que ele diz fica guardado.
- **Nasce da vitória.** É por registrar a Rosa como herdeira que a Marta abre o livro.
- **Foi plantado.** O livro preto está no balcão desde o plano 3 e a Marta o fecha no plano 16. "A terra do meu pai" e
  "o trator do pai" mantêm o pai na conversa.
- **É verdade jurídica.** O testamento público é escrito pelo tabelião no próprio livro de notas, diante de duas
  testemunhas (CC art. 1.864, I e II, lido no planalto em 25/11/2026). O cartório é o lugar onde ele seria encontrado.
- **Congela antes do efeito, no rosto de quem reage.** Quem reage ao contrário (sorrindo) é a vilã. A Cleide perde o
  caso e mesmo assim sai por cima.
- **Abre uma pista fácil para a parte 3.** A Cleide sorri porque já sabia: será que ela foi uma das duas testemunhas?
  E o Dr. tem a virada pronta, também lida na fonte: havendo herdeiros necessários, o testador só dispõe da metade da
  herança (CC art. 1.789). A Rosa não perde tudo, e o Dr. ganha outra entrada de aura.
- **Aura do Dr. preservada.** Ele não é pego de surpresa em close; o choque fica com a Rosa e a sala.

**Opções reservas,** se o editor preferir outro caminho:
- **O Tavares entra pela porta:** "Trouxe o dinheiro do trator, seu Valdir." O trator do pai teria ido para o comprador
  dos dois milhões.
- **A Bruna acha um segundo vídeo** gravado no mesmo dia. Tem risco: a tela do celular precisa aparecer.

**Tempo e custo:** igual à versão anterior. O vídeo tem 89 s, a virada cai aos 48,3% e o auditor dá 1,00. São cerca de
560 créditos. A Marta usa um plano de 5 s no 2.5 (35 créditos), e o sorriso congelado um plano no Mini (4).

## 5. Auditor (`auditar_novela.py`)
Obrigatórias O1 a O10 ok · F1 a F10 todos ok · **nota 1,00 · APROVADO**. Resta só o aviso **A8** (nenhuma fala longa):
a regra de no máximo 10 palavras por plano, que fez a V2c sair certa, briga com a fala longa do padrão ouro. Fica para a
autojustificação da Cleide na parte 3, em dois planos seguidos.

**Atenção na montagem:** a virada cai em **48,3%**, quase no limite. Se a montagem encurtar o começo ou alongar o fim,
o F4 cai. O auditor roda de novo com os tempos reais.

## 6. Passe de julgamento (`REGRAS_ROTEIRO.md` §9)
1. **Cada fala tem uma ação por baixo?** Sim. Exemplos: pressionando (Valdir, plano 2), barrando (Marta), golpeando
   (Cleide, plano 4), desacreditando (planos 8 e 9), armando (previsão), desarmando (lei), virando a palavra dele
   (plano 17), confessando (Valdir), protegendo (Dr.) e revelando (Marta, no gancho).
2. **Tapando os nomes, dá para saber quem fala?** Sim. O Valdir fala de dinheiro, a Cleide fala doce com veneno ("Deus é
   mais, né, amor?"), a Rosa fala do pai, o Dr. fala curto e com a lei, a Marta fala de procedimento.
3. **Exposição?** Não. A data é dita porque a escrevente registra a prova; a preferência é perguntada, não explicada.
4. **Subtexto virou texto?** Não. "Errei" é confissão, não declaração de sentimento.
5. **Estratégia repetida?** Não. A Cleide muda de tática: prova ("tá gravado"), depois descrédito ("já esqueceu"), depois
   bravata ("falou, tá falado").
6. **O valor muda?** Sim. A escritura sai, a escritura cai, o nome da Rosa fica limpo, o casal racha.
7. **Não fazer nada seria saída para a Rosa?** Não. Sem reagir, perde a preferência e a terra do pai hoje.
8. **O argumento da vilã é plausível e a previsão passa nos 4 testes?** Sim. "Falou, tá falado" é o senso comum que a lei
   derruba; os 4 testes estão no JSON.
9. **O gancho nasce da virada e foi plantado?** Sim. É por registrar a Rosa como herdeira que a Marta abre o livro.
   O livro preto está no balcão desde o plano 3.

## 7. Teste da história (`REGRAS_ROTEIRO.md` §10)
1. **Faz sentido em 3 frases?** Sim (§3).
2. **A prova prova?** Sim, duas vezes:
   - pela lei: vídeo não é escritura;
   - pelos fatos: a mesma data e o mesmo trator no recibo.
3. **O público viu antes?** Sim: o ronco do trator, o desprezo do Valdir e a data lida pela Marta, tudo antes da virada.
   Quem revir o vídeo percebe que o Valdir sabia.
4. **O Dr. muda a situação com um gesto?** Sim: põe o recibo no balcão, e a Marta fecha o livro.
5. **O final responde ao começo?** Sim: a escritura não sai, e a Cleide paga na tela (vergonha diante da escrevente e do
   marido) antes do gancho.
6. **Cenas mínimas?** Todas presentes: o que está em jogo (plano 2), o plantio (5, 6 e 8), a acusação (4 e 9), a virada
   (11 a 15), a consequência (16 a 18) e o fecho com gancho (19 a 21).
7. **Depois de corte:** refazer este teste. Os planos 6 e 8 são o plantio: não podem sair.

## 8. Riscos de áudio e imagem
| Risco | Prevenção |
|---|---|
| Palavras proibidas | nenhuma é falada; "roça" virou "fazenda" e "renúncia" fica só no cartão |
| "Cleide" saindo "Cledi" | ninguém fala "Cleide" neste roteiro (o fecho do Dr. ficou sem "dona Cleide") |
| "milhões" (o Mini já disse "milhones") | guia no prompt: mi-LHÕES, nasal; se errar, conserto só do áudio |
| "preferência" (o Mini já disse "preferente") | guia: pre-fe-RÊN-sia; plano no 2.5 |
| "herança", "março", "Rosinha" | guias da v3: e-RÃN-sa, MAR-so, ro-ZI-nha |
| Voz do Dr. | voice change em 4 trechos (planos 11/13, 15, 17 e 19) |
| Inserto no Mini com aparência diferente do 2.5 | só em planos de 1,5 a 3 s sem fala; se destoar, troca para 2.5 (+24 cada) |
| Tela do celular e texto do recibo | nunca legíveis: tela virada para longe, recibo desfocado |
| Ronco do trator | efeito sonoro na montagem, alto o bastante para ser ouvido na primeira vista |

## 9. Custo (preços desta semana: 2.5 a 7 créditos/s, Mini a 1 crédito/s)
| Item | Créditos |
|---|---|
| 14 planos no Seedance 2.5 (75 s gerados) | 525 |
| 5 insertos no Mini | 20 |
| Reprise do plano n3 da V2c | 0 |
| Falas só de voz (Rosa ×2) | 0,4 |
| Folha da Marta, folha do cartório e placa do quadro | 10,5 |
| Amostra de voz da Marta | 0,2 |
| Troca de voz do Dr. (4 trechos) | 4 |
| **Total** | **cerca de 560** |

- **Comparação:** cerca de 49 a menos que a v3 (609) e dentro do teto já aprovado de **650**, com 90 de folga (dá para
  refazer dois planos).
- **Corte possível:** sem o plano 9 (bordão da Cleide), economiza 35, mas a virada cai para 45% e reprova o F4. Não
  recomendo.

## 10. Para registrar em `NOVELAS_USADAS.md` depois de produzido
- **Premissa:** inversão verdadeiro/falso (o vídeo da vilã prova o contrário do que ela diz).
- **Objeto-prova:** o ronco do trator no vídeo, mais o recibo da venda.
- **Frase de impacto:** "Barulho de trator, seu Valdir."
- **Previsão:** "Ela vai dizer que o vídeo vale como assinatura."
- **Gancho:** "Dona Rosa, seu pai deixou testamento.", congelado no sorriso da Cleide.
- **Estado de passagem:**
  - a escritura não saiu;
  - a Rosa continua herdeira, com preferência;
  - o Valdir confessou na frente da mulher;
  - a Marta achou o testamento público do pai no livro do cartório; a Cleide já sabia.
- **Contas abertas para a parte 3:**
  - **principal: o que diz o testamento e por que a Cleide sabia** (testemunha? art. 1.864, II; limite da metade, art. 1.789);
  - como a Rosa paga dois milhões com doze mil (tanto por tanto, art. 1.794);
  - o dinheiro do trator do pai, que o Valdir escondeu da Cleide (inclusive a metade da Rosa);
  - o prazo de 180 dias;
  - a autojustificação da Cleide (a fala longa, A8).
