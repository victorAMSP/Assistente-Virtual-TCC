import sqlite3

DB_NAME = "assistente_virtual.db"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Criar tabela de hábitos
cursor.execute("""
CREATE TABLE IF NOT EXISTS habitos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT NOT NULL,
    acao TEXT NOT NULL,
    horario TEXT NOT NULL,
    categoria TEXT
)
""")

# Criar tabela de conclusões
cursor.execute("""
CREATE TABLE IF NOT EXISTS conclusoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT NOT NULL,
    acao TEXT NOT NULL,
    horario TEXT NOT NULL,
    status TEXT NOT NULL,
    data_registro TEXT NOT NULL,
    categoria TEXT
)
""")

conn.commit()
conn.close()

print("Tabelas criadas com sucesso.")