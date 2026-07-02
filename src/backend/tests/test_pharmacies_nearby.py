
from dotenv import load_dotenv

load_dotenv()

from src.backend.tools.pharmacy_nearby import pharmacy_nearby_tool

response = pharmacy_nearby_tool.invoke({'lat': 32.95, 'lon': -96.89})
print(response)