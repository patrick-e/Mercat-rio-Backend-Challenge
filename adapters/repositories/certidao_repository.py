import os
import json
import base64
from typing import Optional, List, Dict, BinaryIO
from datetime import datetime, timedelta
import hashlib
import requests
import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from core.entities.certidao import (
    Certidao, TipoCertidao, OrigemCertidao, StatusCertidao
)
from ports.interfaces.Icertidao import ICertidaoRepository, ICertidaoApiService
from ports.database.database import Database

class CertidaoApiMock(ICertidaoApiService):
    """
    Mock da API de certidões
    """
    def __init__(self):
        self.db: Optional[Database] = None
        self.scheduler = BackgroundScheduler()
        
    def set_database(self, database: Database):
        """
        Configura a conexão com o banco de dados
        """
        self.db = database

    def buscar_certidoes(self, cpf_cnpj: str) -> List[Dict]:
        """
        Simula busca de certidões na API externa
        """
        # Simula delay de API
        import time
        time.sleep(1)
        
        # Gera dados mockados com base no CPF/CNPJ
        tipos = ["federal", "estadual", "municipal", "trabalhista"]
        status = ["positiva", "negativa", "pendente"]
        
        certidoes = []
        for tipo in tipos:
            # Usa o CPF/CNPJ para gerar dados consistentes
            hash_input = f"{cpf_cnpj}_{tipo}".encode()
            hash_value = int(hashlib.md5(hash_input).hexdigest(), 16)
            
            certidoes.append({
                "tipo": tipo,
                "status": status[hash_value % len(status)],
                "conteudo_base64": base64.b64encode(
                    f"Certidão {tipo.title()} para {cpf_cnpj}".encode()
                ).decode()
            })
        
        return certidoes

    def validar_certidao(self, certidao_id: int) -> StatusCertidao:
        """
        Simula revalidação de uma certidão
        """
        # Gera resultado consistente baseado no ID
        hash_value = int(hashlib.md5(str(certidao_id).encode()).hexdigest(), 16)
        status_list = list(StatusCertidao)
        return status_list[hash_value % len(status_list)]

    def revalidar_certidoes_vencidas(self) -> int:
        """
        Revalida certidões que estão para vencer
        """
        if not self.db:
            raise ValueError("Database não configurada")

        # Busca certidões que vencem em até 5 dias
        query = """
            SELECT id FROM certidoes 
            WHERE valida_ate <= datetime('now', '+5 days')
            AND valida_ate >= datetime('now')
        """
        
        results = self.db.fetch_all(query)
        quantidade = 0
        
        for row in results:
            certidao_id = row['id']
            novo_status = self.validar_certidao(certidao_id)
            
            # Atualiza status e validade
            update_query = """
                UPDATE certidoes
                SET status = ?, valida_ate = datetime('now', '+30 days')
                WHERE id = ?
            """
            
            self.db.execute(update_query, (novo_status.value, certidao_id))
            quantidade += 1
            
        return quantidade

    def iniciar_revalidacao_periodica(self):
        """
        Inicia o job periódico de revalidação usando APScheduler
        """
        if not self.scheduler.running:
            self.scheduler.add_job(
                self.revalidar_certidoes_vencidas,
                'interval',
                hours=24,
                id='revalidacao_certidoes'
            )
            self.scheduler.start()

    def parar_revalidacao_periodica(self):
        """
        Para o job periódico de revalidação
        """
        if self.scheduler.running:
            self.scheduler.shutdown()

