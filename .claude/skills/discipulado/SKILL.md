---
name: discipulado
description: Produz e publica uma lição da coleção Discipulado do portal (12 lições para novos convertidos, em 3 módulos), em fluxo enxuto: pesquisa curta com o texto bíblico NTLH lido na fonte, texto do aluno em Linguagem Simples, guia do discipulador, validador com medidor de legibilidade, conferência das citações e publicação automática na aba Discipulado. Use quando pedirem "/discipulado", "/discipulado N", "próxima lição", "lição N do discipulado", "lição sobre <tema>".
---

# /discipulado N

Produz a lição N (1 a 12) e publica em `discipulado/<slug>/`. Sem número: a primeira lição da coleção que ainda não tem
pasta em `conteudo/discipulado/`.

**Processo simplificado (decisão do editor, 30/10/2026):** sem auditoria por subagente e sem nota. A segurança vem do
que é mecânico e barato: texto bíblico copiado da página lida, citações conferidas com grep e o validador
(`tools/discipulado/checar_licao.py`, que inclui o medidor de legibilidade). A conferência humana é a verificação diária
do portal (skill `verificacao`). Alvo: uma lição em cerca de 15 a 20 minutos.

Regras que continuam valendo (CLAUDE.md): nada inventado, citação literal só de frase lida na fonte, nunca imagem gerada
por IA, não editar HTML gerado, publicação automática registrada como automática.

## 1. Preparar (2 min)

`git pull origin main`. Ler `docs/discipulado/padrao-de-escrita.md` e a seção 7 de `docs/discipulado/padrao-editorial.md`
(formato), e `conteudo/discipulado/base/glossario.md` e `decisoes.md`. Criar `conteudo/discipulado/NN-slug/`.
Modelo pronto: `conteudo/discipulado/01-quem-e-jesus/`.

## 2. Pesquisa curta (um subagente, em segundo plano)

Um subagente (Agent, general-purpose) grava `dossie.md`, curto, com:

- **Texto NTLH conferido** das passagens da lição (seção 5 do padrão editorial dá o tema), copiado da página
  (https://www.bibliaonline.com.br/ntlh/<livro>/<cap>; reserva: biblegateway.com, versão NTLH), com o URL. Páginas salvas
  em `<scratchpad>/web-licaoNN/` para o grep. Nunca de memória. Falas com travessão ficam fora dos recortes.
- **2 ou 3 fontes** de tipos diferentes, com a frase lida e o URL: a Declaração de Fé das Assembleias de Deus
  (https://cgadb.org.br/wp-content/uploads/2021/01/declaracao_de_fe.pdf) e um comentário clássico em domínio público
  (Matthew Henry ou Wesley no biblestudytools.com ou ccel.org). Um comentário moderno só se a frase for lida.
- Erros comuns de interpretação do texto e, se houver, a divergência entre tradições (vai para o guia).

Sem pedir mais que isso: a pesquisa da Lição 1 levou 12 minutos porque pediu 10 fontes. Enquanto ela roda, escolha a
imagem (opcional; obra em domínio público no acervo aberto do Metropolitan Museum, como na skill `estudo`).

## 3. Escrever (redator)

`aluno.md` com as seções na ordem exata (o validador confere):

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

- Texto bíblico em citação (`> `, um versículo por parágrafo), copiado do dossiê, com o crédito provisório de
  `base/decisoes.md`. 1.000 a 1.500 palavras fora das citações.
- Padrão de escrita à risca: leitora Dona Rosa, frases curtas em ordem direta, termo mostrado antes de nomeado (inclusive
  "Evangelho", "profeta", "apóstolo" na primeira vez), uma cena imaginada, nada de clichê, culpa, medo ou promessa.
- Atribuição a autor só do que está na frase lida (erro que a auditoria da Lição 1 achou: acrescentar uma frase ao que
  Wesley disse). Fato bíblico citado com a referência certa (não misturar Marcos com Lucas).

`discipulador.md` (título `# Guia do discipulador: Lição N`), 500 a 900 palavras: objetivo, fundamentação, referências
com `[verificada]` ou `[parcial]`, diferenças de tradução, dúvidas frequentes, cuidados pastorais, roteiro de 40 minutos,
alertas, sinais de compreensão, divergências.

## 4. Conferir e validar (3 min)

1. Cada frase entre aspas (bíblica ou de autor): `grep -F "<trecho>"` nas páginas salvas. Não achou, vira paráfrase ou sai.
2. `python3 tools/discipulado/legibilidade.py conteudo/discipulado/NN-slug/aluno.md` (e `--guia` no guia). Frase
   bíblica longa que não pode ser cortada: comentário `<!-- justificativa: ... -->` no fim do arquivo.
3. `licao.json`: `{"numero", "modulo", "slug" (sem o NN), "titulo", "ideia_central", "descricao", "tempo_min",
   "imagem" (opcional), "ia": {"usada": true, "uso": "..."}, "status": "revisao"}`. Sem o campo `auditoria`.
4. `python3 tools/discipulado/checar_licao.py` até passar.

## 5. Publicar (3 min)

1. `python3 tools/publicar.py aprovar conteudo/discipulado/NN-slug/licao.json --revisor anderson-pelicioni-de-castro --automatica`.
2. Atualizar `base/glossario.md` e `base/versiculos.md` (limite de 500 versículos na coleção).
3. `python3 tools/build_home.py` e as checagens do CLAUDE.md. Commit único e push (antes, `git pull --rebase origin main`).
   Não versionar `previa/`.

## Relato ao usuário

Link da lição, fontes `[parcial]` e decisões pendentes, em poucas linhas.
