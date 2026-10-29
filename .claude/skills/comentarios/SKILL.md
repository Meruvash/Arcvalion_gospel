---
name: comentarios
description: Moderação dos comentários do portal — lê a fila do serviço de interações (worker/), aprova os claramente respeitosos, reprova spam óbvio e deixa os duvidosos para a redação no painel. Use quando pedirem "/comentarios", "moderar comentários" ou quando a tarefa agendada de moderação disparar.
---

# Moderação de comentários

Mesmo fluxo do projeto de origem, adaptado ao portal. Fila: `GET <api>/v1/moderacao/fila` com `Authorization: Bearer $MODERACAO_SENHA` (a `api` está em `config/portal.json`). Decisão: `POST <api>/v1/moderacao/decidir {"id", "estado": "aprovado|reprovado|duvidoso", "parecer", "por": "ia"}`. Os já marcados como `duvidoso` são da redação: não decida de novo.

**Aprovar** (todas): fala da matéria ou do tema; é respeitoso, mesmo discordando do portal, de igrejas, de líderes ou de políticos; sem link, telefone, e-mail ou dado pessoal; não é propaganda.

**Reprovar**: propaganda, venda, golpe, link externo, pedido de contato; texto sem sentido ou repetido; xingamento, discurso de ódio, preconceito, assédio, conteúdo sexual; ameaça; dado pessoal de terceiros.

**Duvidoso** (fica para a redação): acusação a pessoa, igreja ou empresa; afirmação de fato que precisaria ser checada; ironia que pode ser ofensa; debate político acalorado; citação longa de outro site; qualquer hesitação. Na dúvida, duvidoso.

Discordância teológica ou política educada é aprovada. Nunca edite o texto: ou sai como está, ou não sai. Termine com o resumo (aprovados, reprovados, duvidosos com o motivo) e o link do painel `<api>/painel`.
