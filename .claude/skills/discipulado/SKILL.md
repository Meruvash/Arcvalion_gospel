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

## Rotina diária (tarefa agendada, 15:17 de Brasília): 5 estudos no ar até as 18h30

Horário escolhido para não coincidir com as outras rotinas (notícias 2h23, estudos bíblicos 5h13, verificação 21h).

0. **Pelo menos 2 dos 5 do dia vêm do Google Trends** (pedido do editor, 31/10/2026): temas em alta nas buscas
   brasileiras sobre fé (passo 2, "Google Trends"). Registre-os em `em_alta` no catálogo antes de rodar `proximos.py`,
   que os coloca na frente. Se um tema em alta coincidir com um tema de trilha, melhor ainda; depois de publicado, encaixe
   o estudo de trend numa trilha em que ele faça sentido (ou no fim da trilha mais curta).
1. **Ordem: completar as trilhas, depois aumentá-las** (pedidos do editor, 30 e 31/10/2026), para que qualquer pessoa
   possa escolher uma trilha e segui-la até o fim. Trilha de 4 ou 5 estudos é curta demais: quando todas as trilhas do
   catálogo estiverem completas, cada uma cresce até a sua `meta` (no catálogo; 12 estudos), acrescentando ao fim, na
   ordem pedagógica, temas novos dos `previstos` das categorias ou estudos de trend que se encaixem. Novas trilhas podem
   ser propostas ao editor (ex.: "Vida emocional e fé", "Família cristã"). Rode `python3 tools/discipulado/proximos.py 5`: ele lê `conteudo/discipulado/base/catalogo.json`
   e devolve os próximos temas na ordem certa (primeiro os que faltam nas trilhas, a trilha mais perto de ficar completa
   antes; depois os previstos das categorias, a categoria com menos estudos antes). Pule tema que já tenha estudo.
2. Para cada tema, confira a relevância (passo 2 abaixo) só para registrar as evidências: o tema vem da trilha.
3. Pesquisa em paralelo: um subagente por tema, na mesma mensagem (briefing do passo 3). Enquanto pesquisam, escolha
   as 5 imagens.
4. Escreva os 5 estudos no padrão de `nascer-de-novo` (passo 4), valide, publique um por um (passo 7) e troque o
   `{"titulo": ...}` de cada trilha pelo slug e tire o título dos `previstos` da categoria.
5. Commit único, `git pull --rebase origin main` e push. Se às 18h30 houver menos de 5 prontos, publique os que passaram
   e explique; nunca publique estudo com fonte faltando para cumprir a meta.
6. Resumo curto: estudos publicados com link, trilhas que ficaram completas e o que falta em cada uma.

## 1. Preparar (2 min)

`git pull origin main`. Ler `docs/discipulado/padrao-de-escrita.md` e a seção 7 de `docs/discipulado/padrao-editorial.md`
(formato), e `conteudo/discipulado/base/glossario.md` e `decisoes.md`. Criar `conteudo/discipulado/<slug>/` (slug curto, sem acento).
Modelo pronto: `conteudo/discipulado/nascer-de-novo/`.

## 2. Escolher o tema (5 min)

Levante perguntas reais de quem está começando ou pensando na fé, em português, e escolha a mais forte que ainda não
virou lição (veja os títulos já publicados):

- **Google Trends (obrigatório, pedido do editor de 31/10/2026).** O que funciona sem contornar bloqueio:
  - buscas em alta no Brasil, do dia: `curl -s "https://trends.google.com/trending/rss?geo=BR"` (leia os títulos e o
    `ht:approx_traffic`; quase sempre é notícia, mas às vezes há gancho de fé: uma data cristã, uma tragédia, um debate);
  - o ranking do ano: `https://trends.withgoogle.com/year-in-search/<ano>/br/` (WebFetch), seções "O que é", "Por que",
    "Quem é" e "Virou trend";
  - os tópicos que o Trends reconhece para um termo: `curl -s "https://trends.google.com/trends/api/autocomplete/<termo>?hl=pt-BR"`;
  - dados do Trends publicados em reportagens: WebSearch com `"Google Trends"` + o tema (ex.: em dez/2025 o Jornal do Brás
    publicou que "ansiedade e Bíblia" cresceu 38% nas buscas entre 2023 e 2025). Cite a reportagem com link e data.
  A página de comparação do Trends (`/trends/api/explore`) responde 429 para robôs: **não se contorna** (nada de cookie,
  user-agent ou repetição para driblar o limite). Sem dado do Trends, diga isso e use o autocomplete abaixo.
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
(1 a 4 evidências, só o que você viu; quando houver, uma delas do Google Trends). A página mostra isso em "Por que
esta lição".

