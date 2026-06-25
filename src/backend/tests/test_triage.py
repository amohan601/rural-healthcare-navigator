import os
from dotenv import load_dotenv

load_dotenv()
print(os.getenv('OPENAI_API_KEY'))

from src.backend.agents.triage_agent import triage_symptoms

response = triage_symptoms("I have chest pain and shortness of breath")
print(response)