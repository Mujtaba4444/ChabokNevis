from dataclasses import dataclass


@dataclass
class SessionResult:
    session_type: str
    language: str
    wpm: float
    accuracy: float
    correct_characters: int
    incorrect_characters: int
    duration: float
    created_at: str = ""
