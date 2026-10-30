"""Testes do portal no formato do Elite: padrão das notícias e dos estudos, build, prévia de revisão, SEO e isolamento.

Uso: python3 -m unittest discover -s tests -v
"""
import copy
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "tools"))
import portal  # noqa: E402
from noticias.checar_noticia import checar_dia, problemas as p_nota  # noqa: E402
from estudos.checar_estudo import problemas as p_estudo  # noqa: E402
from discipulado.legibilidade import META_ALUNO, analisar, falhas  # noqa: E402

EX = RAIZ / "exemplos" / "conteudo"


def rodar(*args, env=None):
    return subprocess.run([sys.executable, *args], cwd=RAIZ, capture_output=True, text=True, env=env)


def ler(rel):
    return json.loads((EX / rel).read_text(encoding="utf-8"))


class Noticias(unittest.TestCase):
    def setUp(self):
        portal.iniciar(conteudo=EX, config=RAIZ / "exemplos" / "config", exemplo=True)
        self.n = ler("noticias/2026-10-29-exemplo-manchete.json")

    def erros(self, **mud):
        a = copy.deepcopy(self.n)
        for k, v in mud.items():
            a.pop(k, None) if v is None else a.__setitem__(k, v)
        return " | ".join(p_nota(a, publicar=True))

    def test_exemplo_passa(self):
        self.assertEqual(self.erros(), "")

    def test_revisao_humana(self):
        self.assertIn("revisão humana", self.erros(revisao=None))
        self.assertIn("ia:", self.erros(ia=None))

    def test_fontes(self):
        self.assertIn("pelo menos 2", self.erros(fontes=self.n["fontes"][:1]))
        self.assertIn("primária", self.erros(fontes=[dict(f, tipo="secundaria") for f in self.n["fontes"]]))

    def test_texto(self):
        self.assertIn("caça-clique", self.erros(titulo="Você não vai acreditar no que aconteceu com a igreja nesta semana no Brasil"))
        self.assertIn("não identificável", self.erros(corpo=[self.n["corpo"][0] + " Segundo fontes, haverá mudança."]))
        self.assertIn("loja", self.erros(corpo=[self.n["corpo"][0] + " Está à venda na Amazon."]))
        self.assertIn("selo inválido", self.erros(selo="Vale a compra"))
        self.assertIn("categoria inexistente", self.erros(categoria="jogos"))

    def test_foto_obrigatoria(self):
        self.assertIn("sem foto", self.erros(imagem=None))

    def test_manchete_maior_pontuacao(self):
        a, b = copy.deepcopy(self.n), copy.deepcopy(self.n)
        a["crivo"]["pontos"], b["crivo"]["pontos"], b["manchete"] = 9, 3, True
        a["manchete"] = False
        self.assertTrue(checar_dia([a, b]))

    def crivo100(self, impacto=25, afinidade=20, atualidade=17, comprovacao=13, originalidade=5, **mud):
        """Crivo de 0 a 100 (config/relevancia.json) de uma nota fictícia de depois da vigência."""
        pts = {"impacto": impacto, "afinidade": afinidade, "atualidade": atualidade, "comprovacao": comprovacao, "originalidade": originalidade}
        c = {"escala": 100, "pontos": sum(pts.values()), "trilha": "quente", "abrangencia": "nacional",
             "origem": {"nome": "Exemplo", "url": "https://example.org/"},
             "tema": {"eixo": "familia", "porque": "fato fictício de teste sobre proteção de crianças na família"},
             "publico": {"pontos": 7, "eixos": {"valor": 5, "viral": 1, "cristao": 1},
                         "criterios": ["Documento primário (2)", "Ato de poder (2)", "Duas fontes independentes (1)", "Utilidade (1)", "Pede resposta do cristão (1)"]},
             "criterios": {k: {"pontos": v, "porque": "fato fictício de teste com efeito concreto descrito"} for k, v in pts.items()}}
        c.update(mud)
        return c

    def test_crivo_de_cem_pontos(self):
        dia = "2026-11-02"
        erros = lambda c: self.erros(crivo=c, data=dia)  # noqa: E731
        self.assertEqual(erros(self.crivo100()), "")  # 80: alta relevância
        self.assertIn("soma dos critérios", erros(self.crivo100(pontos=81)))
        self.assertIn("de 0 a 30", erros(self.crivo100(impacto=31)))
        sem_porque = self.crivo100()
        sem_porque["criterios"]["impacto"]["porque"] = "importante"
        self.assertIn("justifique Impacto público", erros(sem_porque))
        # declaração sem consequência, de outro país: baixa prioridade, não entra
        self.assertIn("abaixo do corte de 60", erros(self.crivo100(impacto=2, afinidade=12, atualidade=13, comprovacao=12, originalidade=5)))
        # pontuação alta não substitui verificação: só uma reportagem, sem confirmação
        self.assertIn("comprovação 5", erros(self.crivo100(impacto=30, afinidade=25, atualidade=20, comprovacao=5, originalidade=10)))
        self.assertIn("motor de 0 a 100", erros({"pontos": 15, "eixos": {"valor": 6, "viral": 5, "cristao": 4}}))
        self.assertIn("trilha", erros(self.crivo100(trilha="morna")))
        # eliminatório 10: notícia de cidade sem eixo temático não entra, por mais pontos que tenha
        self.assertIn("eliminatório 10", erros(self.crivo100(tema=None)))
        self.assertIn("eliminatório 10", erros(self.crivo100(tema={"eixo": "cidade", "porque": "parque depredado em Porto Velho dias depois"})))
        self.assertIn("tema.porque", erros(self.crivo100(tema={"eixo": "familia", "porque": "versículo cabe"})))
        # a página mostra o crivo de até 20 pontos (crivo.publico), não o motor
        self.assertIn("'publico'", erros(self.crivo100(publico=None)))
        torto = self.crivo100()
        torto["publico"] = dict(torto["publico"], pontos=9)
        self.assertIn("somam 7", erros(torto))
        self.assertEqual(self.erros(crivo={"pontos": 5}), "")  # nota de antes da vigência mantém o crivo antigo

    def test_manchete_do_motor(self):
        a, b = copy.deepcopy(self.n), copy.deepcopy(self.n)
        for x in (a, b):
            x["data"] = "2026-11-02"
        a["crivo"], b["crivo"] = self.crivo100(), self.crivo100(impacto=5, afinidade=20, atualidade=17, comprovacao=13, originalidade=8)
        a["manchete"], b["manchete"] = False, True
        self.assertIn("maior pontuação", " ".join(checar_dia([a, b])))
        a["manchete"], b["manchete"] = True, False
        self.assertEqual(checar_dia([a, b]), [])
        a["crivo"] = self.crivo100(impacto=15, afinidade=15, atualidade=17, comprovacao=13, originalidade=5)  # 65
        b["crivo"] = self.crivo100(impacto=10, afinidade=15, atualidade=17, comprovacao=13, originalidade=5)
        self.assertIn("70 pontos", " ".join(checar_dia([a, b])))

    def test_pesos_configuraveis(self):
        from noticias.checar_noticia import checar_config, faixa
        self.assertEqual(checar_config(portal.RELEVANCIA), [])
        torto = copy.deepcopy(portal.RELEVANCIA)
        torto["criterios"][0]["peso"] = 40
        self.assertIn("somam 110", checar_config(torto)[0])
        self.assertEqual([faixa(p) for p in (90, 77, 55, 30)], ["prioridade máxima", "alta relevância", "relevância moderada", "baixa prioridade"])

    def test_fonte_local(self):
        loc = lambda d: {"nome": d, "url": f"https://{d}/noticia/x", "data": "30/10/2026", "tipo": "reportagem_local"}  # noqa: E731
        crivo = dict(self.n["crivo"], abrangencia="porto-velho")
        self.assertNotIn("primária", self.erros(fontes=[loc("rondoniaovivo.com"), loc("rondoniagora.com")], crivo=crivo))
        self.assertIn("primária", self.erros(fontes=[loc("rondoniaovivo.com"), loc("www.rondoniaovivo.com")], crivo=crivo))
        self.assertIn("primária", self.erros(fontes=[loc("rondoniaovivo.com"), loc("rondoniagora.com")]))  # nacional: não vale

    def test_crivo_juridico(self):
        self.assertIn("risco jurídico", self.erros(veredito="O relator é um mentiroso e o projeto, uma farsa de quem quer aparecer na foto."))
        self.assertIn("checagem_juridica", self.erros(checagem_juridica=None))
        self.assertNotIn("risco jurídico", self.erros(veredito="A prefeitura pede que ninguém use fogo para eliminar lixo e que todos economizem água nesta seca."))

    def test_versiculo_fora_da_opiniao(self):
        meio = "A gente apoia a medida. “Tive sede, e destes-me de beber” (Mateus 25.35, ARC). Vale cobrar o prazo da prefeitura."
        self.assertIn("veredito com versículo", self.erros(veredito=meio))
        verso = {"texto": "Tive sede, e destes-me de beber", "referencia": "Mateus 25.35", "traducao": "ARC"}
        self.assertEqual(self.erros(versiculo=verso), "")
        self.assertIn("versiculo:", self.erros(versiculo=dict(verso, referencia="Mateus")))
        self.assertIn("tradução", self.erros(versiculo=dict(verso, traducao="")))

    def test_opiniao_forte_dois_de_cinco(self):
        dia = []
        for i in range(5):
            n = copy.deepcopy(self.n)
            n["manchete"], n["crivo"]["pontos"], n["opiniao_forte"] = i == 0, 9 - i, i < 1
            dia.append(n)
        self.assertTrue(any("Opinião Forte" in e for e in checar_dia(dia)))
        dia[1]["opiniao_forte"] = True
        self.assertEqual(checar_dia(dia), [])


