from enum import Enum
from typing import Optional, List

from pydantic import BaseModel

ALTERNATIVES = {1: "A", 2: "B", 3: "C", 4: "D"}
def get_alternative_by_name(k: str) -> int:
    try:
        return next(_k for _k, _v in ALTERNATIVES.items() if _v == k.upper())
    except StopIteration:
        return -1

class QuizLimitedByTimeResponse(BaseModel):
    allowed: Optional[bool] = False
    current_time: Optional[str] = None


class QuizEnumChoices(Enum):
    A = 1
    B = 2
    C = 3
    D = 4

class QuizEnumStatus(Enum):
    opened = 1
    closed = 2

class Quiz(BaseModel):
    question: str
    truth: Optional[QuizEnumChoices] = QuizEnumChoices.A
    alternatives: Optional[List[str]] = []
    amount: Optional[int] = 0
    voice_url: Optional[str] = None
