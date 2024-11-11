import os
from flask import Flask, request, jsonify, render_template, url_for
from flask_cors import CORS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import google.generativeai as genai




# Configuração do Flask
app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)  # Habilita CORS para todas as origens

# Configuração da chave da API

# Carrega o arquivo .env
load_dotenv()

# Obtém a chave GEMINI_API_KEY
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("A chave GEMINI_API_KEY não foi configurada!")
genai.configure(api_key=GEMINI_API_KEY)

# Configuração do vetorstore
VECTORSTORE_DIR = "./chroma_db"
os.makedirs(VECTORSTORE_DIR, exist_ok=True)  # Garante que o diretório exista apenas localmente
#EMBEDDING_MODEL = "paraphrase-MiniLM-L3-v2"  # Modelo mais leve
EMBEDDING_MODEL = "distilbert-base-uncased"
embedding_function = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

vectorstore = Chroma(persist_directory=VECTORSTORE_DIR, embedding_function=embedding_function)

# Função para carregar e processar PDFs
def carregar_pdfs(diretorio, limite=5):
    docs = []
    for i, nome_arquivo in enumerate(os.listdir(diretorio)):
        if nome_arquivo.endswith('.pdf'):
            if i >= limite:  # Limita o número de PDFs carregados
                break
            caminho_pdf = os.path.join(diretorio, nome_arquivo)
            with open(caminho_pdf, 'rb') as arquivo:
                reader = PdfReader(arquivo)
                texto_pdf = "".join([pagina.extract_text() for pagina in reader.pages])
                docs.append(Document(page_content=texto_pdf))
    return docs


# Processar PDFs e popular o vetorstore
diretorio_pdfs = os.path.join('.', 'arquivos')
docs = carregar_pdfs(diretorio_pdfs)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)  # Reduz tamanho
split_docs = text_splitter.split_documents(docs)

# Persistência condicional
if not os.path.exists(VECTORSTORE_DIR):
    vectorstore.add_documents(split_docs)
    vectorstore.persist()


# Função para gerar prompts
def generate_rag_prompt(query, context, last_answer=""):
    escaped_context = context.replace("'", "").replace('"', "").replace("\n", " ")
    escaped_last_answer = last_answer.replace("'", "").replace('"', "").replace("\n", " ")
    return f"""
Você é um bot útil e informativo que responde perguntas sobre a Universidade Presbiteriana Mackenzie usando o contexto abaixo. 
ÚLTIMA RESPOSTA: '{escaped_last_answer}'
PERGUNTA: '{query}'
CONTEXTO: '{escaped_context}'
RESPOSTA:
"""

# Função para buscar contexto relevante
def get_relevant_context(query):
    search_results = vectorstore.similarity_search(query, k=3)
    return "\n".join([result.page_content for result in search_results])

# Função para gerar resposta
#def generate_answer(prompt):
    #model = genai.GenerativeModel(model_name='gemini-pro')
    #answer = model.generate_content(prompt)
    #return answer.text
def generate_answer(prompt):
    response = genai.generate(model='gemini-pro', messages=[{"role": "system", "content": prompt}])
    return response['candidates'][0]['content']


#rota para carregar o chatbot
@app.route('/')
def index():
    return render_template("index.html")


# Rota para processar o prompt
@app.route('/ragfci', methods=['POST'])
def ragfci():
    data = request.get_json()
    prompt = data.get('prompt')
    if not prompt:
        return jsonify({"erro": "O campo 'prompt' é obrigatório."}), 400

    print(f"Recebido prompt: {prompt}")
    context = get_relevant_context(prompt)
    rag_prompt = generate_rag_prompt(prompt, context)
    resposta = generate_answer(rag_prompt)
    print(f"Resposta gerada: {resposta}")
    return jsonify({"resposta": resposta})

if __name__ == '__main__':
    if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
    print("Servidor Flask iniciado com sucesso!")