class Estudos(unittest.TestCase):
    def setUp(self):
        portal.iniciar(conteudo=EX, config=RAIZ / "exemplos" / "config", exemplo=True)
        self.c = ler("estudos/exemplo-estudo.json")

    def test_exemplo_passa(self):
        self.assertEqual(p_estudo(self.c, publicar=True), [])

    def test_versiculo_com_traducao(self):
        c = copy.deepcopy(self.c)
        c["versiculo_chave"].pop("traducao")
        self.assertTrue(any("tradução" in x for x in p_estudo(c, publicar=True)))

    def test_estudo_de_passagem(self):
        c = copy.deepcopy(self.c)
        c["tipo"] = "passagem"
        c["vozes"] = c["posicoes"][0]["teologos"]
        for k in ("posicoes", "convergencias", "questao"):
            c.pop(k, None)
        self.assertEqual(p_estudo(c, publicar=True), [])
        c["vozes"] = c["vozes"][:1]
        self.assertTrue(any("vozes" in x for x in p_estudo(c, publicar=True)))

    def test_estrutura_com_referencia(self):
        c = copy.deepcopy(self.c)
        c["estrutura"][0] = ["Sem referência", "texto sem a passagem indicada"]
        self.assertTrue(any("referência" in x for x in p_estudo(c, publicar=True)))


