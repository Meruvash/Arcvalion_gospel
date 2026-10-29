"""Gera o conteúdo FICTÍCIO de exemplos/ (prévia de layout e testes). Nada aqui é notícia nem estudo real.

Uso: python3 exemplos/gerar.py   e depois   python3 tools/build.py --exemplo
Textos dizem que são demonstração, fontes apontam para o domínio reservado .invalid, imagens são abstratas.
"""
import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
C = AQUI / "conteudo"
F = "Texto de demonstração para conferir o layout do portal, sem descrever fato real, pessoa real ou instituição real."
CORES = [(29, 79, 145), (122, 35, 53), (44, 100, 71), (123, 84, 16), (36, 90, 107), (95, 59, 134), (143, 66, 22)]


def imagem(nome, cor, semente, w=1600, h=900):
    rnd = random.Random(semente)
    im = Image.new("RGB", (w, h), cor)
    d = ImageDraw.Draw(im, "RGBA")
    for _ in range(14):
        x, y, r = rnd.randint(-200, w), rnd.randint(-200, h), rnd.randint(120, 520)
        d.ellipse((x, y, x + r, y + r), fill=(255, 255, 255, rnd.randint(14, 40)))
    try:
        f = ImageFont.truetype("DejaVuSans-Bold.ttf", 64)
    except OSError:
        f = ImageFont.load_default()
    d.text((90, h - 140), "IMAGEM DE EXEMPLO", font=f, fill=(255, 255, 255, 230))
    (C / "imagens").mkdir(parents=True, exist_ok=True)
    im.save(C / "imagens" / nome, "JPEG", quality=82)


def fontes():
    return [{"nome": "Fonte de exemplo (domínio fictício)", "url": "https://fonte.exemplo.invalid/a", "data": "29/10/2026", "tipo": "primaria"},
            {"nome": "Outra fonte de exemplo", "url": "https://outra.exemplo.invalid/b", "data": "29/10/2026", "tipo": "secundaria"}]


def nota(i, slug, cat, selo, titulo, pontos, status="publicado", **extra):
    n = {"slug": slug, "data": f"2026-10-{29 - i % 3:02d}", "categoria": cat, "status": status, "titulo": titulo,
         "lide": "Lide de exemplo com trinta e cinco palavras ou mais, escrito apenas para testar o layout da notícia, a quebra de linha da abertura e o tamanho do texto no celular, sem descrever nenhum fato real.",
         "corpo": [F + " " + F, F], "fontes": fontes(), "imagem": {"arquivo": f"{slug}.jpg", "credito": "Imagem abstrata de exemplo", "alt": "Imagem abstrata"},
         "crivo": {"pontos": pontos, "criterios": ["Critério de exemplo (2)"]}, "selo": selo, "instituicao": "Instituição fictícia",
         "por_que_importa": "Análise de exemplo: este parágrafo existe só para mostrar como o quadro de análise aparece separado do relato dos fatos na página da notícia, sempre assinado pela redação e nunca misturado ao contexto factual.",
         "numeros": [["10", "número de exemplo", "Fonte de exemplo"], ["2026", "ano de exemplo", "Fonte de exemplo"]],
         "no_brasil": "Bloco de exemplo sobre o efeito no Brasil, com vinte e cinco palavras ou mais, para testar a faixa verde da página da notícia no layout do portal.",
         "critica": [{"fonte": "Personagem de exemplo, cargo fictício", "texto": "Posição de exemplo atribuída a uma personagem fictícia.", "citacao": False}],
         "para_quem": ["Interessa a quem quer conferir o layout"], "nao_e_para": ["Quem procura notícia real"],
         "veredito": "Opinião de exemplo com vinte palavras ou mais, só para testar o bloco Nossa opinião e o selo da notícia na página do portal.",
         "ia": {"usada": True, "uso": "demonstração"}, "revisao": {"revisor": "revisor-exemplo", "data": "2026-10-29T08:00:00-03:00"},
         "publicado_em": f"2026-10-{29 - i % 3:02d}T{8 + i:02d}:00:00-03:00"}
    n.update(extra)
    return n


