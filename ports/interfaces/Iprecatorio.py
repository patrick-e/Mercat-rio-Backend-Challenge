from abc import ABC, abstractmethod
from typing import Optional, List
from core.entities.precatorio import Precatorio

class IPrecatorioRepository(ABC):
    @abstractmethod
    def criar(self, precatorio: Precatorio) -> Precatorio:
        """
        Cria um novo precatório
        """
        pass

    @abstractmethod
    def buscar_por_id(self, precatorio_id: int) -> Optional[Precatorio]:
        """
        Busca um precatório por ID
        """
        pass

    @abstractmethod
    def buscar_por_numero(self, numero_precatorio: str) -> Optional[Precatorio]:
        """
        Busca um precatório por número
        """
        pass

    @abstractmethod
    def buscar_por_credor(self, credor_id: int) -> List[Precatorio]:
        """
        Busca todos os precatórios de um credor
        """
        pass

    @abstractmethod
    def listar_todos(self) -> List[Precatorio]:
        """
        Lista todos os precatórios
        """
        pass

    @abstractmethod
    def atualizar(self, precatorio: Precatorio) -> Precatorio:
        """
        Atualiza os dados de um precatório
        """
        pass

    @abstractmethod
    def deletar(self, precatorio_id: int) -> bool:
        """
        Deleta um precatório
        """
        pass

    @abstractmethod
    def buscar_por_foro(self, foro: str) -> List[Precatorio]:
        """
        Busca precatórios por foro
        """
        pass