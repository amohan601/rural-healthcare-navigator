from src.backend.model.llm import LLM
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel,Field
from src.backend.state.health_state import HealthState
from src.backend.tools.medical_tools import ask_medical_question
from src.backend.logging.logger import logger


# ── Structured output — fields match HealthState["triage_result"] ──────
class TriageResponse(BaseModel):
    urgency:        str       = Field(description="LOW, MEDIUM, or HIGH")
    reasoning:      str       = Field(description="Why this urgency level")
    conditions:     list[str] = Field(description="1-4 possible conditions. Never a diagnosis.")
    recommendation: str       = Field(description="Recommended next action for the patient")




structured_llm = LLM.with_structured_output(TriageResponse)

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

def _is_high_urgency(state):
    logger.info("[supervisor] entered _is_high_urgency")
    triage_result = state.get("triage_result") or {}
    return str(triage_result.get("urgency", "")).upper() == "HIGH"


def triage_node(state: HealthState) -> dict:
    logger.info('[triage_agent]Running triage node ')
    response = triage_symptoms(state["interview_data"]["summary"])
    #print(f'Response from triage_symptoms {type(response)} {response}')
    triage_result  = {
        "urgency": response.urgency,
        "reasoning": response.reasoning,
        "conditions": response.conditions,
        "recommendation": response.recommendation
    }
    logger.debug(f"[triage_agent] urgency={response.urgency}")
    logger.debug(f"[triage_agent] reasoning={response.reasoning}")
    logger.debug(f"[triage_agent] conditions={response.conditions}")
    logger.debug(f"[triage_agent] recommendation={response.recommendation}")

    #return only what changed
    return {
        "triage_result":triage_result
    }
