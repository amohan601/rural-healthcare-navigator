from contextvars import ContextVar

thread_id_var = ContextVar("thread_id", default="unknown")
agent_var = ContextVar("agent", default="system")