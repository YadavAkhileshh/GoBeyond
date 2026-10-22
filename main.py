import argparse
import uuid

from langchain_core.messages import HumanMessage
from langgraph.types import Command

from graph import app
from state import default_state


def run(user_query: str, user_id: str = "user") -> None:
    thread_id = f"{user_id}_{uuid.uuid4().hex[:8]}"
    config    = {"configurable": {"thread_id": thread_id}}

    print(f"\nGoBeyond | Thread: {thread_id}\nQuery: {user_query}\n")

    result = app.invoke(default_state(user_query, user_id), config=config)

    if "__interrupt__" in result:
        draft = result["__interrupt__"][0].value.get("draft_itinerary", result.get("itinerary", ""))
        print("\n--- Draft Itinerary ---")
        print(draft)
        print("-----------------------")

        choice = input("\nApprove? [y/n]: ").strip().lower()
        approved = choice == "y"
        feedback = ""
        if not approved:
            feedback = input("Feedback: ").strip()

        result = app.invoke(
            Command(resume={"approved": approved, "feedback": feedback}),
            config=config,
        )

    print("\n--- Final Plan ---")
    print(result.get("final_response", "(no response)"))


def main() -> None:
    parser = argparse.ArgumentParser(description="GoBeyond CLI")
    parser.add_argument("--query", type=str, default="")
    parser.add_argument("--user-id", type=str, default="user")
    args = parser.parse_args()

    query = args.query.strip() or input("Travel request: ").strip()
    if query:
        run(query, user_id=args.user_id)


if __name__ == "__main__":
    main()
