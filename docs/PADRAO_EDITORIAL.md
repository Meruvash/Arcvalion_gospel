# Padrão editorial

Copiado do padrão das notícias e das resenhas do Elite Boardgamers ("fato tem fonte, opinião tem dono"), adaptado ao
jornalismo cristão. `tools/noticias/checar_noticia.py` e `tools/estudos/checar_estudo.py` conferem o que a máquina
consegue; `tools/build.py` não publica o que não passa. O resto (a fonte diz mesmo isso? a frase existe? a foto é do
fato certo?) é da pessoa revisora, que aprova com `tools/publicar.py`.

## Notícias (`conteudo/noticias/<AAAA-MM-DD>-<assunto>.json`)

| Campo | Seção da página | Regra |
|---|---|---|
| `categoria` | etiqueta | slug de uma editoria de `config/editorias.json` |
| `selo` | selo da nota | Boa notícia, Vale acompanhar, Para refletir, Motivo de alerta ou Informativo |
| `titulo` | título | 8 a 16 palavras, o fato e quem; sem "!", caixa alta ou caça-clique |
| `lide` | abertura | 35 a 70 palavras: o fato, quando, onde |
| `por_que_importa` | Por que importa | 30 a 70 palavras de análise nossa, assinada pelo portal |
| `numeros` | Em números | 2 a 4 `[valor, rótulo, fonte]`, todos com fonte |
| `corpo` | Contexto | 1 a 3 parágrafos, 40 a 200 palavras |
| `no_brasil` | No Brasil | 25 a 80 palavras: o efeito ou a situação no Brasil |
| `critica` | O que dizem | 1 a 3 posições `{fonte, texto, citacao, url}`; paráfrase com o nome dentro do texto; `citacao: true` só com frase literal lida na página de `url`; `traducao: true` quando a frase foi traduzida (a página mostra "tradução livre") |
| `para_quem` / `nao_e_para` | O que muda para você / Pontos de atenção | 1 a 3 / 1 a 3 |
|  |  | **O que muda para você**: o efeito concreto do fato na vida da família, da igreja ou do cidadão, tirado do que está nas fontes (se ainda depende de votação, diga "Se virar lei, …"). **Pontos de atenção**: o que está pendente ou incerto (votação que falta, prazo, dado de outro país, ressalva da própria fonte), só fato com fonte, sem opinião. |
| `veredito` | Nossa opinião | 20 a 60 palavras: o **posicionamento do portal** sobre o fato ("a gente apoia/concorda/cobra/discorda…"), o porquê e um conselho concreto. **Sem versículo no texto** (pedido de 30/10/2026; o validador recusa referência bíblica aqui) |
| `versiculo` | fim da Nossa opinião | opcional: `{texto, referencia, traducao}`, sai embaixo do posicionamento, em linha separada. Só quando a passagem cabe sem forçar |
| `fontes` | Fontes | 2 ou mais, com nome, link, data e `tipo` (pelo menos uma `primaria`) |
| `crivo` | Por que esta notícia entrou | motor de relevância de 0 a 100 (`config/relevancia.json`, `docs/CRIVO_NOTICIAS.md`, seção 4): pontos, trilha, abrangência, origem e os 5 critérios com o porquê; manchete = maior pontuação do dia, com 70 ou mais |
| `instituicao` | linha de data | quem fez o fato (Senado, CGADB, Pew…) |
| `imagem` | foto | obrigatória: arquivo em `conteudo/imagens/`, crédito com licença, `alt`; nunca IA |
| `estudos` | Estudos citados | `[{nome, estudo: <slug>}]` |
| `ia`, `status`, `revisao`, `publicado_em`, `correcoes` | Como foi feita | `status: revisao` até a aprovação humana; `publicar.py` grava o resto |

Regras de texto: tom opinativo só em Por que importa, O que muda para você e Nossa opinião (Pontos de atenção é factual); o
resto é neutro. Política com os dois lados e a fonte de cada um. Sem fonte anônima ("segundo fontes"), sem verbo de
torcida, sem loja de varejo no texto, sem citação que não esteja na fonte. Chamadas para redes em
`conteudo/chamadas.json`: emoção e curiosidade, mas tudo o que a chamada promete está no texto. Meta: **5 notícias por
dia**, 2 delas com Opinião Forte (seção abaixo).

## Opinião Forte (30/10/2026)

Pedido do responsável editorial: **2 de cada 5 notícias do dia** saem com Opinião Forte, marcadas com
`"opiniao_forte": true`. Base: a seção "Opinião forte" do Elite Boardgamers (PADRAO_EDITORIAL.md na raiz),
adaptada para notícia e para a linha do portal. Objetivo: gerar reação e compartilhamento sem abrir mão do fato.

