Updated 10-Day Plan
Day 1 — DONE

Your existing triage agent with CDC RAG is committed and working. Verify it returns structured output (urgency, conditions, recommendation). Tag it v0.1-triage-working. Nothing else to touch here.

Day 2 — LangGraph state graph + supervisor + LangSmith

Define NavigatorState as a TypedDict — nail this on day 2 because every other agent reads from it. Set up LangSmith tracing with two env vars (LANGCHAIN_TRACING_V2=true, LANGCHAIN_API_KEY). Wrap your triage agent as a LangGraph node. Build the supervisor with conditional edges. Goal: graph compiles, triage node runs, you can see the trace in LangSmith dashboard. The observability setup is 10 minutes of work and you get a visual graph of every run for free from this day forward.

Day 3 — Resource finder agent + tool calling

Build two @tool functions: Nominatim geocoding (free, no API key) and CMS NPI Registry lookup (free public API). Create the resource finder AgentExecutor using llm.bind_tools([...]). Wire into the graph. Test: "find a cardiologist near 27501." The LLM should autonomously decide to call geocoding first, then NPI. This is your primary tool-calling demo moment — practice explaining it out loud as you build it.

Day 4 — Insurance checker agent + second RAG pipeline

Download Medicaid eligibility PDFs and FQHC fact sheets from CMS.gov and HRSA.gov. Ingest into a second Chroma collection — reuse your existing ingestion code, just point it at different docs. Build the insurance checker agent with a RAG retriever tool. Wire the resource finder and insurance checker to run as parallel nodes in LangGraph. This is the most architecturally interesting day — parallel agent execution is a concrete thing you can explain and demo.

Day 5 — Appointment prep agent (merged with care plan)

Single agent, no external tools — pure prompt engineering over triage state. Two structured outputs in one response: a "what to tell your doctor" script (5 bullet points) and a care plan (immediate action, 48-hour follow-up, red flags). Structured output using Pydantic models with llm.with_structured_output(AppointmentPrepOutput). This shows you know how to get reliable JSON from an LLM. Wire into graph. Run full pipeline end-to-end for first time — tag v0.5-pipeline-complete.

Day 6 — Reflection agent + human-in-the-loop

Reflection agent grades the full output 1-5 on safety, completeness, and clarity. Add a conditional edge: if score < 3, loop back and regenerate. Human approval node uses LangGraph's interrupt() — pauses the graph, prints the plan, waits for y/n. This is the most interview-impressive feature in the whole project. Practice the explanation: "the graph literally pauses mid-execution and waits for a human decision before continuing." That's agentic AI safety patterns — exactly what senior AI engineers care about.

Day 7 — MemorySaver + multi-turn conversations

Add MemorySaver checkpointer to your graph with a thread_id. Now a follow-up query like "what if I also have diabetes?" picks up from where the last conversation left off — the agent already knows your urgency, conditions, and location. Build a simple loop in your CLI runner that keeps the conversation going. Demo: first turn triage + resources, second turn refine based on new info. This is the difference between a chatbot and a stateful agent.

Day 8 — Streaming + Streamlit UI

Switch to graph.astream_events() so each agent result appears in the UI as it completes rather than all at the end. Build the Streamlit app: text input, submit button, and a live output area that fills in progressively — urgency badge first (red/yellow/green), then provider cards, then eligibility, then doctor script. The streaming makes it feel alive. Show each agent's contribution in a separate section so the multi-agent architecture is visually obvious to anyone watching.

Day 9 — Evaluation + LangSmith traces

Write 8 test scenarios spanning different urgencies, insurance situations, and locations. Run all 8, document results in a markdown eval table: expected urgency vs actual, provider count returned, eligibility accuracy, appointment script relevance (1-5 human rating). Pull up your LangSmith dashboard — you'll have traces for every run showing exactly which tools were called, how long each agent took, and where any failures happened. Screenshot this for your portfolio README. Evaluation methodology is a serious talking point that most junior candidates skip entirely.

Day 10 — README, demo, portfolio polish

Update README with: architecture diagram, tech stack table, how to run locally (single make run command ideally), sample inputs/outputs for 3 scenarios, a "design decisions" section explaining why each tech choice was made (LangGraph for stateful routing, Chroma for local vector DB, MemorySaver for persistence, LangSmith for observability). Record a 2-minute Loom walking through one full query — show the Streamlit UI, then flip to LangSmith to show the trace of what happened inside. That combination of working demo plus observability dashboard is what separates this from a toy project.

The key shift in this plan vs what you had before: Days 6-7 now cover the features (human-in-the-loop, memory) that are most specific to production agentic AI — the things that distinguish someone who understands the full picture from someone who just chained a few LLM calls. LangSmith on Day 2 means every subsequent day's work is automatically traced, so by Day 10 you have a rich portfolio of run traces without any extra effort.