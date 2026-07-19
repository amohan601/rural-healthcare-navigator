from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from functools import lru_cache
from src.backend.logging.logger  import logger
MEDICAL_DOCS_COLLECTION_NAME = "rural_health_medical"

'''
test this file with 
python -c "from src.backend.rag.vectorstore import load_vectorstore; print('ok')"
it should print ok and not crash
'''
def _embeddings():
    """Lazy — only instantiates when first called, after .env is loaded."""
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    return embeddings

@lru_cache(maxsize=1)
def qdrant_client():
    logger.info('[vectorstore] inside qdrant_client')
    return QdrantClient(path="./qdrant_data")

def create_vectorstore(chunks,collection_name):
    logger.info(f'[vectorstore] inside create_vectorstore collection_name = {collection_name}')
    vectorstore = QdrantVectorStore.from_documents(documents = chunks,
                                                   embedding = _embeddings(),
                                                   path="./qdrant_data",
                                                   collection_name = collection_name)
    return vectorstore

def load_vectorstore(collection_name):
    client = qdrant_client()
    logger.info(f'[vectorstore] inside load_vectorstore collection_name = {collection_name}')
    return QdrantVectorStore(client = client, embedding =  _embeddings(), collection_name = collection_name)

# def add_chunks(chunks):
#     print('[vectorstore] inside add_chunks')
#     vectorstore = load_vectorstore()
#     vectorstore.add_documents(chunks)
#     return vectorstore