# Direção artística das pinturas em código (pedido do editor, 25/11/2026)

> "As pessoas se atraem mais pela qualidade da animação. Uma animação bonita, de qualidade, está valendo mais do que as
> imagens geradas. […] Tem que ser uma imagem completa, bem acabada, com direção artística, atraente para os olhos, com
> os padrões das obras de arte." (editor, depois de "Multa ambiental prescreve?")

**Daqui em diante, a pintura animada é a estrela do vídeo.**
- IA (Higgsfield) só onde for indispensável mostrar gente.
- Cartão e letreiro entram a serviço da pintura: nunca tapam o ponto focal.

Este arquivo vale para toda cena de `tools/video/agro-arte/cenas/`. É lido junto com `DIRECAO_VIDEO_AGRO.md`.

## 1. O que faz alguém parar para admirar um quadro (e o que copiamos disso)

| Princípio | Na prática, em cada cena |
|---|---|
| **Cena completa** | Um quadro inteiro, com mundo e atmosfera: céu trabalhado, horizonte, chão, primeiro plano. **Proibido:** objeto solto sobre fundo chapado ("um livrinho", "um pedacinho"), retângulo e elipse lisos sem textura, área vazia sem intenção. |
| **Ponto focal único** | Um só centro de interesse por cena (a porteira, a casa, a ponte), com o maior contraste de claro e escuro e o maior detalhe. Fica num ponto dos terços ou da proporção áurea do recorte de 1080 × 1080. |
| **Linhas que conduzem** | Estrada, rio, cerca, sulco ou fileira de árvores levam o olho até o foco. Prefira diagonais e curvas em S a linhas paralelas à borda. |
| **Profundidade em camadas** | No mínimo 4 planos: céu, fundo (serra azulada), plano médio e primeiro plano escuro. O primeiro plano emoldura a cena (*repoussoir*: um galho, um tronco, uma touceira na borda). O parallax é lento, com cada plano numa velocidade. |
| **Perspectiva atmosférica** | Quanto mais longe, mais claro, azulado e menos saturado. Quanto mais perto, mais escuro, quente e detalhado. |
| **Luz com intenção** | Uma fonte clara, de preferência a hora dourada ou o contraluz. Sombras projetadas coerentes com o sol, luz de borda nas copas e raios de luz quando couber. **Teste de valores:** a cena em escala de cinza ainda se lê, e o foco é a área de maior contraste. |
| **Cor harmônica** | Paleta de 3 a 5 cores dominantes e 1 acento (ex.: verdes e ocres com acento vermelho da terra). Luz quente e sombra fria. Nada de cores puras de computador (#00ff00). |
| **Detalhe onde importa** | Folhagem com variedade de tons e formas, nuvens com volume (luz em cima, sombra embaixo), textura de madeira, pedra e terra. A densidade de detalhe sobe no foco e cai nas bordas. |
| **Movimento vivo e sutil** | Vento no capim e nas copas, nuvens andando, luz mudando, água correndo, pássaros ao longe, poeira na luz. Nada pula nem gira à toa. A câmera faz dolly ou parallax lento, sem zoom brusco. |
| **Referência de mestre** | Cada cena parte da **estrutura** de uma obra real em domínio público: composição, paleta e luz, com o título e o acervo anotados no topo do arquivo de cenas. O assunto é o campo brasileiro, sem copiar o quadro. |
| **Brasil no quadro** | Cerrado, ipê, buriti, araucária, terra roxa, pasto com cupinzeiro, porteira de madeira, mata-burro, cascalho, serra azul, céu de fim de tarde do interior. |
| **Sem gente pintada** | Mantém a regra de 21–22/11/2026. A presença humana aparece pelos objetos e pelo rastro: chapéu, porteira aberta, fumaça da chaminé, marca de pneu. |

## 2. Como construir uma cena (ordem de trabalho)

1. **Esboço de valores:** 3 tons (claro, médio, escuro), em blocos grandes no recorte de 1080 × 1080 (x 420 a 1500 do
   quadro de 1920). Confira o foco nos terços.
2. **Céu e luz:** gradiente de várias paradas, nuvens com volume e o sol, ou a fonte de luz, definidos antes de tudo.
3. **Planos do fundo para a frente:** serra, mata, campo, plano médio com o foco, primeiro plano com moldura.
4. **Sombras e luz de borda** coerentes com o sol.
5. **Detalhe no foco:** textura, pequenas peças (dobradiça, pedra, flor) e variação de cor.
6. **Pincelada:** `MEDIUM.broken` ou `MEDIUM` adequado ao mestre, com `jit` e `skip` calibrados para não "derreter" o desenho.
   **A textura de tela vem por último.**
7. **Animação:** de 3 a 5 camadas vivas no máximo (vento, nuvem, luz, água, partículas), todas lentas.
8. **Conferência:** o quadro parado precisa funcionar como pôster. Se não funcionar parado, não entra animado.

## 3. Crivo artístico (junto do crivo de qualidade, antes de mandar ao editor)

Cada cena é avaliada num quadro parado, em tamanho cheio. **Qualquer reprovação: refazer a cena.**

| # | Pergunta | Reprova se |
|---|---|---|
| A1 | É uma cena completa? | Objeto solto em fundo chapado; quadro "vazio" |
| A2 | Tem um ponto focal claro? | O olho não sabe para onde ir; dois focos brigando |
| A3 | Há linhas que levam ao foco? | Tudo paralelo à borda; foco isolado |
| A4 | Tem 4 planos de profundidade e moldura? | Tudo no mesmo plano; sem primeiro plano |
| A5 | A luz tem direção e as sombras batem? | Luz chapada; sombra no lado errado |
| A6 | A paleta é harmônica, com 1 acento? | Cores cruas; tudo saturado igual |
| A7 | O foco tem detalhe e textura? | Formas geométricas lisas no foco |
| A8 | O movimento é vivo e sutil? | Quadro parado; elemento que pula; vários movimentos rápidos |
| A9 | Funciona como pôster parado? | Só "funciona" em movimento |
| A10 | Letreiros e cartões deixam o foco livre? | Texto em cima do ponto focal |

## 4. Proporção no vídeo
- **Tempo de tela:** pinturas em código, no mínimo 75%. IA só nas cenas com gente indispensável. Documento só como prova
  curta, de 2 a 3 cartões.
- **Cada pintura aparece limpa,** sem letreiro, por pelo menos 1,5 s ao entrar.
- **Menos cenas, mais bem feitas:** de 4 a 5 pinturas por vídeo, cada uma com 8 a 12 s de vida, em vez de muitas cenas
  pobres. Quando uma pintura volta no vídeo, volta noutro enquadramento (outro ponto de partida da câmera).
