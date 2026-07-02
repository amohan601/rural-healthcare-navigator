from src.backend.tools.fqhc_lookup import fqhc_lookup_tool

request = {
    'provider_name': 'Johnston Health',
    'state': 'NC',
    'city': 'Smithfield'
}
response = fqhc_lookup_tool.invoke(request)
print(request, response)

request = {
    'provider_name': 'Genesee Community Health Center',
    'state': 'MI',
    'city': 'Flint'
}
response = fqhc_lookup_tool.invoke(request)
print(request, response)
