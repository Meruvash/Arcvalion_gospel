---
name: revisao
description: Checagem de fatos de apoio à revisão humana — confere rascunhos em "revisao" e matérias publicadas contra as fontes e o padrão editorial, e entrega um relatório com os problemas e as correções sugeridas. Não publica nem corrige matéria publicada sozinha. Use quando pedirem "/revisao", "checar matéria", "verificação do dia" ou quando a tarefa agendada de verificação disparar.
---

# Checagem de fatos (apoio à revisão humana)

No original esta rotina corrigia e publicava sozinha. Aqui ela **só aponta**: quem decide e aprova é a pessoa revisora (`tools/publicar.py aprovar|corrigir|despublicar --revisor <slug>`).

1. `python3 tools/editorial/checar.py` e `python3 tools/build.py && python3 tools/checar_seo.py` — liste o que falhar.
2. Para cada matéria em `revisao` e cada publicada nas últimas 24 h: abra as fontes (WebFetch respeitando robots.txt) e confira nomes, cargos, datas, números, valores, votações, nomes de projetos de lei e citações literais (a frase precisa existir na fonte). Confira se a foto é do fato certo e se tem licença e crédito.
3. Confira a separação: fato no relato, análise só no quadro rotulado, opinião só no tipo `opiniao`; patrocínio identificado; nenhuma fonte anônima; título sem sensacionalismo.
4. Entregue o relatório: por matéria, "ok" ou a lista de problemas com a evidência (link e trecho) e a correção sugerida. Erro em matéria publicada vai marcado como **correção necessária**, com o texto proposto para `--texto` do `tools/publicar.py corrigir`.

Nunca troque um número por outro sem fonte, nunca reescreva matéria publicada sem erro apontado, nunca contorne bloqueio de site.
