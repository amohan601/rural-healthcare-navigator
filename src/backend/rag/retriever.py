
from functools import lru_cache
from src.backend.rag.vectorstore import load_vectorstore

@lru_cache(maxsize=1)
def get_retriever(top_k= 5):
    vectorstore = load_vectorstore()
    print('loaded vectorstore')
    return vectorstore.as_retriever(search_type="mmr",search_kwargs={"k": top_k,
                                                              "fetch_k": 20,
                                                              "lambda_mult": 0.5})

def retrieve_documents(question):
    retriever = get_retriever()
    docs = retriever.invoke(question)
    return docs


