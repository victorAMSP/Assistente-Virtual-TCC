import os
import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta

# importe conforme o caminho dos seus novos UCs
from application.use_cases.adiar_habito_use_case import AdiarHabitoUseCase
from application.use_cases.marcar_concluido_use_case import MarcarConcluidoUseCase

# Stub leve que grava em 'conclusoes' (mantém seu fluxo atual)
class StubRegistrarConclusaoUC:
    def __init__(self, db_path: str):
        self.db_path = db_path
    def executar(self, usuario, acao, horario, status, categoria):
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        cur.execute(
            "INSERT INTO conclusoes (usuario, acao, horario, status, data_registro, categoria) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (usuario, acao, horario, status, datetime.now().replace(microsecond=0).isoformat(), categoria)
        )
        con.commit()
        con.close()

def _create_temp_db():
    fd, path = tempfile.mkstemp(prefix="tcc_uc_", suffix=".sqlite")
    os.close(fd)
    con = sqlite3.connect(path)
    cur = con.cursor()
    cur.executescript("""
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS habitos (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      usuario TEXT NOT NULL,
      acao TEXT NOT NULL,
      horario TEXT NOT NULL,
      categoria TEXT,
      status TEXT DEFAULT 'pendente',
      snooze_until TEXT,
      ultimo_disparo TEXT
    );

    CREATE TABLE IF NOT EXISTS conclusoes (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      usuario TEXT NOT NULL,
      acao TEXT NOT NULL,
      horario TEXT NOT NULL,
      status TEXT NOT NULL,
      data_registro TEXT NOT NULL,
      categoria TEXT
    );
    """)
    # seed
    cur.execute("INSERT INTO habitos (usuario, acao, horario, categoria) VALUES (?,?,?,?)",
                ("victor", "beber água", "09h00", "hidratação"))
    cur.execute("INSERT INTO habitos (usuario, acao, horario, categoria) VALUES (?,?,?,?)",
                ("victor", "correr", "18h00", "exercício"))
    con.commit()
    con.close()
    return path

def _fetchone(con, sql, params=()):
    cur = con.cursor()
    cur.execute(sql, params)
    return cur.fetchone()

class TestNovosUseCases(unittest.TestCase):
    def setUp(self):
        self.db_path = _create_temp_db()

    def tearDown(self):
        try:
            os.remove(self.db_path)
        except FileNotFoundError:
            pass

    def test_adiar_habito_persiste_snooze_e_status(self):
        # Arrange
        adiar_uc = AdiarHabitoUseCase(habito_repo=None, db_path=self.db_path)
        con = sqlite3.connect(self.db_path)
        habito_id = _fetchone(con, "SELECT id FROM habitos WHERE acao='beber água'")[0]

        # Act
        ok = adiar_uc.execute(habito_id=habito_id, minutos=20)

        # Assert
        self.assertTrue(ok)
        row = _fetchone(con, "SELECT status, snooze_until FROM habitos WHERE id=?", (habito_id,))
        con.close()

        self.assertIsNotNone(row)
        status, snooze = row
        self.assertEqual(status, "adiado")
        dt = datetime.fromisoformat(snooze)
        self.assertGreater(dt, datetime.now() - timedelta(minutes=1))
        self.assertLessEqual(dt, datetime.now() + timedelta(minutes=25))

    def test_marcar_concluido_atualiza_status_e_registra_conclusao(self):
        # Arrange
        registrar_stub = StubRegistrarConclusaoUC(self.db_path)
        concluir_uc = MarcarConcluidoUseCase(habito_repo=None, registrar_conclusao_uc=registrar_stub, db_path=self.db_path)
        con = sqlite3.connect(self.db_path)
        habito = _fetchone(con, "SELECT id, usuario, acao, horario, categoria FROM habitos WHERE acao='correr'")
        habito_id = habito[0]

        # Act
        ok = concluir_uc.execute(habito_id=habito_id, fonte_acao="teste")

        # Assert
        self.assertTrue(ok)

        # 1) status do hábito
        st = _fetchone(con, "SELECT status FROM habitos WHERE id=?", (habito_id,))[0]
        self.assertEqual(st, "concluido")

        # 2) registro em conclusoes
        reg = _fetchone(con, "SELECT usuario, acao, horario, status FROM conclusoes WHERE acao='correr' ORDER BY id DESC LIMIT 1")
        con.close()
        self.assertIsNotNone(reg)
        usuario, acao, horario, status = reg
        self.assertEqual(status, "sim")

if __name__ == "__main__":
    unittest.main()