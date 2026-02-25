"""CLI entrypoint for the v0 core loop."""

from .loop import run_single_turn


if __name__ == "__main__":
    user_input = input("You: ")
    result = run_single_turn(user_input)
    print(f"Assistant: {result.assistant_output}")
