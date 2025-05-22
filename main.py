from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import List, Optional, Dict
import uvicorn
from datetime import datetime
from pydantic import BaseModel
from decimal import Decimal
import base64
import traceback
from datetime import timedelta

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

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instância do banco de dados
db = Database()

# Instâncias dos repositórios
credor_repo = CredorRepository(db)
precatorio_repo = PrecatorioRepository(db)
documento_repo = DocumentoRepository(db)
certidao_repo = CertidaoRepository(db)
certidao_api = CertidaoApiMock()
certidao_api.set_database(db)

# Models Pydantic para validação de requests
class PrecatorioRequest(BaseModel):
    numero_precatorio: str
    valor_nominal: Decimal
    foro: str
    data_publicacao: datetime

    class Config:
        json_encoders = {Decimal: lambda v: str(v)}

class CredorRequest(BaseModel):
    nome: str
    cpf_cnpj: str
    email: str
    telefone: str
    precatorio: PrecatorioRequest

# Rota da API Mock de Certidões
@app.get("/api/certidoes")
async def mock_certidoes(cpf_cnpj: str):
    try:
        certidoes = certidao_api.buscar_certidoes(cpf_cnpj)
        return {"cpf_cnpj": cpf_cnpj, "certidoes": certidoes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Rotas da API
@app.post("/credores", status_code=201)
async def criar_credor(credor_request: CredorRequest):
    try:
        credor = Credor(
            nome=credor_request.nome,
            cpf_cnpj=credor_request.cpf_cnpj,
            email=credor_request.email,
            telefone=credor_request.telefone
        )
        
        erros = credor.validar()
        if erros:
            raise HTTPException(status_code=400, detail=erros)
        
        precatorio = Precatorio(
            numero_precatorio=credor_request.precatorio.numero_precatorio,
            valor_nominal=credor_request.precatorio.valor_nominal,
            foro=credor_request.precatorio.foro,
            data_publicacao=credor_request.precatorio.data_publicacao
        )
        
        erros = precatorio.validar()
        if erros:
            raise HTTPException(status_code=400, detail=erros)
        
        credor = credor_repo.criar(credor, precatorio)
        return {"message": "Credor cadastrado com sucesso", "id": credor.id}

    except Exception as e:
        print(f"Erro ao criar credor: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/credores/{credor_id}/documentos", status_code=201)
async def upload_documento(credor_id: int, tipo: TipoDocumento, arquivo: UploadFile = File(...)):
    try:
        documento = Documento(
            credor_id=credor_id,
            tipo=tipo,
            enviado_em=datetime.now()
        )
        
        documento = documento_repo.criar(documento, arquivo.file)
        return {"message": "Documento enviado com sucesso", "id": documento.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Erro ao fazer upload de documento: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/credores/{credor_id}/certidoes", status_code=201)
async def upload_certidao(credor_id: int, tipo: TipoCertidao, arquivo: UploadFile = File(...)):
    try:
        certidao = Certidao(
            credor_id=credor_id,
            tipo=tipo,
            origem=OrigemCertidao.MANUAL,
            status=StatusCertidao.PENDENTE,
            recebida_em=datetime.now(),
            valida_ate=datetime.now() + timedelta(days=30)
        )
        
        certidao = certidao_repo.criar(certidao, arquivo.file)
        return {"message": "Certidão enviada com sucesso", "id": certidao.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Erro ao fazer upload de certidão: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/credores/{credor_id}/buscar-certidoes")
async def buscar_certidoes(credor_id: int, background_tasks: BackgroundTasks):
    try:
        credor = credor_repo.buscar_por_id(credor_id)
        if not credor:
            raise HTTPException(status_code=404, detail="Credor não encontrado")

        certidoes = certidao_api.buscar_certidoes(credor.cpf_cnpj)
        
        for cert_data in certidoes:
            certidao = Certidao(
                credor_id=credor_id,
                tipo=TipoCertidao(cert_data['tipo']),
                origem=OrigemCertidao.API,
                conteudo_base64=cert_data['conteudo_base64'],
                status=StatusCertidao(cert_data['status']),
                recebida_em=datetime.now(),
                valida_ate=datetime.now() + timedelta(days=30)
            )
            certidao_repo.criar(certidao)
        
        return {
            "message": f"{len(certidoes)} certidões obtidas com sucesso",
            "certidoes": certidoes
        }
    except Exception as e:
        print(f"Erro ao buscar certidões: {str(e)}")
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

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)