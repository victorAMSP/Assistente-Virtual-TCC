import sqlite3
from datetime import datetime, timedelta
from domain.entities.habito import Habito
from domain.repositories.habito_repository import IHabitorepository
from typing import List
from domain.value_objects.horario_do_habito import HorarioDoHabito
from domain.value_objects.categoria_do_habito import CategoriaDoHabito

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
        """, (habito.usuario, habito.acao, habito.horario.to_db(), habito.categoria.to_db()))
        conn.commit()
        conn.close()

    def listar_por_usuario(self, usuario: str):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, acao, horario, categoria FROM habitos WHERE usuario = ?", (usuario,))
        rows = cursor.fetchall()
        conn.close()

        habitos: List[Habito] = []
        for h_id, acao, horario_txt, categoria in rows:
            habitos.append(
                Habito(
                    id=h_id,
                    usuario=usuario,
                    acao=acao,
                    horario=HorarioDoHabito.from_db(horario_txt),  
                    categoria=CategoriaDoHabito.from_db(categoria),
                )
            )
        return habitos

    def buscar_por_id(self, habito_id: int) -> Habito | None:
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, usuario, acao, horario, categoria FROM habitos WHERE id = ?", (habito_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        h_id, usr, acao, horario_txt, categoria = row
        return Habito(
            id=h_id,
            usuario=usr,
            acao=acao,
            horario=HorarioDoHabito.from_db(horario_txt),
            categoria=CategoriaDoHabito.from_db(categoria),
        )

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
        """, (habito.acao, habito.horario.to_db(), habito.categoria.to_db(), habito.id))
        conn.commit()
        conn.close()

    def buscar_proximos(self, usuario: str, tolerancia_min: int) -> List[Habito]:
        agora = datetime.now()
        horarios_alvo = [(agora + timedelta(minutes=i)).strftime("%Hh%M") for i in range(-tolerancia_min, tolerancia_min + 1)]

        conn = self.conectar()
        cursor = conn.cursor()
        placeholder = ",".join("?" for _ in horarios_alvo)
        query = f"""
            SELECT id, usuario, acao, horario, categoria FROM habitos
            WHERE usuario = ? AND horario IN ({placeholder})
        """
        cursor.execute(query, (usuario, *horarios_alvo))
        rows = cursor.fetchall()
        conn.close()

        proximos: List[Habito] = []
        for h_id, usr, acao, horario_txt, categoria in rows:
            proximos.append(
                Habito(
                    id=h_id,
                    usuario=usr,
                    acao=acao,
                    horario=HorarioDoHabito.from_db(horario_txt), 
                    categoria=CategoriaDoHabito.from_db(categoria),
                )
            )
        return proximos