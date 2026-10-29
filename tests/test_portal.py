"""Testes do portal: padrão editorial, build de exemplo e de produção, SEO, isolamento.

Uso: python3 -m unittest discover -s tests -v
"""
import copy
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "tools"))
import portal  # noqa: E402
from editorial import checar  # noqa: E402
from editorial.vicios import sensacionalismo  # noqa: E402

SAIDA = "publico-teste"


def rodar(*args):
    return subprocess.run([sys.executable, *args], cwd=RAIZ, capture_output=True, text=True)


def exemplo(slug):
    return json.loads((RAIZ / "exemplos" / "conteudo" / "artigos" / f"{slug}.json").read_text(encoding="utf-8"))


class Editorial(unittest.TestCase):
    def setUp(self):
        portal.iniciar(conteudo=RAIZ / "exemplos" / "conteudo", config=RAIZ / "exemplos" / "config", exemplo=True)
        self.base = exemplo("exemplo-manchete-gospel")

    def erros(self, **mud):
        a = copy.deepcopy(self.base)
        for k, v in mud.items():
            if v is None:
                a.pop(k, None)
            else:
                a[k] = v
        return " | ".join(checar.problemas(a, publicar=True))

    def test_exemplo_passa(self):
        self.assertEqual(self.erros(), "")

    def test_sem_revisao_humana_nao_publica(self):
        self.assertIn("revisão humana", self.erros(revisao=None))
        self.assertIn("revisão humana", self.erros(revisao={"revisor": "autora-exemplo", "data": "2026-10-29T10:00:00-03:00"}))

    def test_ia_precisa_ser_declarada(self):
        self.assertIn("ia:", self.erros(ia=None))
        self.assertIn("diga em que a IA ajudou", self.erros(ia={"usada": True}))

    def test_fontes_verificaveis(self):
        self.assertIn("pelo menos 2", self.erros(fontes=self.base["fontes"][:1]))
        sec = [dict(f, tipo="secundaria") for f in self.base["fontes"]]
        self.assertIn("fonte primária", self.erros(fontes=sec))
        self.assertIn("link", self.erros(fontes=[{"nome": "x", "url": "", "data": "", "tipo": "primaria"}] * 2))

    def test_citacao_atribuida(self):
        corpo = self.base["corpo"] + [{"citacao": "Frase", "fonte": 0}]
        self.assertIn("citação sem autor", self.erros(corpo=corpo))
        corpo = self.base["corpo"] + [{"citacao": "Frase", "autor": "Fulano", "fonte": 9}]
        self.assertIn("apontar a fonte", self.erros(corpo=corpo))

    def test_fonte_anonima_e_caca_clique(self):
        self.assertIn("fonte não identificável", self.erros(lide=self.base["lide"] + " Segundo fontes, haverá mudanças."))
        self.assertTrue(sensacionalismo("Você não vai acreditar no que o pastor disse"))
        self.assertTrue(sensacionalismo("Igreja anuncia congresso!"))
        self.assertTrue(sensacionalismo("URGENTE: votação no Senado"))
        self.assertFalse(sensacionalismo("STF julga recurso sobre ensino religioso nesta quinta"))

    def test_opiniao_e_patrocinado(self):
        self.assertIn("análise", self.erros(tipo="opiniao"))  # quadro de análise não existe em opinião
        pat = exemplo("exemplo-patrocinado")
        self.assertEqual(checar.problemas(pat, publicar=True), [])
        pat["manchete"] = True
        self.assertIn("não pode ser manchete", " ".join(checar.problemas(pat, publicar=True)))
        self.assertIn("só existe no tipo 'patrocinado'", self.erros(patrocinador={"nome": "X"}))

    def test_correcao_precisa_de_data_e_atualizacao(self):
        self.assertIn("correcoes[0]", self.erros(correcoes=[{"data": "2026-10-30", "texto": "x"}]))

    def test_imagem_ia_proibida(self):
        im = dict(self.base["imagem"], gerada_por_ia=True)
        self.assertIn("gerada por IA", self.erros(imagem=im))


