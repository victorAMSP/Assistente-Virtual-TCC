import sqlite3
from typing import List, Optional
from domain.entities.conclusao import Conclusao
from domain.repositories.conclusao_repository import ConclusaoRepository
from datetime import datetime

class ConclusaoRepositorySQLite(ConclusaoRepository):
    def __init__(self, db_path: str = "assistente_virtual.db"):
        self.db_path = db_path

    def salvar(self, conclusao: Conclusao) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conclusoes (usuario, acao, horario, status, data_registro, categoria)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                conclusao.usuario,
                conclusao.acao,
                conclusao.horario,
                conclusao.status,
                conclusao.data_registro,
                conclusao.categoria
            ))
            conn.commit()
            conclusao.id = cursor.lastrowid  # Atribui o ID gerado a entidade Conclusao

    def registrar(self, conclusao: Conclusao) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO conclusoes (usuario, acao, horario, status, data_registro, categoria)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            conclusao.usuario,
            conclusao.acao,
            conclusao.horario,
            conclusao.status,
            conclusao.data_registro.strftime("%Y-%m-%d %H:%M:%S"),
            conclusao.categoria
        ))
        conclusao.id = cursor.lastrowid
        conn.commit()
        conn.close()

    def listar(self, usuario: str) -> List[Conclusao]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, usuario, acao, horario, status, data_registro, categoria
            FROM conclusoes
            WHERE usuario = ?
        """, (usuario,))
        resultados = cursor.fetchall()
        conn.close()

        return [
            Conclusao(
                id=r[0],
                usuario=r[1],
                acao=r[2],
                horario=r[3],
                status=r[4],
                data_registro=datetime.strptime(r[5], "%Y-%m-%d %H:%M:%S"),
                categoria=r[6]
            ) for r in resultados
        ]

    def listar_por_usuario(self, usuario: str) -> List[Conclusao]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, usuario, acao, horario, status, data_registro, categoria
                FROM conclusoes
                WHERE usuario = ?
                ORDER BY data_registro DESC
            """, (usuario,))
            rows = cursor.fetchall()
            return [Conclusao(*row) for row in rows]

    def listar_filtrado(
    self,
    usuario: str,
    categoria: Optional[str] = None,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None
) -> List[Conclusao]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = """
                SELECT id, usuario, acao, horario, status, data_registro, categoria
                FROM conclusoes
                WHERE usuario = ?
            """
            params = [usuario]

            if categoria:
                query += " AND categoria = ?"
                params.append(categoria)

            if data_inicio and data_fim:
                query += " AND DATE(data_registro) BETWEEN ? AND ?"
                params.extend([data_inicio, data_fim])

            query += " ORDER BY data_registro DESC"
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            return [
                Conclusao(
                    id=r[0],
                    usuario=r[1],
                    acao=r[2],
                    horario=r[3],
                    status=r[4],
                    data_registro=datetime.strptime(r[5], "%Y-%m-%d %H:%M:%S"),
                    categoria=r[6]
                ) for r in rows
            ]