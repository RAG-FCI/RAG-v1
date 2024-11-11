# Use uma imagem base oficial com Python
FROM python:3.10-slim

# Defina o diretório de trabalho no contêiner
WORKDIR /app

# Copie os arquivos de dependência para o contêiner
COPY requirements.txt ./

# Instale as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Copie todo o código para o contêiner
COPY . .

# Configure a variável de ambiente para a chave do Gemini

# Define a variável de ambiente no contêiner (o valor será passado no momento da execução)
ENV GEMINI_API_KEY=""


# Exponha a porta que a aplicação Flask usará
EXPOSE 5000

# Comando para rodar o app, iniciar o aplicativo
CMD ["python", "app.py"]