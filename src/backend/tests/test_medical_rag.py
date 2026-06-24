import os
from dotenv import load_dotenv
load_dotenv()
api = os.getenv('OPENAI_API_KEY')
print('API Key ', api)


from src.backend.rag.medical_rag import ask_medical_question

response = ask_medical_question("What are symptoms of a heart attack?")
print(response)