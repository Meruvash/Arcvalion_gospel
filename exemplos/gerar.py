"""Gera o conteúdo FICTÍCIO de exemplos/ usado só na prévia de layout (python3 tools/build.py --exemplo) e nos testes.

Nada aqui é notícia: os textos dizem que são demonstração, as fontes apontam para o domínio reservado .invalid
(que não existe), as pessoas são personagens de exemplo e as imagens são abstratas, geradas aqui mesmo.
O build de exemplo sai com faixa de aviso em todas as páginas, noindex e robots.txt bloqueando tudo.
Uso: python3 exemplos/gerar.py
"""
import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
CONT = AQUI / "conteudo"
CFG = AQUI / "config"

FRASE = ("Este parágrafo é texto de demonstração, escrito só para conferir o layout do portal: tamanho de linha, "
         "espaçamento, quebra de títulos e comportamento no celular. Ele não descreve nenhum fato real, pessoa real ou instituição real.")
EDS = {"noticias-gospel": (29, 79, 145), "politica-e-sociedade": (122, 35, 53), "familia-e-valores": (44, 100, 71), "fe-e-biblia": (123, 84, 16),
       "economia-e-negocios": (36, 90, 107), "musica-e-cultura": (95, 59, 134), "eventos": (143, 66, 22)}


def imagem(nome, cor, semente):
    rnd = random.Random(semente)
    w, h = 1600, 900
    im = Image.new("RGB", (w, h), cor)
    d = ImageDraw.Draw(im, "RGBA")
    for _ in range(14):
        x, y, r = rnd.randint(-200, w), rnd.randint(-200, h), rnd.randint(120, 520)
        d.ellipse((x, y, x + r, y + r), fill=(255, 255, 255, rnd.randint(14, 40)))
    for i in range(0, w, 80):
        d.line((i, h, i + 300, 0), fill=(255, 255, 255, 10), width=2)
    try:
        f = ImageFont.truetype("DejaVuSans-Bold.ttf", 64)
    except OSError:
        f = ImageFont.load_default()
    d.rectangle((60, h - 150, 760, h - 60), fill=(0, 0, 0, 90))
    d.text((90, h - 140), "IMAGEM DE EXEMPLO", font=f, fill=(255, 255, 255, 230))
    (CONT / "imagens").mkdir(parents=True, exist_ok=True)
    im.save(CONT / "imagens" / nome, "JPEG", quality=82)


def fontes(n=2):
    return [{"nome": f"Fonte de exemplo {i + 1} (domínio fictício)", "url": f"https://fonte-{i + 1}.exemplo.invalid/documento",
             "data": "29/10/2026", "tipo": "primaria" if i == 0 else "secundaria"} for i in range(n)]


def base(slug, ed, tipo, titulo, dias_atras, hora, **extra):
    pub = f"2026-10-{29 - dias_atras:02d}T{hora}:00-03:00"
    a = {"slug": slug, "status": "publicado", "tipo": tipo, "editoria": ed, "titulo": titulo,
         "linha_fina": "Linha fina de exemplo, com o resumo da matéria em uma ou duas frases curtas para testar o layout.",
         "corpo": [FRASE, {"intertitulo": "Intertítulo de exemplo"}, FRASE, FRASE, FRASE],
         "fontes": fontes(), "autor": "autora-exemplo", "tags": ["exemplo", ed.split("-")[0]],
         "imagem": {"arquivo": f"{slug}.jpg", "credito": "Imagem abstrata de exemplo, gerada para teste", "alt": "Imagem abstrata colorida de exemplo"},
         "ia": {"usada": True, "uso": "demonstração do quadro de transparência"},
         "revisao": {"revisor": "revisor-exemplo", "data": pub}, "publicado_em": pub}
    if tipo in ("noticia", "analise"):
        a["lide"] = ("Lide de exemplo: este parágrafo de abertura existe só para testar o layout da matéria e responde, de forma fictícia, "
                     "às perguntas de quem, o quê, quando, onde e por quê.")
    a.update(extra)
    return a


