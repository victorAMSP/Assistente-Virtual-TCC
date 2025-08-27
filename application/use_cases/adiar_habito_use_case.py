from datetime import datetime, timedelta
import sqlite3

class AdiarHabitoUseCase:
    """
    Adia um hábito persistindo no banco:
      - snooze_until = now + minutos
      - status = 'adiado' (apenas se a coluna existir)
    Tudo é condicional ao esquema atual, sem quebrar se as colunas não existirem.
    """
    def __init__(self, habito_repo, db_path: str = "assistente_virtual.db"):
        self.habito_repo = habito_repo
        # Mantém compatível com seu projeto atual:contentReference[oaicite:3]{index=3} e o script de criação:contentReference[oaicite:4]{index=4}
        self.db_path = db_path

    def _has_col(self, cur, table: str, col: str) -> bool:
        cur.execute(f"PRAGMA table_info('{table}')")
        return any(r[1] == col for r in cur.fetchall())

    def execute(self, habito_id: int, minutos: int = 15) -> bool:
        if not isinstance(habito_id, int):
            return False

        dt = datetime.now() + timedelta(minutes=minutos)
        dt_iso = dt.replace(microsecond=0).isoformat()

        con = sqlite3.connect(self.db_path)
        try:
            cur = con.cursor()
            has_snooze = self._has_col(cur, "habitos", "snooze_until")
            has_status = self._has_col(cur, "habitos", "status")

            if not has_snooze:
                # Sem coluna -> não persiste snooze (mantém comportamento atual em memória)
                return False

            # Monta UPDATE apenas com as colunas existentes
            sets = ["snooze_until = ?"]
            vals = [dt_iso]
            if has_status:
                sets.append("status = ?")
                vals.append("adiado")

            vals.append(habito_id)
            sql = f"UPDATE habitos SET {', '.join(sets)} WHERE id = ?"
            cur.execute(sql, vals)
            con.commit()
            return True
        finally:
            con.close()