# Rural Healthcare Navigator — Agent Reference (Current)

## Active Agent Topology

Nodes registered in `build_graph()` (`src/backend/graph/supervisor.py`):

1. `interview` → `interview_node`
2. `chat_state` → `chat_state_generator_node` — **Human-in-the-Loop**: the only node that calls `interrupt()`
3. `triage` → `triage_node`
4. `emergency` → `emergency_state_node` (HIGH urgency only)
5. `resource_finder` → `resource_finder_node` (LOW/MEDIUM urgency only)
6. `appointment` → `appointment_prep_node`

`emergency`, `resource_finder`, and `appointment` all route back through `chat_state` before the graph decides whether to continue or hit `END`.

## HealthState (Current Contract)

`src/backend/state/health_state.py`:

```python
class InterviewData(TypedDict, total=False):
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
    provider_selection: int          # -1 sentinel = not yet selected

    # Interview agent
    interview_data: InterviewData

    # Generic UI output contract
    chat_output: Dict[str, Any]

    # triage agent
    triage_result: Dict

    # resource finder agent
    resource_finder_result: Dict

    # appointment prep agent
    appointment_prep_result: Dict

    # interruption
    should_resume_after_interrupt: bool
    chat_purpose: str
```

`provider_selection` **must** be seeded to `-1` in the fresh-state branch of `run_graph` (it is — see `supervisor.py`). If it's ever left unset (`None`) instead, the `-1` sentinel check in `_chat_state_routing` breaks and can misroute the emergency path into `appointment` — this was a real bug found and fixed during development.

## `chat_purpose` values (`src/backend/state/chat_purpose.py`)

```python
class ChatPurpose:
    INTERVIEW_QUESTION = "interview_question"
    EMERGENCY = "emergency"
    LOCATION_REQUEST = "location_request"
    PROVIDER_SELECTION = "provider_selection"
    FINAL_OUTPUT = "final_output"
    STATUS_UPDATE = "status_update"
    STATUS_EMERGENCY = "status_emergency"
    APPOINTMENT_PREP = "appointment_prep"
```

`chat_purpose` is how an agent node tells `chat_state_generator_node` what to do next. It is always cleared back to `None` once `chat_state_generator_node` has handled it.

## `chat_output` Contract

Built by `chat_state_generator_node` (interrupt path) or `interrupt_to_chat_output()` (resume path) each turn, so the UI stays generic:

```python
{
  "input_required": bool,
  "input_type": (
      "interview_question" | "location_request" | "provider_selection"
      | "status_emergency" | "status_update"
  ),
  "question": str | None,
  "display_message": str | None,
  "options": list,   # populated only for provider_selection
}
```

Only three `chat_purpose` values actually pause the graph via `interrupt()`: `INTERVIEW_QUESTION`, `LOCATION_REQUEST`, `PROVIDER_SELECTION`. `EMERGENCY` and `APPOINTMENT_PREP` produce a terminal, non-interrupting `chat_output` (`input_required=False`) — the graph keeps running to `END` in the same `run_graph()` call.

## Routing Behavior

### `_entry_routing`

- interview not complete → `interview`
- interview complete → `END` (chat_state/triage/etc. take over on the *next* pass through `_chat_state_routing`)

### `_chat_state_routing`

- interview not complete → `interview`
- interview complete, no `triage_result` yet → `triage`
- `provider_selection != -1` (a provider has been picked) and no `appointment_prep_result` yet → `appointment`
- otherwise → `END`

### `_triage_routing`

- `_is_high_urgency(state)` (urgency == `HIGH`) → `emergency`
- else → `resource_finder`

## Agent Details

### Interview Agent

**File:** `src/backend/agents/interview_agent.py`

- Asks one question per turn via a structured `InterviewDecision` (`interview_complete`, `question`, `summary`, `reasoning`), capped at `MAX_INTERVIEW_QUESTIONS = 4`
- On completion, sets `chat_purpose = LOCATION_REQUEST` — location is requested immediately after the interview, **before** triage runs
- On each intermediate turn, sets `chat_purpose = INTERVIEW_QUESTION`

### Chat State Generator Agent — Human-in-the-Loop

**File:** `src/backend/agents/chat_state_generator_agent.py`

The single node responsible for turning internal state into the `chat_output` the UI reads, and the only node that ever calls `interrupt()` — this is the human-in-the-loop mechanism for the whole graph: it's what actually pauses execution and waits for a real person to respond, resumed later via `Command(resume=...)`. Branches on `chat_purpose`:

- `INTERVIEW_QUESTION` → interrupts with the next question; on resume, stores the answer into `most_recent_user_input`
- `LOCATION_REQUEST` → interrupts asking for city/state/ZIP; on resume, stores it into `location`
- `EMERGENCY` → builds a terminal `status_emergency` message from `triage_result.recommendation` (no interrupt)
- `PROVIDER_SELECTION` → interrupts with `resource_finder_result["providers"]` as `options`; on resume, stores the chosen list index into `provider_selection`
- `APPOINTMENT_PREP` → builds a terminal "Appointment confirmed" `status_update` message (no interrupt)
- anything else → generic terminal "Done" `status_update`

