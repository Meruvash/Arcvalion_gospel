#!/usr/bin/env python3
"""Telas de conversa da novela (design próprio, sem logo nem marca de aplicativo), em 1080×1920.

Uso: python3 tools/video/novela/telas_chat.py estados.json pasta_saida
- Gera um HTML por estado e captura um PNG com o Playwright (Node, já instalado).
- estados.json: lista de {"id", "tipo": "chat|chamada|cartao|parte2", ...}. Ver docs/video/novela/producao_v1/estados.json.

Regras (docs/video/novela/ELENCO_FIXO.md e CLAUDE.md):
- personagens fictícios;
- faixa fixa "DRAMATIZAÇÃO";
- cores próprias, sem o verde nem o desenho de nenhum aplicativo real;
- o Dr. Pelicioni só aparece com a foto real dele.
"""
import html, json, os, subprocess, sys, base64

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
FOTO_DR = os.path.join(RAIZ, "docs/video/novela/personagem/avatar_whatsapp.jpg")
COR = {"Rosa": "#e58fa8", "Valdir": "#a0742a", "Cleide": "#c62828", "Tavares": "#7d8794", "Bruna": "#e0b400",
       "Antônio": "#8d7b5e", "Zuleide": "#9575cd", "Dr. Pelicioni": "#16324f"}

