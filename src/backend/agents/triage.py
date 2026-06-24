from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel

class TriageResponse(BaseModel):
    urgency: str
    reasoning: str
    something: str


from src.backend.tools.medical_tools import ask_medical_question

llm = ChatOpenAI(model='gpt-5.4-mini', temperature = 0)
structured_llm = llm.with_structured_output(TriageResponse)

prompt = """
You are a rural health triage assistant.

Based on the symptoms and medical context:

1. Determine urgency level:
   - LOW
   - MEDIUM
   - HIGH

2. Explain your reasoning.

3. Recommend next action.

Never diagnose a condition.

Symptoms:
{symptoms}

Medical Context:
{context}
"""

prompt_template = PromptTemplate.from_template(prompt)
chain = prompt_template | structured_llm

def triage_symptoms(symptoms):
    medical_context = ask_medical_question(symptoms)
    response = chain.invoke({'symptoms': symptoms, 'context': medical_context})
    return response


def triage_node(state):
    print('Running triage node ')
    return state