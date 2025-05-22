from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from core.entities.precatorio import Precatorio
from ports.interfaces.Iprecatorio import IPrecatorioRepository
from ports.database.database import Database

class PrecatorioRepository(IPrecatorioRepository):
    def __init__(self, database: Database):
        self.db = database

    def criar(self, precatorio: Precatorio) -> Precatorio:
        """
        Cria um novo precatório
        """
        query = """
            INSERT INTO precatorios (
                credor_id, numero_precatorio, valor_nominal,
                foro, data_publicacao
            ) VALUES (?, ?, ?, ?, ?)
        """
        precatorio_id = self.db.execute(
            query,
            (
                precatorio.credor_id, precatorio.numero_precatorio,
                float(precatorio.valor_nominal), precatorio.foro,
                precatorio.data_publicacao
            )
        )
        precatorio.id = precatorio_id
        return precatorio

    def buscar_por_id(self, precatorio_id: int) -> Optional[Precatorio]:
        """
        Busca um precatório por ID
        """
        query = "SELECT * FROM precatorios WHERE id = ?"
        result = self.db.fetch_one(query, (precatorio_id,))
        
        if result:
            return Precatorio(
                id=result['id'],
                credor_id=result['credor_id'],
                numero_precatorio=result['numero_precatorio'],
                valor_nominal=Decimal(str(result['valor_nominal'])),
                foro=result['foro'],
                data_publicacao=datetime.fromisoformat(result['data_publicacao'])
            )
        return None

    def buscar_por_numero(self, numero_precatorio: str) -> Optional[Precatorio]:
        """
        Busca um precatório por número
        """
        query = "SELECT * FROM precatorios WHERE numero_precatorio = ?"
        result = self.db.fetch_one(query, (numero_precatorio,))
        
        if result:
            return Precatorio(
                id=result['id'],
                credor_id=result['credor_id'],
                numero_precatorio=result['numero_precatorio'],
                valor_nominal=Decimal(str(result['valor_nominal'])),
                foro=result['foro'],
                data_publicacao=datetime.fromisoformat(result['data_publicacao'])
            )
        return None

    def buscar_por_credor(self, credor_id: int) -> List[Precatorio]:
        """
        Busca todos os precatórios de um credor
        """
        query = "SELECT * FROM precatorios WHERE credor_id = ?"
        results = self.db.fetch_all(query, (credor_id,))
        
        return [
            Precatorio(
                id=row['id'],
                credor_id=row['credor_id'],
                numero_precatorio=row['numero_precatorio'],
                valor_nominal=Decimal(str(row['valor_nominal'])),
                foro=row['foro'],
                data_publicacao=datetime.fromisoformat(row['data_publicacao'])
            )
            for row in results
        ]

    def listar_todos(self) -> List[Precatorio]:
        """
        Lista todos os precatórios
        """
        query = "SELECT * FROM precatorios"
        results = self.db.fetch_all(query)
        
        return [
            Precatorio(
                id=row['id'],
                credor_id=row['credor_id'],
                numero_precatorio=row['numero_precatorio'],
                valor_nominal=Decimal(str(row['valor_nominal'])),
                foro=row['foro'],
                data_publicacao=datetime.fromisoformat(row['data_publicacao'])
            )
            for row in results
        ]

    def atualizar(self, precatorio: Precatorio) -> Precatorio:
        """
        Atualiza os dados de um precatório
        """
        query = """
            UPDATE precatorios
            SET credor_id = ?, numero_precatorio = ?, valor_nominal = ?,
                foro = ?, data_publicacao = ?, updated_at = ?
            WHERE id = ?
        """
        self.db.execute(
            query,
            (
                precatorio.credor_id, precatorio.numero_precatorio,
                float(precatorio.valor_nominal), precatorio.foro,
                precatorio.data_publicacao, datetime.now(),
                precatorio.id
            )
        )
        return precatorio

    def deletar(self, precatorio_id: int) -> bool:
        """
        Deleta um precatório
        """
        query = "DELETE FROM precatorios WHERE id = ?"
        self.db.execute(query, (precatorio_id,))
        return True

    def buscar_por_foro(self, foro: str) -> List[Precatorio]:
        """
        Busca precatórios por foro
        """
        query = "SELECT * FROM precatorios WHERE foro = ?"
        results = self.db.fetch_all(query, (foro,))
        
        return [
            Precatorio(
                id=row['id'],
                credor_id=row['credor_id'],
                numero_precatorio=row['numero_precatorio'],
                valor_nominal=Decimal(str(row['valor_nominal'])),
                foro=row['foro'],
                data_publicacao=datetime.fromisoformat(row['data_publicacao'])
            )
            for row in results
        ]