---
name: baixar-youtube
description: Baixa um vídeo PÚBLICO do YouTube em MP4 com áudio, na melhor resolução disponível, sem login Google e sem cookies, e confere a integridade do arquivo. Três motores em sequência automática: @distube/ytdl-core, youtubei.js e, se a rede bloquear os dois (caso da nuvem do Claude Code), o site loader.to aberto num Chromium sem tela. Use quando pedirem "/baixar-youtube <url>", "baixar vídeo do YouTube", "salvar este vídeo do YouTube em MP4".
---

# Baixar vídeo público do YouTube

Ferramenta: `tools/youtube/baixar.mjs` (CLI). Pesquisa, testes e limitações em `docs/youtube/PESQUISA_DOWNLOAD_YOUTUBE.md`.

## Regras

- Só vídeo **público** cujo uso esteja autorizado (licença Creative Commons, domínio público, material do próprio
  canal ou com permissão do titular). Baixar não dá direito de republicar: em matéria do portal, vale o
  `docs/PADRAO_EDITORIAL.md` (crédito e fonte), e nada de vídeo de terceiro sem licença. Se o usuário não disser de quem é
  o vídeo e ele parecer de terceiro (clipe musical, filme, programa de TV), pergunte antes.
- **Nunca** usar login, cookies, conta Google nem Cobalt. Vídeo com restrição de idade, privado ou só para membros fica de fora.
- Não resolver CAPTCHA, não trocar user-agent e não forçar rotas de rede para passar de bloqueio. Não clicar em anúncio.
- O motor `site` usa um serviço de terceiros (loader.to): o link do vídeo vai para ele. Não usar com vídeo não listado ou
  privado do usuário sem avisar.

## Passo a passo

1. Dependências (rápido; só instala se faltar):
   ```bash
   [ -d tools/youtube/node_modules ] || (cd tools/youtube && npm ci --no-audit --no-fund)
   ```
   Precisa de Node 22.22.2+ e ffmpeg (já existem na nuvem do Claude Code). O motor `site` precisa do Playwright com Chromium:
   na nuvem do Claude Code já vem instalado (não reinstale); em máquina local, `npm i -g playwright && npx playwright install chromium`.
2. Baixar (padrão recomendado: 1080p, que é o que o site converte mais rápido):
   ```bash
   node tools/youtube/baixar.mjs "<url>" --max-altura 1080 --saida <pasta> --json
   ```
   - sem `--max-altura`: a maior resolução (4K em AV1/MP4 pelos motores 1–2; no site, 4K demora bem mais);
   - `--h264`: só H.264, que toca em qualquer aparelho (até 1080p);
   - `--motor site`: pula direto para o site (economiza ~10 s na nuvem, onde os motores 1–2 sempre levam 403);
   - `--verificar-decodificacao`: decodifica o arquivo inteiro (mais lento, pega corrupção).
   Rode em segundo plano (`run_in_background`): pelo site, um vídeo de 10 min em 1080p leva ~5–10 min para baixar.
   O progresso vai para o stderr e para `<pasta>/baixar-youtube.log`.
3. Conferir o JSON final (`ok`, `motor`, `video.altura`, `audio.codec`, `duracao`) e entregar o arquivo ao usuário
   (na nuvem: `SendUserFile` com o caminho do campo `arquivo`).
4. Se falhar, relatar a `explicação` impressa. `--diagnostico` mostra se a rede consegue baixar direto do YouTube.

## Códigos de saída

| código | significado | o que fazer |
|---|---|---|
| 0 | MP4 baixado e verificado (1 trilha de vídeo, áudio, duração coerente) | entregar o arquivo |
| 2 | argumento inválido / link não reconhecido | corrigir o link |
| 3 | extração falhou (LOGIN_REQUIRED, 429, indisponível) | outra rede ou esperar; não usar cookies |
| 4 | download recusado (403) ou site não entregou | ver explicação; o site pode ter saído do ar ou mudado |
| 5 | arquivo reprovado na verificação | repetir; se persistir, relatar |
| 6 | falta ffmpeg/ffprobe | instalar ffmpeg |

## Se o site mudar ou sair do ar

O motor `site` depende do layout do loader.to (`#link`, `#format`, `#load`, `a[id$="_downloadLink"]`). Se quebrar, a
mensagem diz "layout mudou?" ou "não terminou a conversão". Conserte os seletores em `linkDoSite` (`tools/youtube/baixar.mjs`)
olhando a página com uma captura do Playwright, rode `npm test` e registre no relatório. Sites como yt1s e 9convert já
foram derrubados (hoje mostram página da IFPI).
