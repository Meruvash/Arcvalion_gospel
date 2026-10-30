# Regras para agentes neste repositório

- **Publicação automática** (ordem de Wan Anderson Pelicioni de Castro, responsável editorial, em 29/10/2026): as rotinas
  (skills `noticias`, `estudo`) publicam sozinhas o que passa nos validadores, com
  `python3 tools/publicar.py aprovar <arquivo> --revisor anderson-pelicioni-de-castro --automatica`, que registra a
  aprovação como automática (não como leitura humana). A conferência é diária, pela verificação noturna das 21h (tarefa agendada) e
  pela skill `verificacao`; correção ou despublicação de matéria no ar segue com `tools/publicar.py`.
- **Linha editorial pentecostal** (pedido de 30/10/2026): o portal é cristão pentecostal e os estudos dizem onde estão (seção "Nossa posição", referência na Declaração de Fé das Assembleias de Deus), respeitando e relatando com fidelidade os outros lados. Ver `docs/PADRAO_EDITORIAL.md`, "Linha editorial pentecostal".
- **Sem menção à advocacia do editor** (decisão de 30/10/2026): nenhuma matéria diz que o editor é advogado nem oferece serviço ou contato profissional; o "Quem somos" e o Instagram dele bastam. Ver `docs/PADRAO_EDITORIAL.md`, "Sem menção à advocacia do editor".
- **Discipulado** (pedido de 30/10/2026): a aba Discipulado ocupa no menu o lugar da Agenda. Lições para novos convertidos
  pela skill `discipulado`, com as regras de `docs/discipulado/` (padrão editorial e de escrita da coleção) e o material fixo de
  `conteudo/discipulado/base/`. Texto bíblico do aluno na NTLH, lido na fonte; quem redige não audita.
- Nada inventado: todo fato com fonte identificável (link + data); citação literal só de frase lida na fonte.
- Não edite HTML gerado: como no Elite, o site sai de `tools/build_home.py` (na raiz do repositório) a partir de `conteudo/`, `config/`, `pauta.json` e `consulta/index.html` (bloco RAW dos livros). O deploy publica a raiz sem os arquivos de trabalho (`tools/montar_publicacao.py`).
- Nunca use imagem gerada por IA em matéria. Nunca coloque segredo no repositório (ver `docs/DEPLOY.md`).
- Antes de commit: `python3 tools/noticias/checar_noticia.py`, `python3 tools/estudos/checar_estudo.py`, `python3 tools/discipulado/checar_licao.py`, `python3 -m unittest discover -s tests`, `python3 tools/checar_isolamento.py`.
- O workflow Deploy publica a cada push na main (aprovado em 29/10/2026); o que está em revisão fica só em /previa/.
- Design: copiado do Elite Boardgamers com o preto trocado por azul (tools/estilo_elite.py). Mantenha classes e medidas.
- `exemplos/` é conteúdo FICTÍCIO só para prévia e testes: nunca copie dali para `conteudo/`.
