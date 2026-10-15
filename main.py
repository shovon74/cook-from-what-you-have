"""Terminal front end (optional). Run with: uv run main.py"""

import uuid

from agent import ask, build_agent


def main():
    agent = build_agent()
    thread_id = str(uuid.uuid4())
    print("Personal Chef. Tell me what's in your kitchen (type 'quit' to exit).\n")
    while True:
        text = input("You: ").strip()
        if text.lower() in {"quit", "exit", "q"}:
            break
        if text:
            print(f"\nChef: {ask(agent, text, thread_id)}\n")


if __name__ == "__main__":
    main()