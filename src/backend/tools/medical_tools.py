from src.backend.rag.medical_rag import  ask_medical_question

def medical_rag_tool(question):
    return ask_medical_question(question)

