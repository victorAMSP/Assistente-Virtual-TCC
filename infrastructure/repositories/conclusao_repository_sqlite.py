import sqlite3
from typing import List, Optional
from datetime import datetime
from domain.entities.conclusao import Conclusao
from domain.repositories.conclusao_repository import ConclusaoRepository
from domain.value_objects.horario_do_habito import HorarioDoHabito

class ConclusaoRepositorySQLite(ConclusaoRepository):
    def __init__(self, db_path: str = "assistente_virtual.db"):
        self.db_path = db_path

    def _parse_dt(self, value: str) -> datetime:
        # Garante compatibilidade com datas com ou sem microssegundos
        data_txt = value.replace("T", " ")
        if "." in data_txt:
            data_txt = data_txt.split(".", 1)[0]
        return datetime.strptime(data_txt, "%Y-%m-%d %H:%M:%S")

    def conectar(self):
        return sqlite3.connect(self.db_path)
    
    def registrar(self, conclusao: Conclusao) -> None:
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO conclusoes (usuario, acao, horario, status, data_registro, categoria)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            conclusao.usuario,
            conclusao.acao,
            conclusao.horario.to_db(),
            conclusao.status,
            conclusao.data_registro.strftime("%Y-%m-%d %H:%M:%S"),
            conclusao.categoria
        ))
        conclusao.id = cursor.lastrowid  # Atribui o ID gerado a entidade Conclusao
        conn.commit()
        conn.close()
            
    def listar(self, usuario: str) -> List[Conclusao]:
        return self.listar_por_usuario(usuario)

    def listar_por_usuario(self, usuario: str) -> List[Conclusao]:
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, usuario, acao, horario, status, data_registro, categoria
            FROM conclusoes
            WHERE usuario = ?
            ORDER BY data_registro DESC
        """, (usuario,))
        rows = cursor.fetchall()
        conn.close()

        return [
            Conclusao(
                id=row[0],
                usuario=row[1],
                acao=row[2],
                horario=HorarioDoHabito.from_db(row[3]),   
                status=row[4],
                data_registro=self._parse_dt(row[5]),
                categoria=row[6],
            )
            for row in rows
        ]

    def listar_filtrado(
        self,
        usuario: str,
        categoria: Optional[str] = None,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None
) -> List[Conclusao]:
        
        conn = self.conectar()
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
        elif data_inicio:
            query += " AND date(data_registro) >= ?"
            params.append(data_inicio)
        elif data_fim:
            query += " AND date(data_registro) <= ?"
            params.append(data_fim)

        query += " ORDER BY data_registro DESC"
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        conn.close()

        return [
            Conclusao(
                id=r[0],
                usuario=r[1],
                acao=r[2],
                horario=HorarioDoHabito.from_db(r[3]),
                status=r[4],
                data_registro=self._parse_dt(r[5]),
                categoria=r[6],
            ) for r in rows
        ]