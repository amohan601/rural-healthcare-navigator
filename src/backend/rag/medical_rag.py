from src.backend.model.llm import LLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from src.backend.rag.retriever import  get_retriever
from src.backend.rag.vectorstore import MEDICAL_DOCS_COLLECTION_NAME
from langchain_core.output_parsers import StrOutputParser
from src.backend.logging.logger import logger

PROMPT_TEMPLATE = """
You are medical information assistant.
Use only the supplied context to answer the question

If the answer is not present in the context,
say:

"I could not find this information in the medical knowledge base."

context: 
{context}

Question:
{question}

"""
PROMPT = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)


def ask_medical_question(question):
    logger.info('[medical_rag] inside ask_medical_question')
    logger.info(f'[medical_rag] Question: {question}')
    retriever = get_retriever(MEDICAL_DOCS_COLLECTION_NAME)
    chain = ({'context': retriever, 'question': RunnablePassthrough()} | PROMPT | LLM | StrOutputParser() )
    response =  chain.invoke(question)
    logger.info(f"[medical_rag] Context retrieved ({len(response)} chars)")
    return response