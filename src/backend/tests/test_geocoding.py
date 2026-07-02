from src.backend.tools.geocoding import geocode_tool


response = geocode_tool.invoke({"location": 'virginia beach'})
print(response)


response = geocode_tool.invoke({"location": '75006'})
print(response)

response = geocode_tool.invoke({"location": 'Allegheny county'})
print(response)