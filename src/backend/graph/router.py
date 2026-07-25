from src.backend.state.health_state import HealthState
from src.backend.agents.triage_agent import _is_high_urgency
from src.backend.logging.logger import logger

def _entry_routing(state: HealthState):
    logger.info(f'[router] _entry_routing')
    logger.info("[router] entered _entry_routing")
    interview_data = dict(state.get("interview_data") or {})

    if not interview_data.get("interview_complete"):
        logger.info(f'[router] interview not complete. up next -> interview')
        return "interview"

    return "END"

def _chat_state_routing(state: HealthState):
    logger.info(f'[router] _chat_state_routing state={state}')

    interview_data = dict(state.get("interview_data") or {})

    if not interview_data.get("interview_complete"):
        logger.info(f'[router] interview not complete. back to -> interview')
        return "interview"
    elif interview_data.get("interview_complete") and not state.get("triage_result"):
        logger.info(f'[router] interview complete. Triage npending... on to -> triage')
        return "triage"
    elif state.get("provider_selection") != -1 and not state.get("appointment_prep_result") :
        logger.info(f'[router] Providers identified and selected... on to -> appointment')
        return "appointment"

    logger.info(f'[router] next to -> END')
    return "END"


def _triage_routing(state: HealthState):
    logger.info("[router] entered _triage_routing")
    if _is_high_urgency(state):
        logger.info(f'[router] _triage_routing _is_high_urgency upnext emergency')
        return "emergency"
    logger.info(f'[router] _triage_routing upnext -> resource_finder')
    return "resource_finder"
