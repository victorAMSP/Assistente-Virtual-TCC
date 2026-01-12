from datetime import datetime
import sqlite3

class MarcarConcluidoUseCase:
    """
    Marca um hábito como concluído:
      - Se a coluna 'status' existir: atualiza habitos.status = 'concluido'
      - Sempre registra uma conclusão usando o caso de uso já existente (registrar_conclusao_uc)
    """
    def __init__(self, habito_repo, registrar_conclusao_uc, db_path: str = "assistente_virtual.db"):
        self.habito_repo = habito_repo
        self.registrar_conclusao_uc = registrar_conclusao_uc
        self.db_path = db_path

    def _has_col(self, cur, table: str, col: str) -> bool:
        cur.execute(f"PRAGMA table_info('{table}')")
        return any(r[1] == col for r in cur.fetchall())

    def _get_habito_by_id(self, cur, habito_id: int):
        # Consulta direta, mantendo compatibilidade com seu repositório atual:contentReference[oaicite:5]{index=5}
        cur.execute(
            "SELECT id, usuario, acao, horario, categoria FROM habitos WHERE id = ?",
            (habito_id,)
        )
        row = cur.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "usuario": row[1],
            "acao": row[2],
            "horario": row[3],
            "categoria": row[4],
        }

    def execute(self, habito_id: int, fonte_acao: str = "chatbot") -> bool:
        if not isinstance(habito_id, int):
            return False

        con = sqlite3.connect(self.db_path)
        try:
            cur = con.cursor()
            has_status = self._has_col(cur, "habitos", "status")

            # Carrega dados do hábito para registrar conclusão depois
            h = self._get_habito_by_id(cur, habito_id)
            if not h:
                return False

            # Atualiza status se a coluna existir
            if has_status:
                cur.execute("UPDATE habitos SET status = ? WHERE id = ?", ("concluido", habito_id))

            con.commit()

            # Sempre registra conclusão (mantém compatível com a lógica de hoje)
            # RegistrarConclusaoUseCase espera: (usuario, acao, horario, status, categoria) conforme o fluxo atual
            self.registrar_conclusao_uc.executar(
                h["usuario"],
                h["acao"],
                h["horario"],
                "sim",           # concluído
                h["categoria"]
            )
            return True
        finally:
            con.close()