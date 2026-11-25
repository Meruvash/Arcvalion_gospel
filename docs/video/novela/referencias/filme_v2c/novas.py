import json,hashlib
src=open('montar_prompts.py').read().split('C={}')[0]
exec(src)
F="50f9076d-b63d-4cac-9de1-8b55b5a5d885"; L="0dc112fe-2509-4425-8662-e43af14aa357"
M={"c1":"210cf905-ecfb-46d4-8b5c-c7e21a833e74","c2":"eab5fde7-a9a6-4c68-bb76-74e59ee8fe63","c4":"9bed35b9-220b-4e47-9903-21aa4c37d6b2","c6":"4d3fe191-e934-470e-9b63-faa40c6ad378","p1":"6c16267d-23fc-4a85-82b2-0d80ea98d4c5"}
A={"c2":"e79b4fd2-b6ca-4e69-924f-e02985bdde05","c4":"c260b885-8639-4c4f-851a-79082f03a1bb","c6":"f63b90cb-6944-4b4e-adac-9058332f3c03"}
N={}
N["n1_dr_armadilha"]=(["frame:k1@0.5","l1","c4","c6"],["c4"],[
"0-4.2 s: Medium shot in the sand ring beside the Auctioneer's wooden pulpit, the view of @Image2's right panel, the black iron gate soft behind; two people in frame: Doutor Pelicioni and the Auctioneer. Doutor Pelicioni stands at the side of the pulpit, close to it, his face turned three-quarter toward the Auctioneer, eyes on him, discreet. The Auctioneer stands behind the pulpit, the handheld microphone lowered against his chest, listening, brows level. At 0.8 s Doutor Pelicioni says, in his calm, low baritone, quiet and unhurried: \"Antes de olhar a vaca, pergunta onde ela marcou.\"",
"4.2-6 s: In silence, the Auctioneer, still behind the pulpit, gives one slow nod and raises the microphone toward his chin; Doutor Pelicioni stands still at the side of the pulpit, to the last frame."])
N["n2_leiloeiro_fora"]=(["frame:k1@0.5","l1","c6"],["c6"],[
"0-4.6 s: Medium close-up of the Auctioneer standing behind his wooden pulpit, the black iron gate soft behind him; his face turned three-quarter toward the bleachers on his right, eyes past the lens, brows lowered, mouth firm; the handheld microphone at his chin in his left hand, his right arm raised and pointing toward the iron gate. At 0.8 s he says, in his dry, flat baritone, firm and slow: \"A senhora acusou sem prova. Fora do meu leilão.\"",
"4.6-6 s: In silence, the Auctioneer stands behind the pulpit and holds his arm pointing at the gate, still, to the last frame."])
N["n3_cleide_gancho"]=(["frame:k1@0.5","l1","c2"],["c2"],[
"0-4.6 s: Medium close-up of Cleide standing just outside the open black iron gate of the ring, the gate and the sand ring of @Image2's right panel soft behind her, golden late light; she has turned back toward the ring, her face three-quarter toward the left of the lens, eyes on someone in the ring, a slow, cold smile; in her right hand she raises a black smartphone to shoulder height, its screen turned toward the ring. At 0.8 s she says, in her husky, sly voice, quiet and sweet: \"Doze mil não apaga o que eu gravei.\" She pronounces \"Doze\" as DÔ-zi, the number twelve, never \"dois\".",
"4.6-6 s: In silence, Cleide stands outside the gate and holds the phone up, the smile held, to the last frame."])
reqs=[];idx=1
for nome,(imgs,voices,beats) in N.items():
    p=prompt(imgs,voices,beats); open(nome+".txt","w").write(p)
    med=[{"value":F,"role":"image_references"},{"value":L,"role":"image_references"}]+[{"value":M[i],"role":"image_references"} for i in imgs[2:]]+[{"value":A[v],"role":"audio_references"} for v in voices]
    reqs.append({"index":idx,"params":{"model":"seedance_2_5","mode":"omni_reference","generate_audio":True,"resolution":"720p","aspect_ratio":"9:16","duration":6,"use_unlim":False,"drama_ads_id":"6a548052-726d-4157-a3bd-2a68a38f6762","medias":med,"prompt":{"ref":f"sandbox:/home/user/films/marca-da-estrela/{nome}.txt"}}})
    print(idx,nome,hashlib.sha256(p.encode()).hexdigest()[:12],len(p)); idx+=1
open("n4_anca_limpa.txt","w").write("Cinematic live action, natural golden late-afternoon light, shallow depth of field. A slow close shot in a sand cattle auction ring of @Image1, Estrela, a red-and-white spotted dairy heifer with a thin sisal rope halter: the camera begins on her hip and rump, a clean spotted coat with no brand and no mark of any kind, and glides slowly forward along her flank to the left side of her neck, where one small R-shaped old healed hot-iron brand scar shows, the size of a palm, rough paler hair along the letter. She stands calm, flicks her tail once and breathes. No people in frame. No music, no subtitles, no on-screen text.\n")
reqs.append({"index":4,"params":{"model":"seedance_2_0_mini","resolution":"720p","aspect_ratio":"9:16","duration":5,"use_unlim":False,"drama_ads_id":"6a548052-726d-4157-a3bd-2a68a38f6762","medias":[{"value":M["p1"],"role":"image_references"}],"prompt":{"ref":"sandbox:/home/user/films/marca-da-estrela/n4_anca_limpa.txt"}}})
json.dump({"requests":reqs},open("novas.json","w"),ensure_ascii=False,indent=1)