def b64(p):
    return "data:image/jpeg;base64," + base64.b64encode(open(p, "rb").read()).decode()

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{width:1080px;height:1920px;font-family:'Segoe UI',Roboto,Arial,sans-serif;background:#efe6da;overflow:hidden;position:relative}
.drama{position:absolute;top:0;left:0;right:0;height:56px;background:#0b1a2a;color:#fff;font-size:26px;letter-spacing:3px;
 display:flex;align-items:center;justify-content:center;z-index:5;font-weight:600}
.top{position:absolute;top:56px;left:0;right:0;height:150px;background:#16324f;color:#fff;display:flex;align-items:center;padding:0 36px;gap:26px}
.top .av{width:96px;height:96px}
.top .nm{font-size:44px;font-weight:700}
.top .sub{font-size:28px;opacity:.85;margin-top:4px}
.av{border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:40px;flex:none;
 background-size:cover;background-position:center}
.fundo{position:absolute;top:206px;left:0;right:0;bottom:150px;padding:30px 34px;display:flex;flex-direction:column;justify-content:flex-end;gap:22px;
 background-image:radial-gradient(#e3d7c6 2px,transparent 2px);background-size:36px 36px}
.linha{display:flex;gap:16px;align-items:flex-end}
.linha.eu{justify-content:flex-end}
.linha .av{width:70px;height:70px;font-size:30px}
.bal{max-width:800px;background:#fff;border-radius:28px;padding:20px 28px 14px;font-size:42px;line-height:1.28;color:#111;
 box-shadow:0 2px 3px rgba(0,0,0,.12)}
.eu .bal{background:#d6e8ff}
.quem{font-size:30px;font-weight:700;margin-bottom:6px}
.hora{font-size:24px;color:#6b6b6b;text-align:right;margin-top:6px}
.lido{color:#2f7de1;font-weight:700}
.sis{align-self:center;background:#fbf3d0;color:#4a4a4a;font-size:32px;border-radius:20px;padding:12px 26px}
.apag{font-style:italic;color:#777}
.reac{display:inline-block;background:#fff;border-radius:30px;padding:2px 12px;font-size:36px;margin:-10px 0 0 90px;box-shadow:0 1px 2px rgba(0,0,0,.2)}
.audio{display:flex;align-items:center;gap:22px;min-width:640px}
.play{width:0;height:0;border-left:38px solid #16324f;border-top:24px solid transparent;border-bottom:24px solid transparent}
.onda{display:flex;gap:6px;align-items:center;height:60px}
.onda i{display:block;width:8px;background:#7a8ea3;border-radius:4px}
.dur{font-size:28px;color:#555}
.foto{width:620px;height:520px;border-radius:18px;display:flex;align-items:center;justify-content:center;text-align:center;
 background:linear-gradient(135deg,#7a5c3a,#c9a36b);color:#fff;font-size:30px;padding:30px;background-size:cover;background-position:center}
.dig{font-size:32px;color:#555;font-style:italic;padding-left:10px}
.base{position:absolute;bottom:0;left:0;right:0;height:150px;background:#f7f2eb;display:flex;align-items:center;padding:0 30px;gap:20px}
.base .cx{flex:1;height:90px;border-radius:45px;background:#fff;color:#999;font-size:34px;display:flex;align-items:center;padding:0 34px}
.base .bt{width:90px;height:90px;border-radius:50%;background:#16324f}
/* chamada de vídeo */
.cham{position:absolute;inset:0;background:#0b1a2a;color:#fff}
.cham .foto-dr{position:absolute;top:56px;left:0;right:0;height:1300px;background-size:cover;background-position:center 20%}
.cham .nome{position:absolute;top:110px;left:0;right:0;text-align:center;font-size:46px;font-weight:700;text-shadow:0 2px 8px #000}
.cham .tempo{position:absolute;top:172px;left:0;right:0;text-align:center;font-size:30px;text-shadow:0 2px 8px #000}
.cartao{position:absolute;left:50px;right:50px;bottom:120px;background:#fffdf6;color:#1b1b1b;border-radius:26px;padding:40px 44px;
 border-left:16px solid #16324f;box-shadow:0 8px 30px rgba(0,0,0,.45)}
.cartao .lei{font-size:32px;font-weight:800;color:#16324f;letter-spacing:1px}
.cartao .txt{font-size:38px;line-height:1.35;margin-top:16px;font-family:Georgia,'Times New Roman',serif}
.cartao .fonte{font-size:24px;color:#666;margin-top:18px}
.parte2{position:absolute;left:0;right:0;bottom:330px;text-align:center;font-size:120px;font-weight:900;color:#ffd400;
 text-shadow:0 6px 20px rgba(0,0,0,.6);letter-spacing:6px}
.congela{position:absolute;inset:0;background:rgba(10,20,35,.35)}
"""

def av(nome, tam=""):
    if nome == "Dr. Pelicioni":
        return f'<div class="av" style="background-image:url({b64(FOTO_DR)})"></div>'
    ini = nome.split()[0][0]
    return f'<div class="av" style="background:{COR.get(nome, "#555")}">{ini}</div>'

def onda(seg):
    import random
    random.seed(seg)
    return "".join(f'<i style="height:{random.randint(14, 58)}px"></i>' for _ in range(28))

def msg(m):
    tipo = m.get("tipo", "texto")
    if tipo == "sistema":
        return f'<div class="sis">{html.escape(m["texto"])}</div>'
    eu = m.get("eu", False)
    quem = m.get("quem", "")
    cab = "" if eu or m.get("sem_nome") else f'<div class="quem" style="color:{COR.get(quem, "#333")}">{html.escape(quem)}</div>'
    hora = f'{m.get("hora", "14:32")}' + (' <span class="lido">✓✓</span>' if eu else "")
    if tipo == "audio":
        corpo = f'<div class="audio"><div class="play"></div><div class="onda">{onda(m.get("seg", 6))}</div><div class="dur">0:{m.get("seg", 6):02d}</div></div>'
    elif tipo == "foto":
        st = f' style="background-image:url({b64(m["img"])})"' if m.get("img") and os.path.exists(m["img"]) else ""
        corpo = f'<div class="foto"{st}>{"" if st else html.escape(m.get("rotulo", "foto"))}</div>'
        if m.get("legenda"):
            corpo += f'<div style="margin-top:10px">{html.escape(m["legenda"])}</div>'
    elif tipo == "apagada":
        corpo = '<div class="apag">🚫 Esta mensagem foi apagada</div>'
    else:
        corpo = html.escape(m["texto"])
    lado = "" if eu else av(quem)
    reac = f'<div class="reac">{m["reacao"]}</div>' if m.get("reacao") else ""
    return f'<div><div class="linha{" eu" if eu else ""}">{lado}<div class="bal">{cab}{corpo}<div class="hora">{hora}</div></div></div>{reac}</div>'

def pagina(e):
    if e["tipo"] == "chat":
        top_av = av(e["contato_av"]) if e.get("contato_av") else '<div class="av" style="background:#4b6b8c">👥</div>'
        corpo = (f'<div class="top">{top_av}<div><div class="nm">{html.escape(e["titulo"])}</div>'
                 f'<div class="sub">{html.escape(e.get("sub", ""))}</div></div></div>'
                 f'<div class="fundo">{"".join(msg(m) for m in e["msgs"])}'
                 + (f'<div class="dig">{html.escape(e["digitando"])}</div>' if e.get("digitando") else "") + '</div>'
                 + '<div class="base"><div class="cx">Mensagem</div><div class="bt"></div></div>')
    elif e["tipo"] == "chamada":
        cart = ""
        if e.get("lei"):
            cart = (f'<div class="cartao"><div class="lei">{html.escape(e["lei"])}</div>'
                    f'<div class="txt">“{html.escape(e["texto_lei"])}”</div><div class="fonte">{html.escape(e["fonte"])}</div></div>')
        corpo = (f'<div class="cham"><div class="foto-dr" style="background-image:url({b64(FOTO_DR)})"></div>'
                 f'<div class="nome">Dr. Pelicioni</div><div class="tempo">{e.get("tempo", "00:12")}</div>{cart}</div>')
    else:
        raise ValueError(e["tipo"])
    extra = '<div class="congela"></div><div class="parte2">PARTE 2</div>' if e.get("parte2") else ""
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body><div class="drama">DRAMATIZAÇÃO · PERSONAGENS FICTÍCIOS</div>{corpo}{extra}</body></html>'

def main():
    estados, saida = json.load(open(sys.argv[1], encoding="utf-8")), os.path.abspath(sys.argv[2])
    os.makedirs(saida, exist_ok=True)
    base = os.path.dirname(os.path.abspath(sys.argv[1]))
    for e in estados:
        for m in e.get("msgs", []):
            if m.get("img"):
                m["img"] = os.path.join(base, m["img"])
        open(os.path.join(saida, f'{e["id"]}.html'), "w", encoding="utf-8").write(pagina(e))
    js = """const {chromium}=require('playwright');const fs=require('fs'),path=require('path');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
const d=process.argv[2];for(const f of fs.readdirSync(d).filter(x=>x.endsWith('.html')).sort()){
await p.goto('file://'+path.resolve(d,f));await p.waitForTimeout(150);await p.screenshot({path:path.resolve(d,f.replace('.html','.png'))});}
await b.close();})();"""
    jsf = os.path.join(saida, "_cap.cjs"); open(jsf, "w").write(js)
    subprocess.run(["node", jsf, saida], check=True, cwd="/tmp")
    os.remove(jsf)
    for f in os.listdir(saida):
        if f.endswith(".html"):
            os.remove(os.path.join(saida, f))
    print("telas:", sorted(f for f in os.listdir(saida) if f.endswith(".png")))

if __name__ == "__main__":
    main()
