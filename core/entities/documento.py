from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from enum import Enum

class TipoDocumento(Enum):
    IDENTIDADE = "identidade"
    COMPROVANTE_RESIDENCIA = "comprovante_residencia"
    OUTROS = "outros"

@dataclass
class Documento:
    id: Optional[int] = None
    credor_id: int = 0
    tipo: TipoDocumento = TipoDocumento.OUTROS
    arquivo_url: str = ""
    enviado_em: datetime = datetime.now()
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    
    def validar_arquivo_url(self) -> bool:
        """
        Valida se a URL do arquivo está no formato esperado
        """
        return bool(self.arquivo_url and self.arquivo_url.strip())
    
    def validar_tipo_documento(self) -> bool:
        """
        Valida se o tipo do documento é válido
        """
        return isinstance(self.tipo, TipoDocumento)
    
    def validar(self) -> List[str]:
        """
        Retorna lista de erros de validação.
        Lista vazia significa que está tudo válido.
        """
        erros = []
        
        if not self.credor_id:
            erros.append("Credor é obrigatório")
            
        if not self.validar_tipo_documento():
            erros.append("Tipo de documento inválido")
            
        if not self.validar_arquivo_url():
            erros.append("URL do arquivo é obrigatória")
            
        if not self.enviado_em:
            erros.append("Data de envio é obrigatória")
            
        return erros

    @staticmethod
    def extensoes_permitidas() -> List[str]:
        """
        Retorna lista de extensões de arquivo permitidas
        """
        return ['.pdf', '.jpg', '.jpeg', '.png']

    @staticmethod
    def tamanho_maximo() -> int:
        """
        Retorna tamanho máximo permitido para arquivos em bytes
        10MB = 10 * 1024 * 1024
        """
        return 10 * 1024 * 1024