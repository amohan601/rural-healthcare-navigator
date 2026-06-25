from langgraph.graph import StateGraph
from backend.state.health_state import HealthState
from backend.agents.triage_agent import triage_node
from backend.agents.insurance_agent import insurance_node
from backend.agents.resource_finder_agent import resource_finder_node

graph = StateGraph()
graph.add_node("triage",triage_node)
graph.add_node("insurance", insurance_node)
graph.add_node("resource", resource_finder_node)