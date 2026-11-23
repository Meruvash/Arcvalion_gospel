# Novela em cena atuada (decisão de 23/11/2026)

**Por que mudou.** A V1 em prints (telas de conversa e o editor numa chamada de vídeo) foi reprovada pelo editor: faltava
impacto visual, faltava trilha e a voz do Tavares estava ruim. O fluxo de microdrama do próprio Higgsfield ("drama-ads",
`references/story-rules.md`, lido em 23/11/2026) dá a razão:
- **O gancho é corpo, não texto.** Documento ou tela só confirmam o que um corpo já mostrou.
- **Câmera:** 60 a 80% de closes, corte médio de 2 a 3 s e alternância entre os dois rostos no confronto.
- **Cena de papelada perde a tensão.** Quem carrega a cena são os corpos e as distâncias entre eles.

## Como os episódios passam a ser feitos
| Etapa | Ferramenta | Regra |
|---|---|---|
| Roteiro | `auditar_novela.py` (fórmula) e as regras de `story-rules.md` | o gancho é uma ação física; o Dr. Pelicioni chega em pessoa na virada |
| Folhas de personagem | Higgsfield (Nano Banana Pro ou Seedream) | uma folha por personagem, reaproveitada em todos os episódios |
| Vozes | ElevenLabs, a voz fixa de cada personagem (`ELENCO_FIXO.md`) | o editor sempre por `voz_editor_s_neutro.py` |
| Cenas com fala | **Seedance 2.5** `omni_reference`, com as folhas e a amostra de voz como `audio_references` | um falante por plano, cerca de 1 s de folga depois da fala, sem música |
| Reações mudas e ambientação | Seedance 2.5 ou Kling 3.0 (mais barato, sem áudio) | o Kling no Higgsfield só aceita quadro inicial e final, não folha de personagem |
| Trilha | **ElevenLabs Music** (instrumental, por trechos: tensão, suspense, virada, acorde final) | só descrever o som, sem nome de compositor ou de obra; plano pago tem uso comercial online (termos de 09/10/2026) |
| Montagem | `montar_episodio.py`, mais trilha e efeitos | legenda amarela; cartão de lei com a fonte como inserto; rótulo de IA no post |

## Preços cotados no Higgsfield (23/11/2026)
| Item | Créditos |
|---|---|
| Episódio de cerca de 78 s, 720p (6 folhas, 3 cenários, 6 cenas de 13 s, trilha), sem refação | **583** |
| O mesmo episódio em 1080p | **1.285** |
| Seedance 2.5, 15 s: rascunho 480p / final 720p / 1080p | 45 / 105 / 240 |

Com rascunho e refação, a conta fica entre **700 e 1.200 créditos por episódio em 720p**.

## Riscos ainda abertos
1. **Fala em português gerada pelo modelo:** não existe teste público. O Kling não lista o português. Por isso a voz entra
   como amostra do ElevenLabs, e a primeira cena é um teste curto em 480p antes do episódio inteiro.
2. **Dois personagens falando no mesmo plano:** a boca troca de dono. Cada plano tem um só falante.
3. **Contato físico e mudança de estado** (empurrão, papel rasgando) quebram na geração. O roteiro usa ações simples:
   soltar, pegar, entregar, recuar.
