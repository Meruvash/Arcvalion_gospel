# Regras para agentes neste repositório

- **A IA não publica sozinha.** As rotinas (skills `noticias`, `estudo`) gravam com `"status": "revisao"`, que só aparece em /previa/.
  Publicar, corrigir ou despublicar é decisão de pessoa revisora de `config/equipe.json`; rode `tools/publicar.py` só quando essa
  pessoa aprovar explicitamente, na conversa, cada matéria pelo nome, e use o slug dela em `--revisor`.
- Nada inventado: todo fato com fonte identificável (link + data); citação literal só de frase lida na fonte.
- Não edite HTML gerado: o site sai de `tools/build.py` a partir de `conteudo/` e `config/`. `publico*/` não é versionado.
- Nunca use imagem gerada por IA em matéria. Nunca coloque segredo no repositório (ver `docs/DEPLOY.md`).
- Antes de commit: `python3 tools/noticias/checar_noticia.py`, `python3 tools/estudos/checar_estudo.py`, `python3 -m unittest discover -s tests`, `python3 tools/checar_isolamento.py`.
- O workflow Deploy publica a cada push na main (aprovado em 29/10/2026); o que está em revisão fica só em /previa/.
- Design: copiado do Elite Boardgamers com o preto trocado por azul (tools/estilo_elite.py). Mantenha classes e medidas.
- `exemplos/` é conteúdo FICTÍCIO só para prévia e testes: nunca copie dali para `conteudo/`.
