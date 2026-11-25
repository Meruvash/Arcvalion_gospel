# Parte 2 «O vídeo inteiro»: passagem para a sessão de produção (25/11/2026)

**Roteiro aprovado pelo editor:** `docs/video/novela/roteiros/drama/v3_o_video_inteiro.md`, **versão completa, com os
17 planos** (o editor quer o Valdir debochando e a Marta confirmando a lei, que dão aura ao Dr.). Teto: **650 créditos**.

**Ordem do editor:** quando ele disser "pode criar", produzir o vídeo inteiro sem pedir confirmação a cada passo. Ele
pré-autorizou todas as gerações dentro do teto. Mostrar cada cena assim que ficar pronta. Só parar e perguntar se for
passar do teto ou se o roteiro precisar mudar.

## Ler antes (nesta ordem)
1. `.claude/skills/novela/SKILL.md`, com a regra "palavra errada: conserte o áudio primeiro".
2. `docs/video/novela/REGRAS_ROTEIRO.md` §10 (teste da história).
3. O roteiro aprovado (acima).
4. `docs/video/novela/producao_v2c/REFAZER.md` e `drama/prompts_cenas_novas.md` (o que deu certo e o que deu errado
   na V2c).
5. `tools/video/novela/drama_prompt.py`: gerador de prompts, IDs do elenco, vozes e amostras.

## Ferramentas (todas testadas na V2c)
- **Higgsfield (MCP):**
  - `get_drama_ads_config` (cotação stage antes de cada lote);
  - `generate_image` (seedream_5_5 para folhas e placas);
  - `generate_video_batch` com os parâmetros `model: seedance_2_5`, `mode: omni_reference`, `generate_audio: true`,
    `resolution: 720p`, `aspect_ratio: 9:16`, `use_unlim: false`, `drama_ads_id`, e o prompt por referência
    `{"ref":"sandbox:/home/user/films/<pasta>/<arquivo>.txt"}`;
  - `seedance_2_0_mini` para insertos sem gente;
  - `generate_audio_batch` (`seed_audio` com `voice_id`/`voice_type` de `VOZ`) para as falas só de voz;
  - `voice_change` (clone do Dr. `95b656d3…`, `element`) só no trecho em que só o Dr. fala;
  - `media_upload`, depois o PUT com o cabeçalho `If-None-Match: *`, depois `media_confirm`.
- **Sandbox do Higgsfield:** `~/films/marca-da-estrela/` tem `montar_prompts.py`, `novas.py` (modelo de lote),
  `checks_pt.py` e `jobs.json`. Ela some depois de 24 h sem uso, mas o `drama_prompt.py` daqui tem tudo de que se
  precisa.
- **Conferência** (aqui no repositório):
  - transcrição: ElevenLabs `scribe_v1` (`api.elevenlabs.io/v1/speech-to-text`, chave falsa "dummy", o proxy injeta a
    verdadeira);
  - cortes: `ffmpeg scdet`;
  - imagem: folhas de quadros;
  - `tools/video/agro-arte/crivo_qualidade.py`;
  - `tools/video/agro-arte/auditar_video.py`.
- **Trilha:** ElevenLabs `/v1/music` com `composition_plan` (modelo em `producao_v2c/trilha/plano_trilha_v3.json`;
  virada na **entrada do Dr.**).
- **Montagem:** `tools/video/novela/montar_cena.py montagem.json saida.mp4`, com legenda amarela, cartão de lei
  (`tools/video/novela/cartao_lei.py`), trilha com sidechain e "PARTE N" opcional. Um plano que precisa de voz por cima
  se prepara antes com ffmpeg, como `c_pergunta.mp4` na V2c.

## Novas referências a gerar (planos 1 e 2 do roteiro)
- **l2: cartório da Vila do Jatobá, manhã** (folha de lugar com dois painéis, como a l1): balcão de madeira escura com
  tampo de vidro, divisória de vidro atrás, armário de aço com pastas, livro grande de capa preta, carimbos, ventilador
  de teto parado, janela à esquerda com luz da manhã, banco de madeira na parede, porta de vidro à direita.
- **c7: Marta**, escrevente do cartório: mulher de 45 anos, cabelo castanho curto, óculos de leitura numa correntinha,
  cardigã verde-oliva sobre blusa branca, sem crachá. Voz: um preset feminino calmo e seco do Higgsfield; gravar o
  voice_id na tabela de `ELENCO_FIXO.md`.
- **Placa do quadro:** um quadro do plano 1 sem os personagens (edição seedream), para segurar sala e luz nos outros
  planos.
- **Prop do Dr.:** pasta de couro marrom fina e recibo branco dobrado, sem texto legível.

## Regras que não se negociam
- **Nada inventado:** a lei do cartão é o CC art. 1.806, lido no planalto.gov.br em 25/11/2026: "A renúncia da herança
  deve constar expressamente de instrumento público ou termo judicial."
- **Linguagem do Dr.:** sem ponto de exclamação, sem promessa, sem "contrate" (OAB).
- **Palavras faladas:** "renúncia", "calúnia", "anca", "novilha", "roça" e "mamadeira" não são faladas.
- **Pronúncia:** guia no prompt para "herança", "março" e "Rosinha".
- **Áudio errado:** palavra errada se conserta primeiro no áudio; regerar só com a boca errada.
- **Git:** vídeo e áudio fora do git; ficam os JSON, os prompts e os documentos. Antes do commit, rodar os verificadores
  do `CLAUDE.md`. Branch `claude/webdoc-ai-studio-research-fvo7ty`, sem PR.
- **Entrega:** mandar ao editor o arquivo (o original e uma cópia leve de 15 MB, porque ele baixa pelo celular), os
  créditos gastos e a legenda do Instagram sem entregar a trama.
