---
name: baixar-youtube
description: Baixa um vídeo PÚBLICO do YouTube em MP4 com áudio, na melhor resolução disponível, sem login Google, sem cookies, sem yt-dlp e sem Cobalt (motores @distube/ytdl-core e youtubei.js + ffmpeg), e verifica a integridade do arquivo. Use quando pedirem "/baixar-youtube <url>", "baixar vídeo do YouTube", "salvar este vídeo do YouTube em MP4".
---

# Baixar vídeo público do YouTube

Ferramenta: `tools/youtube/baixar.mjs` (CLI). Pesquisa, testes e limitações em `docs/youtube/PESQUISA_DOWNLOAD_YOUTUBE.md`.

## Regras

- Só vídeo **público** cujo uso esteja autorizado (licença Creative Commons, domínio público, material do próprio
  canal ou com permissão do titular). Baixar não dá direito de republicar: em matéria do portal, vale o
  `docs/PADRAO_EDITORIAL.md` (crédito e fonte), e nada de vídeo de terceiro sem licença.
- **Nunca** usar login, cookies, conta Google, yt-dlp nem Cobalt. Vídeo com restrição de idade, privado ou só para membros
  fica de fora: a ferramenta recusa e explica.
- Não trocar user-agent nem forçar rotas de rede para "passar" de bloqueio. Se o YouTube bloquear o IP, relatar.

## Passo a passo

1. Instalar (uma vez por máquina; precisa de Node 22.22.2+ e ffmpeg):
   `cd tools/youtube && npm ci && cd -` (sem `package-lock.json`, use `npm install`).
2. Conferir os formatos sem baixar: `node tools/youtube/baixar.mjs <url> --info`
3. Baixar: `node tools/youtube/baixar.mjs <url> --saida <pasta>`
   - padrão: a maior resolução em MP4 (acima de 1080p o YouTube só tem AV1 em MP4);
   - `--max-altura 1080 --h264` para MP4 H.264 1080p, que toca em qualquer aparelho;
   - `--verificar-decodificacao` para decodificar o arquivo inteiro (mais lento, pega corrupção);
   - `--json` para resumo estruturado (arquivo, resolução, codecs, duração, tamanho).
   O caminho do MP4 sai no stdout; o progresso e os erros vão para o stderr e para `<pasta>/baixar-youtube.log`.
4. Se falhar, rodar `node tools/youtube/baixar.mjs <url> --diagnostico` e relatar a explicação impressa.

## Códigos de saída

| código | significado | o que fazer |
|---|---|---|
| 0 | MP4 baixado e verificado (1 trilha de vídeo, áudio, duração coerente) | usar o arquivo |
| 2 | argumento inválido / link não reconhecido | corrigir o link |
| 3 | extração falhou (LOGIN_REQUIRED, 429, indisponível) | outra rede ou esperar; não usar cookies |
| 4 | download recusado (403) | `--diagnostico`; se "REDE INCOMPATÍVEL", rodar de outra máquina |
| 5 | arquivo reprovado na verificação | repetir; se persistir, relatar |
| 6 | falta ffmpeg/ffprobe | instalar ffmpeg |

## Limite conhecido (17/11/2026)

No contêiner de nuvem do Claude Code (claude.ai/code), o YouTube vê os metadados por um IPv6 interno do Google e o
servidor de mídia vê um IPv4 público: a URL assinada para um IP é usada pelo outro, e **todo** download dá 403, com qualquer
ferramenta. Lá a extração funciona, mas o download não. Rode a skill no Claude Code local (máquina do usuário, sem VPN).