def copia_do_site(exemplos=False):
    """Cópia temporária do repositório para rodar o build do Elite (tools/build_home.py) sem mexer na raiz.

    Com exemplos=True, troca as notícias e os estudos pelos FICTÍCIOS de exemplos/ (uma publicada por revisor-exemplo e uma em
    revisão) e a equipe pela de exemplos/config: serve só para testar a página de nota publicada."""
    tmp = Path(tempfile.mkdtemp()) / "site"
    lixo = shutil.ignore_patterns(".git", "node_modules", ".cache", "__pycache__", "_site", "publico*")
    shutil.copytree(RAIZ, tmp, ignore=lixo)
    if exemplos:
        for p in (tmp / "conteudo" / "noticias").glob("*.json"):
            p.unlink()
        for p in (EX / "noticias").glob("*.json"):
            shutil.copy(p, tmp / "conteudo" / "noticias" / p.name)
        for p in (EX / "imagens").glob("*.jpg"):
            shutil.copy(p, tmp / "noticias" / p.name)
        for p in (tmp / "conteudo" / "estudos").glob("*.json"):
            p.unlink()
        for p in (EX / "estudos").glob("*.json"):
            shutil.copy(p, tmp / "conteudo" / "estudos" / p.name)
        shutil.copy(EX / "imagens" / "exemplo-estudo.jpg", tmp / "conteudo" / "imagens" / "exemplo-estudo.jpg")
        for d in (tmp / "conteudo" / "discipulado").glob("[0-9][0-9]-*"):  # lições reais têm revisor da equipe real
            shutil.rmtree(d)
        shutil.copy(RAIZ / "exemplos" / "config" / "equipe.json", tmp / "config" / "equipe.json")
    r = subprocess.run([sys.executable, "tools/build_home.py"], cwd=tmp, capture_output=True, text=True)
    if r.returncode:
        raise AssertionError(r.stdout + r.stderr)
    return tmp


