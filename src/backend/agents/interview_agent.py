from typing import List, Optional

from langchain_core.prompts import PromptTemplate
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from src.backend.model.llm import LLM
from src.backend.state.health_state import HealthState
from src.backend.state.chat_purpose import ChatPurpose
from src.backend.logging.logger import logger

MAX_INTERVIEW_QUESTIONS = 4

class InterviewDecision(BaseModel):
    interview_complete: bool = Field(
        description=(
            "False if one more follow-up question is needed. "
            "True when enough information has been collected for triage."
        )
    )
    question: Optional[str] = Field(
        default=None,
        description="Exactly one follow-up question when interview_complete is False.",
    )
    summary: Optional[str] = Field(
        default=None,
        description=(
            "Factual symptom summary for the triage agent when interview_complete is True. "
            "Report symptoms and patient-stated facts only — no diagnoses. "
            "Leave empty when interview_complete is False."
        ),
    )
    reasoning: str = Field(
        description="Brief explanation of why you asked this question or chose to summarize."
    )


structured_llm = LLM.with_structured_output(InterviewDecision)

INTERVIEW_PROMPT = """
You are a rural health intake assistant conducting a brief patient interview.

Decide whether to ask ONE more follow-up question or finish the interview.

If the interview is NOT complete (interview_complete=False):
- Set question to exactly one clear follow-up question.
- Leave summary empty.

If the interview IS complete (interview_complete=True):
- Leave question empty.
- Set summary to a factual symptom summary for the triage agent.

The triage agent will use your summary to determine urgency, reasoning, possible
conditions, and next steps — you do NOT do that work here.

Rules:
- Ask at most one question per turn.
- Questions asked so far: {questions_asked} of {max_questions} maximum.
- If questions asked so far - {questions_asked}, has reached the maximum allowed {max_questions} then
  , you MUST set interview_complete=True and generate summary from the conversation — do not ask another question.
- Do not repeat a question already answered in the conversation.
- Prefer plain language suitable for rural patients with limited healthcare access.
- Focus questions on symptoms: severity, duration, progression, associated symptoms,
  and red flags (chest pain, difficulty breathing, confusion, severe bleeding).
- Do NOT ask about location or insurance — other agents handle those.
- Do NOT diagnose, name conditions, or suggest what the patient might have.
- Do NOT include diagnoses or condition labels in the summary.
- When generating summary, include only what the patient reported: chief complaint,
  symptom details, duration/severity, progression, relevant history they mentioned,
  and any red flags they described.

Conversation so far:
{conversation}
"""

prompt_template = PromptTemplate.from_template(INTERVIEW_PROMPT)
chain = prompt_template | structured_llm


def _format_conversation(history: List[BaseMessage]) -> str:
    logger.info(f"[interview_agent] _format_conversation")
    if not history:
        return "(no prior messages)"
    lines = []
    for message in history:
        if isinstance(message, HumanMessage):
            label = "Patient"
        elif isinstance(message, SystemMessage):
            label = "Interviewer"
        else:
            label = message.type.capitalize()
        lines.append(f"{label}: {message.content}")

    result = "\n".join(lines)
    logger.debug(f"[interview_agent] lines \n = {result}")
    return result


def _run_interview_decision(
    history: List[BaseMessage],
    questions_asked: int,
) -> InterviewDecision:
    logger.info(f"[interview_agent] _run_interview_decision")
    must_complete = questions_asked >= MAX_INTERVIEW_QUESTIONS
    return chain.invoke(
        {
            "conversation": _format_conversation(history),
            "questions_asked": questions_asked,
            "max_questions": MAX_INTERVIEW_QUESTIONS
        }
    )


def interview_node(state: HealthState) -> dict:
    logger.info("[interview_agent] Running interview node----------")
    logger.debug(f"[interview_agent] Starting .. state={state}")
    most_recent_user_input = (state.get("most_recent_user_input") or "").strip()
    interview_data = dict(state.get("interview_data") or {})
    interview_history = list(interview_data.get("interview_history") or [])
    interview_questions_asked = int(interview_data.get("interview_questions_asked") or 0)

    if most_recent_user_input:
        interview_history.append(HumanMessage(content=most_recent_user_input))

    decision = _run_interview_decision(interview_history, interview_questions_asked)
    logger.debug(f"[interview_agent] decision={decision}")

    if decision.interview_complete:
        return {
            "interview_data": {
                "interview_history": interview_history,
                "interview_questions_asked": interview_questions_asked,
                "next_interview_question": "",
                "interview_complete": True,
                "summary": decision.summary or "",
                "reasoning": decision.reasoning,
            },
           "chat_purpose": ChatPurpose.LOCATION_REQUEST
        }

    question = decision.question or ""
    interview_history.append(SystemMessage(content=question))
    logger.debug(f"[interview_agent] Ending .. state={state}")
    return {
        "interview_data": {
            "interview_history": interview_history,
            "interview_questions_asked": interview_questions_asked + 1,
            "next_interview_question": question,
            "interview_complete": False,
            "summary": "",
            "reasoning": decision.reasoning,
        },
        "chat_purpose": ChatPurpose.INTERVIEW_QUESTION
    }
