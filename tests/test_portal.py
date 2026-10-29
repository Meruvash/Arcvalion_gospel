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
SAIDA = "publico-teste"


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


class Build(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        r = rodar("tools/build.py", "--exemplo", "--saida", SAIDA, "--sem-og")
        if r.returncode:
            raise AssertionError(r.stdout + r.stderr)
        cls.s = RAIZ / SAIDA

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(RAIZ / SAIDA, ignore_errors=True)

    def html(self, rel):
        return (self.s / rel).read_text(encoding="utf-8")

    def test_rotas(self):
        for rel in ["index.html", "noticias/index.html", "noticias/exemplo-manchete/index.html", "estudos/index.html", "estudos/exemplo-estudo/index.html",
                    "agenda/index.html", "biblia/index.html", "politica-editorial/index.html", "404.html", "feed.xml", "sitemap.xml",
                    "sitemap-noticias.xml", "robots.txt", "llms.txt", "busca.json", "previa/index.html"]:
            self.assertTrue((self.s / rel).exists(), rel)

    def test_revisao_so_na_previa(self):
        self.assertFalse((self.s / "noticias" / "exemplo-em-revisao").exists())
        self.assertTrue((self.s / "previa" / "noticias" / "exemplo-em-revisao" / "index.html").exists())
        previa = self.html("previa/noticias/exemplo-em-revisao/index.html")
        self.assertIn('content="noindex"', previa)
        self.assertIn("Prévia em revisão", previa)
        for rel in ("index.html", "noticias/index.html", "sitemap.xml", "busca.json", "feed.xml"):
            self.assertNotIn("exemplo-em-revisao", self.html(rel), rel)

    def test_formato_elite(self):
        nota = self.html("noticias/exemplo-manchete/index.html")
        for secao in ("Por que importa", "Em números", "Contexto", "No Brasil", "O que dizem", "Interessa a você se", "Nossa opinião",
                      "Fontes", "Por que esta notícia entrou", "revisada por"):
            self.assertIn(secao, nota)
        est = self.html("estudos/exemplo-estudo/index.html")
        for secao in ("Resumo em 30 segundos", "Estrutura de", "Para a vida hoje", "O que o texto ensina", "Leituras equivocadas",
                      "Para quem é", "Para guardar", "Ficha do livro", "Perguntas frequentes", "progresso"):
            self.assertIn(secao, est)

    def test_cores_azuis(self):
        s = self.html("index.html")
        self.assertIn("#0a1a33", s)
        self.assertNotRegex(s, r"--ground:#000[;}]")

    def test_seo(self):
        r = rodar("tools/checar_seo.py", SAIDA, "--exemplo")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_sem_marca_antiga(self):
        for p in self.s.rglob("*.html"):
            self.assertNotRegex(p.read_text(encoding="utf-8"), r"(?i)elite ?boardgamers", str(p))


class Producao(unittest.TestCase):
    def test_cloudflare_e_github(self):
        amb = {**os.environ, "CF_PAGES": "1", "CF_PAGES_URL": "https://8f3a1b2c.arcvalion.pages.dev"}
        r = rodar("tools/build.py", "--producao", "--saida", "publico-teste-prod", "--sem-og", env=amb)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('href="https://arcvalion.pages.dev/"', (RAIZ / "publico-teste-prod" / "index.html").read_text(encoding="utf-8"))
        r = rodar("tools/build.py", "--saida", "publico-teste-prod", "--sem-og")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("/Arcvalion_gospel/marca/favicon.svg", (RAIZ / "publico-teste-prod" / "404.html").read_text(encoding="utf-8"))
        shutil.rmtree(RAIZ / "publico-teste-prod", ignore_errors=True)

    def test_saida_fora_recusada(self):
        self.assertNotEqual(rodar("tools/build.py", "--saida", "/tmp/qualquer", "--sem-og").returncode, 0)

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


if __name__ == "__main__":
    unittest.main()
