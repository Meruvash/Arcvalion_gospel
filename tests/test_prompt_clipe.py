import copy, json, os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "video", "novela"))
import prompt_clipe as pc

BASE = {"id": "t", "duracao": 6, "cenario": "terreiro", "personagens": ["Valdir"], "voz": "Valdir",
        "planos": [{"de": 0, "ate": 3, "quadro": "close-up", "quem": "Valdir", "acao": "talks", "fala": True},
                   {"de": 3, "ate": 6, "quadro": "close-up", "quem": "Valdir", "acao": "stops"}],
        "fala": {"texto": "A parte é minha.", "inicio": 0.5}}


class TestPromptClipe(unittest.TestCase):
    def test_ok(self):
        txt, erros = pc.montar(copy.deepcopy(BASE))
        self.assertEqual(erros, [])
        self.assertIn("No background music", txt)
        self.assertIn("@Audio1 is the voice of @Image1, Valdir", txt)
        self.assertIn(pc.TRAVAS["Valdir"], txt)

    def test_planos_nao_somam(self):
        c = copy.deepcopy(BASE); c["planos"][1]["ate"] = 5
        self.assertTrue(any("somam" in e for e in pc.montar(c)[1]))

    def test_dois_falantes(self):
        c = copy.deepcopy(BASE); c["personagens"].append("Rosa")
        c["planos"][1].update(quem="Rosa", fala=True)
        self.assertTrue(any("mais de um falante" in e for e in pc.montar(c)[1]))

    def test_fala_nao_cabe(self):
        c = copy.deepcopy(BASE); c["fala"]["texto"] = " ".join(["palavra"] * 20)
        self.assertTrue(any("não cabe" in e for e in pc.montar(c)[1]))

    def test_clipes_da_v1_conferem(self):
        pasta = os.path.join(os.path.dirname(__file__), "..", "docs", "video", "novela", "producao_v1c", "clipes")
        for f in sorted(os.listdir(pasta)):
            if f.endswith(".json"):
                self.assertEqual(pc.montar(json.load(open(os.path.join(pasta, f), encoding="utf-8")))[1], [], f)


if __name__ == "__main__":
    unittest.main()
