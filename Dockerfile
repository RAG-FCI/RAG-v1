FROM python:3.10-slim as builder

# Defina o diretório de trabalho no contêiner
WORKDIR /app

# Copie os arquivos de dependência para o contêiner
COPY requirements.txt ./

# Instale as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Copie todo o código para o contêiner
COPY . .

RUN python -m pip install -e .

# Etapa de produção
FROM python:3.10-slim

WORKDIR /app

ENV GEMINI_API_KEY=${GEMINI_API_KEY}

COPY --from=builder /app/app.py .
COPY --from=builder /app/requirements.txt .
COPY --from=builder /app/chroma_db .
COPY --from=builder /app/static .
COPY --from=builder /app/templates .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]