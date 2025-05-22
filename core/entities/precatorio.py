from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from decimal import Decimal

@dataclass
class Precatorio:
    id: Optional[int] = None
    credor_id: int = 0
    numero_precatorio: str = ""
    valor_nominal: Decimal = Decimal('0.0')
    foro: str = ""
    data_publicacao: datetime = datetime.now()
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    def validar_numero_precatorio(self) -> bool:
        """
        Valida o formato do número do precatório.
        Formato esperado: XXXXXXX-XX.XXXX.X.XX.XXXX
        """
        import re
        padrao = r'^\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}$'
        return bool(re.match(padrao, self.numero_precatorio))

    def validar_valor_nominal(self) -> bool:
        """
        Valida se o valor nominal é positivo
        """
        return self.valor_nominal > Decimal('0.0')

    def validar(self) -> List[str]:
        """
        Retorna lista de erros de validação.
        Lista vazia significa que está tudo válido.
        """
        erros = []

        # Não validamos credor_id na criação inicial
        # if not self.credor_id:
        #     erros.append("Credor é obrigatório")

        if not self.validar_numero_precatorio():
            erros.append("Número do precatório inválido")

        if not self.validar_valor_nominal():
            erros.append("Valor nominal deve ser maior que zero")

        if not self.foro:
            erros.append("Foro é obrigatório")

        if not self.data_publicacao:
            erros.append("Data de publicação é obrigatória")

        return erros