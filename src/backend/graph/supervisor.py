from typing import Any, Union

from langgraph._internal._typing import DataclassLike, TypedDictLikeV1, TypedDictLikeV2
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel
from langgraph.types import Command

from src.backend.agents.chat_state_generator_agent import interrupt_to_chat_output
from src.backend.agents.chat_state_generator_agent import chat_state_generator_node
from src.backend.agents.interview_agent import interview_node
from src.backend.agents.emergency_state_agent import emergency_state_node
from src.backend.agents.triage_agent import triage_node
from src.backend.agents.resource_finder_agent import resource_finder_node
from src.backend.agents.appointment_prep_agent import appointment_prep_node
from src.backend.state.health_state import HealthState
from src.backend.graph.router import _entry_routing,_chat_state_routing,_triage_routing
from src.backend.logging.context import thread_id_var
from src.backend.logging.logger import logger

_compiled_graph = None


def build_graph():
    logger.debug("[supervisor] entered build_graph")
    graph = StateGraph(HealthState)
    graph.add_node("interview", interview_node)
    graph.add_node("chat_state", chat_state_generator_node)
    graph.add_node("triage", triage_node)
    graph.add_node("emergency", emergency_state_node)
    graph.add_node("resource_finder", resource_finder_node)
    graph.add_node("appointment", appointment_prep_node)

    graph.add_conditional_edges(
        START,
        _entry_routing,
        {
            "interview": "interview",
            "END": END
        },
    )
    graph.add_edge("interview", "chat_state")
    graph.add_conditional_edges(
        "chat_state",
        _chat_state_routing,
        {
            "interview": "interview",
            "triage": "triage",
            "appointment": "appointment",
            "END": END
        },
    )
    graph.add_conditional_edges(
        "triage",
        _triage_routing,
        {
            "emergency": "emergency",
            "resource_finder": "resource_finder"
        },
    )
    graph.add_edge("emergency", "chat_state")
    graph.add_edge("resource_finder", "chat_state")
    graph.add_edge("appointment", "chat_state")

    checkpoint = InMemorySaver()
    return graph.compile(checkpoint)


def get_compiled_graph():
    logger.debug("[supervisor] entered get_compiled_graph")
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
    return _compiled_graph


def _load_graph_state(graph, thread_config):
    logger.debug("[supervisor] entered _load_graph_state")
    snapshot = graph.get_state(thread_config)
    if not snapshot or not snapshot.values:
        return {}
    return dict(snapshot.values)



def _build_and_update_interruption_payload(
        graph: CompiledStateGraph[Union[TypedDictLikeV1, TypedDictLikeV2, DataclassLike, BaseModel], Any, Any, Any],
        graph_state: Union[dict[Any, Any], dict[str, Any], dict[str, str], dict[bytes, bytes], dict[
            str, Union[dict[str, Union[list[Any], int, str, bool]], Any]]], result: Union[dict[str, Any], Any],
        thread_config: dict[str, dict[str, Any]]) -> Union[Union[
    dict[str, Any], dict[Any, Any], dict[str, str], dict[bytes, bytes], dict[
        str, Union[dict[str, Union[list[Any], int, str, bool]], Any]]], Any]:
    logger.info(f'[supervisor] interrupted state identified after invoke finished')
    interrupt_payload = result["__interrupt__"][0]
    interrupt_value = getattr(interrupt_payload, "value", interrupt_payload)
    snapshot = graph.get_state(thread_config)
    interrupted_state = snapshot.values if snapshot and snapshot.values else graph_state
    interrupted_state["chat_output"] = interrupt_to_chat_output(interrupt_value)
    interrupted_state["should_resume_after_interrupt"] = True
    graph.update_state(thread_config, interrupted_state)
    logger.debug(f'[supervisor] building customer interruption state response interrupted_state={interrupted_state}')
    return {
        "chat_output": interrupted_state["chat_output"]
    }


def run_graph(most_recent_user_input, thread_id):
    logger.info("[supervisor] entered run_graph ***** ")
    graph = get_compiled_graph()
    thread_config = {"configurable": {"thread_id": thread_id}}
    thread_id_var.set(thread_config)
    logger.info("[supervisor] thread_id set for this execution")
    prior_state = _load_graph_state(graph, thread_config)

    if prior_state:
        prior_state["most_recent_user_input"] = most_recent_user_input
        graph_state = prior_state
        logger.debug(f"[supervisor] existing graph state {graph_state}")
    else:
        graph_state = {
            "most_recent_user_input": most_recent_user_input,
            "thread_id": thread_id,
            "provider_selection": -1,
            "interview_data": {
                "interview_history": [],
                "interview_questions_asked": 0,
                "next_interview_question": "",
                "interview_complete": False,
                "summary": "",
                "reasoning": "",
            },
        }
        logger.debug(f"[supervisor] fresh graph state {graph_state}")

    logger.debug(f"[supervisor] (Before) graph_state={graph_state}")
    should_resume_after_interrupt = graph_state.get("should_resume_after_interrupt")

    result = None
    if should_resume_after_interrupt:
        logger.info(f'[supervisor] invoke should_resume_after_interrupt flow')
        graph_state["should_resume_after_interrupt"] = False
        graph.update_state(thread_config, graph_state)
        result = graph.invoke(Command(resume=most_recent_user_input.strip()), thread_config)
    else:
        logger.info(f'[supervisor] invoke graph regular flow')
        result = graph.invoke(graph_state, thread_config)

    logger.debug(f"[supervisor] (After) invocation graph_state={_load_graph_state(graph,thread_config)}")
    logger.debug(f"[supervisor] result={result}")
    interrupted = "__interrupt__" in result

    if  interrupted:
        interrupted_state = _build_and_update_interruption_payload(graph, graph_state, result, thread_config)
        logger.debug(f"[supervisor] (After) interruption flow.. graph_state={_load_graph_state(graph,thread_config)}")
        logger.debug(f"[supervisor] output back .. {interrupted_state}")
        logger.debug(f"[supervisor] interrupted and returning")
        return interrupted_state
    else:
        logger.info("[supervisor] no interruption..exiting")
        graph.update_state(thread_config, result)

    graph_state = _load_graph_state(graph,thread_config)
    logger.debug(f"[supervisor] (After) graph_state={graph_state}")

    logger.info(f"[supervisor] ***END of Supervisor***")
    return {
        "chat_output": graph_state["chat_output"]
    }
