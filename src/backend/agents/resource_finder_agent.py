
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.graph import START, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from src.backend.tools.fqhc_lookup import fqhc_lookup_tool
from src.backend.tools.geocoding import geocode_tool
from src.backend.tools.npi_lookup import npi_lookup_tool
from src.backend.tools.pharmacy_nearby import pharmacy_nearby_tool
from src.backend.tools.places_detail import places_detail_tool
from src.backend.state.health_state import HealthState
from typing import Optional
from src.backend.model.llm import LLM
from pydantic import BaseModel, Field
from src.backend.state.chat_purpose import ChatPurpose
from src.backend.logging.logger import logger
# src/backend/agents/resource_finder.py
# Add Pydantic models for structured output



class PharmacyDetail(BaseModel):
    name:           str            = Field(description="Pharmacy name")
    address:        Optional[str]  = Field(description="Full address",                      default=None)
    distance_miles: Optional[float]= Field(description="Distance from provider in miles",   default=None)
    open_now:       Optional[bool] = Field(description="Whether pharmacy is open now",       default=None)


class ProviderDetail(BaseModel):
    name:            str                      = Field(description="Provider or clinic name")
    specialty:       Optional[str]            = Field(description="Medical specialty",          default=None)
    address:         Optional[str]            = Field(description="Full address",               default=None)
    phone:           Optional[str]            = Field(description="Phone number",               default=None)
    distance_miles:  Optional[float]          = Field(description="Distance from patient",      default=None)
    rating:          Optional[float]          = Field(description="Google Places rating 1-5",   default=None)
    review_count:    Optional[int]            = Field(description="Number of Google reviews",   default=None)
    open_now:        Optional[bool]           = Field(description="Whether clinic is open now", default=None)
    weekday_hours:   list[str]                = Field(description="Hours per weekday",          default=[])
    is_fqhc:         Optional[bool]           = Field(description="Is FQHC",                    default=None)
    sliding_scale:   Optional[bool]           = Field(description="Sliding scale fees",         default=None)
    telehealth:      Optional[bool]           = Field(description="Telehealth available",       default=None)
    pharmacy_nearby: Optional[PharmacyDetail] = Field(description="Nearest pharmacy",          default=None)


class ResourceFinderOutput(BaseModel):
    providers: list[ProviderDetail] = Field(description="List of up to 3 nearby providers")
    summary: str = Field(description="Plain language summary for the patient")


TOOLS = [
    geocode_tool,
    npi_lookup_tool,
    pharmacy_nearby_tool,
    places_detail_tool,
    fqhc_lookup_tool
]


STRUCTURED_LLM = LLM.with_structured_output(ResourceFinderOutput)

RESOURCE_FINDER_SYSTEM_PROMPT = """
You are a resource finder agent for rural healthcare patients.
 
Your job is to find nearby healthcare providers based on the patient's
location and medical conditions. Follow this sequence:
 
1. Call geocode_tool to convert the patient location to lat/lon
2. Extract the medical specialty from the conditions provided
3. Call npi_lookup_tool with the specialty, city, state, and lat/lon
4. For each provider returned, call places_detail_tool to get rating and reviews
5. Call fqhc_lookup_tool for each provider to check sliding scale eligibility
6. Call geocode_tool for each provider address to get that provider's lat/lon
7. Call pharmacy_nearby_tool using each provider's lat/lon from step 6
 
Return a structured summary of the top 3 providers with all enriched details.
Always prioritize FQHC providers for uninsured patients.
"""

STRUCTURED_OUTPUT_PROMPT = """
You are summarizing healthcare provider search results for a rural patient.
 
Based on the tool results in the conversation, produce a structured response
with the top 3 providers and their full details including pharmacy information.
 
For the summary field write 2-3 plain language sentences the patient can understand.
Prioritize FQHC providers for uninsured patients.
"""


def _build_agent_graph():
    llm_with_tools = LLM.bind_tools(TOOLS)
    return llm_with_tools


def _build_input(state: HealthState):
    logger.info("[resource_finder_agent]  building input from health state")
    triage = state.get("triage_result", {})
    query = state.get("most_recent_user_input", "")
    location = state.get("location", "")
    conditions = triage.get("conditions", [])
    urgency = triage.get("urgency", "MEDIUM")
    insurance = state.get("insurance", "unknown")
    return f"""
    Patient query: {query}
    Urgency: {urgency}
    location: {location}
    Conditions: {', '.join(conditions)}
    Insurance: {insurance}
    
    Use the location given here for geocoding.
    Find nearby healthcare providers. Extract the location from the patient query.
    If no insurance or unknown, prioritize FQHC providers.
    """


"""
    After tool calling loop completes, run a second LLM call
    with structured output to convert raw tool results into
    a clean ResourceFinderOutput Pydantic model.
"""


def _build_structured_output(messages: list) -> ResourceFinderOutput:
    """
    Second LLM call — converts raw tool results into structured Pydantic output.
    FIXED: receives messages list directly (not result dict).
    """
    logger.info('[resource_finder_agent]  Running _build_structured_output')
    """
        After tool calling loop completes, run a second LLM call
        with structured output to convert raw tool results into
        a clean ResourceFinderOutput Pydantic model.
        """
    response = STRUCTURED_LLM.invoke([SystemMessage(content=STRUCTURED_OUTPUT_PROMPT), *messages])
    return response



def _custom_tool_node(state: MessagesState):
    logger.info('[resource_finder_agent]  Running _custom_tool_node ')
    last_message = state["messages"][-1]

    # Print BEFORE execution — we're inside the tool node now
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        for tc in last_message.tool_calls:
            logger.info(f"  → executing tool : {tc['name']}")
            logger.info(f"    args: {tc['args']}")

    # Then execute
    return ToolNode(TOOLS).invoke(state)


def resource_finder_node(state: HealthState):
    logger.info('[resource_finder_agent]  Running resource_finder node ')
    llm_with_tools = _build_agent_graph()
    initial_messages = [
        SystemMessage(content=RESOURCE_FINDER_SYSTEM_PROMPT),
        HumanMessage(content=_build_input(state))
    ]
    """
    The actual llm execution happens here. 
    """

    def resource_finder(state: MessagesState):
        logger.info('[resource_finder_agent] Running resource_finder ')
        return {"messages": [llm_with_tools.invoke(state["messages"])]}

    # ── Build mini agent graph ─────────────────────────────────────
    builder = StateGraph(MessagesState)
    builder.add_node("resource_finder", resource_finder)
    builder.add_node("tools", _custom_tool_node)

    builder.add_edge(START, "resource_finder")
    builder.add_conditional_edges("resource_finder", tools_condition)
    builder.add_edge("tools", "resource_finder")
    graph_compiled = builder.compile()

    # ── Step 1: Run tool calling loop ──────────────────────────────
    logger.info('[resource_finder_agent] Invoking agent graph')
    result = graph_compiled.invoke({"messages": initial_messages})
    # print(result["messages"][-1].pretty_print())
    messages = result["messages"]

    # ── Step 2: Extract structured output ──────────────────────────
    resource_finder_output = _build_structured_output(messages)
    logger.debug(f"[resource_finder_agent] Found {len(resource_finder_output.providers)} providers")

    return {
        "resource_finder_result": {
            "providers": resource_finder_output.providers,
            "summary": resource_finder_output.summary
        },
        "chat_purpose": ChatPurpose.PROVIDER_SELECTION
    }