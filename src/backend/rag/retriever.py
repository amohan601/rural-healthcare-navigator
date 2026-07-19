
from functools import lru_cache
from src.backend.rag.vectorstore import load_vectorstore
from src.backend.logging.logger import logger

@lru_cache(maxsize=1)
def get_retriever(collection_name,top_k= 5):
    logger.info(f'[get_retriever] loaded vectorstore collection name = {collection_name}')
    vectorstore = load_vectorstore(collection_name)
    retriever = vectorstore.as_retriever(search_type="mmr",search_kwargs={"k": top_k,
                                                              "fetch_k": 20,
                                                              "lambda_mult": 0.5})
    logger.debug(f'[get_retriever] retriever = {type(retriever)}')
    return retriever

def retrieve_documents(question,collection_name):
    logger.info(f'[retrieve_documents] question = {question} vectorstore collection name = {collection_name}')
    retriever = get_retriever(collection_name)
    docs = retriever.invoke(question)
    return docs


