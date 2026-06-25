from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from src.backend.rag.retriever import  get_retriever
from langchain_core.output_parsers import StrOutputParser
llm = ChatOpenAI(model='gpt-4o-mini', temperature = 0)

TEMPLATE = """
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
prompt_template = PromptTemplate.from_template(TEMPLATE)


def ask_medical_question(question):
    print('inside ask_medical_question')
    print('invoke openai with ',question)
    retriever = get_retriever()
    print(retriever)
    chain = ({'context': retriever, 'question': RunnablePassthrough()} | prompt_template | llm | StrOutputParser() )
    response =  chain.invoke(question)
    print(f"[medical_rag] Context retrieved ({len(response)} chars)")
    return response