**Onde vai o tom:** só em `por_que_importa`, `para_quem` (O que muda para você) e `veredito` (Nossa opinião), e na
`chamada` para redes. **Onde não vai:** título, lide, números, contexto, No Brasil, O que dizem, Pontos de atenção e
fontes continuam informativos e exatos. O título pode ter força, desde que tudo nele seja fato e diga o que aconteceu
e com quem (nada de caça-clique).

1. **Uma tese por notícia.** Uma frase que o leitor possa repetir ou contestar, firme e do ponto de vista cristão e
   conservador do portal. Ela abre o Por que importa ou o veredito.
2. **O tom nasce do fato.** A ironia vem do contraste entre o que a decisão, a lei ou o discurso promete e o que os
   dados e o próprio texto oficial mostram. Todo número e toda posição citada continuam com fonte.
3. **Alvo certo.** A crítica mira decisões, leis, políticas, argumentos e instituições no exercício do poder. Nunca a
   honra de pessoas (nada de acusação sem prova, apelido ou ataque pessoal), nunca vítimas, nunca grupos de pessoas
   por fé, origem, aparência, doença ou deficiência.
4. **Justiça na mesma página.** O lado contrário aparece em O que dizem, com o argumento mais forte dele e a fonte. A
   opinião forte responde a esse argumento, não a uma caricatura.
5. **Frase pronta para compartilhar.** Pelo menos uma frase curta e citável no veredito, e a chamada fecha com uma
   pergunta que provoque resposta.
6. **Inteligente, não grosseiro.** Sem palavrão, xingamento ou deboche fácil, e sem adjetivo de torcida (detonou,
   lacrou, humilhou). Comparações concretas e inesperadas valem mais que adjetivos.
7. **Nada inventado para causar.** Se a apuração não sustenta a polêmica, o tom fica firme mas sem a tese. A opinião é
   do portal e precisa ser defensável diante da fonte e passar no crivo jurídico (seção abaixo).
8. **Voz: "a gente".** Tom de conversa, mas a voz é do portal: "a gente", nunca "eu". Nunca cite humoristas.
9. **Sem muleta.** A mesma piada ou bordão no máximo uma vez por notícia e não se repete na notícia seguinte. Repita as
   técnicas, não as frases.
10. **Fé com respeito.** Nada de deboche com a fé de ninguém, nem com outras denominações ou religiões. Versículo só
    com referência e tradução, nunca usado como arma contra pessoas, e na notícia só no campo `versiculo`, no fim
    da Nossa opinião: no meio do posicionamento ele não entra.

As outras 3 notícias de cada 5 seguem o tom padrão: opinião clara e fundamentada, sem ironia.

## Opinião pelo consenso conservador (30/10/2026)

Pedido do responsável editorial: a opinião (Por que importa, O que muda para você, Nossa opinião e versículo) agrada o
público conservador e mantém a proteção jurídica do portal, as duas coisas juntas.

1. **Parta do consenso da direita.** A tese sai dos princípios que a direita e os conservadores, no Brasil e fora
   dele, defendem em comum: devido processo e Estado de Direito igual para todos, limites ao poder do Estado e do
   Judiciário, transparência das decisões, liberdade de expressão e religiosa, família, vida, imunidades e
   prerrogativas do mandato, responsabilidade fiscal.
2. **O que desagrada esse público vai com tremenda sutileza.** Quando o fato pede uma ressalva incômoda para a
   direita (uma ordem judicial descumprida, um boato que circula entre os nossos), ela entra como conselho em nome do
   próprio campo ("a melhor defesa é a que se faz com documento"), nunca como sermão ou acusação.
3. **O fato não muda.** Título, lide, números, contexto, No Brasil, O que dizem e Pontos de atenção seguem neutros e
   completos, inclusive quando o fato é desfavorável a quem está perto da linha do portal (CRIVO_NOTICIAS, seção 4).
4. **O crivo jurídico continua valendo** (seção abaixo): a crítica mira atos, com fato e fonte; nada de imputar crime
   ou intenção.

## Crivo jurídico (30/10/2026)

Pedido do responsável editorial: a opinião pode ser forte, mas não pode abrir espaço para processo. Vale para toda
notícia, e com mais rigor para as de Opinião Forte. Antes de publicar, faça a **leitura hostil**: leia cada frase de
opinião como a pessoa ou o grupo citado leria, e como um juiz leria. Se alguma leitura possível acusa alguém de crime,
ofende a honra ou discrimina, reescreva até sobrar uma leitura só.

