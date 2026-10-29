"""Gera as peças da marca a partir de config/portal.json: favicon.svg, logo-512.png, logo-180.png e capa.png (1200×630).

Uso: python3 tools/gerar_marca.py   (rode de novo sempre que trocar o nome ou o slogan do portal; precisa de Node + Playwright)
O símbolo (livro aberto com uma cruz) é desenho próprio e genérico, definido em tools/layout.py (SIMBOLO).
A saída vai para assets/marca/, que o build copia para publico/marca/.
"""
import html
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import portal  # noqa: E402
from layout import SIMBOLO  # noqa: E402

DEST = portal.ROOT / "assets" / "marca"


def main():
    portal.iniciar()
    DEST.mkdir(parents=True, exist_ok=True)
    svg = SIMBOLO.replace(' class="simbolo"', ' xmlns="http://www.w3.org/2000/svg"').replace(' aria-hidden="true"', "")
    (DEST / "favicon.svg").write_text(svg + "\n", encoding="utf-8")
    uri = lambda p: Path(p).resolve().as_uri()  # noqa: E731
    fontes = (f'@font-face{{font-family:SS;src:url({uri(portal.ROOT / "assets/fontes/source-serif-4-700.woff2")})}}'
              f'@font-face{{font-family:PS;src:url({uri(portal.ROOT / "assets/fontes/public-sans.woff2")});font-weight:400 800}}')
    logo = f'<!doctype html><html><head><meta charset="utf-8"><style>*{{margin:0}}body{{width:%dpx;height:%dpx}}svg{{width:100%%;height:100%%;display:block}}</style></head><body>{svg}</body></html>'
    nome, slogan = html.escape(portal.NOME), html.escape(portal.CFG.get("slogan", ""))
    capa = (f'<!doctype html><html><head><meta charset="utf-8"><style>{fontes}*{{margin:0;box-sizing:border-box}}'
            'body{width:1200px;height:630px;background:radial-gradient(circle at 78% 30%,#1f4272 0,#12294a 62%);color:#fff;font-family:PS,sans-serif;'
            'display:flex;align-items:center;gap:56px;padding:0 90px;border-bottom:14px solid #d6b25e}'
            'svg{width:230px;height:230px;flex:none;border-radius:40px;box-shadow:0 18px 50px rgba(0,0,0,.35)}'
            'h1{font-family:SS,Georgia,serif;font-size:92px;line-height:1;letter-spacing:-.02em}p{margin-top:22px;font-size:34px;color:#d5dde9;max-width:640px}'
            f'</style></head><body>{svg}<div><h1>{nome}</h1><p>{slogan}</p></div></body></html>')
    with tempfile.TemporaryDirectory() as tmp:
        tarefas = []
        for nome_arq, w, h, pag in (("logo-512.png", 512, 512, logo % (512, 512)), ("logo-180.png", 180, 180, logo % (180, 180)), ("capa.png", 1200, 630, capa)):
            a = Path(tmp) / f"{nome_arq}.html"
            a.write_text(pag, encoding="utf-8")
            tarefas.append({"html": str(a), "saida": str(DEST / nome_arq), "w": w, "h": h})
        lista = Path(tmp) / "t.json"
        lista.write_text(json.dumps(tarefas), encoding="utf-8")
        js = """const {chromium}=require('playwright');const fs=require('fs');(async()=>{const t=JSON.parse(fs.readFileSync(process.argv[1],'utf8'));
const b=await chromium.launch();for(const x of t){const p=await b.newPage({viewport:{width:x.w,height:x.h}});await p.goto('file://'+x.html);
await p.evaluate(()=>document.fonts.ready);await p.screenshot({path:x.saida,type:'png'});await p.close()}await b.close()})()"""
        r = subprocess.run(["node", "-e", js, str(lista)], cwd=portal.ROOT, capture_output=True, text=True)
        if r.returncode:
            sys.exit("Falhou (precisa de Node + Playwright): " + (r.stderr or r.stdout)[-400:])
    print("ok assets/marca/: favicon.svg, logo-512.png, logo-180.png, capa.png")


if __name__ == "__main__":
    main()
