#!/usr/bin/env python3
"""Mede os ciclos de humilhação e virada na transcrição do modelo (docs/video/novela/FORMULAS_NOVELA.md, seção 1).
Uso: python3 tools/video/novela/medir_modelo.py transcricao.txt > medicao.json (a transcrição fica fora do repositório)."""
import re,json,sys
t=open(sys.argv[1]).read(); low=t.lower(); N=len(low); W=len(t.split())
def pos(s,start=0):
    i=low.find(s.lower(),start)
    if i<0: raise SystemExit("nao achei: "+s)
    return i
# ciclos: (nome, ancora_inicio, ancora_virada, ancora_fim)
C=[("C1 casamento errado","hundred thousand dollar surgery","married the wrong man","three more zeros"),
("C2 elevador do CEO","late on my first day","she can enter the elevator","here for an interview"),
("C3 prima no escritorio","you're born to clean","promote her to my private cleaner","promote her to my private cleaner"),
("C4 avo x neto (ironia)","miss collinsi think she's wonderful","shove every","shove every"),
("C5 ex na mansao","my dumped ex girlfriend","please comein","i'll give you my grandson"),
("C6 anel de poder","that ring looks really familiar","who dares touch her","lying all along"),
("C7 falso CEO no restaurante","my boyfriend is the ceo of cain group","who says no one protects her","take her away"),
("C8 reuniao de turma","community college graduates","my wife when did it become","all collaboration between you and kane group is terminated"),
("C9 camara de comercio","fried chicken poor people's food","that's my grandma","you made me worry"),
("C10 prima rebaixada","throw all the dirty","you and mia will swap jobs","don't test my patience"),
("C11 mae desconfia","how could he possibly fall for you","elizabeth kane","monet's water lilies"),
("C12 ex volta + revelacao final","can we start over","my wife is not someone you can mess with","chubby little boy")]
cats={"dinheiro":r"\$|dollar|million|billion|thousand|hundred",
 "insulto":r"\bpoor\b|bumpkin|bumper|loser|trash|bitch|janitor|cleaner|scavenger|pathetic|clown|maid",
 "suplica":r"spare me|i was wrong|forgive me|give me another chance|please mr",
 "protecao":r"who dares|my wife|i believe her|no one can hurt|i will protect|protect you",
 "prova":r"\bfake\b|\breal\b|authentic|counterfeit|impersonat",
 "descrenca":r"lying|lie\b|liar|don't believe|stop pretending|stop acting|make up|nonsense|dreaming"}
out=[]
prev_end=0
for nome,a,v,f in C:
    i=pos(a,prev_end-2000 if prev_end>2000 else 0); j=pos(v,i); k=max(pos(f,i),j)+len(f)
    seg=low[i:k]
    d={"ciclo":nome,"inicio_pct":round(100*i/N,1),"virada_pct":round(100*j/N,1),"fim_pct":round(100*k/N,1),
       "palavras":len(t[i:k].split()),"palavras_ate_virada":len(t[i:j].split())}
    for c,r in cats.items(): d[c]=len(re.findall(r,seg)); d[c+"_antes_virada"]=len(re.findall(r,low[i:j]))
    out.append(d); prev_end=k
print(json.dumps({"total_palavras":W,"total_caracteres":N,"ciclos":out},ensure_ascii=False,indent=1))
