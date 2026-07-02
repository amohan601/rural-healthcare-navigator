
from src.backend.tools.npi_lookup import npi_lookup_tool

response = npi_lookup_tool.invoke(
    {'specialty': 'Family Medicine',
     'city': 'Carrollton',
     'state': 'TX',
     'patient_lat': 32.95,
     'patient_lon': -96.89}
)
for provider in response:
    print(provider)