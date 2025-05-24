from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Depends
import asyncio
import random
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import List, Optional, Dict
import uvicorn
from datetime import datetime
from pydantic import BaseModel, Field
from decimal import Decimal
import base64
import traceback
from datetime import timedelta
from enum import Enum
import os
from typing import Optional, Union

# Importações das entidades
from core.entities.credor import Credor
from core.entities.precatorio import Precatorio
from core.entities.documento import Documento, TipoDocumento
from core.entities.certidao import Certidao, TipoCertidao, OrigemCertidao, StatusCertidao

# Importações dos repositórios
from ports.database.database import Database
from adapters.repositories.credor_repository import CredorRepository
from adapters.repositories.precatorio_repository import PrecatorioRepository
from adapters.repositories.documento_repository import DocumentoRepository
from adapters.repositories.certidao_repository import CertidaoRepository, CertidaoApiMock

app = FastAPI(
    title="Mercatório Backend Challenge",
    description="API para originação de precatórios",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar servindo de arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

db = Database()
credor_repo = CredorRepository(db)
precatorio_repo = PrecatorioRepository(db)
documento_repo = DocumentoRepository(db)
certidao_repo = CertidaoRepository(db)
certidao_api = CertidaoApiMock()
certidao_api.set_database(db)

from pydantic import BaseModel, Field

class PrecatorioRequest(BaseModel):
    numero_precatorio: str = Field(
        description="Número do precatório no formato 0000000-00.0000.0.00.0000",
        example="0000123-45.2024.1.00.0000"
    )
    valor_nominal: Decimal = Field(
        description="Valor nominal do precatório",
        example="50000.00"
    )
    foro: str = Field(
        description="Foro onde o precatório foi emitido",
        example="São Paulo"
    )
    data_publicacao: datetime = Field(
        description="Data de publicação do precatório",
        example="2024-05-24T00:00:00"
    )

    class Config:
        json_encoders = {Decimal: lambda v: str(v)}

class CredorRequest(BaseModel):
    nome: str = Field(
        description="Nome completo do credor",
        example="João da Silva"
    )
    cpf_cnpj: str = Field(
        description="CPF (11 dígitos) ou CNPJ (14 dígitos), apenas números",
        example="12345678901"
    )
    email: str = Field(
        description="Email válido do credor",
        example="joao@email.com"
    )
    telefone: str = Field(
        description="Telefone com DDD, 10 ou 11 dígitos",
        example="11999999999"
    )
    precatorio: PrecatorioRequest = Field(
        description="Dados do precatório"
    )

class TipoDocumentoEnum(str, Enum):
    IDENTIDADE = "identidade"
    COMPROVANTE_RESIDENCIA = "comprovante_residencia"
    OUTROS = "outros"

class DocumentoRequest(BaseModel):
    tipo: TipoDocumentoEnum = Field(
        description="Tipo do documento",
        example="identidade"
    )

class TipoCertidaoEnum(str, Enum):
    FEDERAL = "federal"
    ESTADUAL = "estadual"
    MUNICIPAL = "municipal"
    TRABALHISTA = "trabalhista"

class CertidaoUploadRequest(BaseModel):
    tipo: TipoCertidaoEnum = Field(
        description="Tipo da certidão",
        example="federal"
    )

def save_uploaded_file(file: UploadFile, folder: str) -> str:
    """
    Salva um arquivo enviado em uma pasta específica e retorna o caminho relativo
    """
    # Cria a pasta se não existir
    os.makedirs(folder, exist_ok=True)
    
    # Gera um nome único para o arquivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    filepath = os.path.join(folder, filename)
    
    # Salva o arquivo
    with open(filepath, "wb") as buffer:
        content = file.file.read()
        buffer.write(content)
    
    return filepath

@app.post("/credores", status_code=201)
async def criar_credor(credor_request: CredorRequest):
    try:
        # Criar e validar o credor
        credor = Credor(
            nome=credor_request.nome,
            cpf_cnpj=credor_request.cpf_cnpj,
            email=credor_request.email,
            telefone=credor_request.telefone
        )
        
        erros = credor.validar()
        if erros:
            print(f"Erros de validação do credor: {erros}")
            raise HTTPException(status_code=400, detail=erros)
        
        # Criar o precatório sem validar (a validação será feita pelo CredorRepository)
        precatorio = Precatorio(
            numero_precatorio=credor_request.precatorio.numero_precatorio,
            valor_nominal=credor_request.precatorio.valor_nominal,
            foro=credor_request.precatorio.foro,
            data_publicacao=credor_request.precatorio.data_publicacao
        )
        
        # Criar credor e precatório em uma única transação
        credor = credor_repo.criar(credor, precatorio)
        return {"message": "Credor cadastrado com sucesso", "id": credor.id}
        
    except HTTPException as http_err:
        print(f"Erro ao criar credor: {str(http_err)}")
        raise http_err
    except ValueError as ve:
        if "Já existe um credor cadastrado com o CPF/CNPJ" in str(ve):
            print(f"Tentativa de criar credor duplicado: {str(ve)}")
            raise HTTPException(status_code=409, detail=str(ve))
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Erro ao criar credor: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/credores/{credor_id}")
async def buscar_credor(credor_id: int):
    try:
        detalhes = credor_repo.buscar_detalhes(credor_id)
        if not detalhes:
            raise HTTPException(status_code=404, detail="Credor não encontrado")
        return detalhes
    except Exception as e:
        print(f"Erro ao buscar credor: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/credores/{credor_id}/documentos", status_code=201)
async def upload_documento(
    credor_id: int,
    tipo: TipoDocumentoEnum,
    arquivo: UploadFile = File(...)
):
    try:
        # Verificar se o credor existe
        credor = credor_repo.buscar_por_id(credor_id)
        if not credor:
            raise HTTPException(status_code=404, detail="Credor não encontrado")
        
        # Validar extensão do arquivo (opcional)
        extensoes_permitidas = {".pdf", ".jpg", ".jpeg", ".png"}
        ext = os.path.splitext(arquivo.filename)[1].lower()
        if ext not in extensoes_permitidas:
            raise HTTPException(
                status_code=400,
                detail=f"Extensão não permitida. Use: {', '.join(extensoes_permitidas)}"
            )
        
        # Salvar arquivo
        pasta_documentos = os.path.join("static", "documentos", str(credor_id))
        arquivo_url = save_uploaded_file(arquivo, pasta_documentos)
        
        # Criar documento
        documento = Documento(
            credor_id=credor_id,
            tipo=tipo.value,
            arquivo_url=arquivo_url,
            enviado_em=datetime.now()
        )
        
        # Salvar no banco
        documento = documento_repo.criar(documento)
        
        return {
            "message": "Documento enviado com sucesso",
            "documento": {
                "id": documento.id,
                "tipo": documento.tipo,
                "arquivo_url": documento.arquivo_url,
                "enviado_em": documento.enviado_em
            }
        }
        
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        print(f"Erro ao fazer upload do documento: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/credores/{credor_id}/certidoes", status_code=201)
async def upload_certidao(
    credor_id: int,
    tipo: TipoCertidaoEnum,
    arquivo: UploadFile = File(...)
):
    try:
        # Verificar se o credor existe
        credor = credor_repo.buscar_por_id(credor_id)
        if not credor:
            raise HTTPException(status_code=404, detail="Credor não encontrado")
        
        # Validar extensão do arquivo
        extensoes_permitidas = {".pdf"}
        ext = os.path.splitext(arquivo.filename)[1].lower()
        if ext not in extensoes_permitidas:
            raise HTTPException(
                status_code=400,
                detail=f"Extensão não permitida. Use: {', '.join(extensoes_permitidas)}"
            )
        
        # Salvar arquivo
        pasta_certidoes = os.path.join("static", "certidoes", str(credor_id))
        arquivo_url = save_uploaded_file(arquivo, pasta_certidoes)
        
        # Converter arquivo para base64
        with open(arquivo_url, "rb") as f:
            conteudo_base64 = base64.b64encode(f.read()).decode()
        
        # Criar certidão
        certidao = Certidao(
            credor_id=credor_id,
            tipo=tipo.value,
            origem="manual",
            arquivo_url=arquivo_url,
            conteudo_base64=conteudo_base64,
            status="pendente",
            recebida_em=datetime.now(),
            valida_ate=datetime.now() + timedelta(days=30)  # Validade padrão de 30 dias
        )
        
        # Salvar no banco
        certidao = certidao_repo.criar(certidao)
        
        return {
            "message": "Certidão enviada com sucesso",
            "certidao": {
                "id": certidao.id,
                "tipo": certidao.tipo,
                "status": certidao.status,
                "valida_ate": certidao.valida_ate
            }
        }
        
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        print(f"Erro ao fazer upload da certidão: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/credores/{credor_id}/buscar-certidoes", status_code=200)
async def buscar_certidoes(credor_id: int):
    try:
        # Verificar se o credor existe
        credor = credor_repo.buscar_por_id(credor_id)
        if not credor:
            raise HTTPException(status_code=404, detail="Credor não encontrado")
        
        # Consultar certidões via API mock
        certidoes = await mock_consulta_certidoes(credor.cpf_cnpj)
        
        # Salvar cada certidão retornada
        for cert_data in certidoes["certidoes"]:
            certidao = Certidao(
                credor_id=credor_id,
                tipo=cert_data["tipo"],
                origem="api",
                conteudo_base64=cert_data["conteudo_base64"],
                status=cert_data["status"],
                recebida_em=datetime.now(),
                valida_ate=datetime.now() + timedelta(days=30)
            )
            certidao_repo.criar(certidao)
        
        return {
            "message": "Certidões consultadas e salvas com sucesso",
            "quantidade": len(certidoes["certidoes"])
        }
        
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        print(f"Erro ao buscar certidões: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# API Mock para consulta de certidões
@app.get("/api/certidoes")
async def mock_consulta_certidoes(cpf_cnpj: str):
    try:
        # Simular delay de API externa
        await asyncio.sleep(1)
        
        # Gerar certidões aleatórias
        tipos = ["federal", "estadual", "municipal", "trabalhista"]
        status = ["positiva", "negativa"]
        
        certidoes = []
        for tipo in tipos:
            # Gerar PDF fake em base64
            fake_pdf = f"Certidão {tipo.upper()} para {cpf_cnpj}".encode()
            conteudo_base64 = base64.b64encode(fake_pdf).decode()
            
            certidoes.append({
                "tipo": tipo,
                "status": random.choice(status),
                "conteudo_base64": conteudo_base64
            })
        
        return {
            "cpf_cnpj": cpf_cnpj,
            "certidoes": certidoes
        }
        
    except Exception as e:
        print(f"Erro na API mock: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Criar pastas necessárias
    os.makedirs(os.path.join("static", "documentos"), exist_ok=True)
    os.makedirs(os.path.join("static", "certidoes"), exist_ok=True)
    
    # Iniciar servidor
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)