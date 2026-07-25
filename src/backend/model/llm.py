
from langchain_openai import ChatOpenAI
from src.backend.logging.logger import logger
import os

LLM = None

if os.environ.get("OPENAI_API_KEY"):
    logger.info('[llm] OPEN AI based LLM model will be created')
    LLM = ChatOpenAI(model='gpt-4o-mini', temperature = 0)

else:
    logger.info('[llm] model not created, provider key not found')
