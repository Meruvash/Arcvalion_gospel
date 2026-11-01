---
name: comentarios
description: Moderação dos comentários do portal — lê a fila do serviço de interações (worker/), aprova os respeitosos e reprova os que ferem as regras, decidindo todos sozinha (sem fila para a redação, decisão do editor de 01/11/2026). Use quando pedirem "/comentarios", "moderar comentários" ou quando a tarefa agendada de moderação disparar.
---

# Moderação de comentários

Mesmo fluxo do projeto de origem, adaptado ao portal. Fila: `GET <api>/v1/moderacao/fila` com `Authorization: Bearer $MODERACAO_SENHA` (a `api` está em `config/portal.json`). Decisão: `POST <api>/v1/moderacao/decidir {"id", "estado": "aprovado|reprovado", "parecer", "por": "ia"}`. **Todo comentário recebe decisão na própria rotina** (01/11/2026): não use mais `duvidoso`, e os que ficaram marcados como `duvidoso` em rodadas antigas também são decididos agora.

**Aprovar** (todas): fala da matéria ou do tema; é respeitoso, mesmo discordando do portal, de igrejas, de líderes ou de políticos; sem link, telefone, e-mail ou dado pessoal; não é propaganda.

**Reprovar**: propaganda, venda, golpe, link externo, pedido de contato; texto sem sentido ou repetido; xingamento, discurso de ódio, preconceito, assédio, conteúdo sexual; ameaça; dado pessoal de terceiros.

**Casos difíceis** (antes iam para a redação; agora a rotina decide): acusação a pessoa, igreja ou empresa sem fonte, ou afirmação de fato grave que não dá para conferir, é **reprovada** (risco jurídico); ironia ou debate político acalorado, mas sem ofensa pessoal, é **aprovado**; citação longa de outro site é **reprovada**. O parecer diz o motivo em uma frase.

Discordância teológica ou política educada é aprovada. Nunca edite o texto: ou sai como está, ou não sai. Termine com o resumo (aprovados, reprovados com o motivo) e o link do painel `<api>/painel`.
