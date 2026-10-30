---
name: discipulado
description: Produz e publica uma lição da coleção Discipulado do portal (12 lições para novos convertidos, em 3 módulos): dossiê de pesquisa por subagente, texto do aluno em Linguagem Simples com texto bíblico NTLH conferido, medidor de legibilidade, guia do discipulador, auditoria por subagente independente (nota 85+), build e publicação automática na aba Discipulado. Use quando pedirem "/discipulado", "/discipulado N", "próxima lição", "lição N do discipulado", "lição sobre <tema>" ou "rodar o piloto".
---

# /discipulado N

Produz a lição de número N (1 a 12) nas quatro fases, com separação de funções, e publica na aba Discipulado
(`discipulado/<slug>/`). Sem número: a primeira lição da coleção que ainda não tem pasta em `conteudo/discipulado/`.

Regras do portal que valem aqui (CLAUDE.md): nada inventado, citação literal só de frase lida na fonte, nunca imagem
gerada por IA, não editar HTML gerado, checagens antes do commit, publicação automática registrada como automática.

## Antes de começar

1. `git pull origin main`.
2. Ler por inteiro `docs/discipulado/padrao-editorial.md` e `docs/discipulado/padrao-de-escrita.md`.
3. Ler `conteudo/discipulado/base/glossario.md`, `decisoes.md` e `versiculos.md`. Termo já explicado recebe a mesma explicação.
4. Criar `conteudo/discipulado/NN-slug/` (NN com dois dígitos, slug curto sem acento, ex.: `01-quem-e-jesus`).
5. Criar a lista de tarefas com as quatro fases e os portões.

## Fase A: Dossiê (subagente pesquisador)

Lançar um subagente (Agent, general-purpose) com o papel de pesquisador bíblico e teológico. Passar: tema, texto central e
complementares (seção 5 e, para a Lição 1, seção 12 do padrão editorial), fontes prioritárias, seções 2, 3 e 6 (etapas 1 a 3).
Ele não escreve a lição. Ele grava `dossie.md` com:

- objetivo espiritual e pedagógico, e a dúvida principal do aluno;
- síntese exegética do texto central (contexto histórico e literário, público original, ensinamento central, estrutura);
- passagens complementares e o que cada uma acrescenta; erros comuns de interpretação;
- referências (mínimo 3, de tipos diferentes), cada uma com autor, obra, edição, localização, o que acrescenta,
  `[verificada]`, `[parcial]` ou `[não verificada]` e como foi verificada (URL e trecho), via WebSearch e WebFetch;
