"""Persona profile loading and rendering."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from importlib import resources
from pathlib import Path


@dataclass
class PersonaProfile:
    name: str
    version: str
    style: str
    principles: list[str]
    constraints: list[str]
    escalation: str

    def system_prompt(self) -> str:
        principles = "\n".join(f"- {item}" for item in self.principles)
        constraints = "\n".join(f"- {item}" for item in self.constraints)
        return (
            f"Persona: {self.name} ({self.version})\n"
            f"Style: {self.style}\n"
            f"Principles:\n{principles}\n"
            f"Constraints:\n{constraints}\n"
            f"Escalation: {self.escalation}"
        )


def _parse_profile(data: dict) -> PersonaProfile:
    return PersonaProfile(
        name=str(data["name"]),
        version=str(data["version"]),
        style=str(data["style"]),
        principles=[str(item) for item in data.get("principles", [])],
        constraints=[str(item) for item in data.get("constraints", [])],
        escalation=str(data["escalation"]),
    )


def _default_profile_path() -> Path:
    return Path(resources.files("local_assistant.persona") / "default.json")


def load_persona(profile_path: str | None = None) -> PersonaProfile:
    path_value = profile_path or os.getenv("PERSONA_PROFILE_PATH")
    path = Path(path_value) if path_value else _default_profile_path()
    data = json.loads(path.read_text(encoding="utf-8"))
    return _parse_profile(data)
