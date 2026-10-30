# Padrão de escrita: como o texto deve soar

Este documento define a qualidade literária da coleção. Ele existe porque "escreva simples e acolhedor" é instrução que todo redator acha que já cumpre. Aqui a simplicidade é medida, e o acolhimento tem técnica.

A base vem de três lugares: as diretrizes brasileiras de Linguagem Simples (Lei 15.263/2025, ABNT NBR ISO 24495-1:2024, guias do CNJ e dos tribunais), a pesquisa sobre legibilidade em português (fórmula de Flesch adaptada por Martins et al., ICMC/USP, 1996) e a tradição de prosa clara em escrita cristã (o registro da NTLH, as regras de C. S. Lewis para escrever, o modelo de Zinsser em On Writing Well).

---

## 1. A quem estamos escrevendo

Imagine uma leitora específica. Chame-a de Dona Rosa. Tem 52 anos, estudou até a sexta série, trabalha em casa de família, começou a ir à igreja há dois meses porque a filha insistiu. Lê devagar. Entende tudo o que lê quando o texto é claro, e desiste em silêncio quando não é. Ela nunca vai dizer que não entendeu.

Cada frase da lição é escrita para a Dona Rosa. O engenheiro recém-convertido que ler o mesmo texto não vai se sentir subestimado, porque clareza não é condescendência. Ele vai se sentir respeitado por não ter que decifrar nada.

Essa escolha tem base numérica. Cerca de 29% dos brasileiros entre 15 e 64 anos são analfabetos funcionais, e a proporção de leitores proficientes fica na casa de 10% a 12% (Inaf 2024). Um texto escrito para o leitor médio exclui um terço da igreja. Um texto escrito para a Dona Rosa inclui todo mundo.

---

## 2. Metas mensuráveis (o portão)

O `tools/discipulado/legibilidade.py` mede isto. O texto do aluno só segue para auditoria se passar.

| Medida | Meta | Por quê |
|---|---|---|
| Índice de Flesch adaptado ao português | 75 ou mais | Faixa "fácil", leitura confortável para quem concluiu o ensino fundamental |
| Média de palavras por frase | 12 a 18 | Guias de Linguagem Simples recomendam até 20; a Lei 15.263 manda frases curtas |
| Frases com mais de 25 palavras | Nenhuma no texto do aluno | Uma frase longa é onde o leitor lento se perde e não volta |
| Média de sílabas por palavra | Até 1,9 | Palavra longa custa mais que frase longa para quem lê devagar |
| Parágrafos | Até 5 frases, uma ideia por parágrafo | Exigência explícita da Lei 15.263/2025 |
| Travessões | Zero | Decisão editorial da coleção |
| Termos teológicos sem explicação no ato | Zero | Ver glossário em `conteudo/discipulado/base/glossario.md` |

Limites e honestidade: fórmulas de legibilidade medem a superfície do texto (tamanho de frase e de palavra). Elas não medem se a ideia foi entendida. Um texto pode passar no índice e ser confuso, e pode ter uma frase de 30 palavras que funciona como poesia. Por isso o índice é portão, não juiz. O juiz é a leitura por pessoas reais na revisão humana. Quando o redator decidir manter uma frase que viola a meta, ele registra o motivo no fim do arquivo. Isso é permitido. Fazer isso toda hora não é.

A fórmula usada (Martins et al., 1996): 248,835 menos 1,015 vezes (palavras por frase) menos 84,6 vezes (sílabas por palavra). O ajuste de 42 pontos em relação à fórmula original em inglês compensa o fato de palavras em português terem mais sílabas.

---

## 3. As regras de frase e de palavra

Estas regras vêm da Linguagem Simples e valem para o texto do aluno. No guia do discipulador há mais folga, nunca muita.

