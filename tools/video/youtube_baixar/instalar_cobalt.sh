#!/bin/sh
# Instala e sobe uma instância LOCAL do Cobalt (imputnet/cobalt, AGPL-3.0) em http://localhost:9000/.
# Não usa cookies nem conta Google. Commit fixado: o testado em 17/11/2026.
# Uso: sh instalar_cobalt.sh [pasta]   (padrão: ~/cobalt)
set -e
DIR="${1:-$HOME/cobalt}"
COMMIT=a636575b09de1fc55d9b8cd98cac88f5f2f16b42
command -v pnpm >/dev/null || npm install -g pnpm@9
if [ ! -d "$DIR/.git" ]; then git clone https://github.com/imputnet/cobalt.git "$DIR"; fi
cd "$DIR" && git fetch -q origin "$COMMIT" 2>/dev/null || true; git checkout -q "$COMMIT"
pnpm install --frozen-lockfile --filter @imput/cobalt-api...
cd api
API_URL=http://localhost:9000/ API_PORT=9000 nohup node src/cobalt > "$DIR/cobalt.log" 2>&1 &
sleep 5
curl -fsS http://localhost:9000/ >/dev/null && echo "cobalt no ar: http://localhost:9000/ (registro em $DIR/cobalt.log)" || { echo "cobalt não respondeu; veja $DIR/cobalt.log"; exit 1; }
