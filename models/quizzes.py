from typing import Optional

from pydantic import BaseModel

class QuizLimitedByTimeResponse(BaseModel):
    allowed: Optional[bool] = False
    current_time: Optional[str] = None