1. **Ordem direta.** Quem faz, o que faz, para quem. "Deus perdoa quem se arrepende", não "Àquele que se arrepende é concedido perdão por Deus".
2. **Uma ideia por frase.** Se tem "e", "mas", "porque" ligando duas ideias cheias, são duas frases.
3. **Voz ativa.** "Jesus curou o cego", não "O cego foi curado por Jesus". A exceção é quando quem sofre a ação é o foco.
4. **Palavra curta e comum vence palavra longa e rara.** "Começo", não "início"; "usar", não "utilizar"; "mostrar", não "evidenciar"; "pedir", não "solicitar"; "quem crê", não "o crente".
5. **Verbo concreto, não substantivo abstrato.** "Deus nos perdoa" em vez de "há a concessão do perdão divino". Substantivo terminado em "ção", "mento" e "dade" quase sempre esconde um verbo melhor.
6. **Termo teológico: mostrar antes de nomear.** Primeiro a cena ou a comparação. Depois a palavra. "Quando alguém paga uma dívida que era sua e você fica livre dela, a Bíblia chama isso de redenção." Nunca o contrário.
7. **Segunda pessoa com naturalidade.** "Você" e "a gente" são bem-vindos. "Nós" quando o redator se inclui de verdade. Sem "vocês" genérico de púlpito.
8. **Sem jargão de igreja sem tradução.** "Varão", "irmão em Cristo", "ministrar", "ungido", "ser tocado", "mover de Deus". Se precisar, explicar como se explica para alguém de fora.
9. **Sem adjetivo que faz o trabalho do leitor.** Não escrever "uma verdade maravilhosa". Mostrar a verdade; o leitor decide se é maravilhosa.
10. **Número e referência bíblica do jeito mais simples.** "João, capítulo 1, versículo 14" na primeira vez; "João 1:14" depois de explicar como se lê.

---

## 4. Apelo emocional sem manipulação

A emoção certa vem do concreto, não do adjetivo. Esta é a regra que separa texto que toca de texto que grita.

### 4.1 O que a pesquisa diz

Textos concretos são lembrados e entendidos melhor que textos abstratos (efeito de concretude, Paivio; Chip e Dan Heath sintetizam isso em Made to Stick: ideias que grudam são simples, inesperadas, concretas, críveis, emocionais e contadas como história). Uma frase sobre "a graça de Deus" não é lembrada. Uma frase sobre "a mãe que deixa a porta destrancada todas as noites esperando o filho voltar" é lembrada, e ensina graça.

### 4.2 As regras de Lewis, adaptadas

C. S. Lewis, numa carta a uma leitora jovem, deu conselhos de escrita que servem de código aqui:

- Use a palavra simples que diz exatamente o que você quer dizer.
- Não use palavra grande demais para o assunto. Não diga "infinitamente" quando quer dizer "muito".
- Em vez de dizer que algo foi terrível, descreva de um jeito que o leitor sinta o terror. Em vez de dizer que algo foi lindo, mostre, e deixe o leitor dizer "lindo".
- Escreva com o ouvido, não só com os olhos. Leia em voz alta.

A terceira regra é a mais importante para esta coleção. Texto devocional ruim diz ao leitor como se sentir. Texto devocional bom cria a cena e confia.

### 4.3 Ferramentas permitidas

- **Uma cena por lição.** Abre a seção "Para começar". Pessoa, lugar, hora, um detalhe físico. "Marcos chega do turno da noite, senta na beira da cama e não consegue dormir." Apresentada como cena imaginada ("Pense em alguém que..."), nunca como testemunho real inventado.
- **Comparação com o cotidiano.** Dívida, contrato de trabalho, pai esperando filho, remédio que precisa ser tomado, chave que abre a porta. Usar uma por conceito, bem escolhida. Comparação ruim ensina errado.
- **Pergunta que o leitor já se fez.** "Será que Deus ainda me quer depois do que eu fiz?" Colocar a pergunta na página antes de responder.
- **Ritmo.** Frases curtas depois de frases médias. Uma frase de três palavras depois de uma de quinze tem peso. Usar com parcimônia.
- **Silêncio depois da afirmação forte.** Quando o texto diz algo grande, parar o parágrafo ali. Não explicar o que acabou de dizer.
- **Honestidade sobre a dificuldade.** "Isso não é fácil de entender. Vamos devagar." O leitor confia em quem admite.

