
from dotenv import load_dotenv
import os
load_dotenv()
api = os.getenv('OPENAI_API_KEY')
print('API Key ', api)

from src.backend.rag.ingestion import  ingest_urls
from src.backend.rag.vectorstore import create_vectorstore,load_vectorstore

urls = [

    "https://www.cdc.gov/heart-disease/about/heart-attack.html",

    "https://www.cdc.gov/stroke/signs-symptoms/index.html",

    "https://medlineplus.gov/diabetes.html",

    "https://medlineplus.gov/highbloodpressure.html"
]

chunks = ingest_urls(urls)
print(f'Len of chunks {len(chunks)}')
vectorstore = create_vectorstore(chunks)
print(vectorstore)
