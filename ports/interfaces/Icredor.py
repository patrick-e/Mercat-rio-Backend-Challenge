from abc import ABC, abstractmethod
from typing import Optional, List
from core.entities.credor import Credor
from core.entities.precatorio import Precatorio
from core.entities.documento import Documento
from core.entities.certidao import Certidao

class ICredorRepository(ABC):
    @abstractmethod
    def criar(self, credor: Credor, precatorio: Precatorio) -> Credor:
        """
        Cria um novo credor com seu precatório associado
        """
        pass

    @abstractmethod
    def buscar_por_id(self, credor_id: int) -> Optional[Credor]:
        """
        Busca um credor por ID
        """
        pass

    @abstractmethod
    def buscar_por_cpf_cnpj(self, cpf_cnpj: str) -> Optional[Credor]:
        """
        Busca um credor por CPF/CNPJ
        """
        pass

    @abstractmethod
    def listar_todos(self) -> List[Credor]:
        """
        Lista todos os credores
        """
        pass

    @abstractmethod
    def buscar_detalhes(self, credor_id: int) -> Optional[dict]:
        """
        Busca todos os detalhes do credor, incluindo:
        - Dados do credor
        - Precatório
        - Documentos
        - Certidões
        """
        pass

    @abstractmethod
    def atualizar(self, credor: Credor) -> Credor:
        """
        Atualiza os dados de um credor
        """
        pass

    @abstractmethod
    def deletar(self, credor_id: int) -> bool:
        """
        Deleta um credor e seus dados relacionados
        """
        pass