### 4.4 Ferramentas proibidas

- Medo como motor. "Se você não fizer isso, vai se perder."
- Culpa como ferramenta. "Um verdadeiro cristão nunca..."
- Promessa de resultado. "Se orar assim, Deus vai responder."
- Exclamação em série, caixa alta, pontos de exclamação dentro do ensino.
- Clichê de pregação: "amado", "irmão", "a Palavra diz", "Deus tem um propósito", "não é por acaso que você está lendo isso".
- Repetir a conclusão no fim de cada subtópico. Dizer uma vez. Confiar.
- Qualquer frase que o redator reconheceria como "sermão gerado automaticamente": lista de três abstrações, paralelismo retórico vazio, pergunta retórica seguida de resposta óbvia.

---

## 5. O registro da coleção

O tom é o de um professor que sabe muito, gosta do aluno e não tem pressa. Três modelos de registro para calibrar:

- **NTLH (Nova Tradução na Linguagem de Hoje).** É a tradução bíblica feita pela SBB exatamente para este público, com equivalência dinâmica e vocabulário cotidiano. O texto do aluno deve soar como quem conversa com a NTLH, não como quem comenta a Almeida Revista e Corrigida.
- **Prosa de explicação clara.** O padrão de Zinsser: cada palavra trabalha, cada frase tem um dono, o leitor nunca precisa reler.
- **Devocional brasileiro de qualidade.** Luciano Subirá e Ricardo Barbosa, quando escrevem para o público amplo, mantêm profundidade sem perder a pessoa comum. Usar como referência de tom, nunca de texto.

Não é o registro da coleção: linguagem de teologia sistemática, linguagem de púlpito pentecostal com suas fórmulas, linguagem de autoajuda, linguagem de livro infantil.

---

## 6. Antes e depois

**Antes:** "A doutrina da encarnação, fundamental para a cristologia ortodoxa, afirma que o Verbo eterno assumiu a natureza humana sem prejuízo de sua divindade, conforme João 1:14."

**Depois:** "Deus se tornou gente. Ele não parou de ser Deus. Mas passou a ter fome, a sentir frio, a cansar. João escreveu assim: a Palavra se tornou um ser humano e morou entre nós (João 1:14). Os cristãos chamam isso de encarnação."

Índice do primeiro: por volta de 30 (muito difícil). Do segundo: acima de 80 (fácil).

**Antes:** "A graça divina é uma realidade maravilhosa e transformadora que deve ser experimentada por todo crente."

**Depois:** "Pense em alguém que deve uma quantia que nunca vai conseguir pagar. Um dia, a dívida aparece zerada. Ninguém cobrou. Alguém pagou por ele. A Bíblia tem uma palavra para isso: graça."

**Antes:** "Devemos buscar mais a Deus em oração."

**Depois:** "Esta semana, escolha um horário. Pode ser cinco minutos antes de sair de casa. Fale com Deus do jeito que fala com alguém que conhece bem. Conte o que está pesando. Agradeça uma coisa. Só isso."

---

## 7. Checklist do redator antes de entregar

- Li em voz alta o texto inteiro? Travei em algum lugar? Lá tem problema.
- Cada termo teológico foi mostrado antes de nomeado?
- Tem alguma frase dizendo ao leitor o que sentir? Substituir por cena.
- A seção "A fé na vida real" diz o que fazer na terça-feira de manhã?
- Rodei o `legibilidade.py`? Passou? Se não, por que mantive?
- Procurei travessão? Procurei "amado", "irmão", "a Palavra diz", "propósito", "não é por acaso"?
- A Dona Rosa leria até o fim?
