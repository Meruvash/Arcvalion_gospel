# Download de vídeo público do YouTube sem yt-dlp, sem Cobalt e sem login: pesquisa e testes

Data: 17/11/2026. Ponto de partida: yt-dlp (falhou, pediu login/cookies) e Cobalt estão descartados.
Ferramenta implementada: `tools/youtube/` (CLI) + skill `.claude/skills/baixar-youtube/`.

## Resumo

1. Há mecanismos **realmente independentes** do yt-dlp, mantidos em novembro de 2026, e eles **extraem** a lista
   completa de formatos (até 2160p60) de um vídeo público **sem login e sem cookies**. Testado e comprovado em 4 de 5
   candidatos: `@distube/ytdl-core`, `youtubei.js`, NewPipeExtractor e pytubefix (só no cliente ANDROID_VR).
2. **Nenhum download completo foi comprovado neste ambiente.** O motivo foi medido, não suposto: o contêiner de nuvem
   (rede do Google, AS396982) chega ao `youtube.com` por um IPv6 interno (`fda3:…`) e ao `googlevideo.com` por um IPv4
   público (`160.79.106.x`, pool rotativo). A URL de mídia vem assinada para o IPv6 (`ip=`); o servidor de mídia vê o
   IPv4 (`mip=`), redireciona e devolve 403. Isso afetou **todos** os cinco candidatos, inclusive o 360p progressivo.
3. Melhor solução: `@distube/ytdl-core` 5.2.1 (motor principal) + `youtubei.js` 18.3.0 (reserva), via CLI direta com uma
   skill que a documenta. **Status: implementada e testada até a extração; o download ponta a ponta ainda precisa ser
   confirmado numa máquina com IP único** (o Claude Code local do usuário). Rode `--diagnostico` primeiro.

## 1. Tabela comparativa

Legenda: S = sim · N = não · ? = não verificado · "teste" = medido aqui em 17/11/2026.

