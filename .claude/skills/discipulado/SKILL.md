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

**Sem etapas de revisão (decisão do editor, 30/10/2026):** nada de auditoria, nota, leitura literária, releitura em
camadas ou conferência separada das citações. Escreva já copiando o texto bíblico e as citações das páginas lidas, rode
o validador automático (`tools/discipulado/checar_licao.py`, que o build exige) e publique. A revisão é feita à noite,
pela verificação diária do portal (skill `verificacao`). Alvo: um estudo em cerca de 15 a 20 minutos.

Regras que continuam valendo (CLAUDE.md): nada inventado, citação literal só de frase lida na fonte, nunca imagem gerada
por IA, não editar HTML gerado, publicação automática registrada como automática.

## 1. Preparar (2 min)

`git pull origin main`. Ler `docs/discipulado/padrao-de-escrita.md` e a seção 7 de `docs/discipulado/padrao-editorial.md`
(formato), e `conteudo/discipulado/base/glossario.md` e `decisoes.md`. Criar `conteudo/discipulado/<slug>/` (slug curto, sem acento).
Modelo pronto: `conteudo/discipulado/nascer-de-novo/`.

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

**Leia antes `docs/discipulado/padrao-literario.md`: ele manda no tom.** `aluno.md` com as seções na ordem exata (o validador confere):

```
# <Título em pergunta, igual ao licao.json>
## Questão central
## Introdução
## Fundamentação bíblica
## Desenvolvimento            (subtópicos "### ")
## Aplicação prática
## Perguntas para reflexão
## Resumo
## Continue aprendendo
## Referências                (links das fontes lidas)
```

- Texto bíblico em citação (`> `, um versículo por parágrafo), copiado do dossiê, com o crédito provisório de
  `base/decisoes.md`. Corpo de 1.200 a 2.600 palavras, fora citações e referências.
- Prosa madura (Lewis, Stott, Yancey como técnica): abrir por uma questão real, um episódio bíblico ou um fato
  histórico com fonte, nunca por personagem inventado; uma analogia forte, com os limites ditos; nada de clichê.
- Atribuição a autor só do que está na frase lida (erro já cometido: acrescentar uma frase ao que Wesley disse).
  Fato bíblico com a referência certa. Fato histórico com link na seção Referências.
- **Elementos visuais (obrigatórios; o validador confere).** No texto, pelo menos 3 destaques, cada um num bloco de citação
  que começa com a marca: `> [!chave]` (Ideia-chave, uma frase forte), `> [!termo] **Palavra:** explicação` (Palavra-chave),
  `> [!atencao]` (Cuidado com esta leitura) e `> [!citacao] frase` com a linha seguinte `> Fonte: autor, obra` (frase
  de autor em destaque, em português; original entre parênteses na fonte). No licao.json: `resumo_rapido` {resposta, 3
  ideias, texto_central} (Resumo em 1 minuto), `versiculo_chave` {texto NTLH, referencia}, `contexto` com 3 ou 4
  [rótulo, valor, detalhe] (Em poucas linhas) e `equivocos` com 2 a 4 [Leve|Moderada|Grave, título, explicação]
  (Leituras equivocadas). A página já transforma a Questão central em destaque, a Aplicação em lista com marcas, as
  Perguntas em passos numerados e o Resumo em "Para guardar". Modelo: `conteudo/discipulado/nascer-de-novo/`.
- Falas da NTLH em bloco: troque o travessão por aspas, com as palavras exatas, e avise no texto.
- `titulo_seo` no licao.json: "<pergunta>? Entenda o que a Bíblia ensina".
- **Sem etapa de revisão** (decisão do editor, 30/10/2026): escreva já copiando as citações das páginas salvas e publique. A revisão é feita à noite, pela verificação diária (skill `verificacao`).

`discipulador.md` (título `# Guia do discipulador`), 500 a 900 palavras: objetivo, fundamentação, referências
com `[verificada]` ou `[parcial]`, diferenças de tradução, dúvidas frequentes, cuidados pastorais, roteiro de 40 minutos,
alertas, sinais de compreensão, divergências.

## 5. Validar (1 min)

1. `python3 tools/discipulado/legibilidade.py conteudo/discipulado/<slug>/aluno.md` (e `--guia` no guia). Frase
   bíblica longa que não pode ser cortada: comentário `<!-- justificativa: ... -->` no fim do arquivo.
2. `licao.json`: `{"slug", "titulo", "titulo_seo", "ideia_central", "descricao", "tempo_min" (leitura),
   "resumo_rapido", "versiculo_chave", "contexto", "equivocos", "relevancia", "imagem" (opcional), "ia": {"usada": true, "uso": "..."}, "status": "revisao"}`. Sem o campo `auditoria`.
3. `python3 tools/discipulado/checar_licao.py` até passar.

## 6. Publicar (3 min)

1. `python3 tools/publicar.py aprovar conteudo/discipulado/<slug>/licao.json --revisor anderson-pelicioni-de-castro --automatica`.
2. Atualizar `base/glossario.md` e `base/versiculos.md` (limite de 500 versículos na coleção).
3. `python3 tools/build_home.py` e as checagens do CLAUDE.md. Commit único e push (antes, `git pull --rebase origin main`).
   Não versionar `previa/`.

## Relato ao usuário

Link da lição, fontes `[parcial]` e decisões pendentes, em poucas linhas.
