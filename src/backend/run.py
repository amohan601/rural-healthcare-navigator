# src/backend/run.py
# CHANGE: added --location and --insurance as optional CLI arguments
# WHY: resource finder needs location explicitly for geocoding
#      insurance checker needs insurance type explicitly
# If not provided, LLM will attempt to extract from user_query (fallback)

from dotenv import load_dotenv
load_dotenv()

import argparse
import uuid
from src.backend.graph.supervisor import run_graph

def main():
    print('Inside main() method')

    parser = argparse.ArgumentParser(description="Rural Healthcare Navigator")
    parser.add_argument("query",       type=str, help="Patient symptoms or situation")
    parser.add_argument("--location",  type=str, default=None,
                        help="Patient location e.g. 'Carrollton TX' or '75006'")
    parser.add_argument("--insurance", type=str, default=None,
                        help="Insurance type e.g. 'Medicaid', 'BlueCross', 'none'")
    parser.add_argument("--thread",    type=str, default=None,
                        help="Thread ID for multi-turn conversation")
    args = parser.parse_args()

    thread_id = args.thread or str(uuid.uuid4())

    print(f"\n{'='*60}")
    print(f"Query:     {args.query}")
    print(f"Location:  {args.location or 'extract from query'}")
    print(f"Insurance: {args.insurance or 'extract from query'}")
    print(f"Thread:    {thread_id}")
    print(f"{'='*60}\n")

    response = run_graph(
        user_query=args.query,
        location=args.location,
        insurance=args.insurance,
        thread_id=thread_id
    )

    print(f"\n{'─'*60}")
    print("RESULT")
    print(f"{'─'*60}")

    triage = response.get("triage_result", {})
    print(f"Urgency:        {triage.get('urgency', 'N/A')}")
    print(f"Conditions:     {', '.join(triage.get('conditions', []))}")
    print(f"Recommendation: {triage.get('recommendation', 'N/A')}")
    print(f"\nThread ID: {thread_id}")
    print("(Use --thread to continue this conversation)\n")
    rf = response.get("resource_finder_result", {})
    providers = rf.get("providers", [])
    summary = rf.get("summary", "")

    if summary:
        print(f"\nSUMMARY:\n{summary}")

    if providers:
        print(f"\nPROVIDERS ({len(providers)} found):")
        print("─" * 60)
        for i, p in enumerate(providers, 1):
            print(f"\n{i}. {p.name}")
            print(f"   Specialty      : {p.specialty}")
            print(f"   Address        : {p.address}")
            print(f"   Phone          : {p.phone}")
            print(f"   Distance       : {p.distance_miles} miles")
            print(f"   Rating         : {p.rating} ⭐ ({p.review_count} reviews)")
            print(f"   Open Now       : {'Yes' if p.open_now else 'No' if p.open_now is False else 'Unknown'}")
            print(f"   Weekday Hours  : {', '.join(p.weekday_hours) if p.weekday_hours else 'N/A'}")
            print(f"   FQHC           : {'Yes — sliding scale fees' if p.is_fqhc else 'No'}")
            print(f"   Sliding Scale  : {'Yes' if p.sliding_scale else 'No'}")
            print(f"   Telehealth     : {'Yes' if p.telehealth else 'No'}")
            if p.pharmacy_nearby:
                print(f"   Pharmacy       : {p.pharmacy_nearby.name}")
                print(f"   Pharmacy Addr  : {p.pharmacy_nearby.address}")
                print(f"   Pharmacy Dist  : {p.pharmacy_nearby.distance_miles} miles")
                print(
                    f"   Pharmacy Open  : {'Yes' if p.pharmacy_nearby.open_now else 'No' if p.pharmacy_nearby.open_now is False else 'Unknown'}")
            else:
                print(f"   Pharmacy       : Not found")
    else:
        print("\nNo providers found.")


if __name__ == "__main__":
    main()