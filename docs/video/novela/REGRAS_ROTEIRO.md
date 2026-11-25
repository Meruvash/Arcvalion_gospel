# Regras de roteiro e de cena da novela (23/11/2026)

Este documento completa `FORMULAS_NOVELA.md` (a estrutura medida no modelo de 1 hora) e
`PERSONAGEM_DR_PELICIONI.md` (o protagonista). As regras foram adaptadas, com palavras nossas, de quatro fontes lidas em
23/11/2026:
- **story-rules do fluxo "drama-ads" do Higgsfield**;
- **drama-skills** (zenstory-ai, licença MIT, © 2026 drama-skills contributors);
- **screenwriting-skills** (jtydhr88, licença MIT, © 2026 Terry Jia);
- **micro-drama-skills** (zhaihao118, sem arquivo de licença: só ideias foram aproveitadas).

Nenhuma citação de livro ou roteiro foi copiada.

## 1. Gancho e escada
1. **O gancho é corpo, não texto.** Nos 3 primeiros segundos, uma pessoa faz algo contra outra: solta o livro na terra,
   balança o contrato, gira a chave da caminhonete. Tela, documento ou mensagem só confirmam o que o corpo já mostrou.
2. **Teste do quadro parado (3 s).** Pausado no terceiro segundo, um desconhecido entende quem ataca quem.
3. **Escada a cada 8 a 15 s.** A tensão sobe: palavra, depois objeto, depois espaço do corpo (passo para dentro, dedo
   apontado), depois consequência. Entre dois degraus seguidos, pelo menos um é ação física e não só fala.
4. **Humilhação em cadeia.** Quem é humilhado repassa a humilhação a alguém mais fraco na cena seguinte. Exemplo: a Cleide
   rebaixa o Valdir, e o Valdir desconta na Rosa. Isso dá camada ao vilão e alimenta o F1.
5. **Teste do "então / mas".** Toda batida se liga à anterior por "então" ou "mas". Se só couber "e depois", falta uma
   escolha, um contra-ataque ou uma consequência: reescreva. No JSON, cada batida tem o campo `porque`.

## 2. Vilão que pensa (sem isso, o doutor não parece inteligente)
1. **Dê uma faca ao vilão.** O argumento do vilão soa jurídico e plausível, nunca "porque ele é mau". Exemplo do
   Tavares: "Está tudo registrado em cartório, dona Rosa." Quanto mais forte o argumento, maior a vitória.
2. **O vilão troca de tática.** A cada degrau ele muda de argumento: desprezo, depois "a lei está do meu lado", depois
   testemunha, depois dinheiro. Nunca o mesmo grito duas vezes.
3. **A frase solta vira prova.** Uma bravata do vilão no começo (gravada pela Bruna, dita na frente de testemunhas)
   volta na virada como confissão. Exemplo: "O senhor mesmo disse: 'nem avisei ela'."

## 3. O doutor parece inteligente
1. **A previsão prevê o argumento do vilão** (`PERSONAGEM_DR_PELICIONI.md`, regra 2): o vilão diz a frase prevista com
   convicção, e a frase é o erro jurídico do caso.
2. **Virada numa palavra.** O doutor repete com calma a versão do vilão por inteiro e vira tudo numa palavra:
   "Sua parte, seu direito, sua venda. Só que…"
3. **Palavra plantada, sentido trocado.** A palavra de desprezo do vilão vira a chave do doutor. A Cleide: "Isso é papel
   velho." O Dr.: "Papel velho. É ele que diz quem tem preferência."
4. **Ironia dramática.** Um plano rápido mostra ao público a pista que o vilão ignora (o carimbo, a data, o "digitando…").
   A pergunta muda de "o que vai acontecer?" para "quando ele vai perceber?".
5. **A frase mais forte do doutor corta para o rosto de quem ouve.** A reação do vilão vale mais que a boca do doutor.
6. **Ele é anunciado antes de aparecer, sem mostrar o rosto:** o carro na porteira, o sapato na terra, a pasta, a
   silhueta.

## 4. Diálogo
1. **Por baixo de cada fala há uma ação no gerúndio** (rebaixando, ameaçando, seduzindo, desarmando). Fala sem ação sai.
2. **Teste do nome coberto.** Tapando os nomes, dá para saber quem fala. Vocabulário próprio de cada um:
   - Valdir: negócio e dinheiro;
   - Cleide: doçura de igreja e de sociedade, com veneno ("Coitada, ela nem sabe ler escritura, né, amor?");
   - Tavares: termos de corretor;
   - Rosa: memória do pai e da terra;
   - Dr. Pelicioni: frase curta, lei, calma.
3. **Teste da troca.** Trocando as falas de dois personagens, alguma coisa tem que quebrar. Se nada quebra, falta motivo
   a eles.
4. **Nada de exposição.** Ninguém conta ao outro o que os dois já sabem, a não ser como arma.
5. **A fala termina na palavra que provoca a reação.**
6. **Dinheiro e números ditos em voz alta** (dois milhões, cento e oitenta dias).
7. **No máximo 2,9 palavras por segundo** (O5) e **um falante por clipe** (`FORMATO_CENA.md`).

## 5. Gancho final e série
1. **O gancho nasce do resultado da virada.** A vitória do doutor revela uma ameaça maior ou uma conta nova. Não vale
   cortar no meio da frase sem consequência. Exemplo: a Cleide, sorrindo: "Então o senhor não sabe do testamento."
