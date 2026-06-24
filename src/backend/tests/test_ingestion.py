import os
from dotenv import load_dotenv
load_dotenv()
api = os.getenv('OPENAI_API_KEY')
print('API Key ', api)

urls = [
    "https://www.cdc.gov/heart-disease/about/heart-attack.html"
]

from src.backend.rag.ingestion import load_web_documents,chunk_documents

docs = load_web_documents(urls)
chunks = chunk_documents(docs)
