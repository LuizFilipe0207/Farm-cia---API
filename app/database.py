import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "farmacia.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS medicamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            principio_ativo TEXT NOT NULL,
            fabricante TEXT NOT NULL,
            categoria TEXT NOT NULL,
            requer_receita INTEGER NOT NULL DEFAULT 0,
            preco REAL NOT NULL,
            criado_em TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS estoque (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medicamento_id INTEGER NOT NULL UNIQUE,
            quantidade INTEGER NOT NULL DEFAULT 0,
            quantidade_minima INTEGER NOT NULL DEFAULT 10,
            lote TEXT NOT NULL,
            data_validade TEXT NOT NULL,
            atualizado_em TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (medicamento_id) REFERENCES medicamentos(id) ON DELETE CASCADE
        );
    """)

    conn.commit()
    conn.close()
