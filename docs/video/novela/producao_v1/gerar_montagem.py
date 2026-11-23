"""Gera montagem.json da V1. Os clipes do Dr. Pelicioni (Intone) têm duração própria: a linha do tempo se ajusta."""
import json, subprocess, os
def dur(p):
    return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",p],capture_output=True,text=True).stdout)
FOTO="../personagem/foto_oficial.jpg"
def dr(nome, padrao):
    p=f"planos/{nome}.mp4"
    return (p, round(dur(p),2)) if os.path.exists(p) else (None, padrao)
d46=dr("dr46",9); d55=dr("dr55",7); d66=dr("dr66",3)
S=[]; A=[]; B=[]
def seg(d, **k):
    t=S[-1]["fim"] if S else 0
    S.append(dict(t=round(t,2), fim=round(t+d,2), **k)); return t
t=seg(9,fundo="planos/f1.mp4",ini=0,vel=0.89,cartoes=[{"png":"telas/t00.png","de":0.3,"ate":3},{"png":"telas/t03.png","de":3,"ate":9,"entra":False}],
  legendas=[{"txt":"Valdir: Você nunca teve dinheiro nem pra adubo, Rosa.","de":3.0,"ate":5.9},{"txt":"Agora quem manda lá é o doutor Tavares.","de":5.9,"ate":9}])
A.append({"arq":"voz/03_valdir.mp3","t":3.0}); B+= [0.3,3.0]
t=seg(6,fundo="planos/f4.mp4",ini=0,cartoes=[{"png":"telas/t09.png","de":0.3}],
  legendas=[{"txt":"Tavares: Dona Rosa, segunda eu chego com o trator.","de":0.2,"ate":2.9},{"txt":"Paguei dois milhões à vista.","de":2.9,"ate":6}])
A.append({"arq":"voz/09_tavares.mp3","t":t+0.2}); B.append(t+0.3)
t=seg(6,fundo="planos/f3.mp4",ini=0,cartoes=[{"png":"telas/t15.png","de":1.0}],
  legendas=[{"txt":"Cleide: Livro velho do seu pai, Rosinha?","de":0.2,"ate":2.4},{"txt":"Isso não vale nada, querida. Joga no lixo.","de":2.4,"ate":6}])
A.append({"arq":"voz/15_cleide.mp3","t":t+0.2}); B.append(t+1.0)
for d,kw,b in [(6,dict(fundo="planos/f2.mp4",ini=0,cartoes=[{"png":"telas/t21.png","de":1.2}]),1.2),
               (5,dict(fundo="planos/f2.mp4",ini=4,vel=0.8,borrar=True,cartoes=[{"png":"telas/t27.png","de":0.2}]),0.2),
               (6,dict(fundo="planos/f3.mp4",ini=2,borrar=True,cartoes=[{"png":"telas/t32.png","de":0.2}]),0.2),
               (5,dict(fundo="planos/f4.mp4",ini=3,borrar=True,cartoes=[{"png":"telas/t38.png","de":0.2}]),0.2),
               (3,dict(fundo="planos/f1.mp4",ini=5,borrar=True,cartoes=[{"png":"telas/t43.png","de":0.1}]),0.1)]:
    t=seg(d,**kw); B.append(t+b)
def bloco_dr(info, voz, lei, legs):
    p,d=info
    kw=dict(fundo=p,ini=0) if p else dict(foto=FOTO)
    if lei: kw["lei"]=lei
    t=seg(d, legendas=legs, **kw)
    if p:
        wav=p.replace(".mp4",".wav")
        subprocess.run(["ffmpeg","-v","error","-y","-i",p,"-vn","-ac","2","-ar","44100",wav],check=True)
        A.append({"arq":wav,"t":t})
    else:
        A.append({"arq":voz,"t":t+0.4})
    return t,d
def L(txts, d, off=0.3):
    n=len(txts); w=[len(x.split()) for x in txts]; tot=sum(w); out=[]; c=off
    for x,k in zip(txts,w):
        e=c+(d-off-0.3)*k/tot; out.append({"txt":x,"de":round(c,2),"ate":round(e,2),"y":1230}); c=e
    return out
bloco_dr(d46,"voz/fala46.mp3",{"png":"telas/t46.png","de":1.0},
  L(["Herança ainda não dividida: irmão tem preferência.","Pelo mesmo preço, a parte fica com a família.","Está no livro do seu pai."],d46[1]))
bloco_dr(d55,"voz/fala55.mp3",{"png":"telas/t55.png","de":0.6},
  L(["E como ninguém avisou a dona Rosa,","ela tem cento e oitenta dias pra depositar o preço."],d55[1]))
t=seg(4,fundo="planos/f4.mp4",ini=4,borrar=True,cartoes=[{"png":"telas/t62.png","de":0.2}]); B.append(t+0.2)
bloco_dr(d66,"voz/fala66.mp3",None,L(["Dona Rosa, a senhora não está sozinha."],d66[1]))
seg(2.5,fundo="planos/f5.mp4",ini=5.0)
t=seg(4,fundo="planos/f1.mp4",ini=3,borrar=True,cartoes=[{"png":"telas/t71.png","de":0.2}]); B.append(t+0.2)
D=S[-1]["fim"]
json.dump({"duracao":D,"segmentos":S,"audios":A,"blips":[round(x,2) for x in B]},open("montagem.json","w"),ensure_ascii=False,indent=1)
print("duração",D)
