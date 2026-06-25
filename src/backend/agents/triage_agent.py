from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel,Field
from src.backend.state.health_state import HealthState

# ── Structured output — fields match HealthState["triage_result"] ──────
class TriageResponse(BaseModel):
    urgency:        str       = Field(description="LOW, MEDIUM, or HIGH")
    reasoning:      str       = Field(description="Why this urgency level")
    conditions:     list[str] = Field(description="1-4 possible conditions. Never a diagnosis.")
    recommendation: str       = Field(description="Recommended next action for the patient")



from src.backend.tools.medical_tools import ask_medical_question

llm = ChatOpenAI(model='gpt-4o-mini', temperature = 0)
structured_llm = llm.with_structured_output(TriageResponse)

prompt = """
You are a rural health triage assistant.

Based on the symptoms and medical context:

1. Determine urgency level: LOW, MEDIUM, or HIGH
2. Explain your reasoning briefly.
3. List 1-4 possible conditions (do NOT diagnose — frame as possibilities).
4. Recommend next action for the patient.

Never diagnose. Frame conditions as possibilities only.

Symptoms:
{symptoms}

Medical Context:
{context}
"""

prompt_template = PromptTemplate.from_template(prompt)
chain = prompt_template | structured_llm

def triage_symptoms(symptoms):
    """Runs RAG retrieval then structured LLM triage."""
    medical_context = ask_medical_question(symptoms)
    response = chain.invoke({'symptoms': symptoms, 'context': medical_context})
    return response


def triage_node(state: HealthState) -> dict:
    print('Running triage node ')
    response = triage_symptoms(state["user_query"])
    #print(f'Response from triage_symptoms {type(response)} {response}')
    triage_result  = {
        "urgency": response.urgency,
        "reasoning": response.reasoning,
        "conditions": response.conditions,
        "recommendation": response.recommendation
    }
    print(f"[triage] urgency={response.urgency}")
    print(f"[triage] reasoning={response.reasoning}")
    print(f"[triage] conditions={response.conditions}")
    print(f"[triage] recommendation={response.recommendation}")

    #return only what changed
    return {"triage_result":triage_result }
