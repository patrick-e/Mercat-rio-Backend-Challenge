import sqlite3
from typing import Any, List, Tuple, Optional
from contextlib import contextmanager
import os

class Database:
    def __init__(self, db_path: str = "database.db"):
        self.db_path = db_path
        self._create_tables()

    @contextmanager
    def get_connection(self):
        """
        Gerencia a conexão com o banco de dados usando context manager
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _create_tables(self):
        """
        Cria as tabelas do banco de dados se não existirem
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Tabela de credores
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS credores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    cpf_cnpj TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL,
                    telefone TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Tabela de precatórios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS precatorios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    credor_id INTEGER NOT NULL,
                    numero_precatorio TEXT NOT NULL UNIQUE,
                    valor_nominal DECIMAL(15,2) NOT NULL,
                    foro TEXT NOT NULL,
                    data_publicacao DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (credor_id) REFERENCES credores (id) ON DELETE CASCADE
                )
            """)

            # Tabela de documentos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documentos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    credor_id INTEGER NOT NULL,
                    tipo TEXT NOT NULL,
                    arquivo_url TEXT NOT NULL,
                    enviado_em TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (credor_id) REFERENCES credores (id) ON DELETE CASCADE
                )
            """)

            # Tabela de certidões
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS certidoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    credor_id INTEGER NOT NULL,
                    tipo TEXT NOT NULL,
                    origem TEXT NOT NULL,
                    arquivo_url TEXT,
                    conteudo_base64 TEXT,
                    status TEXT NOT NULL,
                    recebida_em TIMESTAMP NOT NULL,
                    valida_ate TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (credor_id) REFERENCES credores (id) ON DELETE CASCADE
                )
            """)

            conn.commit()

    def execute(self, query: str, params: Tuple = ()) -> Any:
        """
        Executa uma query no banco de dados
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid

    def fetch_one(self, query: str, params: Tuple = ()) -> Optional[sqlite3.Row]:
        """
        Busca um único registro no banco de dados
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()

    def fetch_all(self, query: str, params: Tuple = ()) -> List[sqlite3.Row]:
        """
        Busca múltiplos registros no banco de dados
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def table_to_dict(self, row: sqlite3.Row) -> dict:
        """
        Converte um registro do banco de dados para dicionário
        """
        return dict(zip(row.keys(), row))