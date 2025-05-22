FROM python:3.12-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos do projeto
COPY requirements.txt .
COPY . .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Cria diretórios necessários
RUN mkdir -p uploads/documentos uploads/certidoes

# Expõe a porta 8000
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]