import uuid
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel, Field
from src.backend.logging.logger import logger
load_dotenv()

from src.backend.graph.supervisor import run_graph

rural_navigator_app = FastAPI(title="Rural Healthcare Navigator")


class ChatRequest(BaseModel):
    query: str = Field(description="Patient message for this turn")
    thread_id: Optional[str] = Field(
        default=None,
        description="Reuse the same thread_id to continue the interview",
    )


class ChatResponse(BaseModel):
    thread_id: str
    chat_output: dict


@rural_navigator_app.get("/")
def home():
    logger.info('[home]')
    return {"status": "running"}


@rural_navigator_app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    logger.info('[chat]')
    thread_id = request.thread_id or str(uuid.uuid4())

    result = run_graph(most_recent_user_input=request.query, thread_id=thread_id)

    return ChatResponse(
        thread_id=thread_id,
        chat_output=result.get("chat_output", {}),
    )
