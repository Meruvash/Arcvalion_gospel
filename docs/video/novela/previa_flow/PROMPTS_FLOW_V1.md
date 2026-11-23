# Teste grátis da novela V1 ("O livro do pai") no Google Flow (23/11/2026)

**Objetivo:** publicar 1 episódio de teste e medir visualizações antes de assinar qualquer plano pago.

## Por que quase tudo sai de graça
O roteiro V1 (`../roteiros/novela_v1_livro_do_pai.json`) é uma **novela em prints**:
- **Telas de WhatsApp:** feitas por nós em HTML, sem gerar vídeo.
- **Vozes:** ElevenLabs, que já temos.
- **Dr. Pelicioni:** foto e vídeo reais dele, nunca rosto gerado
  (`../PERSONAGEM_DR_PELICIONI.md`).

Só os **5 planos de fundo** abaixo precisam do gerador. Isso cabe em 1 dia de cota grátis do Flow (50 créditos, 10 por
clipe Veo 3.1 Lite). Com refações, são 2 a 3 dias.

## Como gerar (conta Google sem assinatura)
- **Onde:** labs.google/flow, modelo **Veo 3.1 Lite** (até 05/12/2026; depois disso, o Omni Flash 1.2 em 720p).
- **Formato:** vertical 9:16, 8 segundos.
- **Prompt:** cole o texto em inglês exatamente como está. A descrição da Rosa é igual em todos os planos, para ela não
  mudar de rosto entre eles.
- **Som:** o áudio do Veo será descartado; as vozes vêm do ElevenLabs.
- **Horário:** sem assinatura, a geração de vídeo pode ficar fora do ar entre 11h e 14h.
- **Conferência antes de mandar:** rosto, mãos (5 dedos), olhos, objetos que mudam de forma. Se errar, gere de novo.
- **Arquivos:** baixe e mande os MP4 com os nomes `f1.mp4` a `f5.mp4`.

**Rosa (texto fixo de todos os planos):** `a Brazilian woman in her mid-fifties, tanned skin, shoulder-length
dark hair with grey strands tied back, simple floral cotton blouse`

## Passo 0: folha da Rosa no Gemini (grátis), antes do Flow
Abra gemini.google.com com a mesma conta Google e peça a imagem com este texto:

`Create a character reference sheet of one fictional woman (not resembling any real person or actress): a Brazilian woman in her mid-fifties, tanned skin, shoulder-length dark hair with grey strands tied back, kind tired eyes, simple floral cotton blouse in soft pink and green. Five views on a plain light grey background, same person, same clothes: front, three-quarter left, three-quarter right, profile, close-up of the face. Even soft studio light, photorealistic, natural skin texture, no text.`

- **Conferência:** o rosto tem que ser o mesmo nas 5 vistas, sem mão deformada. Se não estiver, peça de novo.
- **Arquivo:** salve a melhor imagem como `rosa_folha.png`.
- **No Flow:** nos planos f1, f2 e f5, use o modo de vídeo a partir de imagem (*Frames to video* ou *Ingredients to
  video*). Envie a vista de frente da Rosa e cole o prompt do plano. Assim o rosto fica igual em todos os planos.
- **Planos sem gente:** f3 e f4 vão só com o texto.

## Como me entregar os arquivos
Crie no Google Drive uma pasta chamada `Novela V1` e coloque lá a `rosa_folha.png` e os vídeos `f1.mp4` a `f5.mp4`.
Eu leio direto do Drive pelo conector desta sessão. Se preferir, mande os arquivos aqui na conversa.

## Os 5 planos

| Plano | Momento do roteiro | Prompt (colar no Flow) |
|---|---|---|
| f1 | 0–15 s, fundo das primeiras mensagens | `Vertical shot. A Brazilian woman in her mid-fifties, tanned skin, shoulder-length dark hair with grey strands tied back, simple floral cotton blouse, sits at a wooden table in a simple rural farmhouse kitchen, reading her phone. Her expression slowly turns from calm to shock and hurt. Morning light from a window, a cup of coffee, an enamel coffee pot. Static camera, slow push in. Realistic, natural colors, cinematic, shallow depth of field. No text, no subtitles.` |
| f2 | 15–27 s, "Livro velho do pai? Joga no lixo." | `Vertical close-up. A Brazilian woman in her mid-fifties, tanned skin, shoulder-length dark hair with grey strands tied back, simple floral cotton blouse, holds an old worn leather-bound ledger book against her chest at a farmhouse kitchen table, eyes wet, holding back tears, looking down. Soft window light. Static camera. Realistic, cinematic, shallow depth of field. No text, no subtitles.` |
| f3 | 46–62 s, o livro decide (fundo dos cartões de lei) | `Vertical close-up of an old worn leather-bound ledger book lying open on a rustic wooden table, yellowed handwritten pages, a breeze slowly lifts a page, dust in a sunbeam, an old pair of reading glasses beside it. No people, no hands. Slow camera push in. Realistic, warm golden light, cinematic. No readable text, no subtitles.` |
| f4 | 62–66 s, queda do vilão (respiro) | `Vertical shot of a green Brazilian farm at golden hour, a wooden gate (porteira) and a dirt road leading to a small white farmhouse, pasture and a few trees, gentle wind in the grass. No people. Slow drone-like movement forward. Realistic, warm vivid colors, cinematic. No text.` |
| f5 | 66–71 s, "Dona Rosa, a senhora não está sozinha." | `Vertical medium close-up. A Brazilian woman in her mid-fifties, tanned skin, shoulder-length dark hair with grey strands tied back, simple floral cotton blouse, at a farmhouse kitchen table, holds her phone close to her chest, exhales with relief and gives a small grateful smile, eyes still wet. Warm afternoon light. Static camera. Realistic, cinematic, shallow depth of field. No text, no subtitles.` |

## O que eu monto depois de receber os planos
1. Gerar as vozes de Valdir, Tavares e Rosa no ElevenLabs. A fala do Dr. Pelicioni sai na voz clonada, por
   `voz_editor_s_neutro.py`.
2. Fazer as telas de WhatsApp em HTML próprio: nomes fictícios, sem marca, com o aviso "dramatização" fixo.
3. Fazer a entrada do Dr. Pelicioni:
   - por enquanto, chamada de vídeo com a foto oficial e leve movimento de câmera;
   - quando o vídeo dele chegar, com o vídeo real.
4. Fazer os cartões de lei (arts. 1.794 e 1.795 do Código Civil, com a fonte) e a legenda.
5. Passar tudo pelo `crivo_qualidade.py`, pela revisão das folhas e pelo `auditar_video.py`. Só depois o vídeo vai ao
   editor.

## Cuidados para publicar o teste
- **Rótulo de IA:** marcar "conteúdo gerado por IA" no Instagram. Desde 31/08/2026, perfil que mostra gente feita por
  IA sem rótulo perde alcance.
- **Termos do Flow grátis:** os termos de uso comercial do plano sem assinatura não foram confirmados. Para um post de
  teste, sem venda, o risco é baixo, mas o editor deve ler os termos antes de transformar isso em série.
- **Gente gerada por IA:** a regra do projeto contra gente gerada por IA vale para os vídeos do agro. Aqui o editor pediu
  expressamente o teste com personagens humanos.
