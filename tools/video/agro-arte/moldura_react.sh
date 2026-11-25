#!/bin/sh
# Monta a "moldura de react": imagem real centralizada com borda clara sobre um fundo da mesma imagem, ampliado e desfocado.
# uso: sh moldura.sh entrada.mp4 inicio duracao recorte(crop=...) largura_fg y_fg saida.mp4
IN=$1; SS=$2; T=$3; CROP=$4; FW=$5; FY=$6; OUT=$7
ffmpeg -v error -y -ss $SS -t $T -i "$IN" -filter_complex "[0:v]$CROP,split[a][b];[a]scale=1080:1080:force_original_aspect_ratio=increase,crop=1080:1080,boxblur=24:2,eq=brightness=-0.12:saturation=1.1[bg];[b]scale=$FW:-2,pad=iw+12:ih+12:6:6:color=0xF6EFD8[fg];[bg][fg]overlay=(W-w)/2:$FY,fps=30,format=yuv420p" -an -c:v libx264 -crf 16 "$OUT"
