---
name: novela
description: Produz um episódio da novelinha do outro Instagram do editor (Reels vertical de 60 a 90 s, cena atuada) com o elenco fixo da Vila do Jatobá e o Dr. Pelicioni como protagonista que chega na virada, prevê o argumento do vilão e resolve com a lei lida na fonte. Roteiro pela fórmula medida e pelas regras de roteiro, prompt conferido clipe a clipe, geração no Higgsfield (Seedance 2.0 Mini, e Seedance 2.5 só nos planos-chave), vozes e trilha no ElevenLabs, montagem e conferências aqui. Use quando pedirem "novela", "novelinha", "episódio da novela", "parte 2", "V1/V2…".
---

# Novela (cena atuada)

**Leia antes de qualquer coisa, nesta ordem:**
1. `docs/video/novela/PERSONAGEM_DR_PELICIONI.md`: o protagonista, a **previsão inteligente** (4 testes) e os limites da
   OAB (Provimento 205/2021).
2. `docs/video/novela/ELENCO_FIXO.md`: elenco, vozes confirmadas (voice_id) e código visual.
3. `docs/video/novela/FORMULAS_NOVELA.md`: a fórmula medida no modelo de 1 hora e os pesos do verificador.
4. `docs/video/novela/REGRAS_ROTEIRO.md`: gancho com o corpo, vilão que pensa, o doutor que parece inteligente, diálogo,
   série e montagem.
5. `docs/video/novela/FORMATO_CENA.md`: modelos, preços e os testes de 23/11/2026.
6. `docs/video/novela/NOVELAS_USADAS.md`: o que já foi usado (objeto, previsão, gancho) e as contas abertas da temporada.

## Fluxo

1. **Premissa.**
   - Escolha 1 premissa da tabela de `FORMULAS_NOVELA.md` §4 e um caso jurídico real.
   - Leia a lei na fonte oficial e anote o link e a data. Nada de lei de memória.
   - Confira em `NOVELAS_USADAS.md`: objeto-prova, previsão e gancho não se repetem.
   - Na parte 2 em diante, retome o estado de passagem e as contas abertas.

2. **Roteiro em JSON** (`docs/video/novela/roteiros/<nome>.json`):
   - cada batida tem `t`, `fim`, `tipo`, `quem`, `modo`, `fala`, `tela`, `marcas` e **`porque`** ("então…" ou "mas…");
   - toda LEI tem `fonte`;
   - parte 2 em diante leva `parte`, `handoff_anterior` e `reprise: true` na primeira batida.

   Rode:
   - `python3 tools/video/novela/auditar_novela.py roteiro.json`: aprovação com as obrigatórias ok e nota de 0,85 ou mais.
     Resolva também os avisos A1 a A4.
   - `python3 tools/video/novela/render_roteiro.py roteiro.md roteiro.json`: a versão legível.
   - **o passe de julgamento** (`REGRAS_ROTEIRO.md` §9, 9 perguntas). As respostas vão na mensagem ao editor.

3. **Mostre o roteiro ao editor e pare.** Nenhum crédito é gasto antes da aprovação do roteiro (pedido do editor).

4. **Clipes.** Divida o roteiro em clipes de 4 a 8 s, **um falante por clipe**, um JSON por clipe em
   `docs/video/novela/producao_<ep>/clipes/`. Para cada um:
   `python3 tools/video/novela/prompt_clipe.py clipe.json --saida clipe.txt`. O prompt só é enviado com "✅ prompt
   conferido": planos somando a duração, fala cabendo com folga, trava visual e "No background music".

5. **Orçamento e aprovação do gasto.**
   - Cote no Higgsfield (`estimate_video_cost`) e some.
   - Padrão: **Seedance 2.0 Mini, 720p** (1 crédito por segundo, já com fala).
   - **Seedance 2.5, 720p** só nos 2 ou 3 planos-chave (gancho, previsão, queda), se o editor aprovar.
   - Mostre o total ao editor e o teto. Não passe do teto sem pedir.
   - Folhas de personagem: reaproveite `docs/video/novela/elenco/folhas/`. Uma folha nova (Nano Banana Pro, cerca de
     2 créditos) só com o personagem descrito em `ELENCO_FIXO.md`.
   - O Dr. Pelicioni sai sempre da foto oficial (`personagem/foto_oficial.jpg`).

6. **Geração.**
   - Cada clipe vai em `generate_video` com as folhas (`image_references`, na ordem dos personagens do JSON) e a amostra
     de voz do falante (`audio_references`).
   - Amostras: os arquivos de `elenco/voz/`. Para o editor, a voz clonada gerada por `voz_editor_s_neutro.py`.
   - Clipes independentes saem juntos. Guarde o job id de cada um num `jobs.json` do episódio.

7. **Triagem de cada clipe** (`REGRAS_ROTEIRO.md` §7):
   - transcrição (scribe_v1), que tem que bater com a fala;
   - quadros e mãos de perto (crivo H1 a H7);
   - sem texto na tela e sem música.

   Destino de cada clipe: manter, cortar, corrigir na montagem ou refazer. Refaça mudando uma variável por vez.

8. **Trilha.** ElevenLabs Music, instrumental, na duração do episódio mais 5 s, em trechos que seguem a fórmula: tensão,
   suspense antes da virada, virada ascendente e acorde de suspense no gancho final. Descreva o som; nunca cite
   compositor, obra ou artista. O plano pago tem uso comercial online (termos de 09/10/2026).

9. **Montagem** com `tools/video/novela/montar_episodio.py`:
   - cortes de 0,25 s antes a 0,4 s depois da fala;
   - fala perto de -19 LUFS, com a trilha por baixo;
   - legenda amarela;
   - cartão da lei literal com a fonte, como inserto;
   - "PARTE 2" no fim;
   - aviso "DRAMATIZAÇÃO · PERSONAGENS FICTÍCIOS".

10. **Conferências antes de mandar:**
    - `python3 tools/video/agro-arte/auditar_video.py ep.mp4` (abertura e ritmo, 5/5);
    - `python3 tools/video/agro-arte/crivo_qualidade.py ep.mp4`, com a revisão de **todas** as folhas;
    - transcrição do episódio inteiro;
    - medida do "S" da fala do editor, quando ela saiu do Seedance.

11. **Entrega e registro.**
    - Mande o vídeo ao editor com os créditos gastos.
    - Registre em `NOVELAS_USADAS.md` a premissa, o objeto, a previsão, o gancho, o estado de passagem e as contas
      abertas.
    - Lembre o editor: rótulo de IA no post do Instagram e conferência da OAB.
    - Vídeos e áudios grandes ficam fora do git (`.gitignore`). Ficam no repositório os JSON, os prompts, as folhas em JPG
      e os documentos.
    - Antes do commit, rode os verificadores do `CLAUDE.md`.

## Nunca
- Nunca gere vídeo antes de o editor aprovar o roteiro, nem passe do teto de créditos aprovado.
- Nunca ponha dois falantes num clipe.
- Nunca use contato físico entre corpos nem mudança de estado dentro de um plano.
- Nunca deixe o Dr. Pelicioni prometer resultado ou pedir contratação. Nas falas dele: nada de ponto de exclamação,
  "garanto", "honorários" ou "me contrate" (O9).
- Nunca copie personagem, nome, fala ou visual de obra existente nem de ator real. O que se aproveita de outras obras é
  só a função do personagem.
- Nunca ponha segredo no repositório. As chaves do Higgsfield e do ElevenLabs entram pelo proxy.
