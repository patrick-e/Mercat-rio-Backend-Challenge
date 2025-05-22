# Mercatório Backend Challenge

API REST para simulação da etapa de originação de precatórios, permitindo o cadastro de credores, seus respectivos precatórios, upload de documentos pessoais e a obtenção de certidões.

## Tecnologias Utilizadas

- Python 3.8+
- FastAPI (framework web)
- SQLite (banco de dados)
- Pydantic (validação de dados)
- APScheduler (agendamento de tarefas)
- Docker (containerização)

## Estrutura do Projeto

```
.
├── adapters/               # Implementações concretas das interfaces
├── core/                  # Regras de negócio e entidades
│   ├── entities/         # Classes de domínio
│   └── tests/           # Testes unitários
├── ports/                # Interfaces e adaptadores
│   ├── database/        # Camada de persistência
│   └── interfaces/      # Interfaces de repositório
├── uploads/             # Diretório para arquivos enviados
├── Dockerfile           # Configuração do container
├── docker-compose.yml   # Configuração do ambiente
├── main.py             # Ponto de entrada da aplicação
└── README.md           # Este arquivo
```

## Executando o Projeto

### Usando Docker (Recomendado)

1. Certifique-se de ter o Docker e Docker Compose instalados

2. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/mercatorio-backend-challenge.git
cd mercatorio-backend-challenge
```

3. Inicie a aplicação:
```bash
docker-compose up -d
```

A API estará disponível em `http://localhost:8000`

### Localmente

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/mercatorio-backend-challenge.git
cd mercatorio-backend-challenge
```

2. Crie um ambiente virtual:
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

4. Inicie a API:
```bash
python main.py
```

A API estará disponível em `http://localhost:8000`

## Documentação da API

A documentação completa da API está disponível em:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Endpoints Principais

#### 1. Cadastro de Credor com Precatório

```bash
POST /credores
```

Exemplo de payload:
```json
{
  "nome": "Maria Silva",
  "cpf_cnpj": "12345678900",
  "email": "maria@email.com",
  "telefone": "11999999999",
  "precatorio": {
    "numero_precatorio": "0001234-56.2020.8.26.0050",
    "valor_nominal": 50000.00,
    "foro": "TJSP",
    "data_publicacao": "2023-10-01T00:00:00Z"
  }
}
```

#### 2. Upload de Documento

```bash
POST /credores/{credor_id}/documentos
```

Parâmetros do form-data:
- arquivo: Arquivo PDF do documento
- tipo: Tipo do documento (identidade, comprovante_residencia)

#### 3. Upload Manual de Certidão

```bash
POST /credores/{credor_id}/certidoes
```

Parâmetros do form-data:
- arquivo: Arquivo PDF da certidão
- tipo: Tipo da certidão (federal, estadual, municipal, trabalhista)

#### 4. Busca Automática de Certidões

```bash
POST /credores/{credor_id}/buscar-certidoes
```

Busca certidões automaticamente usando a API mock.

#### 5. Consulta de Credor

```bash
GET /credores/{credor_id}
```

Retorna todos os dados do credor, incluindo precatório, documentos e certidões.

### API Mock de Certidões

```bash
GET /api/certidoes?cpf_cnpj=12345678900
```

Simula uma API externa de consulta de certidões.

## Recursos Implementados

- [x] Cadastro de credor com dados pessoais
- [x] Cadastro de precatório vinculado a um credor
- [x] Upload de documentos pessoais
- [x] Upload manual de certidões
- [x] Simulação de obtenção automática de certidões via API mock
- [x] Consulta de um credor com seus documentos e certidões
- [x] Validação de extensões e tamanho de arquivos
- [x] Job que revalida certidões automaticamente a cada 24h
- [x] Documentação detalhada
- [x] Dockerfile e docker-compose
- [x] Testes automatizados

## Executando os Testes

```bash
# Com ambiente virtual ativado
python -m unittest core/tests/tests.py

# Ou usando Docker
docker-compose exec api python -m unittest core/tests/tests.py
```

## Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Crie um Pull Request

## Licença

Este projeto está sob a licença MIT.