class CertidaoRepository(ICertidaoRepository):
    def __init__(self, database: Database, upload_dir: str = "uploads/certidoes"):
        self.db = database
        self.upload_dir = upload_dir
        self.api_service = CertidaoApiMock()
        self.api_service.set_database(database)
        os.makedirs(upload_dir, exist_ok=True)
        
        # Inicia job de revalidação
        self.api_service.iniciar_revalidacao_periodica()

    def _salvar_arquivo(self, arquivo: BinaryIO, nome_arquivo: str) -> str:
        """
        Salva o arquivo no sistema de arquivos e retorna o caminho
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_base, extensao = os.path.splitext(nome_arquivo)
        hash_nome = hashlib.md5(f"{nome_base}{timestamp}".encode()).hexdigest()
        novo_nome = f"{hash_nome}{extensao}"
        
        caminho_arquivo = os.path.join(self.upload_dir, novo_nome)
        
        with open(caminho_arquivo, 'wb') as destino:
            arquivo.seek(0)
            destino.write(arquivo.read())
            
        return caminho_arquivo

    def criar(self, certidao: Certidao, arquivo: Optional[BinaryIO] = None) -> Certidao:
        """
        Cria uma nova certidão, opcionalmente com arquivo anexo
        """
        if arquivo:
            erros = self.validar_arquivo(arquivo, arquivo.filename)
            if erros:
                raise ValueError(erros)
            certidao.arquivo_url = self._salvar_arquivo(arquivo, arquivo.filename)

        query = """
            INSERT INTO certidoes (
                credor_id, tipo, origem, arquivo_url,
                conteudo_base64, status, recebida_em,
                valida_ate
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        certidao_id = self.db.execute(
            query,
            (
                certidao.credor_id, certidao.tipo.value,
                certidao.origem.value, certidao.arquivo_url,
                certidao.conteudo_base64, certidao.status.value,
                certidao.recebida_em,
                certidao.valida_ate or (datetime.now() + timedelta(days=30))
            )
        )
        certidao.id = certidao_id
        return certidao

    def buscar_por_id(self, certidao_id: int) -> Optional[Certidao]:
        """
        Busca uma certidão por ID
        """
        query = "SELECT * FROM certidoes WHERE id = ?"
        result = self.db.fetch_one(query, (certidao_id,))
        
        if result:
            return Certidao(
                id=result['id'],
                credor_id=result['credor_id'],
                tipo=TipoCertidao(result['tipo']),
                origem=OrigemCertidao(result['origem']),
                arquivo_url=result['arquivo_url'],
                conteudo_base64=result['conteudo_base64'],
                status=StatusCertidao(result['status']),
                recebida_em=datetime.fromisoformat(result['recebida_em']),
                valida_ate=datetime.fromisoformat(result['valida_ate']) if result['valida_ate'] else None
            )
        return None

    def buscar_por_credor(self, credor_id: int) -> List[Certidao]:
        """
        Busca todas as certidões de um credor
        """
        query = "SELECT * FROM certidoes WHERE credor_id = ?"
        results = self.db.fetch_all(query, (credor_id,))
        
        return [
            Certidao(
                id=row['id'],
                credor_id=row['credor_id'],
                tipo=TipoCertidao(row['tipo']),
                origem=OrigemCertidao(row['origem']),
                arquivo_url=row['arquivo_url'],
                conteudo_base64=row['conteudo_base64'],
                status=StatusCertidao(row['status']),
                recebida_em=datetime.fromisoformat(row['recebida_em']),
                valida_ate=datetime.fromisoformat(row['valida_ate']) if row['valida_ate'] else None
            )
            for row in results
        ]

    def buscar_por_tipo(self, credor_id: int, tipo: TipoCertidao) -> Optional[Certidao]:
        """
        Busca certidão de um credor por tipo
        """
        query = "SELECT * FROM certidoes WHERE credor_id = ? AND tipo = ?"
        result = self.db.fetch_one(query, (credor_id, tipo.value))
        
        if result:
            return Certidao(
                id=result['id'],
                credor_id=result['credor_id'],
                tipo=TipoCertidao(result['tipo']),
                origem=OrigemCertidao(result['origem']),
                arquivo_url=result['arquivo_url'],
                conteudo_base64=result['conteudo_base64'],
                status=StatusCertidao(result['status']),
                recebida_em=datetime.fromisoformat(result['recebida_em']),
                valida_ate=datetime.fromisoformat(result['valida_ate']) if result['valida_ate'] else None
            )
        return None

    def listar_todas(self) -> List[Certidao]:
        """
        Lista todas as certidões
        """
        query = "SELECT * FROM certidoes"
        results = self.db.fetch_all(query)
        
        return [
            Certidao(
                id=row['id'],
                credor_id=row['credor_id'],
                tipo=TipoCertidao(row['tipo']),
                origem=OrigemCertidao(row['origem']),
                arquivo_url=row['arquivo_url'],
                conteudo_base64=row['conteudo_base64'],
                status=StatusCertidao(row['status']),
                recebida_em=datetime.fromisoformat(row['recebida_em']),
                valida_ate=datetime.fromisoformat(row['valida_ate']) if row['valida_ate'] else None
            )
            for row in results
        ]

    def atualizar(self, certidao: Certidao, arquivo: Optional[BinaryIO] = None) -> Certidao:
        """
        Atualiza os dados de uma certidão e opcionalmente o arquivo
        """
        if arquivo:
            erros = self.validar_arquivo(arquivo, arquivo.filename)
            if erros:
                raise ValueError(erros)

            if os.path.exists(certidao.arquivo_url or ''):
                os.remove(certidao.arquivo_url)

            certidao.arquivo_url = self._salvar_arquivo(arquivo, arquivo.filename)

        query = """
            UPDATE certidoes
            SET tipo = ?, origem = ?, arquivo_url = ?,
                conteudo_base64 = ?, status = ?, recebida_em = ?,
                valida_ate = ?, updated_at = ?
            WHERE id = ?
        """
        self.db.execute(
            query,
            (
                certidao.tipo.value, certidao.origem.value,
                certidao.arquivo_url, certidao.conteudo_base64,
                certidao.status.value, certidao.recebida_em,
                certidao.valida_ate, datetime.now(),
                certidao.id
            )
        )
        return certidao

    def deletar(self, certidao_id: int) -> bool:
        """
        Deleta uma certidão e seu arquivo
        """
        certidao = self.buscar_por_id(certidao_id)
        if certidao and certidao.arquivo_url and os.path.exists(certidao.arquivo_url):
            os.remove(certidao.arquivo_url)

        query = "DELETE FROM certidoes WHERE id = ?"
        self.db.execute(query, (certidao_id,))
        return True

    def validar_arquivo(self, arquivo: BinaryIO, nome_arquivo: str) -> List[str]:
        """
        Valida o arquivo enviado
        """
        erros = []
        
        # Valida extensão
        _, extensao = os.path.splitext(nome_arquivo.lower())
        if extensao not in ['.pdf']:
            erros.append("Apenas arquivos PDF são permitidos")

        # Valida tamanho
        arquivo.seek(0, os.SEEK_END)
        tamanho = arquivo.tell()
        arquivo.seek(0)
        
        if tamanho > Certidao.tamanho_maximo():
            erros.append(f"Arquivo muito grande. Máximo: {Certidao.tamanho_maximo()/1024/1024}MB")

        return erros

    def gerar_url_arquivo(self, certidao_id: int) -> str:
        """
        Gera URL para download do arquivo
        """
        certidao = self.buscar_por_id(certidao_id)
        if not certidao:
            raise ValueError("Certidão não encontrada")
            
        return f"/certidoes/download/{certidao_id}"