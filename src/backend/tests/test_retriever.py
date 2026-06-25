
import os
from dotenv import load_dotenv
load_dotenv()
api = os.getenv('OPENAI_API_KEY')
print('API Key ', api)


print('loaded env vars ')
from src.backend.rag.retriever import retrieve_documents
docs = retrieve_documents( "What are symptoms of a heart attack?")
print('Number of docs ',len(docs))

print(docs[0].page_content[:500])