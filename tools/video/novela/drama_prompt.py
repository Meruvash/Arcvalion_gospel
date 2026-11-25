#!/usr/bin/env python3
"""Gerador de prompts da novela no Drama do Higgsfield (Seedance 2.5, omni_reference), no formato que deu certo na V2c.

Cópia fiel do `montar_prompts.py` da sandbox (~/films/marca-da-estrela/), mais os IDs de referência do elenco, para que
qualquer sessão nova monte os prompts sem depender da memória da conversa.

Uso típico:
    from drama_prompt import prompt, D, V, MEDIA, AUDIO, VOZ
    txt = prompt(["frame:...", "l2", "c2", "c7"], ["c2"], ["0-4 s: ...", "4-6 s: In silence, ..."])

Regras que o prompt segue (V2c, 23–24/11/2026):
- ordem das imagens: placa do quadro → folha do lugar → folhas dos personagens → folhas de objeto;
- depois as amostras de voz, com "@AudioN is the voice of @ImageM";
- um falante por plano, fala de até 10 palavras, começando entre 0,6 e 0,8 s, com 1 s ou mais de silêncio no fim;
- guia de pronúncia logo depois da fala ("He pronounces X as ...") quando a palavra for de risco;
- "No music and no score. No subtitles or on-screen text." já vai em H2.
"""

H1 = "Cinematic live action, camera-ready faces in soft, bright, flattering light from the scene's own sources, natural colour."
H2 = ("Shot like a feature film: close shots at eye level with shallow depth of field, the speaking face sharp and the room "
      "behind it soft; camera-ready faces, real skin under everyday makeup; every face fully lit and easy to read in soft, "
      "bright light from the scene's own source, the shadows open, a catchlight in the eyes; natural colour, skin warm, "
      "whites clean; in a single the face turns three-quarter, the eyes to one side of the lens; the camera locked off or "
      "pushing in slowly, moving only with someone who walks; the actors play small and real, their eyes on each other. "
      "Clean, close, quiet voices over the room's own sound; the place makes its own sounds as they happen. No music and "
      "no score. No subtitles or on-screen text.")
LANG = "Every spoken line is in Brazilian Portuguese, exactly the words in quotes; nobody speaks any other language."

# Descrições fixas (iguais às folhas). Lugares e personagens novos entram aqui com a mesma forma.
D = {
    "l1": "a small-town cattle auction ring in the São Paulo countryside: its left panel faces the wooden bleachers, its "
          "right panel faces back across the sand ring to the Auctioneer's wooden pulpit with its gavel and the black iron "
          "gate beside it",
    "c1": "Rosa, one woman of 56, shown from several angles, always in her pale cream blouse with a small pink-and-green "
          "floral print, dark hair with grey strands tied back in a low bun",
    "c2": "Cleide, one woman of 50, shown from several angles, always in her leopard-print satin blouse and big gold hoop "
          "earrings, platinum-blonde blow-dried hair, long red nails",
    "c3": "Valdir, one man of 59, shown from several angles, always in his red-and-navy plaid flannel shirt, big silver belt "
          "buckle, white cowboy hat, thick grey moustache",
    "c4": "Doutor Pelicioni, one man of 45, shown from several angles, always in his navy blazer with a navy pocket square "
          "with small white dots, light blue open-collar shirt, dark rectangular glasses, short dark beard with grey",
    "c5": "Bruna, one woman of 27, shown from several angles, always in her plain yellow t-shirt and light denim jacket, "
          "loose curly dark hair, freckles",
    "c6": "Auctioneer, one man of 55, shown from several angles, always in his white long-sleeved shirt and brown leather "
          "vest, short grey hair, trimmed grey moustache",
    "p1": "Estrela, one red-and-white spotted dairy heifer with short pale horns and a thin sisal rope halter, always with "
          "one small R-shaped hot-iron brand on the left side of her neck, the size of a palm, an old healed burn scar with "
          "rough paler hair along the letter; her hip clean spotted coat",
}
# Descrição da placa de quadro, por placa (a chave depois de "frame:" no prompt()).
FRAMES = {
    "k1@0.5": "the same cattle auction ring seen from the sand toward the wooden bleachers, a frame of this film: the "
              "bleachers, the ring fence, the buyers seated in the rows and the golden light exactly as they are",
}
V = {
    "c1": "Rosa: a warm, gentle countrywoman's alto",
    "c2": "Cleide: a husky, sly woman's voice, low register",
    "c3": "Valdir: a deep, gravelly bass",
    "c4": "Doutor Pelicioni: a calm, low baritone",
    "c6": "Auctioneer: a dry, flat baritone",
}
FEMININAS = {"c1", "c2", "c5"}

