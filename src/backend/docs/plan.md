# Rural Healthcare Navigator — Current Plan

## Current Delivered Flow

| Area | Status | Notes |
|------|--------|-------|
| Interview agent | ✅ Done | Asks one question at a time, capped follow-up loop (`MAX_INTERVIEW_QUESTIONS=4`) |
| Chat state generator agent | ✅ Done | Human-in-the-loop node — single node that owns `interrupt()`; turns internal state into the generic `chat_output` contract |
| Triage agent | ✅ Done | Uses medical RAG context (Qdrant) + structured urgency output |
| Emergency agent | ✅ Done | HIGH urgency → styled `status_emergency` alert, conversation ends |
| Resource finder agent | ✅ Done | Nested tool-calling (ReAct) agent: geocode → NPI lookup → places detail → FQHC lookup → pharmacy nearby |
| Appointment prep agent | ⚠️ Stubbed | Runs after provider selection, but returns a static confirmation message — doesn't yet look up which provider was actually chosen |
| Supervisor routing | ✅ Done | Conditional routing (`_entry_routing`, `_chat_state_routing`, `_triage_routing`) with thread-aware state |
| Human-in-the-loop pause/resume | ✅ Done | Real `interrupt()` / `Command(resume=...)` — not just re-invocation against a reloaded checkpoint |
| Generic UI output (`chat_output`) | ✅ Done | UI reads only the generic prompt/status/options contract |
| Provider selection UI | ✅ Done | Full provider + nested pharmacy detail cards, radio picker resumes the graph with the selected index |
| Emergency alert styling | ✅ Done | UI renders a distinct red alert card when `input_type == "status_emergency"`, not a plain chat bubble |
| Model abstraction | ✅ Done | Single shared `LLM` in `src/backend/model/llm.py`, used by every agent + `medical_rag.py` |
| Structured logging | ✅ Done | JSON logs (`src/backend/logging/`) with `thread_id`/`agent` context, replacing ad-hoc `print()` |
| LangSmith observability | ✅ Done | Verified working — traces visible per conversation turn (see main README) |
| Insurance / reflection / human-approval / synthesizer agents | ❌ Descoped | Earlier agent files for these were removed from the codebase entirely, not just deferred — would need to be rebuilt from scratch if revived |

---

## Latest Execution Plan (Implemented)

1. User sends `most_recent_user_input`
2. Supervisor loads prior graph state using `thread_id`; if the prior turn ended on an `interrupt()`, resumes that exact node via `Command(resume=...)`
3. Graph routes through interview → chat_state → triage → (emergency | resource_finder) → chat_state → (appointment if a provider was picked) → chat_state → END, pausing only at the three `interrupt()` points (next interview question, location request, provider selection)
4. Supervisor builds `chat_output` and persists updated state
5. UI renders `chat_output` — asks the next input, or displays a status/result message (styled specially for the emergency case)

---

## State & UI Conversation Continuity

Current design uses:

- `InMemorySaver` checkpoint store — **in-memory only**, state is lost on process restart. This is the main gap between "demo" and "production" for this project.
- `graph.get_state()` before invoke
- `graph.update_state()` after invoke
- repeated calls with same `thread_id`, resuming via `Command(resume=...)` when the prior turn paused on `interrupt()`

---

## Qdrant Plan and Usage

Qdrant is actively used for symptom triage retrieval.

- Collection populated from medical reference content via `src/backend/rag/ingestion.py` + `populate_medical_docs_vectorstore.py`
- Embeddings: `text-embedding-3-small`; retrieval: MMR
- Triage consumes retrieved context before urgency reasoning

Not yet implemented (see Next Milestones): a second collection or graph store for provider/pharmacy/condition relationships.

---

## Interrupt / Resume Strategy — Implemented

What was previously planned is now the actual mechanism:

- `chat_state_generator_node` calls LangGraph's `interrupt()` for the interview question, location request, and provider selection steps
- The graph genuinely suspends mid-node at each of those points
- The next `run_graph()` call resumes the exact paused node via `graph.invoke(Command(resume=most_recent_user_input), thread_config)`
- `emergency` and `appointment_prep` are terminal, non-interrupting states — they run to `END` within the same call that produced them

---

## Next Milestones

(kept in sync with the Roadmap in the top-level README)

1. Add a labeled eval set for the triage agent (symptom → expected urgency) with agreement/precision scoring
2. Unit tests for `_chat_state_routing` / `_triage_routing` edge cases — three real bugs (falsy-zero provider index, unset `provider_selection` default misrouting emergency into appointment, missing loop guard causing infinite recursion) were found and fixed during development but aren't yet covered by regression tests
3. Have `appointment_prep_node` actually look up and confirm the selected provider (`resource_finder_result["providers"][provider_selection]`) instead of returning a static message
4. Full per-node LangSmith tracing tags + run metadata so a conversation's spans are broken down by node, not one opaque span per turn
5. Route the model abstraction (`src/backend/model/llm.py`) through Azure OpenAI as a selectable provider
6. Dockerfile + docker-compose (app + Qdrant) and a CI workflow running tests/lint on push
7. Replace `InMemorySaver` with a persistent LangGraph checkpointer (SQLite/Postgres) so conversations survive a restart
8. Neo4j-backed graph of provider/pharmacy/condition relationships as an alternative to pure vector retrieval for resource matching