class Discipulado(unittest.TestCase):
    """Medidor de legibilidade da coleção e conversão do Markdown das lições."""

    def test_texto_simples_passa(self):
        t = ("Deus se tornou gente. Ele não parou de ser Deus. Mas passou a ter fome, a sentir frio e a cansar como a gente. "
             "João conta isso no começo do seu livro. A Palavra se tornou um ser humano e morou entre nós. Os cristãos chamam isso de encarnação.\n\n") * 3
        self.assertEqual(falhas(analisar(t, META_ALUNO), META_ALUNO), [])

    def test_frase_longa_e_travessao_reprovam(self):
        t = ("A doutrina da encarnação, fundamental para a cristologia ortodoxa, afirma que o Verbo eterno assumiu a natureza humana "
             "sem prejuízo de sua divindade, conforme o testemunho apostólico registrado no prólogo joanino e confirmado pela igreja — sempre.")
        f = falhas(analisar(t, META_ALUNO), META_ALUNO)
        self.assertTrue(any("frase" in x for x in f) and any("travessão" in x for x in f), f)

    def test_markdown(self):
        from build_discipulado import markdown, secoes
        h = markdown("### Sub\n\nUm **forte** e *leve*.\n\n> Texto\n> bíblico\n\n- a\n- b")
        self.assertIn("<h4>Sub</h4>", markdown("### Sub", 1))
        self.assertIn("<b>forte</b>", h)
        self.assertIn("<i>leve</i>", h)
        self.assertIn("<blockquote><p>Texto bíblico</p></blockquote>", h)
        self.assertIn("<ul><li>a</li><li>b</li></ul>", h)
        self.assertEqual([t for t, _ in secoes("# T\n\n## Um\n\nx\n\n## Dois\n\ny <!-- c -->")], ["Um", "Dois"])


