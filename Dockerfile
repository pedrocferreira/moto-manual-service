FROM python:3.9-slim

WORKDIR /app

# Adicionar a configuração do tokenizer
ENV TOKENIZERS_PARALLELISM=false

# Instala dependências do sistema necessárias
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Primeiro, copiamos apenas os arquivos necessários para instalar as dependências
COPY setup.py .
COPY requirements.txt .

# Instala as dependências Python
RUN pip install -r requirements.txt
RUN pip install -e .
RUN pip install PyPDF2 

# Cria diretórios necessários
RUN mkdir -p application/engine/moto_manual_agent/manuals \
    && mkdir -p application/engine/moto_manual_agent/vector_indices

# Agora copiamos o resto do código
COPY application application/
COPY manage.py .
COPY scripts scripts/

# Expõe a porta que o Django vai usar
EXPOSE 8000

# Comando para inicializar os índices e iniciar o servidor
CMD ["sh", "-c", "python scripts/initialize_indices.py && python manage.py runserver 0.0.0.0:8000"] 