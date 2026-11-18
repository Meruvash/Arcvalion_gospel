# Plano: imagens de arquivo, trechos de terceiros e react nos vídeos e web documentários (18/11/2026)

Pedido do editor (18/11/2026): estudar como os canais de resumo de filmes trabalham, se são monetizados e o que se
aplica a nós. Os web documentários vão precisar de imagens de arquivo público e de trechos curtos de outros vídeos, com
react por cima.

## 1. O que a pesquisa mostrou (18/11/2026)
- **A regra do YouTube que decide a monetização é a de "conteúdo reutilizado", não a de direitos autorais.**
  - O canal é reprovado quando reaproveita conteúdo "sem adicionar comentário original significativo, modificações
    substanciais ou valor educativo ou de entretenimento".
  - Comentário, react e compilação são permitidos quando há esse acréscimo.
  - A análise é do **canal inteiro**, não de cada vídeo.
  - Um vídeo pode não ter nenhuma reivindicação de direitos e, mesmo assim, ser marcado como reutilizado.
  - Ter permissão do autor não muda isso.
  - Fonte: [Central de Ajuda do YouTube, políticas de monetização](https://support.google.com/youtube/answer/1311392?hl=en).
- **Os canais de resumo de filmes que se mantêm são os que fazem crítica e análise com narração própria.** Os guias
  classificam como alto risco o "resumo que reconta a trama por cima de trechos longos" e a "voz automática descrevendo o
  que já está na tela".
  - Fontes: [recapo.ai](https://recapo.ai/blog/fair-use-for-movie-recap-videos/),
    [air.io](https://air.io/en/youtube-hacks/reused-content-monetization-rejected),
    [mediacube](https://mediacube.io/pt/blog/youtube-reused-content).
- **Espelhar a imagem não cria originalidade e, segundo os relatos, não engana o Content ID por muito tempo.** O
  espelhamento serve para driblar a comparação automática, não para cumprir a lei.
  - Fontes: [recapo.ai](https://recapo.ai/blog/fair-use-for-movie-recap-videos/),
    [Wikipedia: Content ID](https://en.wikipedia.org/wiki/Content_ID).
- **Há risco jurídico real no extremo do nicho.** No Japão, os "fast movies" (resumos de 10 minutos com narração da
  trama) terminaram em condenação de ¥500 milhões para os autores (Tribunal Distrital de Tóquio, 2022 e 2023).
  - Fontes: [Japan Times](https://japantimes.co.jp/news/2022/11/17/national/crime-legal/fast-movie-court-ruling),
    [TorrentFreak](https://torrentfreak.com/youtubers-must-pay-3-5m-for-uploading-10-minute-movie-edits-221118/),
    [CODA](https://coda-cj.jp/en/news/177/).
- **O nosso caso:** "O banco leiloa a sua fazenda sem juiz?" usou ~25 s de TikTok, inclusive a abertura, e foi o único
  vídeo que o YouTube Shorts não distribuiu.

## 2. O que fazemos: react e arquivo com segurança

### 2.1 Fontes, nesta ordem
1. **Imagem própria:** pintura e animação em código, que são a base do formato e o que tem dado alcance.
2. **Arquivo público ou aberto, com a licença conferida no dia e registrada:**
   - **Senado:** fotos da Agência Senado e material do Senado Multimídia podem ser reproduzidos livremente, com crédito e
     sem descaracterizar. Os **vídeos da TV Senado** só com autorização, pela TV Senado Agência (seacer@senado.leg.br).
     Fontes: [Política de Uso](https://www12.senado.leg.br/assessoria-de-imprensa/politica-de-uso),
     [Como obter imagens](https://www12.senado.leg.br/assessoria-de-imprensa/como-obter-imagens-audios-e-textos).
   - **Satélite:** Landsat (USGS e NASA) é domínio público, com o crédito da missão e do ano. Copernicus Sentinel tem
     licença aberta com atribuição, a conferir no site oficial. Servem para lavoura, desmatamento, seca, enchente e
     divisa vista do espaço. Fonte: [Berkeley, guia de sensoriamento remoto](https://guides.lib.berkeley.edu/gis/remotesensing).
   - Wikimedia Commons com CC BY, CC BY-SA, CC0 ou domínio público.
   - Agência Brasil **não**: a política dela exige licença para uso em redes sociais e audiovisual.
3. **Trecho de terceiros como citação (react):** art. 46, III, da Lei 9.610/1998 e fair use. Regras:
   - trecho curto, de no máximo 5 a 8 segundos cada, e no máximo 20% do vídeo somados;
   - **nunca na abertura**, porque os 3 primeiros segundos são imagem própria;
   - o trecho é o assunto do comentário: o editor fala sobre ele, com congelamento, zoom no detalhe, seta ou tela
     dividida;
   - crédito na tela o tempo todo, com o link na legenda;
   - imagem na orientação original, sem espelhar, inverter nem disfarçar a origem;
   - nada de marca d'água de terceiro no quadro.
4. **Banco com licença comercial** (Pexels e Pixabay, pela API, com a chave do editor), para imagem de apoio genérica.

### 2.2 Antes de publicar (lista de conferência)
- **Proporção:** pelo menos 80% do tempo de tela é imagem própria ou de domínio público. Medir e anotar.
- **Trechos de terceiros:** cada um ≤ 8 s, fora da abertura, com crédito e com comentário por cima.
- **Metadados:** arquivo final com metadados limpos (`-map_metadata -1`).
- **Verificações do YouTube Studio:** subir como **privado**, esperar o resultado das verificações de direitos autorais
  e de adequação a anúncios ("Checks") e só então publicar.
  - Se aparecer reivindicação: trocar o trecho por imagem própria, ou contestar com base na citação (art. 46, III, ou
    fair use), se o trecho for curto e comentado.
- **Registro:** cada trecho de terceiros e cada imagem de arquivo entram no `CENAS_USADAS.md`, com link, licença e data.

### 2.3 Para os web documentários
- **Estrutura:** narração e análise próprias conduzem; o arquivo prova e ilustra.
- **Arquivo como documento:** sempre datado e creditado ("Agência Senado, 2026"; "Landsat 9, USGS, 2026").
- **Pedir licença cedo:** pedir à TV Senado, à Câmara e às emissoras os trechos de que precisar, antes da edição.
- **Ferramentas:**
  - `tools/video/tiktok_baixar/` e `tools/video/youtube_baixar/` para o trecho a ser citado, que guardam autor e data;
  - um buscador de arquivo aberto (Commons, Senado no Flickr, Landsat) que anote a licença de cada imagem, a construir
    no primeiro web documentário.

## 3. O que não fazemos
Espelhar, inverter, mudar a velocidade ou o tom só para que o sistema não reconheça o trecho de outra pessoa. Não há
proibição legal específica de espelhar. O problema é o propósito: esconder a origem do material, o que vai contra a
citação com crédito e não resolve a regra de conteúdo reutilizado. O assistente não aplica essa técnica.
