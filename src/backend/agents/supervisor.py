
from langgraph.graph import START,END,StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from src.backend.state.health_state import HealthState
from src.backend.agents.triage_agent import triage_node
from src.backend.agents.reflection_agent import reflection_node
from src.backend.agents.resource_finder_agent import resource_finder_node
from src.backend.agents.insurance_agent import insurance_node
from src.backend.agents.appointment_prep_agent import appointment_prep_node
from src.backend.agents.synthesizer_agent import synthesizer_node

def triage_routing(state):
    print('Running triage_routing node ')
    """
    Decide if you want to route to insurance_checker or appointment_prep or resource_finder
    """
    return "insurance_checker"

def reflection_routing(state):
    print('Running reflection_routing node ')
    """
    Decide if you want to route to insurance_checker or appointment_prep or resource_finder
    """
    return "insurance_checker"
def parallel_agents_node(state):
    print('Running parallel_agents_node node ')
    return state


def supervisor_node(state):
    print('Running supervisor node ')
    return state

def build_graph():
    graph = StateGraph(HealthState)
    graph.add_node("triage",triage_node)
    # graph.add_node("parallel_agents",parallel_agents_node)
    # graph.add_node("resource_finder",resource_finder_node)
    # graph.add_node("insurance_checker",insurance_node)
    # graph.add_node("appointment_prep",appointment_prep_node)
    # graph.add_node("reflection",reflection_node)
    # graph.add_node("human_approver",appointment_prep_node)
    # graph.add_node("synthesizer",appointment_prep_node)
    #
    graph.set_entry_point("triage")
    # graph.add_conditional_edges(source = "triage",path = triage_routing,
    #                                             path_map = {"parallel_agents": "parallel_agents",
    #                                                         "synthesizer": "synthesizer"})
    #
    # graph.add_edge("parallel_agents","reflection")
    # graph.add_conditional_edges(source = "reflection",path = reflection_routing,
    #                                             path_map = {"parallel_agents": "parallel_agents",
    #                                                         "human_approver": "human_approver"})
    # graph.add_edge("human_approver","synthesizer")
    # graph.add_edge("synthesizer",END)
    graph.add_edge("triage", END)

    checkpoint = InMemorySaver()
    graph_compiled = graph.compile(checkpoint)
    return graph_compiled

def run_graph(user_query: str, thre
from langgraph.graph import START,END,StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from src.backend.state.health_state import HealthState
from src.backend.agents.triage_agent import triage_node
from src.backend.agents.reflection_agent import reflection_node
from src.backend.agents.resource_finder_agent import resource_finder_node
from src.backend.agents.insurance_agent import insurance_node
from src.backend.agents.appointment_prep_agent import appointment_prep_node
from src.backend.agents.synthesizer_agent import synthesizer_node

def triage_routing(state):
    print('Running triage_routing node ')
    """
    Decide if you want to route to insurance_checker or appointment_prep or resource_finder
    """
    return "insurance_checker"

def reflection_routing(state):
    print('Running reflection_routing node ')
    """
    Decide if you want to route to insurance_checker or appointment_prep or resource_finder
    """
    return "insurance_checker"
def parallel_agents_node(state):
    print('Running parallel_agents_node node ')
    return state


def supervisor_node(state):
    print('Running supervisor node ')
    return state

def build_graph():
    graph = StateGraph(HealthState)
    graph.add_node("triage",triage_node)
    # graph.add_node("parallel_agents",parallel_agents_node)
    # graph.add_node("resource_finder",resource_finder_node)
    # graph.add_node("insurance_checker",insurance_node)
    # graph.add_node("appointment_prep",appointment_prep_node)
    # graph.add_node("reflection",reflection_node)
    # graph.add_node("human_approver",appointment_prep_node)
    # graph.add_node("synthesizer",appointment_prep_node)
    #
    graph.set_entry_point("triage")
    # graph.add_conditional_edges(source = "triage",path = triage_routing,
    #                                             path_map = {"parallel_agents": "parallel_agents",
    #                                                         "synthesizer": "synthesizer"})
    #
    # graph.add_edge("parallel_agents","reflection")
    # graph.add_conditional_edges(source = "reflection",path = reflection_routing,
    #                                             path_map = {"parallel_agents": "parallel_agents",
    #                                                         "human_approver": "human_approver"})
    # graph.add_edge("human_approver","synthesizer")
    # graph.add_edge("synthesizer",END)
    graph.add_edge("triage", END)

    checkpoint = InMemorySaver()
    graph_compiled = graph.compile(checkpoint)
    return graph_compiled

def run_graph(user_query: str, thread_id: str):
    """
        Run the full graph for a patient query.
        Pass the same thread_id to continue a multi-turn conversation.
        """
    graph = build_graph()
    thread_config = {"configurable": {"thread_id": thread_id}}
    initial_state = HealthState(user_query=  user_query,symptoms= user_query,thread_id = thread_id)

    return graph.invoke(initial_state,thread_config)
ad_id: str):
    """
        Run the full graph for a patient query.
        Pass the same thread_id to continue a multi-turn conversation.
        """
    graph = build_graph()
    thread_config = {"configurable": {"thread_id": thread_id}}
    initial_state = HealthState(user_query=  user_query,symptoms= user_query,thread_id = )

    return graph.invoke(initial_state,thread_config)