2. **Contabilidade da temporada.** O caso fecha, mas o custo continua aberto. Cada episódio registra em
   `NOVELAS_USADAS.md`:
   - o que deixou plantado;
   - quem paga e em qual episódio;
   - o estado de passagem: quem sabe o quê, quem está com o objeto, onde cada um está.
3. **A parte 2 abre repetindo a última batida da parte 1** (`reprise: true` na primeira batida).

## 6. Cena e clipe
1. **Um clipe por falante**, de 4 a 8 s, com cerca de 1 s de folga depois da fala.
2. **Os planos somam exatamente a duração do clipe.** Passar do tempo corta o fim da fala; sobrar faz o modelo arrastar
   em câmera lenta.
3. **Reação na ordem percepção → emoção → corpo → pausa.**
4. **Ações que o vídeo aguenta:** olhar, virar, andar, parar, recuar, entregar, soltar, pegar, apontar.
   - **Ações que quebram:** contato entre corpos (empurrão, tapa, agarrão) e mudança de estado dentro do plano (rasgar,
     molhar, quebrar).
   - Mudança de estado é feita em dois planos: antes e depois.
5. **Trava visual:** cada personagem tem uma frase fixa de figurino, sempre a mesma (`tools/video/novela/prompt_clipe.py`,
   TRAVAS), mais a folha anexada.
   - Cenários fixos: terreiro, cozinha, porteira, escritório.
   - Objeto-prova com folha própria quando voltar em mais de um episódio.
6. **Nos prompts:**
   - escrever "No background music" (sem música de fundo), nunca "silêncio total", que apaga a fala;
   - escrever "sem legenda e sem texto na tela", porque a legenda amarela entra na montagem;
   - celular com notificação só na tela, sem balão no ar.
7. **Pronúncia:** os nomes do elenco e os termos (Pelicioni, Incra, CCIR, usucapião) com uma só grafia na série toda.

## 7. Triagem do clipe gerado (antes de montar)
Cada clipe recebe um destino:
- **manter;**
- **cortar** (aproveitar só um trecho);
- **corrigir na montagem** (cor, som);
- **refazer opcional;**
- **refazer obrigatório.**

Refazer é obrigatório quando:
- falta palavra na transcrição;
- o rosto muda ou a mão deforma (crivo H1 a H7);
- aparece texto na tela;
- toca música de fundo.

Ao refazer, mude **uma variável por vez**. Se o mesmo erro aparecer duas vezes, divida o plano ou reescreva a ação.

## 8. Montagem
- Entrar cerca de 0,25 s antes da primeira sílaba e sair cerca de 0,4 s depois da última.
- Igualar as falas perto de -19 LUFS. A trilha fica abaixo da fala, e o som de ambiente segue contínuo para esconder os
  cortes.
- Voz de telefone com filtro de 300 a 3.400 Hz.
- Legenda amarela; cartão de lei com o texto literal e a fonte, como inserto, nunca como gancho.

## 9. Passe de julgamento (depois do `auditar_novela.py`, antes de mostrar ao editor)
Responda sim ou não, com uma linha de justificativa, e reescreva o que falhar:
1. Cada fala tem uma ação por baixo?
2. Tapando os nomes, dá para saber quem fala?
3. Há exposição (alguém contando o que o outro já sabe)?
4. Algum subtexto virou texto ("estou com raiva", "você me humilhou")?
5. Alguma estratégia se repete com outras palavras?
6. O valor em jogo muda do começo ao fim de cada cena?
7. "Não fazer nada" seria uma saída viável para a Rosa? Se sim, a aposta está fraca.
8. O argumento do vilão é plausível, e a previsão do doutor passa nos 4 testes?
9. O gancho final nasce da virada e foi plantado ("devia ter previsto")?

## 10. Teste da história (lição da V2c, avaliação do editor em 24/11/2026)
«A marca da Estrela» passou no verificador e no passe de julgamento, mas o editor viu que **não tinha história**: faltou
coerência, o final não interessava, o Dr. aparecia sem fazer nada e a "anca" não fazia sentido. O verificador mede forma
(tempos, palavras, posições), não lógica. Por isso, antes de mostrar o roteiro, responda também:
1. **Contado em 3 frases** a quem não viu (problema, virada, fim), a história faz sentido sozinha?
2. **A prova prova mesmo?** A virada tem que decidir a dúvida do começo. Na V2c, a lei diz *onde* se pode marcar o gado,
   mas não diz *de quem* é a vaca: a lei sobrava, e a prova de verdade (a anca limpa, o R da Rosa) não foi mostrada.
3. **O público viu antes** tudo o que precisa para entender a virada (o R da Rosa, a regra, o que está em jogo)?
4. **O Dr. muda a situação** com um gesto ou uma decisão que tem consequência na tela, e não só com uma fala?
5. **O final responde à pergunta do começo** (a venda acontece? a terra se salva?), e o vilão paga na tela antes do gancho?
6. **Cenas mínimas:** o que está em jogo, o plantio da prova, a acusação, a virada, a consequência e o fecho com o gancho.
   Se não couber em 60 a 90 s, divida em partes; nunca comprima a história em falas de 10 palavras.
7. **Depois de qualquer corte** (do editor ou da montagem), refaça este teste antes de gerar ou montar: cortar a fala da
   calúnia tirou da V2c a única ação do Dr., e ninguém reconstruiu a cena.
