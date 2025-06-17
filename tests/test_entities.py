import unittest
from domain.entities.habito import Habito
from domain.entities.conclusao import Conclusao
from datetime import datetime

class TestEntidades(unittest.TestCase):

    def test_habito_criacao(self):
        h = Habito(usuario="victor", acao="beber água", horario="14h00", categoria="hidratação")
        self.assertEqual(h.usuario, "victor")
        self.assertEqual(h.acao, "beber água")
        self.assertEqual(h.horario, "14h00")
        self.assertEqual(h.categoria, "hidratação")
        self.assertIsNone(h.id)

    def test_conclusao_criacao(self):
        agora = datetime.now()
        c = Conclusao(usuario="victor", acao="correr", horario="07h00", status="sim", data_registro=agora, categoria="exercício")
        self.assertEqual(c.usuario, "victor")
        self.assertEqual(c.acao, "correr")
        self.assertEqual(c.horario, "07h00")
        self.assertEqual(c.status, "sim")
        self.assertEqual(c.data_registro, agora)
        self.assertEqual(c.categoria, "exercício")

    def test_conclusao_formato_default_data(self):
        c = Conclusao(usuario="teste", acao="dormir", horario="22h00", status="não")
        self.assertIsInstance(c.data_registro, datetime)

if __name__ == "__main__":
    unittest.main()