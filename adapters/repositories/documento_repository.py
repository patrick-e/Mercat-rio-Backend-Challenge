import os
from typing import Optional, List, BinaryIO
from datetime import datetime
import hashlib
from core.entities.documento import Documento, TipoDocumento
from ports.interfaces.Idocumento import IDocumentoRepository
from ports.database.database import Database

class DocumentoRepository(IDocumentoRepository):
    def __init__(self, database: Database, upload_dir: str = "uploads/documentos"):
        self.db = database
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)

    def _salvar_arquivo(self, arquivo: BinaryIO, nome_arquivo: str) -> str:
        """
        Salva o arquivo no sistema de arquivos e retorna o caminho
        """
        # Gera um hash único para o nome do arquivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_base, extensao = os.path.splitext(nome_arquivo)
        hash_nome = hashlib.md5(f"{nome_base}{timestamp}".encode()).hexdigest()
        novo_nome = f"{hash_nome}{extensao}"
        
        caminho_arquivo = os.path.join(self.upload_dir, novo_nome)
        
        with open(caminho_arquivo, 'wb') as destino:
            arquivo.seek(0)  # Volta para o início do arquivo
            destino.write(arquivo.read())
            
        return caminho_arquivo

    def criar(self, documento: Documento, arquivo: BinaryIO) -> Documento:
        """
        Cria um novo documento e salva o arquivo
        """
        # Valida e salva o arquivo
        erros = self.validar_arquivo(arquivo, arquivo.filename)
        if erros:
            raise ValueError(erros)

        caminho_arquivo = self._salvar_arquivo(arquivo, arquivo.filename)
        documento.arquivo_url = caminho_arquivo

        query = """
            INSERT INTO documentos (
                credor_id, tipo, arquivo_url, enviado_em
            ) VALUES (?, ?, ?, ?)
        """
        documento_id = self.db.execute(
            query,
            (
                documento.credor_id, documento.tipo.value,
                documento.arquivo_url, documento.enviado_em
            )
        )
        documento.id = documento_id
        return documento

    def buscar_por_id(self, documento_id: int) -> Optional[Documento]:
        """
        Busca um documento por ID
        """
        query = "SELECT * FROM documentos WHERE id = ?"
        result = self.db.fetch_one(query, (documento_id,))
        
        if result:
            return Documento(
                id=result['id'],
                credor_id=result['credor_id'],
                tipo=TipoDocumento(result['tipo']),
                arquivo_url=result['arquivo_url'],
                enviado_em=datetime.fromisoformat(result['enviado_em'])
            )
        return None

    def buscar_por_credor(self, credor_id: int) -> List[Documento]:
        """
        Busca todos os documentos de um credor
        """
        query = "SELECT * FROM documentos WHERE credor_id = ?"
        results = self.db.fetch_all(query, (credor_id,))
        
        return [
            Documento(
                id=row['id'],
                credor_id=row['credor_id'],
                tipo=TipoDocumento(row['tipo']),
                arquivo_url=row['arquivo_url'],
                enviado_em=datetime.fromisoformat(row['enviado_em'])
            )
            for row in results
        ]

    def buscar_por_tipo(self, credor_id: int, tipo: TipoDocumento) -> Optional[Documento]:
        """
        Busca documento de um credor por tipo
        """
        query = "SELECT * FROM documentos WHERE credor_id = ? AND tipo = ?"
        result = self.db.fetch_one(query, (credor_id, tipo.value))
        
        if result:
            return Documento(
                id=result['id'],
                credor_id=result['credor_id'],
                tipo=TipoDocumento(result['tipo']),
                arquivo_url=result['arquivo_url'],
                enviado_em=datetime.fromisoformat(result['enviado_em'])
            )
        return None

    def listar_todos(self) -> List[Documento]:
        """
        Lista todos os documentos
        """
        query = "SELECT * FROM documentos"
        results = self.db.fetch_all(query)
        
        return [
            Documento(
                id=row['id'],
                credor_id=row['credor_id'],
                tipo=TipoDocumento(row['tipo']),
                arquivo_url=row['arquivo_url'],
                enviado_em=datetime.fromisoformat(row['enviado_em'])
            )
            for row in results
        ]

    def atualizar(self, documento: Documento, arquivo: Optional[BinaryIO] = None) -> Documento:
        """
        Atualiza os dados de um documento e opcionalmente o arquivo
        """
        if arquivo:
            # Valida e salva o novo arquivo
            erros = self.validar_arquivo(arquivo, arquivo.filename)
            if erros:
                raise ValueError(erros)

            # Remove o arquivo antigo
            if os.path.exists(documento.arquivo_url):
                os.remove(documento.arquivo_url)

            # Salva o novo arquivo
            documento.arquivo_url = self._salvar_arquivo(arquivo, arquivo.filename)

        query = """
            UPDATE documentos
            SET tipo = ?, arquivo_url = ?, enviado_em = ?, updated_at = ?
            WHERE id = ?
        """
        self.db.execute(
            query,
            (
                documento.tipo.value, documento.arquivo_url,
                documento.enviado_em, datetime.now(),
                documento.id
            )
        )
        return documento

    def deletar(self, documento_id: int) -> bool:
        """
        Deleta um documento e seu arquivo
        """
        # Busca o documento para obter o caminho do arquivo
        documento = self.buscar_por_id(documento_id)
        if documento and os.path.exists(documento.arquivo_url):
            os.remove(documento.arquivo_url)

        query = "DELETE FROM documentos WHERE id = ?"
        self.db.execute(query, (documento_id,))
        return True

    def validar_arquivo(self, arquivo: BinaryIO, nome_arquivo: str) -> List[str]:
        """
        Valida o arquivo enviado
        """
        erros = []
        
        # Valida extensão
        _, extensao = os.path.splitext(nome_arquivo.lower())
        if extensao not in Documento.extensoes_permitidas():
            erros.append(f"Extensão não permitida. Use: {Documento.extensoes_permitidas()}")

        # Valida tamanho
        arquivo.seek(0, os.SEEK_END)
        tamanho = arquivo.tell()
        arquivo.seek(0)
        
        if tamanho > Documento.tamanho_maximo():
            erros.append(f"Arquivo muito grande. Máximo: {Documento.tamanho_maximo()/1024/1024}MB")

        return erros

    def gerar_url_arquivo(self, documento_id: int) -> str:
        """
        Gera URL para download do arquivo
        """
        documento = self.buscar_por_id(documento_id)
        if not documento:
            raise ValueError("Documento não encontrado")
            
        return f"/documentos/download/{documento_id}"