from typing import Optional, List, Dict
from datetime import datetime
from core.entities.credor import Credor
from core.entities.precatorio import Precatorio
from core.entities.documento import Documento
from core.entities.certidao import Certidao
from ports.interfaces.Icredor import ICredorRepository
from ports.database.database import Database

class CredorRepository(ICredorRepository):
    def __init__(self, database: Database):
        self.db = database

    def criar(self, credor: Credor, precatorio: Precatorio) -> Credor:
        """
        Cria um novo credor com seu precatório associado
        """
        # Verificar se já existe um credor com o mesmo CPF/CNPJ
        credor_existente = self.buscar_por_cpf_cnpj(credor.cpf_cnpj)
        if credor_existente:
            raise ValueError(f"Já existe um credor cadastrado com o CPF/CNPJ {credor.cpf_cnpj}")

        # Criar credor
        credor_query = """
            INSERT INTO credores (nome, cpf_cnpj, email, telefone)
            VALUES (?, ?, ?, ?)
        """
        credor_id = self.db.execute(
            credor_query,
            (credor.nome, credor.cpf_cnpj, credor.email, credor.telefone)
        )
        
        # Criar precatório
        precatorio.credor_id = credor_id
        precatorio_query = """
            INSERT INTO precatorios (
                credor_id, numero_precatorio, valor_nominal,
                foro, data_publicacao
            ) VALUES (?, ?, ?, ?, ?)
        """
        self.db.execute(
            precatorio_query,
            (
                credor_id, precatorio.numero_precatorio,
                float(precatorio.valor_nominal), precatorio.foro,
                precatorio.data_publicacao
            )
        )
        
        credor.id = credor_id
        return credor

    def buscar_por_id(self, credor_id: int) -> Optional[Credor]:
        """
        Busca um credor por ID
        """
        query = "SELECT * FROM credores WHERE id = ?"
        result = self.db.fetch_one(query, (credor_id,))
        
        if result:
            return Credor(
                id=result['id'],
                nome=result['nome'],
                cpf_cnpj=result['cpf_cnpj'],
                email=result['email'],
                telefone=result['telefone']
            )
        return None

    def buscar_por_cpf_cnpj(self, cpf_cnpj: str) -> Optional[Credor]:
        """
        Busca um credor por CPF/CNPJ
        """
        query = "SELECT * FROM credores WHERE cpf_cnpj = ?"
        result = self.db.fetch_one(query, (cpf_cnpj,))
        
        if result:
            return Credor(
                id=result['id'],
                nome=result['nome'],
                cpf_cnpj=result['cpf_cnpj'],
                email=result['email'],
                telefone=result['telefone']
            )
        return None

    def listar_todos(self) -> List[Credor]:
        """
        Lista todos os credores
        """
        query = "SELECT * FROM credores"
        results = self.db.fetch_all(query)
        
        return [
            Credor(
                id=row['id'],
                nome=row['nome'],
                cpf_cnpj=row['cpf_cnpj'],
                email=row['email'],
                telefone=row['telefone']
            )
            for row in results
        ]

    def buscar_detalhes(self, credor_id: int) -> Optional[dict]:
        """
        Busca todos os detalhes do credor
        """
        credor = self.buscar_por_id(credor_id)
        if not credor:
            return None

        # Buscar precatório
        prec_query = "SELECT * FROM precatorios WHERE credor_id = ?"
        prec_result = self.db.fetch_one(prec_query, (credor_id,))
        precatorio = None
        if prec_result:
            precatorio = {
                'numero': prec_result['numero_precatorio'],
                'valor': float(prec_result['valor_nominal']),
                'foro': prec_result['foro'],
                'data_publicacao': prec_result['data_publicacao']
            }

        # Buscar documentos
        doc_query = "SELECT * FROM documentos WHERE credor_id = ?"
        doc_results = self.db.fetch_all(doc_query, (credor_id,))
        documentos = [
            {
                'tipo': doc['tipo'],
                'arquivo_url': doc['arquivo_url'],
                'enviado_em': doc['enviado_em']
            }
            for doc in doc_results
        ]

        # Buscar certidões
        cert_query = "SELECT * FROM certidoes WHERE credor_id = ?"
        cert_results = self.db.fetch_all(cert_query, (credor_id,))
        certidoes = [
            {
                'tipo': cert['tipo'],
                'status': cert['status'],
                'valida_ate': cert['valida_ate']
            }
            for cert in cert_results
        ]

        return {
            'id': credor.id,
            'nome': credor.nome,
            'cpf_cnpj': credor.cpf_cnpj,
            'email': credor.email,
            'telefone': credor.telefone,
            'precatorio': precatorio,
            'documentos': documentos,
            'certidoes': certidoes
        }

    def atualizar(self, credor: Credor) -> Credor:
        """
        Atualiza os dados de um credor
        """
        query = """
            UPDATE credores
            SET nome = ?, cpf_cnpj = ?, email = ?, telefone = ?,
                updated_at = ?
            WHERE id = ?
        """
        self.db.execute(
            query,
            (
                credor.nome, credor.cpf_cnpj, credor.email,
                credor.telefone, datetime.now(), credor.id
            )
        )
        return credor

    def deletar(self, credor_id: int) -> bool:
        """
        Deleta um credor e seus dados relacionados
        """
        query = "DELETE FROM credores WHERE id = ?"
        self.db.execute(query, (credor_id,))
        return True