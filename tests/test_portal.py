"""Testes do portal no formato do Elite: padrão das notícias e dos estudos, build, prévia de revisão, SEO e isolamento.

Uso: python3 -m unittest discover -s tests -v
"""
import copy
import json
import os
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

    def test_crivo_de_vinte_pontos(self):
        def crivo(**mud):
            c = {"pontos": 15, "trilha": "quente", "abrangencia": "nacional", "eixos": {"valor": 6, "viral": 5, "cristao": 4},
                 "origem": {"nome": "The Christian Post", "url": "https://www.christianpost.com/"}}
            c.update(mud)
            return self.erros(crivo=c)
        self.assertEqual(crivo(), "")
        self.assertIn("soma dos eixos", crivo(pontos=16))
        self.assertIn("de 0 a 7", crivo(pontos=17, eixos={"valor": 6, "viral": 8, "cristao": 3}))
        self.assertIn("abaixo do corte", crivo(pontos=7, eixos={"valor": 4, "viral": 2, "cristao": 1}))
        self.assertIn("trilha", crivo(trilha="morna"))
        self.assertIn("abrangencia", crivo(abrangencia="europa"))
        self.assertIn("origem", crivo(origem={"nome": "Daily Wire"}))
        self.assertEqual(self.erros(crivo={"pontos": 5}), "")  # nota antiga, sem eixos, continua valendo

    def test_crivo_juridico(self):
        self.assertIn("risco jurídico", self.erros(veredito="O relator é um mentiroso e o projeto, uma farsa de quem quer aparecer na foto."))
        self.assertIn("checagem_juridica", self.erros(checagem_juridica=None))

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

    def test_estrutura_com_referencia(self):
        c = copy.deepcopy(self.c)
        c["estrutura"][0] = ["Sem referência", "texto sem a passagem indicada"]
        self.assertTrue(any("referência" in x for x in p_estudo(c, publicar=True)))


def copia_do_site(exemplos=False):
    """Cópia temporária do repositório para rodar o build do Elite (tools/build_home.py) sem mexer na raiz.

    Com exemplos=True, troca as notícias pelas FICTÍCIAS de exemplos/ (uma publicada por revisor-exemplo e uma em
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
        shutil.copy(RAIZ / "exemplos" / "config" / "equipe.json", tmp / "config" / "equipe.json")
    r = subprocess.run([sys.executable, "tools/build_home.py"], cwd=tmp, capture_output=True, text=True)
    if r.returncode:
        raise AssertionError(r.stdout + r.stderr)
    return tmp


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
        for rel in ["index.html", "noticias/index.html", "estudos/index.html", "lancamentos/index.html", "consulta/index.html",
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