1. **Nada de imputar crime ou intenção sem fonte oficial.** Calúnia, difamação e injúria (artigos 138 a 140 do Código
   Penal) nascem de atribuir a alguém crime, fato desonroso ou qualidade ofensiva. Investigado é "suspeito" ou
   "investigado, segundo a polícia"; réu é "acusado"; só é "condenado" quem tem condenação. Motivação ("quis esconder",
   "agiu de má-fé") só se estiver em documento oficial ou em fala atribuída.
2. **A crítica mira atos públicos, não a pessoa.** Lei, projeto, voto, decisão, política e argumento podem ser
   criticados com ironia; caráter, vida privada, aparência e família de quem decidiu, não.
3. **Nada de generalizar grupos.** Nenhuma frase que desqualifique pessoas por raça, cor, etnia, religião, origem,
   sexo, orientação sexual ou identidade de gênero (Lei 7.716/1989; desde 2019 o STF aplica a mesma lei à homofobia e à
   transfobia). Discordar de uma lei sobre um grupo é legítimo; atacar o grupo, não.
4. **Sem palavra de duplo sentido.** Ironia que também funcione como insulto a uma pessoa ou grupo sai. Rótulos como
   corrupto, criminoso, bandido, mentiroso, golpista, quadrilha, genocida, nazista ou fascista não entram nas partes
   de opinião (o validador bloqueia); nas partes de fato, só atribuídos a fonte oficial.
5. **Fato conferido e atribuído.** Todo fato que embasa a opinião tem fonte com link e data; citação literal só de
   frase lida na fonte; paráfrase com o nome de quem disse.
6. **Imagem sem constrangimento.** Foto de pessoa só em contexto público e ligado ao fato, nunca em situação que a
   ridicularize; criança e vítima não aparecem identificáveis.
7. **Direito de resposta e correção.** Pedido de resposta ou de correção é atendido com rapidez (Lei 13.188/2015) e
   registrado com `tools/publicar.py corrigir`.

Registro obrigatório em cada notícia: `"checagem_juridica"`, uma ou duas frases dizendo o que foi conferido na leitura
hostil. Sem ele, o validador não deixa publicar. Na dúvida, o tom fica firme e a frase arriscada sai: a força vem do
fato bem apurado, não do adjetivo.

## Estudos bíblicos (`conteudo/estudos/<slug>.json`)

Esqueleto da resenha do Elite: `titulo`, `passagem`, `sigla`, `livro`, `testamento`, `genero`, `nivel` (1 a 3),
`tempo_min`, `selo` (Ótimo para começar, Ideal para grupos, Para aprofundar), `tagline` (12 a 30 palavras), `lede`
(40 a 90), `descricao`, `versiculo_chave` (texto, referência e tradução), `estrutura` (3 a 7 partes com referência),
`contexto`, `aplicacao`, `destaques` (o que o texto ensina), `atencao` (leituras equivocadas, com gravidade), `perfil`,
`formatos` (sozinho, em família, em grupo), `para_quem`, `nao_e_para`, `dica`, `traducoes`, `relacionadas`,
`comparacoes`, `versiculos`, `veredito` (Para guardar), `ficha`, `fontes` (3 ou mais `[nome, link, uso]`), `consulta`,
`legenda` (Instagram), `imagem` (domínio público ou licença livre), `ia`, `status`.

**O que dizem os teólogos (30/10/2026).** No lugar da opinião da crítica nas resenhas do Elite, o centro do estudo é
uma questão em que teólogos brasileiros de referência divergem sobre a passagem: `questao` (a pergunta, em uma frase),
`posicoes` (2 a 4 lados `{lado, resumo, teologos}`; cada lado com 2 a 4 teólogos `{autor, quem, obra, url, data,
texto, citacao?, citacao_url?}`) e `convergencias` (1 a 5 pontos em que os lados concordam). Regras:

1. **Cada lado no seu melhor argumento**, dito como quem o defende diria; nada de caricatura no relato. Os lados
   são relato; a opinião do portal fica em `nossa_posicao`, `veredito`, `aplicacao`, `tagline`, `lede` e `legenda`.
2. **Teólogo brasileiro de referência**, com a igreja ou instituição conferida na fonte (`quem`). Obra ou artigo com
   link e data (`url`, `data`); `texto` é paráfrase fiel de 25 a 110 palavras com o nome dentro.
