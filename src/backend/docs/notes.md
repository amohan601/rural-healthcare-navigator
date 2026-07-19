# Dev Setup Notes (Current)

## Environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt` is a real pinned requirements file (`langgraph`, `langchain`, `langchain-openai`, `langchain-community`, `langchain-core`, `langchain-qdrant`, `langchain-text-splitters`, `qdrant-client`, `fastapi`, `uvicorn`, `python-dotenv`, `geopy`, `streamlit`, `requests`, `pydantic`). It previously contained pasted shell commands instead of package names — if you find an old copy of this file that looks like install instructions rather than a package list, it's stale; the original pasted content was preserved in `mynotes.txt` (gitignored) for reference only.

## `.env`

See `.env.example` at the repo root for the required keys:

```
OPENAI_API_KEY=
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT=rural-healthcare-navigator
GOOGLE_PLACES_API_KEY=
LOG_LEVEL=INFO
```

`LANGCHAIN_TRACING_V2` + `LANGCHAIN_API_KEY` + `LANGCHAIN_PROJECT` enable LangSmith tracing automatically — no code changes needed, LangChain picks these up from the environment.

## Running the app

Streamlit UI (current path — the UI was moved from `src/ui/` to `src/frontend/`):

```bash
streamlit run src/frontend/app.py
```

FastAPI mode (optional):

```bash
uvicorn src.backend.main:rural_navigator_app --reload
```

CLI mode (single-turn or `--thread <id>` for multi-turn):

```bash
python -m src.backend.run "headache and blurred vision" --thread <thread_id>
```

## Populating Qdrant

```bash
python -m src.backend.rag.populate_medical_docs_vectorstore
```

Ingests the medical reference docs (`src/backend/rag/ingestion.py`, `WebBaseLoader` + `RecursiveCharacterTextSplitter`) into the local Qdrant collection the triage agent retrieves from.

## Logs

Structured JSON logs go to `logs/app.log` (gitignored). Set `LOG_LEVEL=DEBUG` in `.env` for verbose output. Log lines carry `thread_id` for correlating a single conversation across turns — see `src/backend/logging/`.

## Tests

```bash
pytest src/backend/tests/
```

Several tests make live LLM/API calls (triage, resource finder, interview agent), so a valid `.env` is required to run the full suite, and running it repeatedly has real API cost.
