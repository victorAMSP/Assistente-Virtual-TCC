import unittest
from domain.services.processador_comando_service import ProcessadorComandoService

class TestNLPIntents(unittest.TestCase):
    def setUp(self):
        self.p = ProcessadorComandoService()

    def test_concluir_com_id(self):
        out = self.p.processar("já concluí 5")
        self.assertTrue(out and out[0]["acao"] == "__concluir__")
        self.assertEqual(out[0]["habito_id"], 5)

    def test_concluir_sem_id(self):
        out = self.p.processar("já conclui minha corrida")
        self.assertTrue(out and out[0]["acao"] == "__concluir__")
        self.assertIsNone(out[0].get("habito_id"))

    def test_adiar_com_id_e_minutos(self):
        out = self.p.processar("adiar 7 em 20 min")
        self.assertTrue(out and out[0]["acao"] == "__adiar__")
        self.assertEqual(out[0]["habito_id"], 7)
        self.assertEqual(out[0]["minutos"], 20)

def test_adiar_sem_id_min_padrao(self):
    # Frase equivalente, sem ID explícito, mas com "adiar" + minutos
    out = self.p.processar("adiar em 15 min")
    self.assertTrue(out and out[0]["acao"] == "__adiar__")
    # Sem ID → a view usará o último notificado
    self.assertIsNone(out[0].get("habito_id"))
    # Padrão que validamos: 15 minutos
    self.assertEqual(out[0]["minutos"], 15)

if __name__ == "__main__":
    unittest.main()