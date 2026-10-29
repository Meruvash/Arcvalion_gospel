#!/usr/bin/env bash
# Build do site no Cloudflare (Workers Builds ou Pages). Comando de build no painel: bash tools/build_cloudflare.sh
# A instalação do Pillow (só necessária quando há fotos nas matérias) é tentada de três jeitos e nunca derruba o build.
set -u
echo "Python: $(python3 --version 2>&1)"
python3 -m pip install -q -r requirements.txt 2>/dev/null \
  || python3 -m pip install -q --user -r requirements.txt 2>/dev/null \
  || python3 -m pip install -q --break-system-packages -r requirements.txt 2>/dev/null \
  || echo "aviso: pip indisponível; o site é montado sem processar fotos"
python3 tools/build.py --producao --sem-og
