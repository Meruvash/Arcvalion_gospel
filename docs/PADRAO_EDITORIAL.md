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
| `critica` | O que dizem | 1 a 3 posições `{fonte, texto, citacao, url}`; paráfrase com o nome dentro do texto; `citacao: true` só com frase literal lida na página de `url` ("tradução livre" quando traduzida) |
| `para_quem` / `nao_e_para` | O que muda para você / Pontos de atenção | 1 a 3 / 1 a 3 |
|  |  | **O que muda para você**: o efeito concreto do fato na vida da família, da igreja ou do cidadão, tirado do que está nas fontes (se ainda depende de votação, diga "Se virar lei, …"). **Pontos de atenção**: o que está pendente ou incerto (votação que falta, prazo, dado de outro país, ressalva da própria fonte), só fato com fonte, sem opinião. |
| `veredito` | Nossa opinião | 20 a 60 palavras, conselho claro e o porquê |
| `fontes` | Fontes | 2 ou mais, com nome, link, data e `tipo` (pelo menos uma `primaria`) |
| `crivo` | Por que esta notícia entrou | pontos (0 a 20), trilha, eixos, portal de origem e critérios (`docs/CRIVO_NOTICIAS.md`); manchete = maior pontuação do dia |
| `instituicao` | linha de data | quem fez o fato (Senado, CGADB, Pew…) |
| `imagem` | foto | obrigatória: arquivo em `conteudo/imagens/`, crédito com licença, `alt`; nunca IA |
| `estudos` | Estudos citados | `[{nome, estudo: <slug>}]` |
| `ia`, `status`, `revisao`, `publicado_em`, `correcoes` | Como foi feita | `status: revisao` até a aprovação humana; `publicar.py` grava o resto |

Regras de texto: tom opinativo só em Por que importa, O que muda para você e Nossa opinião (Pontos de atenção é factual); o
resto é neutro. Política com os dois lados e a fonte de cada um. Sem fonte anônima ("segundo fontes"), sem verbo de
torcida, sem loja de varejo no texto, sem citação que não esteja na fonte. Chamadas para redes em
`conteudo/chamadas.json`: emoção e curiosidade, mas tudo o que a chamada promete está no texto.

## Estudos bíblicos (`conteudo/estudos/<slug>.json`)

Esqueleto da resenha do Elite: `titulo`, `passagem`, `sigla`, `livro`, `testamento`, `genero`, `nivel` (1 a 3),
`tempo_min`, `selo` (Ótimo para começar, Ideal para grupos, Para aprofundar), `tagline` (12 a 30 palavras), `lede`
(40 a 90), `descricao`, `versiculo_chave` (texto, referência e tradução), `estrutura` (3 a 7 partes com referência),
`contexto`, `aplicacao`, `destaques` (o que o texto ensina), `atencao` (leituras equivocadas, com gravidade), `perfil`,
`formatos` (sozinho, em família, em grupo), `para_quem`, `nao_e_para`, `dica`, `traducoes`, `relacionadas`,
`comparacoes`, `versiculos`, `veredito` (Para guardar), `ficha`, `fontes` (3 ou mais `[nome, link, uso]`), `consulta`,
`legenda` (Instagram), `imagem` (domínio público ou licença livre), `ia`, `status`.

Fotos: fontes, licenças e o robô `tools/fotos.py` em `docs/FOTOS.md`.

Interpretação sempre com o nome de quem a defende; divergência entre tradições cristãs aparece como divergência;
tradução da Bíblia sempre indicada.
