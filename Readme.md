Rural Health Navigator is an AI system that helps users in rural areas:

- Understand symptoms and urgency
- Find nearby healthcare providers
- Check insurance coverage (simulated or RAG-based)
- Prepare for doctor visits
- Generate care plans

The system uses multi-agent orchestration (LangGraph),
RAG pipelines, and external tools like maps APIs.


                    ┌───────────────┐
                    │     USER      │
                    └──────┬────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │  SUPERVISOR AGENT    │
                │ (Planner + Router)   │
                └─────────┬────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼

 ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
 │ TRIAGE AGENT │ │ INSURANCE    │ │ RESOURCE     │
 │ (symptoms)   │ │ AGENT        │ │ FINDER       │
 └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
        │                │                 │
        ▼                ▼                 ▼
 Medical RAG      Policy RAG        Google Maps API
 CDC/NIH docs     Medicare docs     Clinics dataset

        └──────────────┬──────────────┘
                       ▼
           ┌────────────────────────┐
           │ APPOINTMENT PREP AGENT │
           └──────────┬─────────────┘
                      ▼
           ┌────────────────────────┐
           │ CARE PLAN AGENT        │
           └──────────┬─────────────┘
                      ▼
           ┌────────────────────────┐
           │ REFLECTION AGENT       │
           └──────────┬─────────────┘
                      ▼
           ┌────────────────────────┐
           │ HUMAN APPROVAL NODE    │
           └──────────┬─────────────┘
                      ▼
                    END