- o que a Declaração de Fé das Assembleias de Deus diz sobre o tema, com a frase conferida
  (https://cgadb.org.br/wp-content/uploads/2021/01/declaracao_de_fe.pdf);
- divergências entre tradições evangélicas; plano pedagógico (ideia central em uma frase, imagem cotidiana, cena de
  abertura, aplicação da semana, modelo validado de onde vem o exercício: Navigators, Alpha, CPAD, MDA);
- termos teológicos que a lição introduz, com a explicação proposta;
- **"Texto NTLH conferido"**: cada passagem que o aluno vai ler, transcrita exatamente da página (bibliaonline.com.br/ntlh,
  bible.com versão 211), com URL e grau (A: página baixada e conferida com grep; B: só WebFetch). Páginas salvas em
  `<scratchpad>/web-licaoNN/`. Passagem que não foi lida não entra: nunca reconstruir de memória.

Site que bloqueia robô (403, Cloudflare) não se contorna: outra fonte. Portão A: nenhuma fonte `[não verificada]` no texto
do aluno; com menos de três fontes verificáveis, registrar a limitação e seguir.

## Fase B: Texto do aluno (redator)

`aluno.md`, formato da seção 7 do padrão editorial, nesta ordem exata (o validador confere):

```
# <Título em pergunta, igual ao licao.json>
## O que vamos aprender?
## Para começar
## Texto bíblico principal
## Entendendo a Palavra        (3 ou 4 subtópicos "### ")
## Entendendo melhor
## A fé na vida real
## Vamos conversar?
## Desafio da semana
## Para guardar no coração
## Resumindo
```

- Texto bíblico em citação (`> `), copiado do "Texto NTLH conferido" do dossiê, com a linha de crédito:
  "Texto bíblico: Nova Tradução na Linguagem de Hoje. Copyright Sociedade Bíblica do Brasil. Usado com permissão."
  (conferir a redação na fonte; o validador exige o nome da tradução). Somar os versículos em `base/versiculos.md` (limite 500).
- Seguir o `padrao-de-escrita.md` à risca: leitora Dona Rosa, ordem direta, uma ideia por frase, termo teológico mostrado
  antes de nomeado, uma cena por lição apresentada como cena imaginada, nada de clichê de púlpito, culpa, medo ou promessa.
- Nada de marca `[verificada]` no texto do aluno; nenhuma menção à advocacia do editor.
- Rodar `python3 tools/discipulado/legibilidade.py conteudo/discipulado/NN-slug/aluno.md` e reescrever até passar. Violação
  mantida de propósito: comentário `<!-- justificativa: ... -->` no fim do arquivo. Colar o relatório final do script em
  comentário no fim do arquivo. Passar o checklist da seção 7 do padrão de escrita.

Portão B: script aprovado, zero travessão, glossário respeitado.

## Fase C: Guia do discipulador (redator)

`discipulador.md` (título `# Guia do discipulador: Lição N`): objetivo, fundamentação adicional, referências com
classificação, dúvidas frequentes com resposta sugerida, cuidados pastorais, roteiro com tempos para 30 a 45 minutos,
alertas de interpretação, sinais de compreensão, divergências entre tradições (comparar NAA ou NVI quando a NTLH muda o
sentido; citar essas traduções só com o texto lido na fonte). 500 a 900 palavras. Rodar o medidor com `--guia`.

## Fase D: Auditoria (subagente auditor independente)

Lançar um NOVO subagente. Passar somente: `aluno.md`, `discipulador.md`, as seções 9 e 10 do padrão editorial, as seções
2, 3 e 4 do padrão de escrita e o relatório do script. Não passar o dossiê nem rascunhos. Instrução literal: "Você não
escreveu este texto. Julgue como um editor externo que será responsabilizado se um erro passar. Procure o que está errado
antes de listar o que está certo. Confira ao menos três citações bíblicas no contexto (e o texto NTLH na fonte). Não
arredonde nota para cima." Ele grava `auditoria.md`: pontuação por critério, nota, pontos fortes, problemas (local e
correção), fontes não confirmadas, eliminatórios, situação.

Portão D: nota 85 ou mais e nenhum eliminatório. Se falhar, voltar à Fase B com a lista, corrigir, medir de novo e lançar
outra auditoria com outro subagente. Limite de três rodadas; na terceira falha, parar e relatar.

## Publicação

1. `licao.json` na pasta:
   `{"numero", "modulo" (1 a 3), "slug" (sem o NN), "titulo" (igual ao aluno.md), "ideia_central" (uma frase),
   "descricao" (resumo de 1 ou 2 frases para busca e prévia), "tempo_min", "auditoria": {"nota", "rodadas",
   "eliminatorios": []}, "ia": {"usada": true, "uso": "..."}, "status": "revisao"}`.
   Imagem é opcional (`imagem`: obra em domínio público em `conteudo/imagens/`, como nos estudos; nunca gerada por IA).
2. `python3 tools/discipulado/checar_licao.py` até passar.
3. `python3 tools/publicar.py aprovar conteudo/discipulado/NN-slug/licao.json --revisor anderson-pelicioni-de-castro --automatica`.
4. Atualizar `base/glossario.md` (termos e explicação usada) e `base/decisoes.md` se houver decisão nova.
5. `python3 tools/build_home.py` e as checagens do CLAUDE.md, mais `python3 tools/discipulado/checar_licao.py` e
   `python3 tools/checar_seo.py`. Conferir a página no Playwright em 390 px.
6. Commit único e push (antes, `git pull --rebase origin main`). Não versionar `previa/`.

## Relato ao usuário

Poucas linhas: link da lição, nota e rodadas, fontes `[parcial]` ou não confirmadas que pedem revisão humana, decisões que
ele precisa tomar. Lembrar que a nota é preliminar e que o teste real é uma pessoa do público ler e dizer o que entendeu.

## O que esta skill nunca faz

Declarar revisão humana que não houve; usar fonte `[não verificada]` no texto do aluno; reconstruir texto bíblico de
memória; alterar o medidor ou seus limites; deixar o mesmo agente escrever e auditar; produzir texto com travessão.