Título criativo e honesto: a própria pergunta, como as pessoas a fazem ("Deus me perdoa se eu errar de novo?"), sem
clickbait. A cena de abertura e as comparações devem surpreender, nunca repetir as da lição anterior.

## 3. Pesquisa curta (um subagente, em segundo plano)

Um subagente (Agent, general-purpose) grava `dossie.md`, curto, com:

- **Texto NTLH conferido** das passagens da lição (o tema e a passagem central saem do passo 2), copiado da página
  (https://www.bibliaonline.com.br/ntlh/<livro>/<cap>; reserva: biblegateway.com, versão NTLH), com o URL. Páginas salvas
  em `<scratchpad>/web-<slug>/` para o grep. Nunca de memória. Falas com travessão ficam fora dos recortes.
- **Pelo menos 2 fontes além da Bíblia, de autores diferentes (regra do editor, 30/10/2026; o validador confere).** O ideal
  são 3 ou 4 vozes de tradições diferentes, sempre com a Declaração de Fé das Assembleias de Deus, e mostrando onde elas
  divergem (ex.: em "nascer de novo", Henry, Wesley e Calvino leem a "água" de modos diferentes). Texto de uma fonte só
  fica suspeito. Cada uma com a frase lida e o URL: a Declaração de Fé das Assembleias de Deus
  (https://cgadb.org.br/wp-content/uploads/2021/01/declaracao_de_fe.pdf) e um comentário clássico em domínio público
  (Matthew Henry, John Wesley e João Calvino têm comentários completos em biblestudytools.com e ccel.org; Spurgeon tem
  sermões em ccel.org). Um comentário moderno só se a frase for lida.
- Erros comuns de interpretação do texto e, se houver, a divergência entre tradições (vai para o guia).

Sem pedir mais que isso: a pesquisa da primeira lição levou 12 minutos porque pediu 10 fontes. Enquanto ela roda, escolha a
imagem (opcional; obra em domínio público no acervo aberto do Metropolitan Museum, como na skill `estudo`). **Prefira obra colorida** (pedido do editor, 31/10/2026): pintura, tapeçaria, vitral, iluminura; na busca do Met, use `&medium=Paintings` primeiro. Gravura ou desenho sem cor só quando não houver obra colorida ligada ao texto.

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
   "resumo_rapido", "versiculo_chave", "contexto", "equivocos", "relevancia", "categoria", "palavras_chave" (3 a 12, para a busca),
   "imagem" (opcional), "ia": {"usada": true, "uso": "..."}, "status": "revisao"}`. Sem o campo `auditoria`.
3. `python3 tools/discipulado/checar_licao.py` até passar.

## 6. Biblioteca e trilhas (1 min)

A seção tem dois modos (pedido do editor, 30/10/2026): a **Biblioteca** (`discipulado/`, com busca, categorias e estudos;
`discipulado/tema/<slug>/`) e as **Trilhas** opcionais (`discipulado/trilha/<slug>/`). Tudo sai de
`conteudo/discipulado/base/catalogo.json`:

- `categoria` do estudo: um dos slugs do catálogo. Se o título estiver em `previstos` da categoria, tire-o de lá.
- Se o tema aparece numa trilha como `{"titulo": "..."}`, troque pelo slug do estudo. A ordem pertence à trilha; um
  estudo pode estar em várias; nunca duplique conteúdo. O validador confere slugs, repetições e categoria.
- Cada estudo é autossuficiente: nada de "como vimos no estudo anterior". As trilhas só sugerem a ordem.

## 7. Publicar (3 min)

1. `python3 tools/publicar.py aprovar conteudo/discipulado/<slug>/licao.json --revisor anderson-pelicioni-de-castro --automatica`.
2. Atualizar `base/glossario.md` e `base/versiculos.md` (limite de 500 versículos na coleção).
3. `python3 tools/build_home.py` e as checagens do CLAUDE.md. Commit único e push (antes, `git pull --rebase origin main`).
   Não versionar `previa/`.

## Relato ao usuário

Link da lição, fontes `[parcial]` e decisões pendentes, em poucas linhas.
