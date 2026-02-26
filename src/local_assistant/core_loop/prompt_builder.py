"""Build model messages from persona + user input."""

from __future__ import annotations

from local_assistant.persona import PersonaProfile


def build_messages(persona: PersonaProfile, user_input: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": persona.system_prompt()},
        {"role": "user", "content": user_input},
    ]
