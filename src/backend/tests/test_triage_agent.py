import os
from dotenv import load_dotenv

load_dotenv()
print(os.getenv('OPENAI_API_KEY'))

from src.backend.agents.triage_agent import triage_node

state = {'most_recent_user_input': 'chest pain for 2 hours', 'symptoms': 'chest pain for 2 hours'}
response = triage_node(state)
print(response)