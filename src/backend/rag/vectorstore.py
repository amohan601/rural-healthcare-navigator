from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

COLLECTION_NAME = "rural_health_medical"
'''
test this file with 
python -c "from src.backend.rag.vectorstore import load_vectorstore; print('ok')"
it should print ok and not crash
'''
def _embeddings():
    """Lazy — only instantiates when first called, after .env is loaded."""
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    return embeddings

def qdrant_client():
    print('inside qdrant_client')
    return QdrantClient(path="./qdrant_data")

def create_vectorstore(chunks):
    print('inside create_vectorstore')
    vectorstore = QdrantVectorStore.from_documents(documents = chunks,
                                                   embedding = _embeddings(),
                                                   path="./qdrant_data",
                                                   collection_name = COLLECTION_NAME)
    return vectorstore

def load_vectorstore():
    client = qdrant_client()
    print('inside load_vectorstore')
    return QdrantVectorStore(client = client, embedding =  _embeddings(), collection_name = COLLECTION_NAME)

def add_chunks(chunks):
    print('inside add_chunks')
    vectorstore = load_vectorstore()
    vectorstore.add_documents(chunks)
    return vectorstore