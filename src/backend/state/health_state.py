from typing import Any, Dict, List, TypedDict


class InterviewData(TypedDict, total=False):
    interview_history: List[Any]
    interview_questions_asked: int
    next_interview_question: str
    interview_complete: bool
    summary: str
    reasoning: str

class ResourceFinderResult(TypedDict, total=False):
    interview_history: List[Any]
    interview_questions_asked: int
    next_interview_question: str
    interview_complete: bool
    summary: str
    reasoning: str


class HealthState(TypedDict, total=False):
    # Input
    most_recent_user_input: str
    location: str
    thread_id: str
    provider_selection: int = -1

    # Interview agent
    interview_data: InterviewData

    # Generic optional fields kept for compatibility with wider project
    chat_output: Dict[str, Any]

    # triage agent
    triage_result: Dict  # triage agent

    # resource finder agent
    resource_finder_result: Dict

    # appointment prep agent
    appointment_prep_result: Dict

    #interruption
    should_resume_after_interrupt: bool
    #chat_purpose
    chat_purpose: str