def main():
    artigos = [
        base("exemplo-manchete-gospel", "noticias-gospel", "noticia", "Exemplo de manchete: título de notícia com o tamanho real de uma chamada principal", 0, "09:10",
             manchete=True, analise="Quadro de análise de exemplo: aqui a redação explicaria, separado do relato, por que o fato importa para o leitor."),
        base("exemplo-politica-congresso", "politica-e-sociedade", "noticia", "Exemplo de notícia de política com título em duas linhas no celular", 0, "08:40", destaque=True,
             corpo=[FRASE, {"citacao": "Esta é uma citação de exemplo, atribuída a uma personagem fictícia.", "autor": "Personagem de Exemplo", "cargo": "cargo fictício", "fonte": 0}, FRASE, FRASE, FRASE]),
        base("exemplo-analise-economia", "economia-e-negocios", "analise", "Exemplo de análise: como um texto interpretativo aparece rotulado", 1, "17:00", destaque=True),
        base("exemplo-opiniao", "politica-e-sociedade", "opiniao", "Exemplo de artigo de opinião assinado por colaborador", 1, "12:00",
             autor="", colaborador={"nome": "Colaborador de Exemplo", "descricao": "personagem fictício usado para testar o layout de opinião"}, imagem=None),
        base("exemplo-familia", "familia-e-valores", "noticia", "Exemplo de notícia da editoria Família e Valores", 1, "10:30"),
        base("exemplo-explica-biblia", "fe-e-biblia", "explicativo", "Exemplo de texto explicativo com perguntas frequentes e passagens citadas", 2, "08:00",
             corpo=[FRASE, {"intertitulo": "Primeira parte do exemplo"}, FRASE, FRASE, {"intertitulo": "Segunda parte do exemplo"}, FRASE, FRASE, FRASE, FRASE],
             referencias_biblicas=["Referência de exemplo 1:1", "Referência de exemplo 2:3-4"], versao_biblica="indicar aqui a tradução e a licença",
             faq=[{"pergunta": "Esta é uma pergunta de exemplo?", "resposta": "Sim. Esta resposta de exemplo existe só para testar o bloco de perguntas frequentes e os dados estruturados correspondentes."},
                  {"pergunta": "O bloco abre e fecha no celular?", "resposta": "Sim. Cada pergunta é um elemento details, que funciona sem JavaScript e com teclado, como esta resposta de demonstração mostra."}]),
        base("exemplo-cultura", "musica-e-cultura", "noticia", "Exemplo de notícia de música e cultura cristã com links de afiliado", 2, "15:20",
             afiliados=[{"texto": "Produto de exemplo", "url": "https://loja.exemplo.invalid/produto", "loja": "Loja de exemplo"}]),
        base("exemplo-evento", "eventos", "noticia", "Exemplo de notícia sobre um congresso para testar a editoria de eventos", 3, "11:00"),
        base("exemplo-patrocinado", "familia-e-valores", "patrocinado", "Exemplo de conteúdo patrocinado identificado em toda a página", 3, "09:00",
             patrocinador={"nome": "Anunciante de Exemplo", "url": "https://anunciante.exemplo.invalid/"}, fontes=[]),
        base("exemplo-corrigida", "noticias-gospel", "noticia", "Exemplo de notícia corrigida com o registro da correção", 4, "13:45",
             atualizado_em="2026-10-26T10:00:00-03:00", correcoes=[{"data": "2026-10-26", "texto": "Exemplo de correção: o número citado no segundo parágrafo foi corrigido."}]),
        base("exemplo-gospel-2", "noticias-gospel", "noticia", "Exemplo de segunda notícia gospel para preencher a faixa da editoria", 5, "16:00"),
        base("exemplo-rascunho", "eventos", "noticia", "Exemplo de rascunho que não pode aparecer no site", 0, "07:00", status="rascunho"),
    ]
    (CONT / "artigos").mkdir(parents=True, exist_ok=True)
    for velho in (CONT / "artigos").glob("*.json"):
        velho.unlink()
    for i, a in enumerate(artigos):
        if a.get("imagem"):
            imagem(a["imagem"]["arquivo"], EDS[a["editoria"]], i)
        (CONT / "artigos" / f"{a['slug']}.json").write_text(json.dumps(a, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    agenda = {"eventos": [
        {"nome": "Congresso de exemplo", "inicio": "2026-11-14", "fim": "2026-11-16", "local": "Local fictício", "cidade": "Cidade de Exemplo", "uf": "EX",
         "organizador": "Organização de exemplo", "url": "https://evento.exemplo.invalid/", "fonte": {"nome": "Página fictícia do evento", "url": "https://evento.exemplo.invalid/", "data": "29/10/2026"}, "confirmado": True},
        {"nome": "Encontro on-line de exemplo", "inicio": "2026-11-21", "online": True, "url": "https://online.exemplo.invalid/", "organizador": "Organização de exemplo",
         "fonte": {"nome": "Página fictícia", "url": "https://online.exemplo.invalid/", "data": "29/10/2026"}, "confirmado": True, "materia": "exemplo-evento"},
        {"nome": "Show de exemplo (divulgação paga)", "inicio": "2026-12-05", "local": "Arena fictícia", "cidade": "Outra Cidade", "uf": "EX", "patrocinado": True,
         "fonte": {"nome": "Página fictícia", "url": "https://show.exemplo.invalid/", "data": "29/10/2026"}, "confirmado": False},
        {"nome": "Evento que já passou (não aparece)", "inicio": "2026-10-01", "cidade": "Cidade de Exemplo", "uf": "EX",
         "fonte": {"nome": "Página fictícia", "url": "https://antigo.exemplo.invalid/", "data": "01/10/2026"}},
    ]}
    (CONT / "agenda.json").write_text(json.dumps(agenda, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    CFG.mkdir(exist_ok=True)
    equipe = {"_ajuda": "Personagens FICTÍCIOS, só para a prévia de exemplo e os testes.", "pessoas": [
        {"slug": "autora-exemplo", "nome": "Autora de Exemplo", "cargo": "Repórter (personagem fictícia)", "bio": "Personagem fictícia usada para testar a página de autor e a assinatura das matérias.", "revisor": False},
        {"slug": "revisor-exemplo", "nome": "Revisor de Exemplo", "cargo": "Editor (personagem fictício)", "bio": "Personagem fictício usado para testar o fluxo de revisão humana.", "revisor": True}]}
    (CFG / "equipe.json").write_text(json.dumps(equipe, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"ok exemplos/: {len(artigos)} matérias fictícias, {len(agenda['eventos'])} eventos, 2 personagens")


if __name__ == "__main__":
    main()
