"""Trilha original instrumental para os vídeos do agro (ElevenLabs Music), em estilos da música caipira.
Padrões e fontes: docs/video/TRILHA_AGRO.md. Nunca ponha nome de artista, dupla, música ou álbum no prompt (Music Terms 2.1).

Uso: python3 gerar_trilha.py saida.mp3 [duracao_ms] [--estilo agronejo|catira|toada|pagode|guarania]
Padrão do editor (12/11/2026): agronejo; alternativa aprovada: catira. Alterne os dois entre vídeos seguidos.
Depois confira que não há voz cantada (o speech-to-text deve achar 0 palavras) e misture com volume ~0,15 sob a narração."""
import json, sys, time, urllib.request, urllib.error

COMUM = ("Instrumental only, no vocals, no choir, no humming. Mixed as a voice-over underscore: sparse and quiet while the "
         "narrator speaks, no busy solos under the voice. Structure: a short solo viola caipira intro of about 2 seconds, a soft "
         "steady accompaniment through the middle, short viola fills only in the gaps, and a clear resolved final phrase on the "
         "last 4 seconds. Do not imitate any existing song.")
ESTILOS = {
    # toada caipira: lenta, binária, reflexiva (padrão do vídeo "Cinco por dia")
    "toada": ("Original Brazilian 'música caipira' instrumental in a slow 'toada' feel, 80 BPM, D major. Lead: viola caipira "
              "(10-string Brazilian guitar in pairs, open tuning, fingerpicked) playing a gentle melody harmonized in parallel thirds; "
              "nylon acoustic guitar keeping a soft binary accompaniment; warm accordion pads in thirds from the second half; light "
              "upright bass. Reflective, nostalgic, countryside at dusk, ending hopeful."),
    # pagode de viola: binário, violão acentuando o contratempo, viola com frases vigorosas nas introduções e interlúdios
    "pagode": ("Original Brazilian 'pagode de viola' instrumental, 96 BPM, E major, binary meter. Steel-string acoustic guitar playing "
               "a constant off-beat accent on the weak part of each beat; viola caipira (10-string, open tuning, fingers) with muted "
               "strums on the first beat and vigorous fast ornamented runs (slides, hammer-ons, pull-offs) only in the intro and the "
               "breaks; electric-free, acoustic; light bass. Firm, energetic, a sense of urgency that resolves into relief."),
    # guarânia: ternário, lenta, emotiva
    "guarania": ("Original Brazilian countryside 'guarânia' instrumental in slow triple meter (3/4), 72 BPM, A minor moving to C major "
                 "at the end. Nylon guitar arpeggios in 3, viola caipira melody in parallel thirds with a second guitar, a sad "
                 "accordion countermelody, soft bass on the downbeat. Emotional, longing, dignified, never melodramatic; the last "
                 "phrase turns to major and resolves with hope."),
    # catira / cateretê: palmas e sapateado, viola rasqueada, festa
    "catira": ("Original Brazilian 'catira' (cateretê) instrumental, 112 BPM, G major, binary. Viola caipira strummed ('rasqueado') "
               "with short bright melodic hooks in thirds, rhythmic hand claps and wooden foot-stomp percussion, acoustic guitar, "
               "accordion stabs, upright bass. Festive, proud, sunny harvest celebration; keep the claps soft under the narration."),
    # sertanejo moderno leve, sem bateria pesada
    "agronejo": ("Original modern Brazilian sertanejo instrumental, light and acoustic, 92 BPM, D major. Steel-string acoustic guitar "
                 "strumming, viola caipira melodic hook, warm accordion, soft cajón and shaker instead of a drum kit, subtle bass. "
                 "Optimistic, young, open-sky countryside feeling; no electric guitar solos, no heavy drums."),
}

args = [a for a in sys.argv[1:] if not a.startswith("--")]
estilo = sys.argv[sys.argv.index("--estilo") + 1] if "--estilo" in sys.argv else "agronejo"   # preferido do editor (12/11/2026)
if estilo in args: args.remove(estilo)
if estilo not in ESTILOS: raise SystemExit(f"estilo desconhecido: {estilo}; use um de {', '.join(ESTILOS)}")
out = args[0]; ms = int(args[1]) if len(args) > 1 else 62000
body = json.dumps({"prompt": ESTILOS[estilo] + " " + COMUM, "music_length_ms": ms, "model_id": "music_v1"}).encode()
feito = False
for i, wait in enumerate([0, 20, 40, 80, 120, 180]):
    time.sleep(wait)
    req = urllib.request.Request("https://api.elevenlabs.io/v1/music?output_format=mp3_44100_128", body, {"xi-api-key": "dummy", "Content-Type": "application/json"})
    try:
        dados = urllib.request.urlopen(req, timeout=600).read()     # lê tudo antes de tocar no arquivo de saída
    except urllib.error.HTTPError as e:
        msg = e.read()[:400].decode("utf-8", "replace")
        print("tentativa", i + 1, "HTTP", e.code, msg)   # 429 = serviço ocupado: tenta de novo; bad_prompt traz sugestão
        if e.code not in (429, 500, 502, 503): break
        continue
    if not dados: print("tentativa", i + 1, "resposta vazia"); continue
    open(out, "wb").write(dados); print("ok", estilo, out); feito = True; break
if not feito: raise SystemExit(f"falhou: nenhuma trilha gerada; {out} não foi alterado")
