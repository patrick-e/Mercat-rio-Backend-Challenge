from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class Credor:
    id: Optional[int] = None
    nome: str = ""
    cpf_cnpj: str = ""
    email: str = ""
    telefone: str = ""
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    
    def validar_cpf_cnpj(self) -> bool:
        """
        Valida o formato do CPF/CNPJ.
        Apenas verifica se contém somente números e tem tamanho correto.
        """
        numeros = ''.join(filter(str.isdigit, self.cpf_cnpj))
        return len(numeros) in [11, 14]  # 11 para CPF, 14 para CNPJ
    
    def validar_email(self) -> bool:
        """
        Validação básica de email.
        """
        import re
        padrao = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return bool(re.match(padrao, self.email))
    
    def validar_telefone(self) -> bool:
        """
        Validação básica de telefone.
        Aceita formato: 11999999999
        """
        numeros = ''.join(filter(str.isdigit, self.telefone))
        return len(numeros) >= 10 and len(numeros) <= 11
    
    def validar(self) -> List[str]:
        """
        Retorna lista de erros de validação.
        Lista vazia significa que está tudo válido.
        """
        erros = []
        
        if not self.nome:
            erros.append("Nome é obrigatório")
            
        if not self.validar_cpf_cnpj():
            erros.append("CPF/CNPJ inválido")
            
        if not self.validar_email():
            erros.append("Email inválido")
            
        if not self.validar_telefone():
            erros.append("Telefone inválido")
            
        return erros