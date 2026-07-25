from langgraph.types import interrupt
from src.backend.state.chat_purpose import ChatPurpose
from src.backend.logging.logger import logger

def interrupt_to_chat_output(interrupt_payload):
    logger.info("[chat_state_generator_agent] entered interrupt_to_chat_output")
    if isinstance(interrupt_payload, dict):
        return {
            "input_required": True,
            "input_type": interrupt_payload.get("input_type", ChatPurpose.INTERVIEW_QUESTION),
            "question": interrupt_payload.get("message"),
            "display_message": interrupt_payload.get("display_message"),
            "options": interrupt_payload.get("options") or []
        }
    return {
        "input_required": False,
        "input_type": ChatPurpose.STATUS_UPDATE,
        "question": None,
        "display_message": "Waiting for next step.",
        "options": []
    }




def chat_state_generator_node(state):
    logger.info("[chat_state_generator_agent] entered chat_state_generator_node")

    logger.info(f"[chat_state_generator_agent] state={state}")
    interview_data = state.get("interview_data")
    next_interview_question = interview_data.get("next_interview_question")
    purpose = state.get("chat_purpose")
    logger.debug(f"[chat_state_generator_agent] interview_question={next_interview_question}")

    if purpose == ChatPurpose.INTERVIEW_QUESTION:
        logger.info(f"[chat_state_generator_agent] interrupting for another question")
        resume_value = interrupt(
            {
                "input_type": ChatPurpose.INTERVIEW_QUESTION,
                "message": next_interview_question
            }
        )

        logger.info(f"[chat_state_generator_agent] moved past interruption resume_value={resume_value}")
        state["chat_output"] =  {
            "input_required": False,
            "input_type": ChatPurpose.STATUS_UPDATE,
            "question": None,
            "display_message": "Waiting for next step.",
            "options": [],
        }
        state["most_recent_user_input"] = str(resume_value or "").strip()
        state["next_interview_question"] = None
        state["reasoning"] = None
        state["summary"] = None
        state["chat_purpose"] = None
        return state

    if purpose == ChatPurpose.LOCATION_REQUEST:
        logger.info(f"[chat_state_generator_agent] interrupting for location details")
        resume_value = interrupt(
            {
                "input_type": ChatPurpose.LOCATION_REQUEST,
                "message": "One last question: please share your location (city, state, or ZIP code).",
                "display_message": None,
                "options": [],
            }
        )
        logger.info(f"[chat_state_generator_agent] moved past interruption resume_value={resume_value}")
        state["chat_output"] =  {
            "input_required": False,
            "input_type": ChatPurpose.STATUS_UPDATE,
            "question": None,
            "display_message": "Assessing next steps...",
            "options": [],
        }
        state["location"] = str(resume_value or "").strip()
        state["next_interview_question"] = None
        state["reasoning"] = None
        state["chat_purpose"] = None
        return state


    if purpose == ChatPurpose.EMERGENCY:
        logger.info(f"[chat_state_generator_agent] informing emergency recommendation")
        triage_result = state.get("triage_result")
        recommendation = triage_result.get("recommendation")
        logger.info(f"[chat_state_generator_agent] recommendation = {recommendation}")
        state["chat_output"] = {
            "input_required": False,
            "input_type": ChatPurpose.STATUS_EMERGENCY,
            "question": None,
            "display_message": recommendation,
            "options": [],
        }
        state["chat_purpose"] = None
        return state

    if purpose ==  ChatPurpose.PROVIDER_SELECTION:
        logger.info(f"[chat_state_generator_agent] requesting provider selection")
        resource_finder_result = state.get("resource_finder_result") or {}
        resume_value = interrupt(
            {
                "input_type": ChatPurpose.PROVIDER_SELECTION,
                "message": "Select provider for setting up an appointment.",
                "display_message": resource_finder_result.get("summary"),
                "options": resource_finder_result.get("providers") or [],
            }
        )
        logger.info(f"[chat_state_generator_agent] moved past interruption resume_value={resume_value}")
        state["chat_output"] =  {
            "input_required": False,
            "input_type": ChatPurpose.STATUS_UPDATE,
            "question": None,
            "display_message": "Setting up appointment with this provider...",
            "options": [],
        }
        state["provider_selection"] = int(resume_value)
        state["next_interview_question"] = None
        state["reasoning"] = None
        state["chat_purpose"] = None
        return state



    if purpose == ChatPurpose.APPOINTMENT_PREP:
        logger.info(f"[chat_state_generator_agent] informing appointment confirmation")
        state["chat_output"] = {
            "input_required": False,
            "input_type": ChatPurpose.STATUS_UPDATE,
            "question": None,
            "display_message": "Appointment confirmed with the provider",
            "options": [],
        }
        state["chat_purpose"] = None
        return state


    state["chat_output"] = {
        "input_required": False,
        "input_type": ChatPurpose.STATUS_UPDATE,
        "question": None,
        "display_message": "Done",
        "options": [],
    }
    logger.info(f"[chat_state_generator_agent] ---end of chat state normal flow --")
    return state

