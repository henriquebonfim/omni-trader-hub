# Usa uma imagem base leve do Python
FROM python:3.11-slim

# Evita que o Python gere arquivos .pyc e força logs para o stdout (bom para Docker)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Define diretório de trabalho
WORKDIR /app

# Instala dependências do sistema necessárias para compilar alguns pacotes
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências Python (aproveita cache do Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código fonte
COPY src/ ./src/

# Cria um usuário não-root para segurança (Boas práticas de DevSecOps!)
RUN useradd -m appuser
USER appuser

# Comando para rodar o script
CMD ["python", "src/main.py"]
