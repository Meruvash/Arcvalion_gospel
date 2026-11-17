---
name: youtube-baixar
description: Baixa um vídeo público do YouTube em MP4 (até 1080p ou mais), sem login, sem cookies e sem yt-dlp, usando uma instância local do Cobalt e o YouTube.js, com FFmpeg para juntar áudio e vídeo. Diagnostica bloqueio de IP, exigência de login e de PO Token. Use quando pedirem "baixa esse vídeo do YouTube", "trecho do YouTube pro react", "download do YouTube".
---

# Baixar vídeo do YouTube

Ferramenta em `tools/video/youtube_baixar/`. Leia o `LEIAME.md` de lá.

## Fluxo
1. Se ainda não houver, rode `npm install` na pasta. Para usar o motor 1, rode também `sh instalar_cobalt.sh`.
2. Rode `node tools/video/youtube_baixar/baixar.mjs "<URL>" --pasta "<destino>" --qualidade 1080 --json`.
3. Leia o JSON:
   - `ok: true`: o arquivo passou no ffprobe. Informe o caminho, a resolução, os codecs e a duração. **Só então** diga
     que o download terminou.
   - `ok: false`: diga ao usuário o código e o motivo de cada motor (`falhas`), sem amenizar. Um código 3 significa "o
     YouTube exige PO Token ou bloqueou o IP"; um código 2, "exige login".
4. Para recortar um trecho, use `ffmpeg -ss INI -to FIM -i arquivo.mp4 -c:v libx264 -crf 16 -c:a aac trecho.mp4` no
   arquivo verificado.

## Não fazer
- Pedir conta Google, senha ou exportação de cookies.
- Usar yt-dlp ou serviço pago ou de terceiros (instâncias públicas do Cobalt incluídas): só a instância local.
- Contornar bloqueios (gerar token BotGuard, trocar de IP, fingir ser navegador) sem decisão expressa do usuário. Se o
  controle de permissões barrar, informe e pare.
- Dizer que baixou sem a linha `VERIFICADO` ou sem `ok: true`.
