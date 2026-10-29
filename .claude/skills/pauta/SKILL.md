---
name: pauta
description: Prepara a pauta e os RASCUNHOS de matérias do portal — coleta nos feeds de fontes primárias, triagem, apuração com fontes verificáveis e escrita no padrão editorial (docs/PADRAO_EDITORIAL.md), sempre com status "rascunho" ou "revisao". Nunca publica. Use quando pedirem "/pauta", "pauta do dia", "preparar rascunhos" ou quando a tarefa agendada de pauta disparar.
---

# Pauta e rascunhos

Regra que não tem exceção: **a IA não publica**. Você entrega rascunhos prontos para uma pessoa revisora da redação conferir e aprovar com `tools/publicar.py`. Nunca preencha `revisao`, nunca mude `status` para `publicado`, nunca rode `tools/publicar.py`.

## 1. Coletar

`python3 tools/editorial/coletar.py --dias 2` grava `.cache/pauta/<data>.md` com as candidatas dos feeds de `config/fontes.json` (respeita robots.txt). Complete com WebSearch/WebFetch em português, lendo só páginas que permitem acesso, e com fontes primárias: Diário Oficial da União, sites do Congresso, STF, ministérios, notas oficiais de igrejas, convenções e organizações cristãs, relatórios de pesquisa.

## 2. Triar

Fica de fora: boato, "fontes dizem", post de rede social sem confirmação, release sem fato novo, conteúdo pago, assunto já publicado e fato que só existe em outro veículo sem fonte primária. Prefira o que tem impacto para o leitor cristão brasileiro e o que permite contexto e apuração própria. Não transforme matéria de outro veículo em paráfrase: acrescente fonte primária, dados ou contexto, e dê o crédito.

## 3. Escrever o rascunho

`python3 tools/novo.py <editoria> <tipo> "<título>"` cria o arquivo. Preencha seguindo `docs/PADRAO_EDITORIAL.md`:

- `lide` responde o quê, quem, quando, onde, como e por quê; o `corpo` só traz fatos com fonte.
- Toda citação literal vai em bloco `{"citacao", "autor", "cargo", "fonte"}` e precisa estar, palavra por palavra, na fonte indicada. Sem a frase exata, use discurso indireto com atribuição ("segundo nota da ...").
- `analise` (quadro "Por que importa") é opcional, curto e separado do relato; opinião de verdade só no tipo `opiniao`, assinada por pessoa real.
- `fontes`: link, data de consulta e `tipo` (primaria/secundaria); notícia precisa de ao menos uma primária.
- `ia`: `{"usada": true, "uso": "pesquisa, organização e primeira versão do texto"}`.
- Título informativo, sem exclamação, caixa alta ou caça-clique. Nada de adjetivo de torcida (detonou, lacrou, humilhou).
- Foto: só real, com licença e crédito. **Nunca imagem gerada por IA.** Rode `python3 tools/fotos.py buscar <slug>` (procura nas páginas das `fontes`; `--url` para outra página oficial, `--tema` para o Commons), abra `.cache/fotos/<slug>/folha.jpg` com Read, escolha pelo que a foto mostra (o fato certo, sem texto por cima) e grave com `python3 tools/fotos.py aprovar <slug> <n> --alt "..."`. Candidata "a confirmar" ou BLOQ não é aprovada pela IA: deixe para a redação. Sem foto adequada, deixe `imagem` vazio e avise. Regras e fontes em `docs/FOTOS.md`.
- Política: relate posições de todos os lados envolvidos com a fonte de cada uma; a linha conservadora do portal aparece na escolha de pautas e na seção de opinião, não na distorção do fato.

`python3 tools/editorial/checar.py conteudo/artigos/<slug>.json` precisa passar (rascunho mostra 📝 com o que falta). Quando estiver completo, troque `status` para `"revisao"`.

## 4. Entregar

Commit numa branch `pauta/<data>` (nunca na `main`) só dos JSON e das imagens, e resumo para a redação: rascunhos prontos para revisão (título, editoria, fontes principais), o que ficou de fora e por quê, o que precisa de confirmação humana (ligação, documento não acessível), avisos da coleta.
