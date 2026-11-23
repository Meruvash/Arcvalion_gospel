import copy, json, os, sys, unittest
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "tools", "video", "novela"))
from auditar_novela import auditar

ROT = os.path.join(RAIZ, "docs", "video", "novela", "roteiros")


class TestAuditarNovela(unittest.TestCase):
    def carregar(self, nome):
        return json.load(open(os.path.join(ROT, nome), encoding="utf-8"))

    def test_roteiros_aprovados(self):
        for nome in sorted(os.listdir(ROT)):
            if nome.startswith("novela_") and nome.endswith(".json"):
                self.assertTrue(auditar(self.carregar(nome))["aprovado"], nome)

    def test_sem_fonte_reprova(self):
        r = copy.deepcopy(self.carregar("novela_v1_livro_do_pai.json"))
        for b in r["batidas"]:
            b.pop("fonte", None)
        self.assertFalse(auditar(r)["aprovado"])

    def test_virada_cedo_demais_perde_nota(self):
        r = copy.deepcopy(self.carregar("novela_v1_livro_do_pai.json"))
        for b in r["batidas"]:
            if b["tipo"] == "REVELACAO":
                b["tipo"] = "TRANSICAO"
        a = auditar(r)
        self.assertFalse(a["aprovado"])
        self.assertLess(a["nota_formula"], 0.85)

    def test_protagonista_antes_da_virada_reprova(self):
        r = copy.deepcopy(self.carregar("novela_v1_livro_do_pai.json"))
        r["batidas"][1]["quem"] = "Dr. Pelicioni"
        self.assertFalse(auditar(r)["aprovado"])

    def test_promessa_de_resultado_reprova(self):
        r = copy.deepcopy(self.carregar("novela_v1_livro_do_pai.json"))
        for b in r["batidas"]:
            if b["tipo"] == "PROTECAO":
                b["fala"] = "Eu garanto que a senhora vai ganhar."
        self.assertFalse(auditar(r)["aprovado"])

class TestSerieEAvisos(unittest.TestCase):
    def _v1(self):
        import json, os
        p = os.path.join(os.path.dirname(__file__), "..", "docs", "video", "novela", "roteiros", "novela_v1c_livro_do_pai_cinema.json")
        return json.load(open(p, encoding="utf-8"))

    def test_parte2_exige_continuidade(self):
        r = self._v1(); r["parte"] = 2
        self.assertFalse(auditar(r)["aprovado"])
        r["handoff_anterior"] = {"objeto": "livro com a Rosa"}; r["batidas"][0]["reprise"] = True
        self.assertTrue(auditar(r)["aprovado"])

    def test_aviso_porque(self):
        r = self._v1()
        self.assertFalse(any(a.startswith("A2") for a in auditar(r)["avisos"]))
        for b in r["batidas"]:
            b.pop("porque", None)
        self.assertTrue(any(a.startswith("A2") for a in auditar(r)["avisos"]))


if __name__ == "__main__":
    unittest.main()
