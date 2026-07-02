# Rural Healthcare Navigator — 10-Day Build Plan

## Progress Summary
| Day | Focus | Status |
|-----|-------|--------|
| 1 | Triage agent + CDC RAG + Qdrant ingestion | ✅ Done |
| 2 | LangGraph state graph + HealthState + InMemorySaver | ✅ Done |
| 3 | Resource finder agent + 5 tools + structured output | ✅ Done |
| 4 | Insurance checker agent + second Qdrant collection | 🔲 Next |
| 5 | Appointment prep agent + structured Pydantic output | 🔲 |
| 6 | Reflection agent + human-in-the-loop interrupt() | 🔲 |
| 7 | Response synthesizer + astream_events() streaming | 🔲 |
| 8 | Streamlit UI | 🔲 |
| 9 | Evaluation — 8 test scenarios + LangSmith review | 🔲 |
| 10 | README polish + Loom demo recording | 🔲 |

---

## Day 1 — Triage Agent + CDC RAG ✅

**What was built:**
- Triage agent using `with_structured_output()` + Pydantic `TriageResponse`
- RAG pipeline: WebBaseLoader → RecursiveCharacterTextSplitter → Qdrant
- MMR retrieval (fetch_k=20, k=5, lambda_mult=0.5)
- CDC URLs ingested: heart attack, stroke, diabetes, hypertension

**Key files:**
- `agents/triage_agent.py` — TriageResponse Pydantic model, triage_node()
- `rag/medical_rag.py` — ask_medical_question() RAG chain
- `rag/vectorstore.py` — Qdrant create/load with lazy embeddings
- `rag/retriever.py` — MMR retriever with lru_cache
- `rag/populate_vectorstore.py` — one-time ingestion script

**Output written to HealthState:**
```python
triage_result: {
    "urgency":        "HIGH" | "MEDIUM" | "LOW",
    "reasoning":      "explanation string",
    "conditions":     ["condition1", "condition2"],
    "recommendation": "plain language advice"
}
```

---

## Day 2 — LangGraph State Graph + Supervisor ✅

**What was built:**
- HealthState TypedDict (total=False — all fields optional)
- LangGraph StateGraph with all nodes registered (stubs for Days 4-7)
- InMemorySaver checkpointer for multi-turn memory via thread_id
- Direct edge: triage → resource_finder (no routing function needed)
- LangSmith tracing via env vars (zero code required)
- CLI run.py entrypoint

**Key changes from original:**
- Removed duplicate `thread_id` field from HealthState
- Added `messages: list` field for Day 7 multi-turn memory
- Removed unused triage_routing, parallel_agents_node, supervisor_node functions
- Wired all nodes — stubs return {} until implemented

**Key files:**
- `state/health_state.py` — HealthState TypedDict
- `graph/supervisor.py` — build_graph(), run_graph()
- `run.py` — CLI entrypoint

**LangSmith setup (.env):**
```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__...
LANGCHAIN_PROJECT=rural-healthcare-navigator
```

---

## Day 3 — Resource Finder Agent + Tool Calling ✅

**What was built:**
- 5 LangChain @tool functions
- Resource finder agent using ToolNode + tools_condition (no AgentExecutor)
- Structured output using Pydantic ProviderDetail + ResourceFinderOutput
- Two-step LLM pattern: tool calling loop → structured extraction

**Tools built:**

| Tool | API | Cost | Auth |
|------|-----|------|------|
| `geocode_tool` | Nominatim (OpenStreetMap) | Free | None |
| `npi_lookup_tool` | CMS NPI Registry | Free | None |
| `places_detail_tool` | Google Places API (New) | Free tier | API key |
| `fqhc_lookup_tool` | HRSA CSV download | Free | None |
| `pharmacy_nearby_tool` | Google Places API (New) | Free tier | API key |

**Key decisions:**
- Used `geopy.distance.geodesic` for distance (more accurate than Haversine)
- Used reverse geocoding to extract city/state from lat/lon (avoids string parsing)
- USA suffix appended to zip-only inputs (fixes Paris France bug with 75006)
- HRSA CSV downloaded once and cached locally (API doesn't return JSON reliably)
- Google Places (New) API used directly via requests (legacy API blocked)
- No AgentExecutor — manual ToolNode + tools_condition loop (more transparent)
- Two LLM calls: tool calling loop (bind_tools) + structured extraction (with_structured_output)

**Output written to HealthState:**
```python
resource_finder_result: {
    "providers": [
        {
            "name": "Metrocare Services",
            "specialty": "Family Medicine",
            "address": "...",
            "phone": "...",
            "distance_miles": 8.3,
            "rating": 4.2,
            "review_count": 127,
            "open_now": True,
            "weekday_hours": ["Monday: 8AM-5PM", ...],
            "is_fqhc": True,
            "sliding_scale": True,
            "telehealth": False,
            "pharmacy_nearby": {
                "name": "CVS Pharmacy",
                "address": "...",
                "distance_miles": 0.3,
                "open_now": True
            }
        }
    ],
    "summary": "2-3 sentence plain language summary"
}
```

---

## Day 4 — Insurance Checker Agent (Next)

**Plan:**
- Ingest Medicaid/FQHC policy docs into second Qdrant collection
- Build insurance_checker agent with RAG retriever tool
- Wire into graph: resource_finder → insurance_checker → appointment_prep

**Output to write into HealthState:**
```python
insurance_result: {
    "status":      "eligible" | "ineligible" | "unknown",
    "programs":    ["Medicaid", "CHIP"],
    "nearest_fqhc": "Metrocare Services — sliding scale"
}
```

---

## Day 5 — Appointment Prep Agent

**Plan:**
- Pure LLM agent — no external tools
- Reads triage_result + resource_finder_result from state
- Structured output: doctor script + care plan + red flags

---

## Day 6 — Reflection + Human-in-the-Loop

**Plan:**
- Reflection agent: scores output 1-5 on safety + completeness
- Conditional edge: score < 3 → loop back to resource_finder
- Human approval: LangGraph interrupt() — pauses graph for y/n

---

## Day 7 — Synthesizer + Streaming

**Plan:**
- Synthesizer reads all state fields → one plain-language response
- astream_events() — streams each agent result to UI as it completes

---

## Day 8 — Streamlit UI

**Plan:**
- Urgency badge (red/amber/green)
- Provider cards with FQHC flag, rating, pharmacy
- Eligibility panel
- Doctor script (copyable)
- Care plan tabs

---

## Day 9 — Evaluation

**Plan:**
- 8 test scenarios across urgency levels + insurance situations
- LangSmith trace review
- Document in eval table in README

---

## Day 10 — Polish + Demo

**Plan:**
- Update README with current state
- Record 2-minute Loom demo
- Screenshot LangSmith traces

---

## MVP+1 Backlog

- Emergency node — HIGH urgency → direct ER routing (bypass normal flow)
- Supervisor LLM node — LLM dynamically decides which agents to invoke
- True parallel execution via LangGraph Send API
- Qdrant Cloud for persistent multi-session memory
- RAGAS evaluation harness
- Google Maps API replacing Nominatim
- Appointment booking tool (Calendly API)
- Spanish language support
- AWS Lambda + API Gateway deployment
- Transportation assistance lookup
