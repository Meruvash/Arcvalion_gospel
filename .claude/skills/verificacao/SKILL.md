---
name: verificacao
description: Verificação diária do portal (cópia da verificação das 22h do Elite Boardgamers) — confere o que está em revisão e o que foi publicado contra as fontes e o padrão editorial, checa páginas, links e o site no ar, e entrega à redação a lista do que corrigir. Correção em matéria publicada só com aprovação humana. Use quando pedirem "/verificacao", "verificação do dia" ou quando a tarefa agendada disparar.
---

# Verificação diária

1. `python3 tools/noticias/checar_noticia.py`, `python3 tools/estudos/checar_estudo.py`, `python3 tools/discipulado/checar_licao.py`, `python3 tools/build_home.py`, `python3 tools/checar_seo.py`, `python3 tools/checar_isolamento.py`.
2. Para cada nota e estudo em revisão ou publicado nas últimas 24 h: abra as fontes (WebFetch respeitando robots.txt) e confira nomes, cargos, datas, números, votações, nomes de projetos de lei, referências bíblicas e citações literais. Confira se a foto é do fato certo e tem licença e crédito.
2a. **Discipulado** (rotina das 15h17, sem revisão na produção: a revisão é esta, à noite). Para cada estudo em `conteudo/discipulado/<slug>/licao.json` publicado nas últimas 24 h: texto bíblico do `aluno.md` idêntico ao da página NTLH (bibliaonline.com.br); cada frase atribuída a autor (Matthew Henry, Wesley, Calvino, Declaração de Fé) presente na fonte linkada em Referências; pelo menos 2 fontes além da Bíblia; nenhum personagem inventado, nenhuma numeração, nenhum pré-requisito ("como vimos no estudo anterior"); categoria e trilhas certas em `conteudo/discipulado/base/catalogo.json`. Padrão: `docs/discipulado/padrao-literario.md`. Correção no `.md` ou no `licao.json`, registrada com `publicar.py corrigir conteudo/discipulado/<slug>/licao.json`.
3. Confira a separação: fato no relato; opinião só em Por que importa e Nossa opinião; posições atribuídas; nenhuma fonte anônima; título sem sensacionalismo; Nossa opinião com posicionamento concreto e versículo só no campo `versiculo`, no fim.
4. Erro em nota **em revisão**: corrija no JSON com a fonte certa e rode o build. Erro em matéria **publicada**: corrija direto (publicação automática autorizada em 29/10/2026) com `python3 tools/publicar.py corrigir <arquivo> --revisor <slug> --texto "..."` para a pessoa revisora aprovar.
5. Commit e push (`Verificação de <dd/mm/aaaa>: <o que mudou>`), e resumo: itens conferidos (notícias, estudos bíblicos e estudos de discipulado), o que foi corrigido (antes → depois, fonte), o que espera aprovação.
