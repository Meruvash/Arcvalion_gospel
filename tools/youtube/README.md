# baixar-youtube

Baixa vídeo **público** do YouTube em MP4 com áudio, na melhor resolução disponível, **sem login Google, sem cookies,
sem yt-dlp e sem Cobalt**. Junta vídeo e áudio com ffmpeg (sem recodificar) e verifica o arquivo com ffprobe.

- Motor 1: [`@distube/ytdl-core`](https://github.com/distubejs/ytdl-core) 5.2.1 (InnerTube próprio; assinatura resolvida
  localmente; PO token gerado localmente via [`bgutils-js`](https://github.com/LuanRT/BgUtils); formatos só-SABR via
  [`googlevideo`](https://github.com/LuanRT/GoogleVideo)).
- Motor 2 (reserva): [`youtubei.js`](https://github.com/LuanRT/YouTube.js) 18.3.0, clientes ANDROID_VR → MWEB → TV.

Versões fixadas em `package.json`: atualizar é decisão consciente (o YouTube muda; as bibliotecas acompanham).
Pesquisa completa e resultados dos testes: [`docs/youtube/PESQUISA_DOWNLOAD_YOUTUBE.md`](../../docs/youtube/PESQUISA_DOWNLOAD_YOUTUBE.md).

## Instalação

Requisitos: Node.js 22.22.2+ (ou 24.15+, 26+) e ffmpeg/ffprobe no PATH.

```bash
cd tools/youtube
npm ci          # ou npm install
npm test        # 9 testes offline (escolha de formato, nomes, erros, verificação de integridade)
```

## Uso

```bash
node tools/youtube/baixar.mjs "https://www.youtube.com/watch?v=aqz-KE-bpKQ" --saida videos/
node tools/youtube/baixar.mjs aqz-KE-bpKQ --max-altura 1080 --h264 --saida videos/   # MP4 H.264 1080p
node tools/youtube/baixar.mjs aqz-KE-bpKQ --info          # lista formatos, não baixa
node tools/youtube/baixar.mjs aqz-KE-bpKQ --diagnostico   # testa se a rede consegue baixar
node tools/youtube/baixar.mjs aqz-KE-bpKQ --json --verificar-decodificacao --saida videos/
```

O caminho do arquivo final sai no stdout; progresso e erros vão para o stderr e para `<saida>/baixar-youtube.log`.
Arquivos temporários são apagados mesmo em caso de falha; arquivo que não passa na verificação não é entregue.

Verificação de integridade (sempre): contêiner MP4 legível, exatamente 1 trilha de vídeo, ao menos 1 de áudio, duração
dentro de 1% (mín. 2 s) da informada pelo YouTube e, no download, bytes recebidos = tamanho anunciado.
Com `--verificar-decodificacao`, decodifica tudo com ffmpeg e reprova qualquer erro.

Códigos de saída: 0 ok · 2 argumentos · 3 extração · 4 download · 5 integridade · 6 falta ffmpeg.

## No Claude Code

A skill `.claude/skills/baixar-youtube/SKILL.md` ensina o agente a usar esta CLI (`/baixar-youtube <url>`).

## Limite conhecido

Em rede cuja saída usa IPs diferentes para `youtube.com` e `googlevideo.com` (caso do contêiner de nuvem do Claude Code,
VPNs e alguns CGNAT), o download dá 403 com **qualquer** ferramenta: a URL de mídia é assinada para o IP que pediu os
metadados. `--diagnostico` mostra os dois IPs.