class Build(unittest.TestCase):
    """Build do Elite com o conteúdo real: as notas em revisão só podem aparecer em /previa/ (noindex)."""

    @classmethod
    def setUpClass(cls):
        cls.s = copia_do_site()
        cls.revisao = [json.loads(p.read_text(encoding="utf-8"))["slug"] for p in (RAIZ / "conteudo" / "noticias").glob("*.json")
                       if json.loads(p.read_text(encoding="utf-8")).get("status") == "revisao"]

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.s.parent, ignore_errors=True)

    def html(self, rel):
        return (self.s / rel).read_text(encoding="utf-8")

    def test_rotas(self):
        for rel in ["index.html", "noticias/index.html", "estudos/index.html", "lancamentos/index.html", "discipulado/index.html", "consulta/index.html",
                    "politica-editorial/index.html", "404.html", "sitemap.xml", "sitemap-noticias.xml", "robots.txt", "llms.txt",
                    "busca.json", "favicon.svg", "marca/o-paladino.webp"]:
            self.assertTrue((self.s / rel).exists(), rel)

    def test_revisao_so_na_previa(self):
        for slug in self.revisao:
            self.assertFalse((self.s / "noticias" / slug).exists(), slug)
            previa = self.html(f"previa/noticias/{slug}/index.html")
            self.assertIn('content="noindex"', previa)
            for rel in ("index.html", "noticias/index.html", "sitemap.xml", "sitemap-noticias.xml", "busca.json", "llms.txt"):
                self.assertNotIn(slug, self.html(rel), rel)
            self.assertFalse(list((self.s / "img").rglob(f"*{slug}*")), slug)  # sem cartão público de prévia

    def test_livros_da_biblia(self):
        s = self.html("consulta/index.html")
        self.assertIn("66 livros · 1.189 capítulos", s)
        raw = s.split("const RAW = `", 1)[1].split("`", 1)[0]
        caps = {"Antigo Testamento": 0, "Novo Testamento": 0}
        livros = {"Antigo Testamento": 0, "Novo Testamento": 0}
        for linha in raw.strip().split("\n"):
            t, _, g = linha.split(" | ")
            for x in g.split("; "):
                livros[t] += 1
                caps[t] += int(x.split("=")[1])
        self.assertEqual((livros, caps), ({"Antigo Testamento": 39, "Novo Testamento": 27}, {"Antigo Testamento": 929, "Novo Testamento": 260}))

    def test_versiculo_diario(self):
        s = self.html("consulta/index.html")
        raw = s.split("const RAW = `", 1)[1].split("`", 1)[0]
        nomes = [x.split("=")[0] for linha in raw.strip().split("\n") for x in linha.split(" | ")[2].split("; ")]
        versos = json.loads(re.search(r"^const VERSOS = (.*);$", s, re.M).group(1))
        self.assertGreaterEqual(len(versos), 1800)
        self.assertEqual({v[0] for v in versos}, set(nomes))  # pelo menos um versículo de cada livro
        self.assertEqual(len({(v[0], v[1], v[2]) for v in versos}), len(versos))
        self.assertTrue(all(v[3].strip() for v in versos))
        self.assertIn("João Ferreira de Almeida", s)
        self.assertIn('id="sortear"', s)
        self.assertRegex(s, r'<blockquote id="vt">[^<]+</blockquote>')  # versículo do dia já no HTML

    def test_cores_azuis(self):
        s = self.html("index.html")
        self.assertIn("#0a1a33", s)
        self.assertNotRegex(s, r"background:#000[;}]")

    def test_sem_marca_antiga(self):
        for p in self.s.rglob("*.html"):
            if "exemplos" in p.parts or "docs" in p.parts:
                continue
            self.assertNotRegex(p.read_text(encoding="utf-8"), r"(?i)elite ?boardgamers|eliteboardgamers|golden geek", str(p))

    def test_publicacao_sem_arquivos_de_trabalho(self):
        r = subprocess.run([sys.executable, "tools/montar_publicacao.py", "_site"], cwd=self.s, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        site = self.s / "_site"
        self.assertTrue((site / "index.html").exists())
        for rel in ("tools", "conteudo", "docs", "worker", "exemplos", "config", "pauta.json", "CLAUDE.md", ".git"):
            self.assertFalse((site / rel).exists(), rel)
        shutil.rmtree(site)

    def test_seo(self):
        r = subprocess.run([sys.executable, "tools/checar_seo.py"], cwd=self.s, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class NotaPublicada(unittest.TestCase):
    """Página de nota publicada no formato do Elite, com as notas FICTÍCIAS de exemplos/ numa cópia temporária."""

    @classmethod
    def setUpClass(cls):
        cls.s = copia_do_site(exemplos=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.s.parent, ignore_errors=True)

    def test_formato_elite(self):
        nota = (self.s / "noticias" / "exemplo-manchete" / "index.html").read_text(encoding="utf-8")
        for secao in ("Por que importa", "Fontes"):
            self.assertIn(secao, nota)
        self.assertNotIn('content="noindex"', nota)
        self.assertIn("exemplo-manchete", (self.s / "index.html").read_text(encoding="utf-8"))
        self.assertFalse((self.s / "noticias" / "exemplo-em-revisao").exists())
        self.assertTrue((self.s / "previa" / "noticias" / "exemplo-em-revisao" / "index.html").exists())


class Legislativo(unittest.TestCase):
    def test_sapl(self):
        """Leitor das casas legislativas (SAPL): leis do tipo pedido e projetos, com link para a página da matéria."""
        from datetime import datetime, timedelta, timezone
        from editorial import coletar
        resp = {"norma": {"results": [
                    {"id": 1, "__str__": "Lei nº 10, de 23 de outubro de 2026", "ementa": "Gratuidade para pessoas com deficiência", "data": "2026-10-23"},
                    {"id": 2, "__str__": "Decreto nº 99, de 23 de outubro de 2026", "ementa": "Crédito suplementar", "data": "2026-10-23"}]},
                "materia": {"results": [
                    {"id": 7, "__str__": "Projeto de Lei nº 5 de 2026", "ementa": "Assistência religiosa a pacientes", "data_apresentacao": "2026-10-27"}]}}
        antes = coletar.baixar, coletar.permitido
        coletar.baixar = lambda url: json.dumps(resp["norma" if "/norma/" in url else "materia"]).encode()
        coletar.permitido = lambda url: True
        try:
            f = {"url": "https://sapl.exemplo.leg.br/", "formato": "sapl", "normas": "Lei", "tipos_materia": [5]}
            itens = coletar.ler_fonte(f, datetime(2026, 10, 20, tzinfo=timezone.utc))
        finally:
            coletar.baixar, coletar.permitido = antes
        titulos = [t for t, _, _, _ in itens]
        self.assertIn("Lei nº 10, de 23 de outubro de 2026: Gratuidade para pessoas com deficiência", titulos)
        self.assertFalse(any(t.startswith("Decreto") for t in titulos))
        self.assertIn("https://sapl.exemplo.leg.br/materia/7", [l for _, l, _, _ in itens])
        self.assertEqual(itens[0][3].tzinfo.utcoffset(None), timedelta(hours=-4))


class Mural(unittest.TestCase):
    def test_mural_de_pautas(self):
        """Mural de pautas sugeridas (Ancapsu): título, data e o link da matéria original, nunca o do mural."""
        from editorial import coletar
        html_ = ('<div class="card col-lg-3 mb-4"><h5 class="card-title fw-bold"> Projeto prevê prisão por boicote </h5>'
                 '<li class="nav-item text-muted"> 30 out. 2026 </li><p class="card-text">Resumo do portal</p>'
                 '<a href="https://jornal.example/materia" target="_blank" class="btn btn-outline-success btn-sm">Ler</a></div>'
                 '<div class="card col-lg-3 mb-4"><p>cartão sem título</p></div>')
        itens = list(coletar.itens_mural(html_))
        self.assertEqual(len(itens), 1)
        titulo, link, resumo, quando = itens[0]
        self.assertEqual((titulo, link, resumo), ("Projeto prevê prisão por boicote", "https://jornal.example/materia", "Resumo do portal"))
        self.assertEqual((quando.day, quando.month, quando.year), (30, 10, 2026))


class Producao(unittest.TestCase):
    def test_isolamento(self):
        r = rodar("tools/checar_isolamento.py")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class Publicacao(unittest.TestCase):
    def test_so_revisor_publica(self):
        tmp = Path(tempfile.mkdtemp()) / "noticias" / "nota.json"
        tmp.parent.mkdir()
        shutil.copy(EX / "noticias" / "2026-10-27-exemplo-em-revisao.json", tmp)
        r = rodar("tools/publicar.py", "aprovar", str(tmp), "--revisor", "autora-exemplo", "--exemplo")
        self.assertNotEqual(r.returncode, 0)
        r = rodar("tools/publicar.py", "aprovar", str(tmp), "--revisor", "revisor-exemplo", "--exemplo")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        a = json.loads(tmp.read_text(encoding="utf-8"))
        self.assertEqual((a["status"], a["revisao"]["revisor"]), ("publicado", "revisor-exemplo"))


class Fotos(unittest.TestCase):
    """Robô de fotos (tools/fotos.py), sem rede: robots.txt, licença por fonte, crédito e extração da página."""

    def setUp(self):
        portal.iniciar()
        import fotos
        self.f = fotos

    def test_robots(self):
        r = self.f.Robots("User-agent: *\nDisallow: /privado\nAllow: /privado/fotos\nCrawl-delay: 5\n", 200)
        self.assertFalse(r.pode("https://x.org/privado/doc"))
        self.assertTrue(r.pode("https://x.org/privado/fotos/a.jpg"))
        self.assertEqual(r.delay, 5)
        self.assertFalse(self.f.Robots("", 503).pode("https://x.org/"))  # servidor fora do ar: não entra
        self.assertTrue(self.f.Robots("", 404).pode("https://x.org/"))   # sem robots.txt: liberado

    def test_licenca_e_credito(self):
        ab = self.f.regra("https://agenciabrasil.ebc.com.br/geral/noticia/x")
        self.assertEqual(ab["uso"], "livre")
        self.assertEqual(self.f.regra("https://www2.camara.leg.br/x")["nome"], "Câmara dos Deputados")
        self.assertEqual(self.f.regra("https://www.gov.br/planalto/foto.jpg")["uso"], "livre")
        self.assertEqual(self.f.regra("https://smpdc.portovelho.ro.gov.br/foto.webp")["uso"], "a confirmar")  # prefeitura não herda o gov.br
        self.assertEqual(self.f.montar_credito(ab, "Foto: Fulana de Tal/Agência Brasil")[0], "Foto: Fulana de Tal/Agência Brasil")
        self.assertEqual(self.f.montar_credito(ab, "")[0], "Foto: Agência Brasil")
        self.assertIsNone(self.f.montar_credito(ab, "Foto: Reuters/Fulano")[0])  # agência de terceiros: bloqueada
        self.assertEqual(self.f.montar_credito(self.f.regra("https://desconhecido.org/a"), "Foto: X")[0], "")  # a confirmar

    def test_extrai_fotos_com_legenda(self):
        html = ('<meta property="og:image" content="/f/capa.jpg"><img src="/f/logo.png" alt="logo">'
                '<figure><img srcset="/f/a-300x200.jpg 300w, /f/a-1200x800.jpg 1200w" alt="Culto"><figcaption>Foto: Beltrano/Agência Senado</figcaption></figure>')
        res = self.f.imagens_da_pagina(html, "https://www12.senado.leg.br/noticias/m")
        urls = [c["url"] for c in res]
        self.assertIn("https://www12.senado.leg.br/f/capa.jpg", urls)
        self.assertIn("https://www12.senado.leg.br/f/a.jpg", urls)  # maior do srcset, sem o sufixo de miniatura
        self.assertFalse(any("logo" in u for u in urls))
        self.assertEqual(self.f.autor_do_credito(res[0]["legenda"]), "Beltrano")  # og:image herda o crédito da página

    def test_aprovar_exige_alt(self):
        with self.assertRaises(SystemExit):
            self.f.aprovar("qualquer", 1, "curto")


if __name__ == "__main__":
    unittest.main()