3. **Citação literal** (`citacao`) só de frase lida na página de `citacao_url` (ou de `url`), copiada sem mudar nada.
4. **Comentaristas clássicos** (Calvino, Matthew Henry etc.) entram em `contexto` ou `destaques`, não como lado.
5. **Respeito entre tradições**: divergência entre irmãos, nunca acusação de heresia a quem defende um dos lados.

**Linha editorial pentecostal (30/10/2026).** O Paladino é um portal cristão **pentecostal**, e o estudo diz isso:
"mesmo que a gente respeite a opinião dos outros, a gente precisa passar aquilo que a gente acredita" (pedido de
30/10/2026). Referência doutrinária: a **Declaração de Fé das Assembleias de Deus** (CGADB/CPAD, 2016,
https://cgadb.org.br/declaracao-de-fe/), conferida no texto antes de cada estudo.

1. **`nossa_posicao`** (obrigatório desde 30/10/2026; 1 a 4 parágrafos, 60 a 350 palavras): a seção "Nossa posição",
   assinada pelo portal, com a tese pentecostal firme, as razões bíblicas e a Declaração de Fé citada. Voz "a gente".
2. **O lado pentecostal vem primeiro** em `posicoes` e, quando a Declaração de Fé trata do tema, ela entra como um dos
   nomes do lado (autor "Declaração de Fé das Assembleias de Deus", com a comissão em `quem`).
3. **Título, tagline, lede, destaques, atenção, aplicação, veredito e legenda** falam a partir da cosmovisão
   pentecostal (dons atuais, batismo no Espírito, batismo de quem crê, santidade, volta de Cristo como as Assembleias
   ensinam). Em `atencao`, a leitura que o portal rejeita pode aparecer como equivocada, explicando por quê.
4. **Firmeza com respeito**: o outro lado continua relatado com fidelidade, com o melhor argumento e as fontes; nada
   de chamar irmão de herege, de ironia com outra denominação ou de caricatura. Discordar com clareza, sim.
5. **Quando os pentecostais divergem entre si** (há assembleianos calvinistas e arminianos, por exemplo), siga a
   Declaração de Fé e diga, numa frase, que há pentecostais que pensam diferente.
6. **Nada inventado continua valendo**: a tese é nossa, mas todo fato, citação e posição atribuída tem fonte.
7. **Escatologia (30/10/2026): a posição do portal é a de Mateus 24.** Uma só vinda de Cristo, pessoal e visível,
   **depois da tribulação**: "logo depois da aflição daqueles dias" o Filho do Homem vem nas nuvens e os anjos, com
   trombeta, ajuntam os escolhidos (Mateus 24:29-31); o arrebatamento de 1 Tessalonicenses 4 acontece nessa vinda.
   Aqui o portal **diverge da Declaração de Fé das Assembleias de Deus** (pré-tribulacionista) e diz isso com respeito,
   relatando a leitura das Lições Bíblicas da CPAD com fidelidade. Ninguém marca data (Mateus 24:36); a ênfase é vigiar
   e perseverar (24:13, 42-44). Modelo: `conteudo/estudos/arrebatamento-1-tessalonicenses-4.json`.

**Mistura de temas (30/10/2026).** Dos 5 estudos do dia, **2 são de debate** (`"tipo": "debate"`: lados + "Nossa
posição") e **3 são de passagem** (`"tipo": "passagem"`: textos que unem os cristãos, com `vozes` de 2 a 4 teólogos e
`nossa_posicao` exibida como "O olhar pentecostal"). A identidade pentecostal fica declarada, e a maior parte dos estudos
acolhe o cristão de qualquer igreja. A página "Quem somos" (`conteudo/paginas/sobre.json`, publicada em /sobre/) explica
isso ao leitor.

**Título do estudo (30/10/2026): curiosidade, não conclusão.** O título apresenta a passagem e a pergunta ou a tensão
que o estudo resolve, do jeito de uma manchete que dá vontade de clicar, sem entregar a resposta. Bom: "1 Tessalonicenses
4: o arrebatamento vem antes da tribulação ou junto com a volta de Cristo". Ruim: "...: o arrebatamento acontece na
volta visível de Cristo, depois da tribulação". A posição do portal fica no corpo (`nossa_posicao`, `veredito`) e pode
aparecer na `tagline` e na `legenda`; o título não a antecipa. Vale também para os títulos ao ajustar estudos já publicados.

Fotos: fontes, licenças e o robô `tools/fotos.py` em `docs/FOTOS.md`.

Interpretação sempre com o nome de quem a defende; divergência entre tradições cristãs aparece como divergência;
tradução da Bíblia sempre indicada.
