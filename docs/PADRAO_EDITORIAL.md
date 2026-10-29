# Padrão editorial

Vale para toda matéria. `tools/editorial/checar.py` confere o que dá para conferir por máquina, e
`tools/build.py` se recusa a publicar matéria que não passe. O que a máquina não confere (se a fonte diz mesmo
aquilo, se a frase citada existe, se a foto é do fato certo) é responsabilidade da pessoa revisora.

## Premissas (e onde cada uma é garantida)

| # | Premissa | Garantia automática |
|---|---|---|
| 1 | IA pode ajudar na pesquisa, organização e preparação | skill `pauta` só cria rascunhos; campo `ia` obrigatório e mostrado na página |
| 2 | Fontes identificáveis e verificáveis | `fontes` com nome, link e data; notícia com ≥ 2 fontes e ≥ 1 primária; bloqueio de "segundo fontes", "nos bastidores", "dizem que" |
| 3 | Fato separado de opinião | tipos rotulados; quadro de análise só em notícia/explicativo; opinião só no tipo `opiniao`, com autor identificado e aviso |
| 4 | Nenhuma notícia inventada | revisão humana obrigatória; exemplos fictícios isolados em `exemplos/`, com noindex e aviso |
| 5 | Citações atribuídas | bloco de citação exige `autor` e o índice da `fonte` onde a frase está; a página mostra "Fulano, cargo, em <fonte>" |
| 6 | Revisão humana antes de publicar | `revisao.revisor` precisa ser pessoa revisora de `config/equipe.json`; quem assina notícia não revisa a própria |
| 7 | Nada de paráfrase superficial | regra da skill `pauta` e da revisão: fonte primária + apuração/contexto próprio; crédito a quem deu primeiro |
| 8 | Contexto, originalidade e valor | mínimo de 120 palavras de corpo (250 no explicativo); intertítulos; quadro "Por que importa" |
| 9 | Publicidade e patrocínio identificados | tipo `patrocinado` exige patrocinador, mostra aviso no topo, rótulo, `rel="sponsored"`, fica fora do sitemap de notícias e do RSS; afiliados com aviso e `rel="sponsored nofollow"` |
| 10 | Jornalismo, opinião e comercial separados | patrocinado não pode ser manchete nem destaque; sem anúncio dentro de conteúdo pago |
| 11 | Correção e atualização | `correcoes` com data e texto, quadro visível, aviso na assinatura, `dateModified`; `tools/publicar.py corrigir` |
| 12 | Nada de sensacionalismo | título sem "!", caixa alta, "você não vai acreditar", "urgente:", "chocante"; avisos para verbos de torcida |

## Tipos de conteúdo

| Tipo | Rótulo | schema.org | Regras |
|---|---|---|---|
| `noticia` | (nenhum) | NewsArticle | lide obrigatório, foto obrigatória, ≥ 2 fontes, ≥ 1 primária |
| `analise` | Análise | AnalysisNewsArticle | igual à notícia; assinada |
| `opiniao` | Opinião | OpinionNewsArticle | autor da equipe ou `colaborador` com nome e descrição; aviso de opinião |
| `explicativo` | Explica | Article | evergreen (Fé e Bíblia, guias); ≥ 250 palavras; pode ter `faq` e `referencias_biblicas` |
| `patrocinado` | Conteúdo patrocinado | Article (`genre`) | `patrocinador` obrigatório; não é escrito pela redação |

## Formato do arquivo (`conteudo/artigos/<slug>.json`)

```json
{
 "slug": "stf-julga-recurso-ensino-religioso",
 "status": "rascunho | revisao | publicado | despublicado",
 "tipo": "noticia",
 "editoria": "politica-e-sociedade",
 "titulo": "STF julga nesta quinta recurso sobre ensino religioso nas escolas públicas",
 "titulo_seo": "(opcional, para a busca)",
 "linha_fina": "Resumo em uma ou duas frases.",
 "lide": "Quem, o quê, quando, onde, como e por quê.",
 "analise": "(opcional) Por que importa, separado do relato.",
 "corpo": ["parágrafo", {"intertitulo": "..."}, {"citacao": "frase exata", "autor": "Nome", "cargo": "cargo", "fonte": 0}],
 "fontes": [{"nome": "STF: pauta do plenário", "url": "https://...", "data": "29/10/2026", "tipo": "primaria"}],
 "autor": "slug-da-equipe",
 "tags": ["STF", "educação"],
 "imagem": {"arquivo": "nome.jpg", "credito": "Foto: Fulano/Agência X (licença)", "alt": "Descrição da imagem"},
 "ia": {"usada": true, "uso": "pesquisa e organização"},
 "revisao": {"revisor": "slug", "data": "ISO 8601"},
 "publicado_em": "2026-10-29T09:10:00-03:00",
 "atualizado_em": "(quando houver)",
 "correcoes": [{"data": "2026-10-30", "texto": "O que mudou"}],
 "manchete": false, "destaque": false, "sem_anuncios": false,
 "faq": [{"pergunta": "...?", "resposta": "..."}],
 "referencias_biblicas": ["João 3:16"], "versao_biblica": "tradução e licença",
 "afiliados": [{"texto": "...", "url": "https://...", "loja": "..."}],
 "colaborador": {"nome": "...", "descricao": "..."},
 "patrocinador": {"nome": "...", "url": "https://..."}
}
```

`revisao` e `publicado_em` são gravados por `tools/publicar.py`, não à mão. A foto fica em `conteudo/imagens/`
(mínimo 800 px de largura; o Discover recomenda 1200 px). Imagem gerada por IA não ilustra notícia. Fontes de foto,
licenças e o robô `tools/fotos.py`: `docs/FOTOS.md`.

## Escrita

- Título informativo, com o fato e o sujeito. Verbos neutros de atribuição: afirmou, disse, criticou, rebateu.
- Em política, relate a posição de cada lado com a fonte de cada uma. A linha cristã e conservadora do portal
  aparece na escolha de pautas, no quadro de análise e na opinião assinada; nunca na alteração do fato.
- Citação literal só de frase lida na fonte; sem ela, discurso indireto atribuído.
- Bíblia: indique a tradução. Use traduções em domínio público ou trechos curtos com crédito, conforme a licença.
- Dados e números sempre com a fonte e a data de referência.
- Evite as expressões listadas em `tools/editorial/vicios.py` (aviso, não bloqueio): troque por um fato concreto.
