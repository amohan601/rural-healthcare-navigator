import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")

from src.backend.agents import interview_agent


def test_interview_agent_asks_next_question():
    original_fn = interview_agent._run_interview_decision
    try:
        interview_agent._run_interview_decision = lambda history, questions_asked: interview_agent.InterviewDecision(
            interview_complete=False,
            question="How long have you had these symptoms?",
            summary=None,
            reasoning="Need duration details before summarizing.",
        )

        state = {
            "most_recent_user_input": "I have chest pain",
            "interview_data": {
                "interview_history": [],
                "interview_questions_asked": 0,
            },
        }

        result = interview_agent.interview_node(state)
        data = result["interview_data"]

        assert data["interview_complete"] is False
        assert data["interview_questions_asked"] == 1
        assert data["next_interview_question"] == "How long have you had these symptoms?"
        assert len(data["interview_history"]) == 2
    finally:
        interview_agent._run_interview_decision = original_fn


if __name__ == "__main__":
    test_interview_agent_asks_next_question()
    print("test_interview_agent_asks_next_question passed")