def main():
    (C / "noticias").mkdir(parents=True, exist_ok=True)
    (C / "estudos").mkdir(parents=True, exist_ok=True)
    for p in list((C / "noticias").glob("*.json")) + list((C / "estudos").glob("*.json")):
        p.unlink()
    notas = [
        nota(0, "exemplo-manchete", "noticias-gospel", "Boa notícia", "Exemplo de manchete com título de tamanho real para testar a página", 9, manchete=True,
             estudos=[{"nome": "Estudo de exemplo", "estudo": "exemplo-estudo"}]),
        nota(1, "exemplo-politica", "politica-e-sociedade", "Vale acompanhar", "Exemplo de notícia de política e sociedade com título em duas linhas", 7),
        nota(2, "exemplo-familia", "familia-e-valores", "Para refletir", "Exemplo de notícia sobre família e valores para preencher a grade", 6),
        nota(3, "exemplo-economia", "economia-e-negocios", "Informativo", "Exemplo de notícia de economia e negócios para a grade do arquivo", 5),
        nota(4, "exemplo-cultura", "musica-e-cultura", "Motivo de alerta", "Exemplo de notícia de música e cultura cristã com selo de alerta", 5),
        nota(5, "exemplo-em-revisao", "eventos", "Informativo", "Exemplo de notícia em revisão que só aparece na área de prévia", 4, status="revisao"),
    ]
    for i, n in enumerate(notas):
        imagem(n["imagem"]["arquivo"], CORES[i % len(CORES)], i)
        (C / "noticias" / f"{n['data']}-{n['slug']}.json").write_text(json.dumps(n, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    estudo = {
        "slug": "exemplo-estudo", "status": "publicado", "titulo": "Estudo de exemplo", "passagem": "Exemplo 1–3", "sigla": "Ex", "livro": "Gênesis",
        "testamento": "Antigo Testamento", "genero": "Narrativa", "nivel": 1, "tempo_min": 20, "selo": "Ótimo para começar",
        "tagline": "Frase de exemplo com doze palavras ou mais para testar o topo do estudo bíblico no portal.",
        "lede": "Abertura de exemplo com quarenta palavras ou mais, escrita só para conferir o layout da página de estudo bíblico, a régua de informações, o selo e o espaçamento no celular e no computador, sem descrever nenhum conteúdo real de estudo.",
        "descricao": "Estudo bíblico de exemplo para testar o layout.",
        "imagem": {"arquivo": "exemplo-estudo.jpg", "credito": "Imagem abstrata de exemplo", "alt": "Imagem abstrata"},
        "versiculo_chave": {"texto": "Versículo de exemplo para testar o destaque.", "referencia": "Exemplo 1:1", "traducao": "tradução fictícia"},
        "estrutura": [["Primeira parte", "Exemplo 1:1-5. " + F], ["Segunda parte", "Exemplo 2:1-9. " + F], ["Terceira parte", "Exemplo 3:1-4. " + F]],
        "estrutura_resumo": "Resumo de exemplo da estrutura do texto.", "contexto": [F, F], "aplicacao": [F, F],
        "destaques": [["Ensino de exemplo um", F], ["Ensino de exemplo dois", F], ["Ensino de exemplo três", F]],
        "atencao": [["Leve", "Leitura equivocada de exemplo", F], ["Moderada", "Outra leitura equivocada", F]],
        "perfil": [["Contexto histórico", 4], ["Aplicação prática", 5], ["Profundidade teológica", 3]],
        "formatos": [["Sozinho", "Formato de exemplo.", 3], ["Em família", "Formato de exemplo.", 2], ["Em grupo", "Formato de exemplo.", 3]],
        "para_quem": ["Quem quer conferir o layout", "Quem testa o portal"], "nao_e_para": ["Quem procura estudo real"], "dica": "Dica de exemplo.",
        "traducoes": "Texto de exemplo sobre traduções.", "relacionadas": "Texto de exemplo sobre passagens relacionadas.",
        "comparacoes": [["Outro estudo de exemplo", "", "Comparação de exemplo."]], "versiculos": [["Exemplo 1:1", "Versículo de exemplo."]],
        "veredito": "Conclusão de exemplo para o bloco Para guardar.", "ficha": [["Livro", "Gênesis (exemplo)"], ["Autor", "Autor de exemplo"], ["Capítulos", "3"]],
        "fontes": [["Fonte de exemplo 1", "https://a.exemplo.invalid/", "uso de exemplo"], ["Fonte de exemplo 2", "https://b.exemplo.invalid/", "uso de exemplo"],
                   ["Fonte de exemplo 3", "https://c.exemplo.invalid/", "uso de exemplo"]],
        "consulta": "29/10/2026", "legenda": "Legenda de exemplo para o Instagram.", "cor": "#f0c24b",
        "ia": {"usada": True, "uso": "demonstração"}, "revisao": {"revisor": "revisor-exemplo", "data": "2026-10-29T08:00:00-03:00"},
        "publicado_em": "2026-10-29T07:00:00-03:00"}
    imagem("exemplo-estudo.jpg", (123, 84, 16), 99, 1200, 1200)
    (C / "estudos" / "exemplo-estudo.json").write_text(json.dumps(estudo, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    home = {"em_alta": [{"nome": "Assunto de exemplo", "motivo": "Citado em notícia de exemplo", "link": "noticias/exemplo-politica/"}],
            "campanhas": [{"nome": "Campanha de exemplo", "organizacao": "Organização fictícia", "onde": "Brasil · aberta", "situacao": "Situação de exemplo", "fonte": "Fonte fictícia, 29/10/2026", "link": "https://exemplo.invalid/"}]}
    (C / "home.json").write_text(json.dumps(home, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    agenda = {"eventos": [{"nome": "Congresso de exemplo", "inicio": "2027-03-14", "fim": "2027-03-16", "local": "Local fictício", "cidade": "Cidade de Exemplo", "uf": "EX",
                           "organizador": "Organização fictícia", "fonte": {"nome": "Página fictícia", "url": "https://evento.exemplo.invalid/"}, "confirmado": True}]}
    (C / "agenda.json").write_text(json.dumps(agenda, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for velho in ("artigos",):
        for p in (C / velho).glob("*") if (C / velho).exists() else []:
            p.unlink()
        if (C / velho).exists():
            (C / velho).rmdir()
    print(f"ok exemplos/: {len(notas)} notícias e 1 estudo fictícios")


if __name__ == "__main__":
    main()
