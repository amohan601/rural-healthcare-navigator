from src.backend.state.chat_purpose import ChatPurpose
from src.backend.state.health_state import HealthState
from src.backend.logging.logger import logger

def emergency_state_node(state: HealthState):
    logger.info("[emergency_state_node] entered emergency_state_node")
    return {"chat_purpose": ChatPurpose.EMERGENCY}