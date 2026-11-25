# Baixar vídeo público do YouTube (sem login, sem cookies, sem yt-dlp)

`baixar.mjs` recebe uma URL do YouTube e tenta dois motores, nesta ordem:
1. **Cobalt local** (imputnet/cobalt, AGPL-3.0). É uma instância própria, em `http://localhost:9000/`; não usa serviço de
   terceiros.
2. **YouTube.js** (LuanRT/YouTube.js, MIT). Escolhe o melhor vídeo até a qualidade pedida (1080p por padrão, ou `max`),
   prefere H.264 e AAC, baixa em pedaços de 10 MB e junta vídeo e áudio com FFmpeg. Áudio Opus vira AAC para caber no
   MP4.

O arquivo só é dado como pronto depois do **ffprobe**: precisa ter vídeo, áudio e duração. Só então o programa imprime
`VERIFICADO: …`. Nada de login Google, exportação de cookies ou yt-dlp.

## Instalação
```sh
cd tools/video/youtube_baixar
npm install                      # youtubei.js 18.3.0 e undici 6
sh instalar_cobalt.sh            # opcional (motor 1): clona o commit testado, instala com pnpm e sobe na porta 9000
```
Precisa de Node 18 ou mais novo (testado no 22.23), FFmpeg e ffprobe no PATH, e git e pnpm 9 para o Cobalt.

## Uso
```sh
node baixar.mjs "https://www.youtube.com/watch?v=ID" --pasta ~/videos --qualidade 1080
node baixar.mjs URL --motor youtubejs --json      # só o YouTube.js, saída em JSON
node baixar.mjs URL --cobalt http://localhost:9000/
```

| Código de saída | Significado |
|---|---|
| 0 | baixado e **verificado** |
| 2 | o YouTube exige login ou verificação "não sou um robô" (ou o vídeo tem restrição de idade) |
| 3 | os formatos aparecem, mas o servidor de vídeo responde 403: exigência de **PO Token** ou bloqueio do IP |
| 4 | limite de pedidos ou bloqueio do IP (429) |
| 5 | vídeo privado, removido, bloqueado na região, ao vivo ou com DRM |
| 6 | instância do Cobalt fora do ar (e o YouTube.js também falhou) |
| 1 | outro erro (detalhe na saída e no registro) |

Cada execução grava um registro JSON por linha em `<pasta>/.youtube_baixar.log`, com cada cliente tentado e a resposta
recebida.

## Teste de 17/11/2026, na nuvem do Claude Code (IP de datacenter)
- **Vídeos:** `JRYKhPZGAPU` (reportagem do Canal do Boi) e `jNQXAC9IVRw` ("Me at the zoo"). Os dois públicos.
- **Cobalt 11.7.1 local:** aceitou o pedido e devolveu um túnel de 1080p H.264, mas o túnel entregou **0 byte**.
- **YouTube.js 18.3.0:**
  - os clientes IOS e MWEB listaram os formatos (até 1080p);
  - o servidor de vídeo (googlevideo) respondeu **403** a todos;
  - o cliente WEB não tinha URL a decifrar;
  - o cliente TV veio como UNPLAYABLE.
- **Resultado:** código 3. O YouTube exige PO Token para entregar o fluxo a clientes anônimos neste IP, ou bloqueia o IP.
  **Nenhum arquivo foi baixado**, e o programa disse isso.
- **PO Token:** gerar um PO Token anônimo (BotGuard, pelo BgUtils) foi barrado pelo controle de permissões da sessão, e
  não foi contornado.
- **Caminhos possíveis, a decidir pelo editor:**
  - rodar estas mesmas ferramentas no computador dele (IP residencial costuma ter menos bloqueio);
  - configurar no Cobalt o `YOUTUBE_SESSION_SERVER` com o yt-session-generator da própria imput, depois de avaliar.
- **Caminho de sucesso:** junção com FFmpeg e verificação de um download que chegue inteiro. Ainda **não foi exercitado de
  ponta a ponta** com um vídeo do YouTube, porque nenhum fluxo chegou.

## Compatibilidade (consultada em 17/11/2026)
| Projeto | Versão | Observação |
|---|---|---|
| imputnet/cobalt (API) | 11.7.1, commit `a636575` (6/4/2026) | Node ≥ 18.17; pnpm 9. Depende de `youtubei.js` **17.0.1** (fixo) e de `isolated-vm` 6 (módulo nativo, compilou no Node 22). PO Token só com `YOUTUBE_SESSION_SERVER`. Cookies são opcionais (`COOKIE_PATH`) e **não** são usados aqui |
| LuanRT/YouTube.js (`youtubei.js`) | 18.3.0 (23/10/2026) | Usado direto no motor 2. Precisa de `Platform.shim.eval` para os scripts do player |
| FFmpeg / ffprobe | do sistema | Junção e verificação |
