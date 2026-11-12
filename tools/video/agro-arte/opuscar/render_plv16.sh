#!/bin/sh
export PLAYWRIGHT_CHROME=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell
P=/home/user/webdoc-research/poc/plv16/lemo; O=/home/user/webdoc-research/poc/plv16/hf/assets/art; cd ~/lemo-opuscar
r() { node core/render/video.mjs $P --fps 30 --workers 3 --size 1080x1080 --q "$1" --out $O/$2.mp4 2>&1 | grep -v "^\[note\]\|GL Driver" | tail -2; }
r "cena=mapa&dur=6.2&n=.45&ne=1&co=1.85&a=2.9&b=3.7&c=4.3" mapa
r "cena=relogio&dur=7" relogio
r "cena=folhinha&dur=6.6" folhinha
r "cena=fim&dur=6.2" fim
echo LEMO_DONE
