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


if __name__ == "__main__":
    unittest.main()
