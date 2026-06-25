
'''
load openai api key
'''
from dotenv import load_dotenv
load_dotenv()

import argparse
from src.backend.agents.supervisor import run_graph
def main():
    print('Inside main() method')
    parser = argparse.ArgumentParser(description="Rural Healthcare Navigator")
    parser.add_argument("query", type=str, help="Patient symptoms or situation")
    parser.add_argument("--thread", type=str, default=None,
                        help="Thread ID for multi-turn conversation")
    args = parser.parse_args()


    response = run_graph(user_query=args.query,thread_id=args.thread)
    print("*********")
    print(response)

if __name__ == "__main__":
    main()