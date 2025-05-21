# Mercatório Backend Challenge

## Sobre o Projeto

API REST que simula a etapa de originação de precatórios na Mercatório, permitindo o cadastro de credores, seus precatórios, upload de documentos pessoais e obtenção de certidões de forma manual ou automática.

## Framework

O projeto utiliza FastAPI como framework web principal, oferecendo:
- Alto desempenho e velocidade de execução
- Documentação automática com Swagger/OpenAPI
- Validação de dados automática com Pydantic
- Suporte nativo a operações assíncronas
- Sistema de dependências robusto

## Arquitetura

O projeto utiliza Arquitetura Hexagonal (Ports and Adapters) para melhor organização e separação de responsabilidades:

```
mercatorio-backend-challenge/
├── adapters/              # Adaptadores para comunicação externa
├── core/                  # Regras de negócio e entidades
│   ├── entities/         # Classes de domínio
│   └── tests/           # Testes unitários
└── ports/               # Interfaces e contratos
    ├── database/        # Interfaces de persistência
    └── interfaces/      # Contratos da aplicação
```

## Tecnologias Utilizadas

- Python 3.8+
- FastAPI
- SQLAlchemy
- SQLite
- Pytest

## Requisitos do Sistema

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Docker 

## Como Executar

### Usando Python local

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/mercatorio-backend-challenge.git
cd mercatorio-backend-challenge
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute a aplicação:
```bash
uvicorn main:app --reload
```

### Usando Docker

1. Construa a imagem:
```bash
docker build -t mercatorio-api .
```

2. Execute o container:
```bash
docker run -p 8000:8000 mercatorio-api
```

A API estará disponível em `http://localhost:8000`

## Endpoints da API

### Credores

#### Cadastrar Credor
```http
POST /credores
```

Payload:
```json
{
  "nome": "Maria Silva",
  "cpf_cnpj": "12345678900",
  "email": "maria@example.com",
  "telefone": "11999999999",
  "precatorio": {
    "numero_precatorio": "0001234-56.2020.8.26.0050",
    "valor_nominal": 50000.00,
    "foro": "TJSP",
    "data_publicacao": "2023-10-01"
  }
}
```

#### Upload de Documentos
```http
POST /credores/{id}/documentos
```
Multipart form data com:
- tipo: string (identidade, comprovante_residencia)
- arquivo: file

#### Upload Manual de Certidões
```http
POST /credores/{id}/certidoes
```
Multipart form data com:
- tipo: string (federal, estadual, municipal, trabalhista)
- arquivo: file

#### Buscar Certidões Automaticamente
```http
POST /credores/{id}/buscar-certidoes
```

#### Consultar Credor
```http
GET /credores/{id}
```

### API Mock de Certidões

```http
GET /api/certidoes?cpf_cnpj=00000000000
```

Resposta:
```json
{
  "cpf_cnpj": "00000000000",
  "certidoes": [
    {
      "tipo": "federal",
      "status": "negativa",
      "conteudo_base64": "..."
    },
    {
      "tipo": "trabalhista",
      "status": "positiva",
      "conteudo_base64": "..."
    }
  ]
}
```

## Testes

Execute os testes automatizados com:

```bash
pytest
```

## Job Automático

Um job automático verifica e revalida as certidões a cada 24 horas. O status da última execução pode ser consultado através do endpoint:

```http
GET /jobs/status
```

## Documentação Adicional

A documentação completa da API está disponível em:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Funcionalidades Implementadas

- [x] Cadastro de credores com dados pessoais
- [x] Cadastro de precatórios
- [x] Upload de documentos pessoais
- [x] Upload manual de certidões
- [x] Simulação de obtenção automática de certidões
- [x] Consulta completa de credores
- [x] Validação de extensões e tamanho de arquivos
- [x] Job automático de revalidação de certidões
- [x] Testes automatizados
- [x] Dockerfile e docker-compose