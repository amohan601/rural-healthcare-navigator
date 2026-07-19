from dotenv import load_dotenv

load_dotenv()
from src.backend.agents.resource_finder_agent import resource_finder_node

state = {
    'most_recent_user_input': 'I have chest pain in Carrollton TX, no insurance',
    'insurance':     'none',
    'location': 'Richardson, TX',
    'triage_result': {
        'urgency':    'HIGH',
        'conditions': ['Angina', 'Myocardial Infarction'],
        'recommendation': 'Seek emergency care'
    }
}
resource_finder_output = resource_finder_node(state)
print(resource_finder_output)