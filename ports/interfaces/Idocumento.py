from abc import ABC, abstractmethod
from typing import Optional, List, BinaryIO
from core.entities.documento import Documento, TipoDocumento

class IDocumentoRepository(ABC):
    @abstractmethod
    def criar(self, documento: Documento, arquivo: BinaryIO) -> Documento:
        """
        Cria um novo documento e salva o arquivo
        """
        pass

    @abstractmethod
    def buscar_por_id(self, documento_id: int) -> Optional[Documento]:
        """
        Busca um documento por ID
        """
        pass

    @abstractmethod
    def buscar_por_credor(self, credor_id: int) -> List[Documento]:
        """
        Busca todos os documentos de um credor
        """
        pass

    @abstractmethod
    def buscar_por_tipo(self, credor_id: int, tipo: TipoDocumento) -> Optional[Documento]:
        """
        Busca documento de um credor por tipo
        """
        pass

    @abstractmethod
    def listar_todos(self) -> List[Documento]:
        """
        Lista todos os documentos
        """
        pass

    @abstractmethod
    def atualizar(self, documento: Documento, arquivo: Optional[BinaryIO] = None) -> Documento:
        """
        Atualiza os dados de um documento e opcionalmente o arquivo
        """
        pass

    @abstractmethod
    def deletar(self, documento_id: int) -> bool:
        """
        Deleta um documento e seu arquivo
        """
        pass

    @abstractmethod
    def validar_arquivo(self, arquivo: BinaryIO, nome_arquivo: str) -> List[str]:
        """
        Valida o arquivo enviado:
        - Extensão permitida
        - Tamanho máximo
        - Integridade do arquivo
        Retorna lista de erros (vazia se válido)
        """
        pass

    @abstractmethod
    def gerar_url_arquivo(self, documento_id: int) -> str:
        """
        Gera URL para download do arquivo
        """
        pass