# 🏥 Rural Healthcare Navigator

> An AI-powered multi-agent system that helps rural patients understand symptoms,
> find nearby providers, check insurance eligibility, and prepare for doctor visits —
> running fully locally on your machine.

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-purple)](https://github.com/langchain-ai/langgraph)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-green)](https://langchain.com)
[![Qdrant](https://img.shields.io/badge/Qdrant-local-orange)](https://qdrant.tech)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-red)](https://streamlit.io)
[![LangSmith](https://img.shields.io/badge/LangSmith-traced-yellow)](https://smith.langchain.com)

---

## Architecture

![Rural Healthcare Navigator Architecture](architecture.svg)

> **Download:** [architecture.svg](architecture.svg)

The system is a **supervisor + specialized workers** multi-agent architecture
orchestrated by LangGraph. A supervisor node routes the patient query through a
state graph, invoking specialized agents sequentially, with a reflection loop and
human-in-the-loop approval before the final response is produced.

### Agent Flow

```
Patient Query ("chest pain, no insurance, Angier NC")
        │
        ▼
LangGraph Supervisor  ←── MemorySaver (multi-turn memory via thread_id)
        │
        ▼
Triage Agent
  RAG on CDC URLs (WebBaseLoader → Qdrant MMR retrieval)
  → urgency · reasoning · conditions · recommendation
  → written to HealthState["triage_result"]
        │
        ▼
Resource Finder Agent                          [Day 3]
  tool calling: geocode_tool (Nominatim)
              + npi_lookup_tool (CMS NPI Registry)
  → written to HealthState["clinic_results"]
        │
        ▼
Insurance Checker Agent                        [Day 4]
  RAG on Medicaid/FQHC policy docs (second Qdrant collection)
  → written to HealthState["insurance_result"]
        │
        ▼
Appointment Prep Agent                         [Day 5]
  structured LLM output (Pydantic)
  → doctor script + care plan
  → written to HealthState["appointment_plan"]
        │
        ▼
Reflection Agent                               [Day 6]
  scores output 1–5 on safety + completeness
  loops back to resource_finder if score < 3
  → written to HealthState["reflection"]
        │
        ▼
Human Approval Node                            [Day 6]
  LangGraph interrupt() — pauses graph
  waits for patient y/n before continuing
  → written to HealthState["approved"]
        │
        ▼
Response Synthesizer                           [Day 7]
  merges all state fields → plain-language action plan
  astream_events() → streams to Streamlit UI
        │
        ▼
Streamlit UI                                   [Day 8]
  urgency badge · provider cards · eligibility panel
  doctor script · care plan tabs
```

---

## Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Orchestration** | [LangGraph](https://github.com/langchain-ai/langgraph) | State graph, supervisor routing, conditional edges, `interrupt()` for human-in-the-loop, `MemorySaver` for multi-turn memory |
| **Agent framework** | [LangChain](https://langchain.com) | `@tool` decorator, `bind_tools()`, `with_structured_output()`, `PromptTemplate`, `RetrievalQA` |
| **LLM backend** | OpenAI `gpt-4o-mini` | Powers all agents — structured output via Pydantic models |
| **Vector database** | [Qdrant](https://qdrant.tech) (local) | Two collections: CDC symptom docs (triage) and Medicaid/FQHC policy docs (insurance). HNSW indexing for fast ANN search |
| **RAG retrieval** | MMR — Maximum Marginal Relevance | `fetch_k=20, k=5, lambda_mult=0.5` — returns diverse chunks, not redundant near-duplicates |
| **Embeddings** | OpenAI `text-embedding-3-small` | Document and query embedding for both Qdrant collections |
| **Document loading** | LangChain `WebBaseLoader` | Loads live CDC and Medicaid URLs directly — no PDF download needed |
| **Tool calling** | LangChain `@tool` + `bind_tools()` | Geocoding (Nominatim, free) + NPI provider registry (CMS public API, free) |
| **Memory** | LangGraph `MemorySaver` | Checkpoints `HealthState` between conversation turns via `thread_id` |
| **Observability** | [LangSmith](https://smith.langchain.com) | Auto-traces every node, tool call, and LLM invocation — zero extra code |
| **Structured output** | Pydantic `BaseModel` + `with_structured_output()` | Guarantees consistent JSON shape from LLM — never crashes the graph on malformed output |
| **Streaming** | LangGraph `astream_events()` | Each agent result streams to UI as it completes |
| **UI** | [Streamlit](https://streamlit.io) | Local web UI |
| **External APIs** | Nominatim (geocoding) · CMS NPI Registry (providers) | Both free, no API key required |

### Why Qdrant Over Chroma?

Qdrant is production-grade — used by Microsoft, Mozilla, and Flipkart at scale.
It supports HNSW indexing, filtered search, and named vectors out of the box.
Chroma works well for tutorials but is rarely seen in production AI systems.
Switching from local to Qdrant Cloud is a single config change (URL + API key)
with zero code changes elsewhere.

### Why MMR Over Similarity Search?

Standard similarity search returns the top-k most similar chunks — often near-identical
paragraphs from the same document section. MMR (Maximum Marginal Relevance) fetches
20 candidates then selects the 5 most *diverse* ones, giving the LLM broader context
and reducing hallucination on edge cases.

---

## Shared State — HealthState

Every agent reads from and writes to a single `HealthState` TypedDict.
LangGraph merges each node's partial return dict into the shared state automatically.

```python
class HealthState(TypedDict, total=False):
    # Input
    user_query:       str          # original patient query
    symptoms:         str          # extracted symptom text
    location:         str          # patient location string
    insurance:        str          # insurance type mentioned
    thread_id:        str          # MemorySaver session ID

    # Triage agent output
    triage_result:    Dict         # {urgency, reasoning, conditions, recommendation}

    # Resource finder output (Day 3)
    clinic_results:   List[Dict]   # [{name, address, phone, distance_miles}]

    # Insurance checker output (Day 4)
    insurance_result: Dict         # {status, programs, nearest_fqhc}

    # Appointment prep output (Day 5)
    appointment_plan: Dict         # {doctor_script, care_plan, red_flags}
    care_plan:        str

    # Reflection output (Day 6)
    reflection:       Dict         # {score, notes}

    # Human approval (Day 6)
    approved:         bool

    # Synthesizer output (Day 7)
    final_response:   str
```

---

## Project Structure

```
rural-healthcare-navigator/
├── src/
│   └── backend/
│       ├── agents/
│       │   ├── triage_agent.py         ✅ working — RAG on CDC URLs
│       │   ├── resource_finder.py      🔲 Day 3
│       │   ├── insurance_checker.py    🔲 Day 4
│       │   ├── appointment_prep.py     🔲 Day 5
│       │   └── reflection_agent.py     🔲 Day 6
│       ├── graph/
│       │   ├── state.py                ✅ HealthState TypedDict
│       │   └── supervisor.py           ✅ LangGraph graph + MemorySaver
│       ├── rag/
│       │   ├── ingestion.py            ✅ WebBaseLoader + chunking
│       │   ├── vectorstore.py          ✅ Qdrant create/load
│       │   ├── retriever.py            ✅ MMR retriever (lru_cache)
│       │   └── medical_rag.py          ✅ RAG chain for triage context
│       ├── tools/
│       │   ├── geocoding.py            🔲 Day 3 — Nominatim @tool
│       │   └── npi_lookup.py           🔲 Day 3 — CMS NPI @tool
│       └── run.py                      ✅ CLI entrypoint
├── src/frontend/
│   └── app.py                          🔲 Day 8 — Streamlit UI
├── populate_vectorstore.py             ✅ one-time Qdrant ingestion
├── architecture.svg
├── requirements.txt
├── .env.example
└── README.md
```

---

## Prerequisites

- Python 3.11+
- `git`
- OpenAI API key (get one at [platform.openai.com](https://platform.openai.com))
- Free [LangSmith](https://smith.langchain.com) account (optional but strongly recommended)

---

## How to Run (MVP — Fully Local)

### 1. Clone the repo

```bash
git clone https://github.com/amohan601/rural-healthcare-navigator.git
cd rural-healthcare-navigator
```

### 2. Create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
# OpenAI
OPENAI_API_KEY=sk-...

# LangSmith observability (free — get key at smith.langchain.com)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__...
LANGCHAIN_PROJECT=rural-healthcare-navigator

# Qdrant — local
QDRANT_PATH=./qdrant_data

# Qdrant Cloud (uncomment to switch — zero other code changes)
# QDRANT_URL=https://xyz.qdrant.io
# QDRANT_API_KEY=your-key-here
```

### 5. Populate the Qdrant vector store

Loads CDC and Medicaid URLs, chunks them, embeds with OpenAI, and persists
to `./qdrant_data`. Run once — not needed again unless you add new URLs.

```bash
python populate_vectorstore.py
```

Expected output:
```
Total chunks: 87
Created 'rural_health_medical' with 87 chunks
```

### 6. Verify RAG pipeline

```bash
python -c "
from src.backend.rag.retriever import retrieve_documents
docs = retrieve_documents('chest pain symptoms')
print(f'Retrieved {len(docs)} chunks')
print(docs[0].page_content[:200])
"
```

### 7. Test triage agent in isolation

```bash
python -c "
from src.backend.agents.triage_agent import triage_node
result = triage_node({
    'user_query': 'I have chest pain and shortness of breath',
    'symptoms':   'I have chest pain and shortness of breath'
})
print(result['triage_result'])
"
```

Expected:
```python
{
  'urgency':        'HIGH',
  'reasoning':      'Chest pain with shortness of breath...',
  'conditions':     ['Angina', 'Myocardial Infarction', 'Pulmonary Embolism', 'GERD'],
  'recommendation': 'Seek immediate medical attention or go to the nearest emergency room.'
}
```

### 8. Run full graph via CLI

```bash
python src/backend/run.py "I have chest pain and shortness of breath"
```

### 9. Multi-turn conversation

```bash
# Copy thread_id from previous output
python src/backend/run.py "I also have a history of diabetes" --thread <thread-id>
```

The agent remembers your previous triage result and refines its response.

### 10. View traces in LangSmith

If `LANGCHAIN_API_KEY` is set, every run is automatically traced.
Visit [smith.langchain.com](https://smith.langchain.com) → project
`rural-healthcare-navigator` to see full node-by-node execution traces,
tool calls, LLM latency, and token usage.

---

## Sample Queries

| Query | Urgency | Key output |
|---|---|---|
| `"chest pain for 2 hours, no insurance, Angier NC"` | 🔴 HIGH | Emergency referral, Medicaid eligibility |
| `"persistent cough 3 weeks, BlueCross, Raleigh NC"` | 🟡 MEDIUM | Pulmonologist options, in-network |
| `"minor ankle sprain, Medicaid, Clayton NC"` | 🟢 LOW | Urgent care, RICE instructions |

---

## 10-Day Build Plan

| Day | Focus | Status |
|---|---|---|
| 1 | Triage agent + CDC RAG + Qdrant ingestion | ✅ Done |
| 2 | LangGraph state graph + HealthState + MemorySaver | ✅ Done |
| 3 | Resource finder agent + tool calling (Nominatim + NPI) | 🔲 Next |
| 4 | Insurance checker agent + second Qdrant collection | 🔲 |
| 5 | Appointment prep agent + structured Pydantic output | 🔲 |
| 6 | Reflection agent + human-in-the-loop interrupt() | 🔲 |
| 7 | Response synthesizer + astream_events() streaming | 🔲 |
| 8 | Streamlit UI | 🔲 |
| 9 | Evaluation — 8 test scenarios, LangSmith trace review | 🔲 |
| 10 | README polish + Loom demo recording | 🔲 |

---

## Design Decisions

**Why LangGraph over plain LangChain?**
LangGraph provides a proper state machine with conditional edges, sequential
node execution, `interrupt()` for human-in-the-loop, and `MemorySaver` for
multi-turn memory. A vanilla LangChain `AgentExecutor` chain cannot pause
mid-execution for human input or route dynamically between multiple agents
based on accumulated state.

**Why individual nodes per agent rather than one combined node?**
Each agent owns exactly one slice of `HealthState`. Keeping them as separate
LangGraph nodes means each can be developed, tested, and replaced independently.
It also makes the graph visible in LangSmith as distinct steps rather than a
single opaque blob.

**Why Qdrant over Chroma?**
Qdrant is production-grade with HNSW indexing, used at scale by companies
like Microsoft and Mozilla. Chroma is popular in tutorials but rarely seen
in production. The local-to-cloud migration path with Qdrant is a single
config change with zero code changes.

**Why MMR retrieval over standard similarity search?**
Standard top-k similarity often returns near-identical chunks from adjacent
paragraphs. MMR fetches 20 candidates and selects the 5 most diverse, giving
the LLM broader context and reducing hallucination risk on rare symptom patterns.

**Why `with_structured_output()` on the triage LLM?**
Guarantees a consistent Pydantic-validated dict is written into `HealthState`
regardless of how the LLM formats its response. A malformed LLM output never
crashes the graph — the Pydantic model catches it and the fallback kicks in.

**Why `lru_cache` on the Qdrant client?**
Without caching, every patient query reloads the entire Qdrant collection from
disk. With `@lru_cache(maxsize=1)` the vectorstore loads once on first call and
is reused for every subsequent query in the same process.

**Why WebBaseLoader over PDFs?**
CDC and Medicaid publish authoritative, up-to-date content on public URLs.
Loading directly from URLs means the knowledge base stays current without
manually downloading and re-ingesting PDF files.

---

## Roadmap (Post-MVP)

- [ ] Add supervisor LLM node — LLM dynamically decides which agents to invoke
- [ ] True parallel agent execution using LangGraph `Send` API
- [ ] Switch Qdrant to cloud for persistent multi-session memory
- [ ] Add RAGAS evaluation harness for RAG quality measurement
- [ ] Replace Nominatim with Google Maps API for richer provider data
- [ ] Add appointment booking tool (Calendly API)
- [ ] Spanish-language query support via LangChain translation chain
- [ ] Deploy to AWS Lambda + API Gateway

---

## Author

**Anju Mohan** — Data Pipeline and Application Engineer, Georgia Tech MS in Machine Learning.
Transitioning to AI Engineering.

[GitHub](https://github.com/amohan601) · [LinkedIn](https://linkedin.com/in/anju-mohan)