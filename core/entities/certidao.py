from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from enum import Enum

class TipoCertidao(Enum):
    FEDERAL = "federal"
    ESTADUAL = "estadual"
    MUNICIPAL = "municipal"
    TRABALHISTA = "trabalhista"

class OrigemCertidao(Enum):
    MANUAL = "manual"
    API = "api"

class StatusCertidao(Enum):
    NEGATIVA = "negativa"
    POSITIVA = "positiva"
    INVALIDA = "invalida"
    PENDENTE = "pendente"

@dataclass
class Certidao:
    id: Optional[int] = None
    credor_id: int = 0
    tipo: TipoCertidao = TipoCertidao.FEDERAL
    origem: OrigemCertidao = OrigemCertidao.MANUAL
    arquivo_url: Optional[str] = None
    conteudo_base64: Optional[str] = None
    status: StatusCertidao = StatusCertidao.PENDENTE
    recebida_em: datetime = datetime.now()
    valida_ate: Optional[datetime] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    def validar_arquivo_ou_conteudo(self) -> bool:
        """
        Valida se possui arquivo_url OU conteudo_base64
        """
        return bool(self.arquivo_url or self.conteudo_base64)

    def validar_tipo_certidao(self) -> bool:
        """
        Valida se o tipo da certidão é válido
        """
        return isinstance(self.tipo, TipoCertidao)

    def validar_origem_certidao(self) -> bool:
        """
        Valida se a origem da certidão é válida
        """
        return isinstance(self.origem, OrigemCertidao)

    def validar_status_certidao(self) -> bool:
        """
        Valida se o status da certidão é válido
        """
        return isinstance(self.status, StatusCertidao)

    def esta_valida(self) -> bool:
        """
        Verifica se a certidão está dentro do prazo de validade
        """
        if not self.valida_ate:
            return False
        return datetime.now() <= self.valida_ate

    def validar(self) -> List[str]:
        """
        Retorna lista de erros de validação.
        Lista vazia significa que está tudo válido.
        """
        erros = []

        if not self.credor_id:
            erros.append("Credor é obrigatório")

        if not self.validar_tipo_certidao():
            erros.append("Tipo de certidão inválido")

        if not self.validar_origem_certidao():
            erros.append("Origem da certidão inválida")

        if not self.validar_arquivo_ou_conteudo():
            erros.append("É necessário informar arquivo_url OU conteudo_base64")

        if not self.validar_status_certidao():
            erros.append("Status da certidão inválido")

        if not self.recebida_em:
            erros.append("Data de recebimento é obrigatória")

        return erros

    @staticmethod
    def extensoes_permitidas() -> List[str]:
        """
        Retorna lista de extensões de arquivo permitidas
        """
        return ['.pdf']

    @staticmethod
    def tamanho_maximo() -> int:
        """
        Retorna tamanho máximo permitido para arquivos em bytes
        5MB = 5 * 1024 * 1024
        """
        return 5 * 1024 * 1024