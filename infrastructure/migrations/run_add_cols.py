import sqlite3
from contextlib import closing

DB_PATH = "assistente_virtual.db"  

NEW_COLS = {
    "status":        "ALTER TABLE habitos ADD COLUMN status TEXT DEFAULT 'pendente'",
    "snooze_until":  "ALTER TABLE habitos ADD COLUMN snooze_until TEXT",
    "ultimo_disparo":"ALTER TABLE habitos ADD COLUMN ultimo_disparo TEXT",
}

def existing_cols(cur, table):
    cur.execute(f"PRAGMA table_info('{table}')")
    return {row[1] for row in cur.fetchall()}

def migrate():
    with closing(sqlite3.connect(DB_PATH)) as con:
        con.execute("PRAGMA foreign_keys = ON")
        cur = con.cursor()
        cols = existing_cols(cur, "habitos")
        missing = [c for c in NEW_COLS if c not in cols]
        if not missing:
            print("OK: nada a migrar."); return
        try:
            con.execute("BEGIN")
            for c in missing:
                print("MIGRANDO:", c)
                cur.execute(NEW_COLS[c])
            con.commit()
            print("OK: migração concluída.")
        except Exception as e:
            con.rollback()
            print("ERRO: rollback:", e)
            raise

if __name__ == "__main__":
    migrate()