### Triage Agent (Qdrant-backed)

**File:** `src/backend/agents/triage_agent.py`

- Reads the interview summary
- Retrieves supporting medical context from **Qdrant** via `ask_medical_question`
- Structured LLM output (`TriageResponse`): `urgency`, `reasoning`, `conditions`, `recommendation`
- `_is_high_urgency(state)` is what `_triage_routing` uses to branch to `emergency` vs `resource_finder`

### Emergency State Agent

**File:** `src/backend/agents/emergency_state_agent.py`

- Trivial node — sets `chat_purpose = EMERGENCY` and nothing else. All the actual message-building happens in `chat_state_generator_node`.

### Resource Finder Agent — Nested Tool-Calling Agent

**File:** `src/backend/agents/resource_finder_agent.py`

Runs only for LOW/MEDIUM urgency. It's a small LangGraph agent (`StateGraph(MessagesState)`) embedded inside the outer graph, running a standard ReAct tool loop:

1. `geocode_tool` — patient location → lat/lon
2. `npi_lookup_tool` — CMS NPI Registry, sorted by geodesic distance
3. `places_detail_tool` — Google Places rating/review count/hours/telehealth
4. `fqhc_lookup_tool` — FQHC / sliding-scale eligibility
5. `pharmacy_nearby_tool` — nearest pharmacy per provider

The tool loop runs via `tools_condition` until the LLM stops requesting tools, then a **second, structured-output LLM call** converts the raw transcript into a typed `ResourceFinderOutput` (list of `ProviderDetail`, each with a nested `PharmacyDetail`). Sets `chat_purpose = PROVIDER_SELECTION`.

### Appointment Prep Agent

**File:** `src/backend/agents/appointment_prep_agent.py`

- Runs after `chat_state_generator_node` records a `provider_selection`
- Currently a stub: returns a static `appointment_prep_result` (`{"status": "ready", "message": ...}`) and sets `chat_purpose = APPOINTMENT_PREP`
- Does **not** yet look up which provider was actually selected (`resource_finder_result["providers"][provider_selection]`) — the confirmation message is generic, not provider-specific. Worth doing before this is presented as "done."

## Model Abstraction

**File:** `src/backend/model/llm.py`

A single shared `LLM` instance (`ChatOpenAI(model='gpt-4o-mini', temperature=0)`), created only if `OPENAI_API_KEY` is present in the environment at import time. `triage_agent`, `interview_agent`, `resource_finder_agent`, and `rag/medical_rag.py` all import this same object rather than constructing their own — the intended seam for adding a second provider (e.g. Azure OpenAI).

Because the check happens at **module import time**, anything that imports this module (directly or transitively) before `load_dotenv()` has run will get `LLM = None` permanently for that process — every real entry point (`main.py`, `run.py`, `src/frontend/app.py`, and the test files that call `load_dotenv()` at the top) calls `load_dotenv()` before importing the graph, so this isn't an issue in practice, but it's an import-order dependency worth knowing about if a new entry point is added.

## Structured Logging

**Directory:** `src/backend/logging/`

- `logger.py` — named logger `rural_health`, level from `LOG_LEVEL` env var, writes JSON lines to `logs/app.log`
- `formatter.py` — `JsonFormatter`: `timestamp`, `level`, `thread_id`, `agent`, `message`, `module`, `function`, `line`
- `context.py` — `contextvars`: `thread_id_var`, `agent_var`

`run_graph()` calls `thread_id_var.set(thread_config)` at the start of each turn — note this currently stores the *whole* `{"configurable": {"thread_id": ...}}` dict into the context var, not the bare thread id string, so log lines will show it nested rather than flat.

## Graph State Continuation

`run_graph()` (`src/backend/graph/supervisor.py`):

- `graph.get_state(thread_config)` before invoke, to load prior turns
- If the prior turn ended on an `interrupt()` (`should_resume_after_interrupt=True`), resumes via `graph.invoke(Command(resume=most_recent_user_input), thread_config)`
- Otherwise, `graph.invoke(graph_state, thread_config)` — a normal run that proceeds synchronously through any number of non-interrupting nodes (e.g. `triage → emergency → chat_state → END` all happen inside one call)
- `graph.update_state(...)` persists the result either way

## Interrupt / Resume — Implemented

This is no longer a planned enhancement — it's the actual mechanism. `chat_state_generator_node` calls LangGraph's `interrupt()` for `INTERVIEW_QUESTION`, `LOCATION_REQUEST`, and `PROVIDER_SELECTION`. The graph genuinely suspends mid-node; the next `run_graph()` call resumes that exact suspended node via `Command(resume=...)`, not just a re-invocation against a re-loaded checkpoint.