# Referências já no Higgsfield (media id ou job id de imagem). Não gerar de novo.
MEDIA = {
    "frame:k1@0.5": "50f9076d-b63d-4cac-9de1-8b55b5a5d885",  # placa da arena (job)
    "l1": "0dc112fe-2509-4425-8662-e43af14aa357",            # folha da arena de leilão (job)
    "c1": "210cf905-ecfb-46d4-8b5c-c7e21a833e74",            # Rosa
    "c2": "eab5fde7-a9a6-4c68-bb76-74e59ee8fe63",            # Cleide
    "c3": "731e554b-c8f2-4635-ae34-df2978269def",            # Valdir
    "c4": "9bed35b9-220b-4e47-9903-21aa4c37d6b2",            # Dr. Pelicioni
    "c5": "b42d33ea-da57-44f2-972d-59f94afd4135",            # Bruna
    "c6": "4d3fe191-e934-470e-9b63-faa40c6ad378",            # leiloeiro (job)
    "p1": "6c16267d-23fc-4a85-82b2-0d80ea98d4c5",            # Estrela (job)
}
# Amostras de voz (media id de áudio) usadas como audio_references.
AUDIO = {
    "c1": "6279f862-17dc-4c3e-a8a8-cbc0219c5467",
    "c2": "e79b4fd2-b6ca-4e69-924f-e02985bdde05",
    "c3": "ab13ff0c-5471-4d79-abd1-d01c449a4c09",
    "c4": "c260b885-8639-4c4f-851a-79082f03a1bb",
    "c6": "f63b90cb-6944-4b4e-adac-9058332f3c03",
}
# Vozes do Higgsfield para seed_audio (falas só de voz) e voice_change.
VOZ = {
    "c1": ("241f8d23-0c5b-4241-b8ed-b520d777ff32", "element"),  # Rosa, clone
    "c2": ("f6448975-768e-4327-b932-1b7c973d58e9", "preset"),   # Cleide, Roxie
    "c3": ("9168ddfd-c4d0-43e8-9bfd-7ad2e700c5a6", "element"),  # Valdir, clone
    "c4": ("95b656d3-17a2-4e00-aead-31e43fd9aeda", "element"),  # Dr. Pelicioni, clone do editor
    "c6": ("1ad38ba4-9cc4-4f2f-9fde-b0fefdf67ae5", "preset"),   # leiloeiro, Gideon
}
DRAMA_ADS_ID_V2C = "6a548052-726d-4157-a3bd-2a68a38f6762"


def prompt(imgs, voices, beats):
    refs = []
    for n, i in enumerate(imgs, 1):
        desc = FRAMES[i.split(":", 1)[1]] if i.startswith("frame:") else D[i]
        refs.append(f"@Image{n} is {desc}.")
    pos = {i: n for n, i in enumerate(imgs, 1)}
    au = [f"@Audio{n} is the voice of @Image{pos[v]}, {V[v]}; every line {'she' if v in FEMININAS else 'he'} speaks is "
          f"in this voice." for n, v in enumerate(voices, 1)]
    return "\n\n".join([H1, H2, " ".join(refs), " ".join(au), LANG] + beats) + "\n"


def medias(imgs, voices):
    """Lista de medias na ordem certa para o generate_video (imagens, depois vozes)."""
    return ([{"value": MEDIA[i], "role": "image_references"} for i in imgs] +
            [{"value": AUDIO[v], "role": "audio_references"} for v in voices])
