---
name: discipulado
description: Produz e publica uma nova lição do Discipulado do portal (para novos convertidos), em fluxo enxuto: tema escolhido pelo que as pessoas estão perguntando (autocomplete do Google e do YouTube, Reddit, Pessoas também perguntam, notícias), pesquisa curta com o texto bíblico NTLH lido na fonte, texto do aluno em Linguagem Simples, guia do discipulador, validador com medidor de legibilidade, conferência das citações e publicação automática na aba Discipulado. Use quando pedirem "/discipulado", "próxima lição", "nova lição do discipulado", "lição sobre <tema>".
---

# /discipulado

Produz uma nova lição e publica em `discipulado/<slug>/`. **Sem numeração** (decisão do editor, 30/10/2026): nada de
"Lição 1", "Lição 2" no título, na página nem no texto, e nenhuma lição remete a outra pelo número ("a próxima lição",
"a Lição 9"); se precisar, "outra lição" ou o título dela. A aba lista da mais recente para a mais antiga. Com um tema pedido ("lição sobre ansiedade"), usa esse tema e só confere a relevância.

**Tema por relevância (decisão do editor, 30/10/2026):** não há mais lista fixa de 12 lições. Cada lição responde a uma
pergunta que as pessoas estão fazendo de verdade sobre a fé, com texto criativo e interessante. A lista antiga (seção 5
do padrão editorial) vira banco de ideias.

**Processo simplificado (decisão do editor, 30/10/2026):** sem auditoria por subagente e sem nota. A segurança vem do
que é mecânico e barato: texto bíblico copiado da página lida, citações conferidas com grep e o validador
(`tools/discipulado/checar_licao.py`, que inclui o medidor de legibilidade). A conferência humana é a verificação diária
do portal (skill `verificacao`). Alvo: uma lição em cerca de 20 a 25 minutos.

Regras que continuam valendo (CLAUDE.md): nada inventado, citação literal só de frase lida na fonte, nunca imagem gerada
por IA, não editar HTML gerado, publicação automática registrada como automática.

## 1. Preparar (2 min)

`git pull origin main`. Ler `docs/discipulado/padrao-de-escrita.md` e a seção 7 de `docs/discipulado/padrao-editorial.md`
(formato), e `conteudo/discipulado/base/glossario.md` e `decisoes.md`. Criar `conteudo/discipulado/<slug>/` (slug curto, sem acento).
Modelo pronto: `conteudo/discipulado/quem-e-jesus/`.

## 2. Escolher o tema (5 min)

Levante perguntas reais de quem está começando ou pensando na fé, em português, e escolha a mais forte que ainda não
virou lição (veja os títulos já publicados):

- **Autocomplete do Google** (funciona nas sessões de nuvem):
  `curl -s "https://suggestqueries.google.com/complete/search?client=firefox&hl=pt-BR&q=<início da pergunta>"`.
  Bons começos: "por que Deus", "como saber se Deus", "é pecado", "como orar", "o que a bíblia diz sobre", "como
  perdoar", "Deus me perdoa", "como ler a bíblia", "como sair da", "crente pode".
- **Autocomplete do YouTube**: o mesmo endereço com `client=youtube&ds=yt`.
- **Reddit** (r/Evangelicos, r/Christianity, r/brasil): o site bloqueia acesso direto (403), então use WebSearch com
  `site:reddit.com`. **"Pessoas também perguntam"**, Google Trends e posts de Instagram e Facebook só pelo que a WebSearch
  mostrar; não contorne bloqueio.
- Notícias e assuntos do momento podem dar o gancho (uma tragédia, uma data, uma série), sem sensacionalismo.

Critérios: a pergunta aparece em mais de uma fonte; é dúvida de quem está começando, não briga entre igrejas; dá para
responder com um texto bíblico central; ajuda na vida real. Registre no `licao.json` o campo `relevancia`:
`{"pergunta": "...", "evidencias": [{"fonte": "Autocomplete do Google", "url": "...", "dado": "a busca \"...\" aparece entre as sugestões de \"...\"", "data": "AAAA-MM-DD"}]}`
(1 a 4 evidências, só o que você viu). A página mostra isso em "Por que esta lição".

Título criativo e honesto: a própria pergunta, como as pessoas a fazem ("Deus me perdoa se eu errar de novo?"), sem
clickbait. A cena de abertura e as comparações devem surpreender, nunca repetir as da lição anterior.

## 3. Pesquisa curta (um subagente, em segundo plano)

Um subagente (Agent, general-purpose) grava `dossie.md`, curto, com:

- **Texto NTLH conferido** das passagens da lição (o tema e a passagem central saem do passo 2), copiado da página
  (https://www.bibliaonline.com.br/ntlh/<livro>/<cap>; reserva: biblegateway.com, versão NTLH), com o URL. Páginas salvas
  em `<scratchpad>/web-<slug>/` para o grep. Nunca de memória. Falas com travessão ficam fora dos recortes.
- **2 ou 3 fontes** de tipos diferentes, com a frase lida e o URL: a Declaração de Fé das Assembleias de Deus
  (https://cgadb.org.br/wp-content/uploads/2021/01/declaracao_de_fe.pdf) e um comentário clássico em domínio público
  (Matthew Henry ou Wesley no biblestudytools.com ou ccel.org). Um comentário moderno só se a frase for lida.
- Erros comuns de interpretação do texto e, se houver, a divergência entre tradições (vai para o guia).

Sem pedir mais que isso: a pesquisa da primeira lição levou 12 minutos porque pediu 10 fontes. Enquanto ela roda, escolha a
imagem (opcional; obra em domínio público no acervo aberto do Metropolitan Museum, como na skill `estudo`).

## 4. Escrever (redator)

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
- Atribuição a autor só do que está na frase lida (erro que a auditoria de "Quem é Jesus Cristo?" achou: acrescentar uma frase ao que
  Wesley disse). Fato bíblico citado com a referência certa (não misturar Marcos com Lucas).

`discipulador.md` (título `# Guia do discipulador`), 500 a 900 palavras: objetivo, fundamentação, referências
com `[verificada]` ou `[parcial]`, diferenças de tradução, dúvidas frequentes, cuidados pastorais, roteiro de 40 minutos,
alertas, sinais de compreensão, divergências.

## 5. Conferir e validar (3 min)

1. Cada frase entre aspas (bíblica ou de autor): `grep -F "<trecho>"` nas páginas salvas. Não achou, vira paráfrase ou sai.
2. `python3 tools/discipulado/legibilidade.py conteudo/discipulado/<slug>/aluno.md` (e `--guia` no guia). Frase
   bíblica longa que não pode ser cortada: comentário `<!-- justificativa: ... -->` no fim do arquivo.
3. `licao.json`: `{"slug", "titulo", "ideia_central", "descricao", "tempo_min",
   "relevancia", "imagem" (opcional), "ia": {"usada": true, "uso": "..."}, "status": "revisao"}`. Sem o campo `auditoria`.
4. `python3 tools/discipulado/checar_licao.py` até passar.

## 6. Publicar (3 min)

1. `python3 tools/publicar.py aprovar conteudo/discipulado/<slug>/licao.json --revisor anderson-pelicioni-de-castro --automatica`.
2. Atualizar `base/glossario.md` e `base/versiculos.md` (limite de 500 versículos na coleção).
3. `python3 tools/build_home.py` e as checagens do CLAUDE.md. Commit único e push (antes, `git pull --rebase origin main`).
   Não versionar `previa/`.

## Relato ao usuário

Link da lição, fontes `[parcial]` e decisões pendentes, em poucas linhas.
