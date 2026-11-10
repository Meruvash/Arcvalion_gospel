# Sistema de roteiro "arroba" para vídeos curtos (Reels, Shorts, TikTok)

> **Substituído para vídeos de agronegócio** (decisão do editor, 10/11/2026): use `PROMPT_VIDEO_AGRO.md`. Este arquivo fica como registro do vídeo de 10 s.

Copiado da estrutura de um Reel de referência (40 s, sobre o Projeto A119) enviado pelo editor em 10/11/2026.
Copiamos a **estrutura e a linguagem visual**, não as imagens: o original usa ilustrações geradas por IA, que o portal não usa.

## As batidas do roteiro (versão longa, ~40 s)

| # | Batida | Na referência | Na tela |
|---|--------|---------------|---------|
| 1 | Gancho de choque + "não é ficção, é real" | "Destroying the Moon wasn't science fiction." | Título 3D com brilho, tremor e clarão |
| 2 | Data + quem + nome próprio | "During the 1950s… Project A119" | Pílula vermelha com a data |
| 3 | A ideia, em uma frase | "detonate a nuclear bomb on the Moon" | Push-in lento de câmera |
| 4 | Correção: "não era X, mas Y" | "It wasn't meant to destroy the Moon, but…" | Palavra-chave em vermelho |
| 5 | Desfecho com documento | "The plan was eventually abandoned…" | Jornal/documento entrando em giro, batida de papel |
| 6 | Virada: "Mas a parte mais estranha?" | "But the strangest part?" | Palavras soltas em serifa itálica, tela escura |
| 7 | Frase-símbolo | "…a nuclear billboard." | Placa amarela que salta |
| 8 | Fecho em laço | "Some editors rewatch this. Others…" | CTA (no portal: só o endereço do site) |

Na versão de 10 s ficam 1–2, 5 (documento), 6 e 7. Áudio: narração rápida, trilha tensa baixa, whoosh em cada corte,
impacto no gancho e na placa, papel no documento, carimbo no realce.

## Regras do portal que valem para o vídeo

- Nada inventado: cada fato com fonte na tela (rodapé fixo) e citação literal só de texto lido na fonte.
- Nenhuma imagem gerada por IA: fundo, documentos e títulos são desenhados em código (`tools/video/*/render.py`).
  A voz e os efeitos sonoros vêm da ElevenLabs (áudio sintético, não imagem).
- Sem menção à advocacia do editor e sem oferta de serviço no fecho.
- Paleta azul do portal no lugar do preto; vermelho e amarelo só nos destaques.

## Vídeo 1: alongamento de dívida rural (10,8 s)

Roteiro narrado:
> Prorrogar dívida rural virou decisão do banco. Desde julho, o Manual de Crédito Rural diz: "por sua conveniência e
> decisão". Mas a parte mais estranha? O STJ diz que é direito do devedor.

Fontes lidas em 10/11/2026:
- Resolução CMN nº 5.314, de 25/6/2026, em vigor em 1º/7/2026, nova redação do MCR 2-6-4 ("Fica a instituição financeira
  autorizada, por sua conveniência e decisão, mediante solicitação do mutuário, a prorrogar a dívida…"):
  https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Resolu%C3%A7%C3%A3o%20CMN&numero=5314
- Súmula 298 do STJ (2ª Seção, julgada em 18/10/2004, DJ 22/11/2004): "O alongamento de dívida originada de crédito rural
  não constitui faculdade da instituição financeira, mas, direito do devedor nos termos da lei."
  https://scon.stj.jus.br/SCON/sumstj/toc.jsp?livre=%27298%27.num.&O=JT

Gerar de novo: `cd tools/video/alongamento-divida-rural && python3 tts.py` (só se mudar o texto; precisa da ElevenLabs),
`python3 render.py quadros && sh mixar.sh quadros saida.mp4`.
