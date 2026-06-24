from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

embeddings = OpenAIEmbeddings(model = "text-embedding-3-small")
COLLECTION_NAME = "rural_health_medical"

def qdrant_client():
    print('inside qdrant_client')
    return QdrantClient(path="./qdrant_data")

def create_vectorstore(chunks):
    print('inside create_vectorstore')
    vectorstore = QdrantVectorStore.from_documents(documents = chunks,
                                                   embedding = embeddings,
                                                   path="./qdrant_data",
                                                   collection_name = COLLECTION_NAME)
    return vectorstore

def load_vectorstore():
    client = qdrant_client()
    print('inside load_vectorstore')
    return QdrantVectorStore(client = client, embedding = embeddings, collection_name = COLLECTION_NAME)

def add_chunks(chunks):
    print('inside add_chunks')
    vectorstore = load_vectorstore()
    vectorstore.add_documents(chunks)
    return vectorstore