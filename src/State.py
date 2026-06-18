from typing import TypedDict,List,Dict
class State(TypedDict):
    user_query: str

    symptoms: str
    location: str
    insurance: str

    triage_result: Dict
    insurance_result: Dict
    clinic_results: List[Dict]

    appointment_plan: Dict
    care_plan: str

    reflection: Dict

