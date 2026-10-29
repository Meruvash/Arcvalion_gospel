# Regras para agentes neste repositório

- **A IA não publica.** Nunca mude `status` para `publicado`, nunca preencha `revisao`, nunca rode `tools/publicar.py`.
  Rascunhos sim (skill `pauta`); publicação, correção e despublicação são de pessoa revisora de `config/equipe.json`.
- Nada inventado: todo fato com fonte identificável (link + data); citação literal só de frase lida na fonte.
- Não edite HTML gerado: o site sai de `tools/build.py` a partir de `conteudo/` e `config/`. `publico*/` não é versionado.
- Nunca use imagem gerada por IA em matéria. Nunca coloque segredo no repositório (ver `docs/DEPLOY.md`).
- Antes de commit: `python3 tools/editorial/checar.py`, `python3 -m unittest discover -s tests`, `python3 tools/checar_isolamento.py`.
- Não faça deploy (workflow Deploy) sem aprovação explícita.
- `exemplos/` é conteúdo FICTÍCIO só para prévia e testes: nunca copie dali para `conteudo/`.
