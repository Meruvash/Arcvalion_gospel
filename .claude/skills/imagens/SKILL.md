---
name: imagens
description: Busca a foto de uma notícia ou de um estudo bíblico em fonte com licença de uso (agências públicas, Wikimedia Commons, divulgação oficial), respeitando o robots.txt, e grava em conteudo/imagens/ com o crédito. Use quando pedirem "/imagens", "foto da notícia" ou na etapa de foto das skills noticias e estudo.
---

# Fotos com licença

1. Procure nesta ordem: foto da própria fonte primária quando ela autoriza uso (Agência Senado, Agência Câmara, Agência Brasil em CC BY 4.0, Flickr oficial do Planalto e dos ministérios), divulgação oficial da igreja, do evento ou do artista para a imprensa, Wikimedia Commons (confira a licença do arquivo; para estudos, obras de arte em domínio público).
2. A foto precisa mostrar o fato, a pessoa ou o lugar da notícia. Retrato genérico de banco de imagens, logo e foto de outro ano não servem.
3. Caminho principal: `python3 tools/fotos.py buscar <slug>` (lê as fontes da matéria, aplica a licença de cada domínio de `config/imagens.json`, monta a folha de contato), depois `python3 tools/fotos.py aprovar <slug> <n> --alt "..."`. Com o link exato da foto: `python3 tools/imagens/baixar.py <url-da-imagem> <slug>.jpg --credito "Foto: <autor>/<agência> (<licença>)" --pagina <página-de-origem>`. Os dois respeitam o robots.txt e recusam foto pequena. A Wikimedia limita servidores de nuvem: se der 429, espere o tempo do Retry-After e tente miniatura de tamanho-padrão (1280 px).
4. Preencha `imagem` no JSON: `arquivo`, `credito` (o mesmo do comando) e `alt` (descrição do que se vê). Cite a página de origem nas `fontes` da nota.
5. Sem foto com licença, a notícia não sai: troque de notícia. **Nunca gere imagem por IA**, nem para estudos.
