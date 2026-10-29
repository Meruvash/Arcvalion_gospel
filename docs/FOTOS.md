# Plano de fotos do portal

Como conseguir foto boa, real e licenciada para cada notícia, e o que o robô (`tools/fotos.py`) já faz sozinho.
Adaptado do plano de fotos do projeto de origem, que era de resenhas de jogos: aqui a foto ilustra um fato, então
vale ainda mais a regra de nunca usar imagem gerada por IA nem foto de outro fato.

## Regras que não mudam

- **Toda foto tem dono.** Estar na internet não libera o uso. Só entra foto com licença conhecida e crédito.
- **Nunca imagem gerada por IA** em matéria (o validador bloqueia `gerada_por_ia`).
- **Foto do fato certo.** Foto de arquivo vai com a data no crédito ou na legenda ("Foto de arquivo, 2024").
- **Agências de terceiros não entram.** Reuters, AFP, AP, EFE, Getty, Folhapress, Estadão Conteúdo e afins
  aparecem dentro de páginas da Agência Brasil e de outros sites, mas não estão na licença deles. O robô bloqueia.
- **robots.txt manda.** O robô confere antes de cada pedido, espera 3 s por host e para em 401/403 sem contornar.
- A IA prepara a foto no rascunho; quem confere a foto é a pessoa revisora (`docs/FLUXO_EDITORIAL.md`).

## Fontes, em ordem

| # | Fonte | Licença (conferida em 29/10/2026) | Crédito | Como |
|---|---|---|---|---|
| 1 | **Agência Brasil** | "Reprodução autorizada para veículos de comunicação com fins jornalísticos, mediante indicação da fonte" ([política](https://agenciabrasil.ebc.com.br/sobre)). Fins comerciais fora do jornalismo: licenciamento@ebc.com.br | Foto: Autor/Agência Brasil | robô (`buscar`) |
| 2 | **Agência Senado** | "A reprodução de matérias e fotografias é livre, mediante a citação da Agência Senado e do autor" ([política de uso](https://www12.senado.leg.br/assessoria-de-imprensa/politica-de-uso)) | Foto: Autor/Agência Senado | robô |
| 3 | **Câmara dos Deputados** | uso livre e gratuito, sem autorização prévia, com crédito "Nome do Fotógrafo/Câmara dos Deputados" ([guia para jornalistas](https://www2.camara.leg.br/comunicacao/assessoria-de-imprensa/guia-para-jornalistas/noticias-e-fotografias)) | Foto: Autor/Câmara dos Deputados | robô |
| 4 | **gov.br** (Planalto, ministérios) | rodapé: CC BY-ND 3.0 (sem derivações: não recortar nem montar) | Foto: Autor/órgão | robô |
| 5 | **Wikimedia Commons** | por foto: CC0, CC BY, CC BY-SA ou domínio público | Foto: Autor · licença · Wikimedia Commons | robô (`--tema`, `--commons`) |
| 6 | **Divulgação oficial** (igreja, convenção, ministério, organizador do evento) | foto enviada ou publicada para a imprensa; guarde o e-mail ou o link da sala de imprensa | Foto: Divulgação/Nome | robô marca "a confirmar"; aprove com `--licenca` e `--credito` |
| 7 | **Bancos gratuitos** (Unsplash, Pexels) | licença própria, uso comercial liberado; os sites bloqueiam robôs | Foto: Autor/Unsplash | a redação baixa; `local` |
| 8 | **Banco pago** (Folhapress, Getty, Shutterstock, Agência Estado) | contrato | conforme o contrato | a redação baixa; `local` |
| 9 | **Foto própria** (repórter, colaborador) | da casa | Foto: Nome/Portal | `local` |

STF, TSE, assembleias, prefeituras e sites de igrejas não estão em `config/imagens.json` porque a política de
cada um não foi conferida: aparecem como "a confirmar". Ao conferir uma política, acrescente o domínio lá
(com o link da política e a data), e o robô passa a preencher o crédito sozinho.

Ficam de fora: Google Imagens, Pinterest, Instagram/Facebook/X (os termos proíbem baixar; post só incorporado
com o código oficial), fotos de outros portais de notícia, Flickr pelo robô (o robots.txt proíbe; a foto
CC de lá entra pela redação com `local`, com o link da página e a licença) e a API do Openverse e do Pexels
(o robots.txt das APIs proíbe robôs).

## Como usar

```bash
python3 tools/fotos.py buscar <slug>                       # fotos das páginas em "fontes" da matéria
python3 tools/fotos.py buscar <slug> --url <página oficial> # outra página (release, sala de imprensa)
python3 tools/fotos.py buscar <slug> --tema congresso       # categorias do Commons em config/imagens.json
python3 tools/fotos.py local <slug> ~/Downloads/fotos.zip --credito "Foto: Divulgação/CGADB" --licenca "divulgação enviada à imprensa em 29/10/2026"
python3 tools/fotos.py aprovar <slug> 3 --alt "Plenário do Senado durante sessão de votação"
```

`buscar` monta `.cache/fotos/<slug>/folha.jpg` (grade numerada: ok, a confirmar ou BLOQ) e `candidatas.json`.
Abra a folha, escolha pelo que a foto mostra e rode `aprovar`: a foto vira `conteudo/imagens/<slug>.jpg` (só
reduzida, até 1600 px e 350 KB, sem recorte) e o campo `imagem` ganha arquivo, crédito, alt, licença, origem e
página. Fotos com menos de 800 px de largura são descartadas (o validador exige 800; o Discover pede 1200).

O Wikimedia limita pedidos vindos de servidores na nuvem (429): o robô avisa uma vez e pula. Do computador da
redação costuma passar.

## O que fazer sempre

1. **Pauta com foto**: na triagem, prefira o fato que tem foto oficial (Agência Brasil, Senado, Câmara, gov.br
   ou divulgação da organização envolvida). Notícia sem foto boa não é publicada (o validador bloqueia).
2. **Lista de imprensa**: cadastrar o e-mail da redação nas assessorias de imprensa das convenções, alianças,
   igrejas grandes, organizações cristãs e órgãos públicos da cobertura. A foto de divulgação chega junto com o release.
3. **Banco de arquivo próprio**: fotos já aprovadas de prédios, instituições e pessoas públicas ficam em
   `conteudo/imagens/` com o crédito. Para assuntos que voltam sempre, mantenha `commons_temas` em
   `config/imagens.json` com categorias boas.
4. **Fotógrafo colaborador** em eventos (marchas, congressos, cultos especiais): foto própria, com termo de cessão.

## Modelos

### Pedido de foto à assessoria

> Assunto: Pedido de foto para matéria — [ASSUNTO]
>
> Olá, equipe de comunicação da [ORGANIZAÇÃO]!
>
> Sou [NOME], do [PORTAL] ([URL]). Estamos preparando uma matéria sobre [ASSUNTO] e gostaríamos de usar uma
> foto oficial, com crédito a [ORGANIZAÇÃO] e ao fotógrafo. Vocês podem enviar uma ou mais imagens em alta
> resolução e confirmar o crédito correto?
>
> Obrigado!

### Pedido de autorização a quem fotografou

> Olá, [NOME]! Vimos a sua foto de [ASSUNTO] em [LINK]. Podemos usá-la na matéria do [PORTAL] sobre [ASSUNTO],
> com crédito a você? Retiramos do ar se você pedir.

Guarde a resposta e use em `--licenca` ("autorizada por e-mail em AAAA-MM-DD").
