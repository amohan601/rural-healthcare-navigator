from src.backend.state.chat_purpose import ChatPurpose
from src.backend.logging.logger import logger

def appointment_prep_node(state):
    logger.info("[appointment_prep_agent] Preparing appointment handoff")
    return {
        "appointment_prep_result": {
            "status": "ready",
            "message": "Appointment preparation is ready. We selected your provider and pharmacy.",
        },
        "chat_purpose": ChatPurpose.APPOINTMENT_PREP,
    }
