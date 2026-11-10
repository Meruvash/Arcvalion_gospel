#!/bin/sh
# Mixa narração, trilha e efeitos e junta com os quadros. Uso: sh mixar.sh <pasta_quadros> <saida.mp4>
Q=$1; OUT=$2
ffmpeg -v error -y -framerate 30 -i "$Q/q%04d.jpg" -i voz.mp3 -i bed.mp3 -i boom.mp3 -i whoosh.mp3 -i paper.mp3 -i stamp.mp3 -i boom.mp3 -i whoosh.mp3 -i whoosh.mp3 -filter_complex "\
[1]volume=1.0,apad[v];\
[2]volume=0.16,afade=t=out:st=10.2:d=0.6[b];\
[3]volume=0.55[i0];\
[4]adelay=2300|2300,volume=0.35[w1];\
[5]adelay=4800|4800,volume=0.6[p];\
[6]adelay=9250|9250,volume=0.6[s];\
[7]adelay=8200|8200,volume=0.35[i1];\
[8]adelay=6650|6650,volume=0.3[w2];\
[9]adelay=7980|7980,volume=0.3[w3];\
[v][b][i0][w1][p][s][i1][w2][w3]amix=inputs=9:normalize=0:duration=first,alimiter=limit=0.95,atrim=0:10.8[a]" \
 -map 0:v -map "[a]" -c:v libx264 -pix_fmt yuv420p -crf 23 -preset slow -c:a aac -b:a 192k -t 10.8 -movflags +faststart "$OUT"
