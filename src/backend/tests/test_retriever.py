
import os
from dotenv import load_dotenv
load_dotenv()


from src.backend.rag.vectorstore import MEDICAL_DOCS_COLLECTION_NAME,INSURANCE_DOCS_COLLECTION_NAME

from src.backend.rag.retriever import retrieve_documents,get_retriever
docs = retrieve_documents( question="What are symptoms of a heart attack?",collection_name=MEDICAL_DOCS_COLLECTION_NAME)
print('Number of docs ',len(docs))

print(docs[0].page_content[:500])


docs = retrieve_documents( question="What is the Medicare copay for specialist visits?",collection_name=INSURANCE_DOCS_COLLECTION_NAME)
print('Number of docs ',len(docs))
for i, doc in enumerate(docs, 1):
    print(f"\n--- Chunk {i} ---")
    print(f"Source: {doc.metadata.get('source_url', 'unknown')}")
    print(f"Content:\n{doc.page_content}")
    print("-" * 60)
