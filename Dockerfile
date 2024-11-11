FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./

# Instale as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Copie todo o código para o contêiner
COPY . .

ENV GEMINI_API_KEY=${GEMINI_API_KEY}

EXPOSE 5000

CMD ["python", "app.py"]