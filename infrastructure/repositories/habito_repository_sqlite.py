import sqlite3
from datetime import datetime, timedelta
from domain.entities.habito import Habito
from domain.repositories.habito_repository import IHabitorepository
from typing import List

DB_NAME = "assistente_virtual.db"

class HabitoRepositorySQLite(IHabitorepository):
    def __init__(self, db_path=DB_NAME):
        self.db_path = db_path

    def conectar(self):
        return sqlite3.connect(self.db_path)

    def salvar(self, habito: Habito):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO habitos (usuario, acao, horario, categoria)
            VALUES (?, ?, ?, ?)
        """, (habito.usuario, habito.acao, habito.horario, habito.categoria))
        conn.commit()
        conn.close()

    def listar_por_usuario(self, usuario: str):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, acao, horario, categoria FROM habitos WHERE usuario = ?", (usuario,))
        dados = cursor.fetchall()
        conn.close()
        return [Habito(usuario, a, h, c, id=h_id) for h_id, a, h, c in dados]

    def listar_com_id(self, usuario: str):
        return self.listar_por_usuario(usuario)

    def apagar_por_id(self, id: int):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM habitos WHERE id = ?", (id,))
        conn.commit()
        conn.close()

    def atualizar(self, habito: Habito):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE habitos
            SET acao = ?, horario = ?, categoria = ?
            WHERE id = ?
        """, (habito.acao, habito.horario, habito.categoria, habito.id))
        conn.commit()
        conn.close()

    def buscar_proximos(self, usuario: str, tolerancia_min: int) -> List[Habito]:
        agora = datetime.now()
        horarios_alvo = [(agora + timedelta(minutes=i)).strftime("%Hh%M") for i in range(-tolerancia_min, tolerancia_min + 1)]

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        placeholder = ",".join("?" for _ in horarios_alvo)
        query = f"""
            SELECT id, usuario, acao, horario, categoria FROM habitos
            WHERE usuario = ? AND horario IN ({placeholder})
        """
        cursor.execute(query, (usuario, *horarios_alvo))
        dados = cursor.fetchall()
        conn.close()

        return [Habito(id=d[0], usuario=d[1], acao=d[2], horario=d[3], categoria=d[4]) for d in dados]