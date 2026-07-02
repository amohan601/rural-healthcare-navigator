from typing import TypedDict,List,Dict

"""
Add total=False and 3 new fields.
Why: total=False means fields are optional — graph won't crash when early nodes haven't populated later fields yet. 
"""

class HealthState(TypedDict,total = False):
    # Input
    user_query:             str    # original patient query
    symptoms:               str    # symptom text
    location:               str    # patient location
    insurance:              str    # insurance type
    thread_id:              str    # InMemorySaver session ID
    messages:               list   # conversation history (Day 7)

    # Agent outputs
    triage_result:          Dict   # triage agent
    resource_finder_result: Dict   # resource finder agent
    insurance_result:       Dict   # insurance checker agent (Day 4)
    appointment_plan:       Dict   # appointment prep agent (Day 5)
    care_plan:              str    # appointment prep agent (Day 5)
    reflection:             Dict   # reflection agent (Day 6)
    approved:               bool   # human approver (Day 6)
    final_response:         str    # synthesizer (Day 7)



