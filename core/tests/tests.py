import unittest
from datetime import datetime, timedelta
from decimal import Decimal
from core.entities.credor import Credor
from core.entities.precatorio import Precatorio
from core.entities.documento import Documento, TipoDocumento
from core.entities.certidao import (
    Certidao,
    TipoCertidao,
    OrigemCertidao,
    StatusCertidao
)

class TestEntidades(unittest.TestCase):
    def test_validacao_credor(self):
        # Credor válido
        credor = Credor(
            nome="João da Silva",
            cpf_cnpj="12345678900",
            email="joao@email.com",
            telefone="11999999999"
        )
        self.assertEqual(len(credor.validar()), 0)

        # Credor inválido
        credor_invalido = Credor(
            nome="",
            cpf_cnpj="123",
            email="email_invalido",
            telefone="123"
        )
        erros = credor_invalido.validar()
        self.assertEqual(len(erros), 4)

    def test_validacao_precatorio(self):
        # Precatório válido
        precatorio = Precatorio(
            credor_id=1,
            numero_precatorio="0001234-56.2020.8.26.0050",
            valor_nominal=Decimal("50000.00"),
            foro="TJSP",
            data_publicacao=datetime.now()
        )
        self.assertEqual(len(precatorio.validar()), 0)

        # Precatório inválido
        precatorio_invalido = Precatorio(
            credor_id=0,
            numero_precatorio="123",
            valor_nominal=Decimal("0.0"),
            foro="",
            data_publicacao=None
        )
        erros = precatorio_invalido.validar()
        self.assertEqual(len(erros), 5)

    def test_validacao_documento(self):
        # Documento válido
        documento = Documento(
            credor_id=1,
            tipo=TipoDocumento.IDENTIDADE,
            arquivo_url="/arquivos/rg.pdf",
            enviado_em=datetime.now()
        )
        self.assertEqual(len(documento.validar()), 0)

        # Documento inválido
        documento_invalido = Documento(
            credor_id=0,
            tipo="tipo_invalido",
            arquivo_url="",
            enviado_em=None
        )
        erros = documento_invalido.validar()
        self.assertEqual(len(erros), 4)

    def test_validacao_certidao(self):
        # Certidão válida
        certidao = Certidao(
            credor_id=1,
            tipo=TipoCertidao.FEDERAL,
            origem=OrigemCertidao.API,
            conteudo_base64="base64_content",
            status=StatusCertidao.NEGATIVA,
            recebida_em=datetime.now(),
            valida_ate=datetime.now() + timedelta(days=30)
        )
        self.assertEqual(len(certidao.validar()), 0)

        # Certidão inválida
        certidao_invalida = Certidao(
            credor_id=0,
            tipo="tipo_invalido",
            origem="origem_invalida",
            arquivo_url="",
            conteudo_base64="",
            status="status_invalido",
            recebida_em=None
        )
        erros = certidao_invalida.validar()
        self.assertEqual(len(erros), 6)

    def test_validade_certidao(self):
        # Certidão válida
        certidao = Certidao(
            credor_id=1,
            tipo=TipoCertidao.FEDERAL,
            origem=OrigemCertidao.API,
            conteudo_base64="base64_content",
            status=StatusCertidao.NEGATIVA,
            recebida_em=datetime.now(),
            valida_ate=datetime.now() + timedelta(days=30)
        )
        self.assertTrue(certidao.esta_valida())

        # Certidão vencida
        certidao_vencida = Certidao(
            credor_id=1,
            tipo=TipoCertidao.FEDERAL,
            origem=OrigemCertidao.API,
            conteudo_base64="base64_content",
            status=StatusCertidao.NEGATIVA,
            recebida_em=datetime.now() - timedelta(days=60),
            valida_ate=datetime.now() - timedelta(days=30)
        )
        self.assertFalse(certidao_vencida.esta_valida())

if __name__ == '__main__':
    unittest.main()