| # | Solução | Motor | Sem login/cookies (extração) | Indep. yt-dlp | Indep. Cobalt | MP4 1080p c/ áudio | Grátis | Open source | API/CLI p/ Claude | Última atualização | Veredito |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **YouTube.js / youtubei.js** (LuanRT) | InnerTube próprio | **S (teste: ANDROID_VR e MWEB até 2160p60; TV "UNPLAYABLE"; WEB sem URL)** | S | S | S, com mux ffmpeg | S | S (MIT) | API Node | 18.3.0, 23/10/2026 | **Top 5**, motor reserva |
| 2 | **@distube/ytdl-core** | InnerTube próprio + googlevideo (SABR) + bgutils (PO token) | **S (teste: visionos, web_embedded, tv, mweb, todos até 2160p60)** | S | S | S, com mux | S | S (MIT) | API Node | 5.2.1, 04/11/2026 (reescrito em 22/10) | **Top 5**, motor principal |
| 3 | @discord-player/youtubei | nome não existe no npm; o real é `discord-player-youtubei` 3.1.0, invólucro de youtubei.js | = youtubei.js | S | S | — | S | S | só p/ bots Discord | 06/09/2026 | Descartado: não é mecanismo próprio |
| 4 | youtubei.js × YouTube.js | mesmo projeto (npm aponta para LuanRT/YouTube.js) | — | — | — | — | — | — | — | — | Contado uma vez (item 1) |
| 5 | **NewPipeExtractor** | extrator Java próprio | **S (teste: 18 vídeo-only até 2160p + 5 áudios)** | S | S | S, com mux | S | S (GPL-3) | biblioteca JVM (JitPack), sem CLI oficial | v0.27.1, ~10/11/2026 | **Top 5**; issue #1528 (360p via Piped) aberta |
| 6 | NewPipe (Android) | NewPipeExtractor | S | S | S | S (app junta DASH) | S | S | N (app Android) | v0.29.3, 10/11/2026 | Não automatizável; use o extrator |
| 7 | Seal | yt-dlp (youtubedl-android) | — | **N** | S | S | S | S | N | v1.13.1 (jan/2026) | Descartado |
| 8 | LibreTube | NewPipeExtractor local + SABR próprio (v32) | S | S | S | S | S | S | N (Android) | v32.1, 20/08/2026 | Não automatizável |
| 9 | Piped | Piped-Backend (NewPipeExtractor) | ? (instâncias públicas instáveis) | S | S | relatos de 360p (#1528) | S | S | API HTTP | backend: commit 29/05/2026 | Fraco: depende de instância de terceiro |
| 10 | Invidious + companion | companion = youtubei.js | ? (instância pública `inv.nadeko.net` deu 502 no teste) | S | S | relato de 144–2160p (ago/2026) | S | S (AGPL) | API HTTP | companion: 07/11/2026 | Só auto-hospedado; bugs abertos (#403, #397) |
| 11 | FreeTube | youtubei.js local (+ Invidious opcional) | S | S | S | baixador embutido removido na v0.24 | S | S | N (desktop) | v0.26.0 (nov) | Descartado p/ automação |
| 12 | Parabolic | yt-dlp | — | **N** | S | S | S | S | N | 2026.5.0 (24/05) | Descartado |
| 13 | MeTube | yt-dlp (Docker) | — | **N** | S | S | S | S | web UI | 2026.11.14 | Descartado (yt-dlp) |
| 14 | JDownloader 2 | plugin Java próprio (YoutubeDashV2) | S (conta opcional) | **S** | S | provável (?) | S | S (GPL) | headless + API MyJDownloader | instaladores 04/09/2026 | Independente, mas pesado; não testado |
| 15 | 4K Video Downloader Plus | próprio, fechado | ? | S (?) | S | S | parcial (limites) | N | sem CLI | 25.3.4 (out/2025) / ? 2026 | Descartado: sem automação |
| 16 | Stacher | yt-dlp | — | **N** | S | S | S | ? | N | 7.1.x | Descartado |
| 17 | ClipGrab | yt-dlp (desde 3.9.7) | — | **N** | S | S | S | S | N | 3.9.x | Descartado |
| 18 | Tartube | youtube-dl/yt-dlp | — | **N** | S | S | S | S | N | v2.5.253 (27/10/2026) | Descartado |
| 19 | MediaHuman | fechado; indício de yt-dlp (componente "EJS") | ? | ? | S | S | S | N | N | 3.9.19 (abr/2026) | Descartado |
| 20 | Extensões (Video DownloadHelper etc.) | captura no navegador; FTODE usa yt-dlp | depende do navegador | VDH: S (?) | S | VDH: premium p/ máxima | parcial | VDH: parcial | N | VDH 10.6 | Sem automação; Chrome Web Store veta YouTube |
| + | **kkdai/youtube** (Go, `youtubedr`) | InnerTube próprio, cliente Android | **N no teste: HTTP 429 neste IP** | S | S | S, com mux | S | S (MIT) | CLI | v2.10.8, 08/11/2026 | **Top 5**; bloqueado por 429 aqui |
| + | **pytubefix** (Python) | InnerTube + BotGuard (Node embutido) | **parcial no teste: WEB/TV/MWEB = 429; ANDROID_VR = OK até 2160p** | S | S | S, com mux | S | S (MIT) | API + CLI | 11.2.1, 16/10/2026 | **Top 5** |
| + | RustyPipe (Rust) | próprio + `rustypipe-botguard` | ? | S | S | ? | S | S | CLI | commit 03/08/2026 | Promissor, não testado |
| + | rusty_ytdl, pytube, @ybd-project/ytdl-core | — | — | S | S | — | S | S | — | 2024, 2023, 2024 | Abandonados |

## 2. Top 5 testados

1. `@distube/ytdl-core` 5.2.1: único com PO token, SABR e retomada de download embutidos e sem configuração.
2. `youtubei.js` 18.3.0: base do FreeTube e do invidious-companion; manutenção semanal.
3. NewPipeExtractor v0.27.1: ecossistema NewPipe/LibreTube/Piped; JVM.
4. `kkdai/youtube` v2.10.8: binário Go único com CLI; corrigido em 04 e 08/11/2026.
5. `pytubefix` 11.2.1: Python, gera PO token via BotGuard.

## 3. Resultados reais dos testes (17/11/2026, contêiner de nuvem)

Vídeo: *Big Buck Bunny 60fps 4K*, canal oficial da Blender Foundation (CC BY 3.0), `aqz-KE-bpKQ`, 635 s.
Cada candidato foi instalado em diretório isolado. Nenhum login, cookie ou token de conta foi usado.

| Candidato | Extração sem login | Maior formato listado | Download | Erro registrado |
|---|---|---|---|---|
| @distube/ytdl-core | OK nos 4 clientes padrão | 2160p60 (AV1/VP9), 1080p60 H.264 | **falhou** | `itag 299: media answered HTTP 403` (também itag 18, 134 e 140) |
| youtubei.js | OK em ANDROID_VR e MWEB | 2160p60 | **falhou** | `The server responded with a non 2xx status code` |
| NewPipeExtractor | OK | 2160p | **falhou** | HTTP 403 |
| pytubefix | só ANDROID_VR (WEB/TV/MWEB: 429) | 2160p | **falhou** | `HTTP Error 403: Forbidden` |
| kkdai/youtube | **falhou** | — | — | `unexpected status code: 429` |

Arquivo criado: nenhum. Áudio/vídeo/resolução do arquivo final: não aplicável. Nenhum exigiu login nem cookies para
extrair; o bloqueio foi no servidor de mídia.

### Prova da causa (rede, não biblioteca)

- URL de mídia emitida: `ip=fda3:e722:ac3:10:20a:d361:fefe:ce53` (IPv6 privado, varia de `…ce52` a `…ce60` entre pedidos).
- Ao pedir a mídia: `302` para outro servidor com `mip=160.79.106.150` e `ipbypass=yes`, e depois `403 Forbidden`
  (`Server: gvs 1.0`, corpo vazio).
- `api64.ipify.org` mostrou 6 IPs públicos diferentes em 6 pedidos seguidos (`160.79.106.145–153`).
- Repetir 15 vezes deu 15 × `403` após 1 redirecionamento: o descompasso é sistemático (IPv6 interno × IPv4 público),
  não azar de rodízio.
- Trocar o host da InnerTube (`youtubei.googleapis.com`, `m.youtube.com`, `youtube-nocookie.com`) não mudou nada:
  todos veem o IPv6 interno.
- Uma tentativa de forçar a conexão ao `googlevideo` por IPv6 foi barrada pela política de permissões do ambiente e não
  foi contornada.

O comando `node tools/youtube/baixar.mjs <id> --diagnostico` reproduz essa medição em qualquer rede.

## 4. Arquitetura escolhida

| Critério | A. Skill | B. MCP Server | C. CLI direta |
|---|---|---|---|
| Confiabilidade | = CLI (só instrui) | processo residente; mais pontos de falha | máxima: um processo, códigos de saída claros |
| Manutenção | mínima (1 Markdown) | servidor, protocolo, registro em `.mcp.json` | mínima (1 arquivo + 2 dependências fixadas) |
| Progresso / formatos / erros | via CLI | ferramentas estruturadas | `--info`, `--json`, log, códigos 0–6 |

Escolha: **C + A**. A CLI `tools/youtube/baixar.mjs` faz o trabalho; a skill `baixar-youtube` só ensina o Claude a chamá-la
e a interpretar a saída. MCP não traz ganho de confiabilidade para um comando local e soma manutenção.

## 5. Por que esses dois motores

- São independentes entre si na camada InnerTube (código diferente), então uma quebra do YouTube que derruba um nem sempre
  derruba o outro. O `@distube/ytdl-core` usa `googlevideo` e `bgutils-js` do mesmo autor do `youtubei.js` só para SABR e PO token.
- Ambos em Node, que o repositório já usa; nada de JVM (NewPipeExtractor), Go ou Python extra.
- `kkdai/youtube` e `pytubefix` ficaram de fora por terem sido bloqueados com 429 já na extração.

## 6. Próximo passo obrigatório

Rodar na máquina do usuário (Claude Code local, sem VPN):

```bash
cd tools/youtube && npm ci && npm test && cd -
node tools/youtube/baixar.mjs aqz-KE-bpKQ --diagnostico
node tools/youtube/baixar.mjs aqz-KE-bpKQ --max-altura 1080 --h264 --json --verificar-decodificacao --saida /tmp/teste-yt
```

Se o diagnóstico disser "rede OK" e o download sair com código 0, a solução está comprovada; registre aqui a data e o resultado.
Se o próprio IP doméstico receber `LOGIN_REQUIRED` ou 429, não há caminho sem autenticação nessa rede: as alternativas
restantes exigem conta (cookies) ou uma instância própria do invidious-companion em outra rede, e ficam a critério do editor.

## Fontes

- YouTube.js: https://github.com/LuanRT/YouTube.js · GoogleVideo: https://github.com/LuanRT/GoogleVideo · BgUtils: https://github.com/LuanRT/BgUtils
- @distube/ytdl-core: https://github.com/distubejs/ytdl-core · https://www.npmjs.com/package/@distube/ytdl-core
- discord-player-youtubei: https://github.com/retrouser955/discord-player-youtubei
- NewPipeExtractor: https://github.com/TeamNewPipe/NewPipeExtractor/releases · issue #1528 · NewPipe: https://github.com/TeamNewPipe/NewPipe/releases
- Piped-Backend: https://github.com/TeamPiped/Piped-Backend · invidious-companion: https://github.com/iv-org/invidious-companion
- FreeTube: https://github.com/FreeTubeApp/FreeTube · LibreTube: https://github.com/libre-tube/LibreTube
- pytubefix: https://github.com/JuanBindez/pytubefix · kkdai/youtube: https://github.com/kkdai/youtube · RustyPipe: https://codeberg.org/ThetaDev/rustypipe
- Guia de PO token (referência dos clientes; não é dependência): https://github.com/yt-dlp/yt-dlp/wiki/PO-Token-Guide
- Seal: https://github.com/JunkFood02/Seal · Parabolic: https://github.com/NickvisionApps/Parabolic · MeTube: https://github.com/alexta69/metube
- Tartube: https://github.com/axcore/tartube · ClipGrab: https://clipgrab.org/ · 4K Video Downloader: https://www.4kdownload.com/products/videodownloader-42/changelog
- Video DownloadHelper: https://www.downloadhelper.net/ · FTODE: https://addons.mozilla.org/en-US/firefox/addon/ftode/
- Relatos SABR/PO token 2026: https://github.com/shy1132/VacuumTube/issues/189 · https://github.com/OpenTubeX/OpenTubeX/pull/2530
