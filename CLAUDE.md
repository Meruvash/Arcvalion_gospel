# Regras para agentes neste repositório

- **Publicação automática** (ordem de Wan Anderson Pelicioni de Castro, responsável editorial, em 29/10/2026): as rotinas
  (skills `noticias`, `estudo`, `discipulado`) publicam sozinhas o que passa nos validadores, com
  `python3 tools/publicar.py aprovar <arquivo> --revisor anderson-pelicioni-de-castro --automatica`, que registra a
  aprovação como automática (não como leitura humana). A conferência é diária, pela verificação noturna das 21h (tarefa agendada) e
  pela skill `verificacao`; correção ou despublicação de matéria no ar segue com `tools/publicar.py`.
- **Todas as rotinas aprovam e publicam sozinhas** (reforçado pelo responsável editorial em 01/11/2026): notícias, estudos
  bíblicos, discipulado, verificação e comentários. Nenhuma rotina deixa item esperando aprovação humana nem em "revisão":
  o que passa nos validadores e nos crivos é aprovado com `--automatica` e publicado no mesmo push; o que não passa não sai.
- **Notícias em duas edições, com varredura completa** (pedido de 02/11/2026): edição da madrugada (2h23) e da tarde (14h43), meta de **pelo menos 5** notas no dia somado (regra de 02/11/2026), completando com notas de 60 a 69, depois de 50 a 59 e trilha atemporal, sem nunca afrouxar a verificação; nenhuma edição fecha com menos de 5 sem cumprir as três rodadas de coleta e usar a janela até o horário-limite. Nunca trocar o user-agent para se passar por navegador. Ver `.claude/skills/noticias/SKILL.md`.
- **Linha editorial pentecostal** (pedido de 30/10/2026): o portal é cristão pentecostal e os estudos dizem onde estão (seção "Nossa posição", referência na Declaração de Fé das Assembleias de Deus), respeitando e relatando com fidelidade os outros lados. Ver `docs/PADRAO_EDITORIAL.md`, "Linha editorial pentecostal".
- **Sem menção à advocacia do editor** (decisão de 30/10/2026): nenhuma matéria diz que o editor é advogado nem oferece serviço ou contato profissional; o "Quem somos" e o Instagram dele bastam. Ver `docs/PADRAO_EDITORIAL.md`, "Sem menção à advocacia do editor". **Exceção** (pedido do editor, 10/11/2026): os vídeos de agronegócio (`docs/video/PROMPT_VIDEO_AGRO.md`) fecham com uma conclusão sutil e informativa que apresenta o editor como advogado e convida a seguir ou chamar no direct, nos limites do Provimento 205/2021 da OAB (sem promessa de resultado, sem preço, sem "contrate"). As matérias do portal continuam sem menção.
- **Discipulado** (pedido de 30/10/2026): a aba Discipulado ocupa no menu o lugar da Agenda. Lições para novos convertidos
  pela skill `discipulado` (rotina diária às 15h17: 5 estudos, na ordem que completa as trilhas), com as regras de `docs/discipulado/` (padrão editorial e de escrita da coleção) e o material fixo de
  `conteudo/discipulado/base/`. Texto bíblico do aluno na NTLH, lido na fonte. Processo enxuto, sem auditoria por subagente (decisão do editor, 30/10/2026).
- **Vídeos: roteiro antes de tudo** (pedido do editor, 10/11/2026): todo vídeo começa pelo roteiro apresentado ao editor na conversa. Nada de voz, áudio, imagem, quadro de estilo ou render antes da aprovação expressa do roteiro. Depois, cada etapa nova (voz, teste de 10 s, render final) também é mostrada antes de seguir. **Prévia tem no máximo 10 s**, sempre (voz, imagem ou vídeo). Narrador padrão: "Marcio - Viral Hook Narrator" (ElevenLabs `plASsyS7JE6GCAvx9uIc`, modelo `eleven_v3`), a voz dos vídeos do Colt Express. Vídeos de agronegócio seguem a estrutura "Você sabia" de `docs/video/PROMPT_VIDEO_AGRO.md` (decisão do editor, 10/11/2026; o molde @saveo.house foi descartado).
- Nada inventado: todo fato com fonte identificável (link + data); citação literal só de frase lida na fonte.
- Não edite HTML gerado: como no Elite, o site sai de `tools/build_home.py` (na raiz do repositório) a partir de `conteudo/`, `config/`, `pauta.json` e `consulta/index.html` (bloco RAW dos livros). O deploy publica a raiz sem os arquivos de trabalho (`tools/montar_publicacao.py`).
- Nunca use imagem gerada por IA em matéria. Nunca coloque segredo no repositório (ver `docs/DEPLOY.md`).
- Antes de commit: `python3 tools/noticias/checar_noticia.py`, `python3 tools/estudos/checar_estudo.py`, `python3 tools/discipulado/checar_licao.py`, `python3 -m unittest discover -s tests`, `python3 tools/checar_isolamento.py`.
- O workflow Deploy publica a cada push na main (aprovado em 29/10/2026); o que está em revisão fica só em /previa/.
- Design: copiado do Elite Boardgamers com o preto trocado por azul (tools/estilo_elite.py). Mantenha classes e medidas.
- `exemplos/` é conteúdo FICTÍCIO só para prévia e testes: nunca copie dali para `conteudo/`.