class Build(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        r = rodar("tools/build.py", "--exemplo", "--hoje", "2026-10-29", "--saida", SAIDA, "--sem-og")
        if r.returncode:
            raise AssertionError(r.stdout + r.stderr)
        cls.s = RAIZ / SAIDA

    def ler(self, rel):
        return (self.s / rel).read_text(encoding="utf-8")

    def test_rotas_principais(self):
        for rel in ["index.html", "noticias/index.html", "opiniao/index.html", "autores/autora-exemplo/index.html", "404.html",
                    "politica-editorial/index.html", "privacidade/index.html", "anuncie/index.html", "newsletter/index.html",
                    "feed.xml", "sitemap.xml", "sitemap-noticias.xml", "robots.txt", "llms.txt", "busca.json"]:
            self.assertTrue((self.s / rel).exists(), rel)
        for x in json.loads((RAIZ / "config" / "editorias.json").read_text(encoding="utf-8"))["editorias"]:
            self.assertTrue((self.s / x["slug"] / "index.html").exists(), x["slug"])

    def test_rascunho_nao_publica(self):
        self.assertFalse((self.s / "noticias" / "exemplo-rascunho").exists())
        self.assertNotIn("exemplo-rascunho", self.ler("sitemap.xml") + self.ler("busca.json") + self.ler("index.html"))

    def test_previa_nao_indexa(self):
        self.assertIn("Disallow: /", self.ler("robots.txt"))
        self.assertIn('content="noindex, follow"', self.ler("index.html"))
        self.assertIn("Demonstração.", self.ler("index.html"))

    def test_patrocinado_identificado_e_fora_do_noticioso(self):
        s = self.ler("noticias/exemplo-patrocinado/index.html")
        self.assertIn("Conteúdo patrocinado por", s)
        self.assertIn('rel="sponsored noopener"', s)
        self.assertNotIn('class="pub', s)  # sem anúncio dentro de conteúdo pago
        self.assertNotIn("exemplo-patrocinado", self.ler("sitemap-noticias.xml") + self.ler("feed.xml"))

    def test_transparencia_e_correcao_visiveis(self):
        s = self.ler("noticias/exemplo-corrigida/index.html")
        self.assertIn('id="correcoes"', s)
        self.assertIn("Revisada por Revisor de Exemplo", s)
        self.assertIn("inteligência artificial", s)
        self.assertIn('"dateModified": "2026-10-26T10:00:00-03:00"', s)

    def test_opiniao_rotulada(self):
        s = self.ler("noticias/exemplo-opiniao/index.html")
        self.assertIn("OpinionNewsArticle", s)
        self.assertIn("Este é um artigo de opinião", s)

    def test_afiliado_identificado(self):
        s = self.ler("noticias/exemplo-cultura/index.html")
        self.assertIn('rel="sponsored nofollow noopener"', s)
        self.assertIn("Links de afiliado", s)

    def test_sitemap_de_noticias_48h(self):
        news = self.ler("sitemap-noticias.xml")
        self.assertIn("exemplo-manchete-gospel", news)
        self.assertNotIn("exemplo-gospel-2", news)  # publicada 5 dias antes

    def test_agenda_esconde_evento_passado_e_marca_pago(self):
        s = self.ler("eventos/index.html")
        self.assertIn("Congresso de exemplo", s)
        self.assertNotIn("Evento que já passou", s)
        self.assertIn("divulgação paga", s)
        self.assertIn('"@type": "Event"', s)
        self.assertNotIn("Show de exemplo (divulgação paga)\", \"startDate", s)  # pago e não confirmado fica fora do Event

    def test_seo_e_links(self):
        r = rodar("tools/checar_seo.py", SAIDA, "--exemplo")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_um_h1_e_sem_marca_antiga(self):
        for p in self.s.rglob("*.html"):
            s = p.read_text(encoding="utf-8")
            self.assertNotRegex(s, re.compile(r"elite ?boardgamers", re.I), str(p))


class Producao(unittest.TestCase):
    def test_producao_no_cloudflare_pages(self):
        import os
        amb = {**os.environ, "CF_PAGES": "1", "CF_PAGES_URL": "https://8f3a1b2c.arcvalion.pages.dev"}
        r = subprocess.run([sys.executable, "tools/build.py", "--producao", "--saida", "publico-teste-prod", "--sem-og"],
                           cwd=RAIZ, capture_output=True, text=True, env=amb)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        s = (RAIZ / "publico-teste-prod" / "index.html").read_text(encoding="utf-8")
        self.assertIn('<link rel="canonical" href="https://arcvalion.pages.dev/">', s)
        self.assertIn('href="/marca/favicon.svg"', (RAIZ / "publico-teste-prod" / "404.html").read_text(encoding="utf-8"))
        r = subprocess.run([sys.executable, "tools/build.py", "--producao", "--saida", "publico-teste-prod", "--sem-og"],
                           cwd=RAIZ, capture_output=True, text=True, env={**os.environ, "SITE_URL": "http://sem-https.test"})
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("https", r.stdout + r.stderr)

    def test_build_local_sem_materias(self):
        r = rodar("tools/build.py", "--saida", "publico-teste-prod", "--sem-og")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        s = (RAIZ / "publico-teste-prod" / "index.html").read_text(encoding="utf-8")
        self.assertIn("passam por revisão humana", s)
        self.assertIn('content="max-image-preview:large"', s)

    def test_saida_fora_do_projeto_recusada(self):
        r = rodar("tools/build.py", "--saida", "/tmp/qualquer", "--sem-og")
        self.assertNotEqual(r.returncode, 0)

    def test_isolamento(self):
        r = rodar("tools/checar_isolamento.py")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class FluxoPublicacao(unittest.TestCase):
    def test_so_revisor_humano_publica(self):
        import shutil
        import tempfile
        tmp = Path(tempfile.mkdtemp()) / "rascunho.json"
        shutil.copy(RAIZ / "exemplos" / "conteudo" / "artigos" / "exemplo-rascunho.json", tmp)
        r = rodar("tools/publicar.py", "aprovar", str(tmp), "--revisor", "autora-exemplo", "--exemplo")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("não é pessoa revisora", r.stdout + r.stderr)
        r = rodar("tools/publicar.py", "aprovar", str(tmp), "--revisor", "revisor-exemplo", "--exemplo")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        a = json.loads(tmp.read_text(encoding="utf-8"))
        self.assertEqual((a["status"], a["revisao"]["revisor"]), ("publicado", "revisor-exemplo"))
        r = rodar("tools/publicar.py", "corrigir", str(tmp), "--revisor", "revisor-exemplo", "--texto", "Data corrigida.", "--exemplo")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        a = json.loads(tmp.read_text(encoding="utf-8"))
        self.assertEqual(a["correcoes"][-1]["texto"], "Data corrigida.")
        self.assertGreaterEqual(a["atualizado_em"], a["publicado_em"])


class Configuracao(unittest.TestCase):
    def test_slug_reservado_e_editoria_oculta(self):
        portal.iniciar()
        portal.EDITORIAS = portal.EDITORIAS + [{"slug": "noticias", "nome": "X", "descricao": "x", "cor": "#000", "fundo": "#fff"}]
        self.assertTrue(any("reservado" in e for e in portal.problemas_config()))
        portal.iniciar()
        portal.EDITORIAS[0] = dict(portal.EDITORIAS[0], visivel=False)
        self.assertNotIn(portal.EDITORIAS[0]["slug"], [x["slug"] for x in portal.visiveis()])


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
