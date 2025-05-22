from abc import ABC, abstractmethod
from typing import Optional, List, BinaryIO, Dict
from core.entities.certidao import Certidao, TipoCertidao, StatusCertidao

class ICertidaoRepository(ABC):
    @abstractmethod
    def criar(self, certidao: Certidao, arquivo: Optional[BinaryIO] = None) -> Certidao:
        """
        Cria uma nova certidão, opcionalmente com arquivo anexo
        """
        pass

    @abstractmethod
    def buscar_por_id(self, certidao_id: int) -> Optional[Certidao]:
        """
        Busca uma certidão por ID
        """
        pass

    @abstractmethod
    def buscar_por_credor(self, credor_id: int) -> List[Certidao]:
        """
        Busca todas as certidões de um credor
        """
        pass

    @abstractmethod
    def buscar_por_tipo(self, credor_id: int, tipo: TipoCertidao) -> Optional[Certidao]:
        """
        Busca certidão de um credor por tipo
        """
        pass

    @abstractmethod
    def listar_todas(self) -> List[Certidao]:
        """
        Lista todas as certidões
        """
        pass

    @abstractmethod
    def atualizar(self, certidao: Certidao, arquivo: Optional[BinaryIO] = None) -> Certidao:
        """
        Atualiza os dados de uma certidão e opcionalmente o arquivo
        """
        pass

    @abstractmethod
    def deletar(self, certidao_id: int) -> bool:
        """
        Deleta uma certidão e seu arquivo
        """
        pass

    @abstractmethod
    def validar_arquivo(self, arquivo: BinaryIO, nome_arquivo: str) -> List[str]:
        """
        Valida o arquivo enviado:
        - Extensão permitida (.pdf)
        - Tamanho máximo
        - Integridade do arquivo
        Retorna lista de erros (vazia se válido)
        """
        pass

    @abstractmethod
    def gerar_url_arquivo(self, certidao_id: int) -> str:
        """
        Gera URL para download do arquivo
        """
        pass

class ICertidaoApiService(ABC):
    @abstractmethod
    def buscar_certidoes(self, cpf_cnpj: str) -> List[Dict]:
        """
        Busca certidões via API mock
        Retorna lista de dicionários com dados das certidões:
        [
            {
                "tipo": "federal",
                "status": "negativa",
                "conteudo_base64": "..."
            }
        ]
        """
        pass

    @abstractmethod
    def validar_certidao(self, certidao_id: int) -> StatusCertidao:
        """
        Revalida uma certidão existente via API mock
        Retorna o novo status da certidão
        """
        pass

    @abstractmethod
    def revalidar_certidoes_vencidas(self) -> int:
        """
        Job para revalidar certidões vencidas automaticamente
        Retorna quantidade de certidões revalidadas
        """
        pass