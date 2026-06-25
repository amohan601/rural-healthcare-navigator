from typing import TypedDict,List,Dict

"""
Add total=False and 3 new fields.
Why: total=False means fields are optional — graph won't crash when early nodes haven't populated later fields yet. 
"""

class HealthState(TypedDict,total = False):
    user_query: str  #from the user
    thread_id: str

    symptoms: str
    location: str  #from the user
    insurance: str #from the user

    triage_result:    Dict        # {urgency, reasoning, conditions, recommendation}
    insurance_result: Dict
    clinic_results: List[Dict]

    appointment_plan: Dict        # Day 5
    care_plan:        str         # Day 5
    reflection:       Dict        # Day 6

    # ── ADD these 3 fields ───────────────────────────────────────────
    thread_id:        str         # MemorySaver multi-turn session ID
    approved:         bool        # human approval node (Day 6)
    final_response:   str         # synthesizer output (Day 7)


