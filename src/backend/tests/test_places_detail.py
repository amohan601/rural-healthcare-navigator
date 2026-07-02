from dotenv import load_dotenv

load_dotenv()

from src.backend.tools.places_detail import places_detail_tool

response = places_detail_tool.invoke({
'provider_name': 'Johnston Health',
    'address': '509 N Bright Leaf Blvd, Smithfield, NC'
})

print(response)