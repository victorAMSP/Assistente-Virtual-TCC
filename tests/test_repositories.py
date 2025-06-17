import unittest
import os
import sqlite3
from datetime import datetime
from domain.entities.habito import Habito
from infrastructure.repositories.habito_repository_sqlite import HabitoRepositorySQLite
from domain.entities.conclusao import Conclusao
from infrastructure.repositories.conclusao_repository_sqlite import ConclusaoRepositorySQLite


TEST_DB = "test_habitos.db"

class TestHabitoRepositorySQLite(unittest.TestCase):

    def setUp(self):
        self.repo = HabitoRepositorySQLite(TEST_DB)
        self._criar_tabela()
        # Limpa a tabela antes de cada teste
        with sqlite3.connect(TEST_DB) as conn:
            conn.execute("DELETE FROM habitos")
            conn.commit()

    def tearDown(self):
        # Libera a conexão para que o arquivo possa ser removido
        del self.repo
        import gc
        gc.collect()
        if os.path.exists(TEST_DB):
            try:
                os.remove(TEST_DB)
            except PermissionError:
                pass

    def _criar_tabela(self):
        with sqlite3.connect(TEST_DB) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS habitos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario TEXT,
                    acao TEXT,
                    horario TEXT,
                    categoria TEXT
                )
            """)
            conn.commit()

    def test_salvar_e_listar(self):
        habito = Habito(usuario="victor", acao="beber água", horario="08h00", categoria="hidratação")
        self.repo.salvar(habito)
        habitos = self.repo.listar_por_usuario("victor")
        self.assertEqual(len(habitos), 1)
        self.assertEqual(habitos[0].acao, "beber água")

    def test_atualizar(self):
        h = Habito(usuario="victor", acao="correr", horario="07h00", categoria="exercício")
        self.repo.salvar(h)
        h_banco = self.repo.listar_por_usuario("victor")[0]
        h_banco.acao = "caminhada"
        self.repo.atualizar(h_banco)
        atualizado = self.repo.listar_por_usuario("victor")[0]
        self.assertEqual(atualizado.acao, "caminhada")

    def test_apagar_por_id(self):
        h = Habito(usuario="victor", acao="meditar", horario="21h00", categoria="bem-estar")
        self.repo.salvar(h)
        habitos = self.repo.listar_por_usuario("victor")
        self.repo.apagar_por_id(habitos[0].id)
        habitos_restantes = self.repo.listar_por_usuario("victor")
        self.assertEqual(len(habitos_restantes), 0)

    def test_buscar_proximos(self):
        agora = datetime.now()
        hora_formatada = f"{agora.hour:02d}h{agora.minute:02d}"
        self.repo.salvar(Habito(usuario="victor", acao="beber água", horario=hora_formatada, categoria="hidratação"))
        encontrados = self.repo.buscar_proximos("victor", tolerancia_min=30)
        self.assertTrue(any(h.acao == "beber água" for h in encontrados))

class TestConclusaoRepositorySQLite(unittest.TestCase):

    def setUp(self):
        self.db_path = "test_conclusoes.db"
        self.repo = ConclusaoRepositorySQLite(self.db_path)
        self._criar_tabela()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM conclusoes")
            conn.commit()

    def tearDown(self):
        del self.repo
        import gc
        gc.collect()
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except PermissionError:
                pass

    def _criar_tabela(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conclusoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario TEXT,
                    acao TEXT,
                    horario TEXT,
                    status TEXT,
                    data_registro TEXT,
                    categoria TEXT
                )
            """)
            conn.commit()

    def test_registrar_e_listar(self):
        c = Conclusao(usuario="victor", acao="dormir", horario="22h00", status="sim", categoria="sono")
        self.repo.registrar(c)
        resultados = self.repo.listar("victor")
        self.assertEqual(len(resultados), 1)
        self.assertEqual(resultados[0].acao, "dormir")
        self.assertEqual(resultados[0].categoria, "sono")

    def test_listar_filtrado_por_categoria(self):
        self.repo.registrar(Conclusao(usuario="victor", acao="correr", horario="07h00", status="sim", categoria="exercício"))
        self.repo.registrar(Conclusao(usuario="victor", acao="beber água", horario="08h00", status="sim", categoria="hidratação"))

        resultados = self.repo.listar_filtrado("victor", categoria="hidratação")
        self.assertEqual(len(resultados), 1)
        self.assertEqual(resultados[0].acao, "beber água")

    def test_listar_filtrado_por_periodo(self):
        hoje = datetime.now().strftime("%Y-%m-%d")
        self.repo.registrar(Conclusao(usuario="victor", acao="ler", horario="20h00", status="sim", categoria="lazer"))

        resultados = self.repo.listar_filtrado("victor", data_inicio=hoje, data_fim=hoje)
        self.assertTrue(len(resultados) >= 1)
        
if __name__ == "__main__":
    unittest.main()