# Sincronia de boca e voz (padrão desde 23/11/2026)

**Pedido do editor:** a V1 tinha trechos em que o personagem mexe a boca sem falar, e a voz dele precisa ser a voz
clonada. A partir de agora, nenhuma cena com fala vai ao editor sem passar por esta medição.

## A medida (`tools/video/novela/sincronia.py`)
- **Boca:** MediaPipe Face Landmarker, com 478 pontos no rosto, em cada quadro.
  - Abertura = distância entre os lábios internos (pontos 13 e 14) dividida pela largura da boca (pontos 61 e 291), no
    maior rosto do quadro.
  - A boca está "falando" quando a abertura passa de p20 + 35% da faixa entre p20 e p95.
- **Voz:** o tempo de cada palavra pela transcrição scribe_v1.
- **Números de cada cena:**
  - **atraso** (correlação cruzada entre a abertura da boca e a presença de voz, ±600 ms);
  - **boca sem voz** (segundos);
  - **voz sem boca** (segundos).
- **Aprovação:** |atraso| ≤ 120 ms, boca sem voz ≤ 0,5 s e voz sem boca ≤ 0,5 s.
- **Instalação:** em ambiente separado (venv) com `mediapipe` e `opencv-python-headless`, mais `libegl1` no sistema e o
  modelo `face_landmarker.task` do Google (storage.googleapis.com/mediapipe-models).

## O que a medição mostrou na V1 (23/11/2026)
| Versão | Cenas aprovadas (de 13) | Observação |
|---|---|---|
| Fala gerada pelo próprio Seedance | **2** (c01, c10) | a boca mexe antes da fala, em risadas e em pausas |
| Fala regravada no ElevenLabs e só encaixada no tempo (`dublar_clipes.py`) | **0** | atrasos de até 583 ms; até 2,8 s de voz com a boca parada |

**Conclusão:** encaixar o áudio na boca que o modelo inventou não funciona, porque a boca tem o ritmo dela e não segue
as sílabas da voz nova. O certo é o contrário: **primeiro o áudio exato, depois a boca redesenhada para seguir o áudio.**

## O fluxo certo
1. Gerar a fala de cada cena no ElevenLabs: a voz fixa do personagem e, para o Dr. Pelicioni, a voz clonada por
   `voz_editor_s_neutro.py`.
2. Colocar a fala no plano do falante, com velocidade natural (`dublar_clipes.py` gera `voz/cNN.wav`).
3. Passar cada cena no **Sync Lipsync 3** do Higgsfield (`sync_so`, entrada `input_video` + `input_audio`,
   `sync_mode: "cut_off"`). Em cena com dois rostos, usar `active_speaker_detection` com um ponto no rosto de quem fala.
   - Preço cotado em 23/11/2026: **28,98 créditos para um clipe de 8 s**, cerca de 3,6 créditos por segundo.
4. Medir de novo com `sincronia.py`. A cena só entra na montagem quando passa.
5. Montar com `montar_cena.py`, que já trava o áudio de cada clipe na duração da imagem.

## Resultado do LatentSync grátis (Kaggle T4, 23/11/2026)
- 13 de 15 clipes saíram (c06 e c08 sem saída). Medidos no clipe inteiro e só na janela da montagem: **2 de 13 aprovados**
  (c01 e c02), igual ao que já passava antes.
- O defeito que sobra é **boca mexendo sem voz** (0,4 a 1,7 s por clipe) e atraso de até 600 ms: o LatentSync 1.5 em 256 px
  redesenha a boca, mas não fecha a boca nos silêncios nem segura planos com mais de um rosto.
- Conclusão: consertar boca depois não salva a V1. O caminho daqui em diante é gerar fala e boca juntas no próprio vídeo
  (fluxo Drama do Higgsfield, Seedance 2.5 com a voz do personagem) e **nunca trocar o áudio depois**.
