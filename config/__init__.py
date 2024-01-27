from typing import Optional, List

from pydantic import BaseModel, PostgresDsn, RedisDsn
from os import getenv
from dotenv import load_dotenv
from orjson import loads
from pathlib import Path
load_dotenv()


class Pet(BaseModel):
    id: int
    name: str
    thumbnail: str
    proba: float
    personality: str
    description: str
    swear_words: Optional[List[str]] = None
    informal_greeting: Optional[List[str]] = None
    level: Optional[int] = 0

def pets_config() -> List[Pet]:
    result: List[Pet] = []
    with open(f"{Path(__file__).parent}/pets.json", "r") as r:
        data = loads(r.read())["pets"]
        r.close()
        for pet in data:
            result.append(Pet(**pet))
    return result

class Settings(BaseModel):
    TOKEN: Optional[str] = getenv("TOKEN")
    POSTGRES_PASSWORD: Optional[str] = getenv("POSTGRES_PASSWORD")
    POSTGRES_DSN: Optional[PostgresDsn] = getenv("POSTGRES_DSN")
    REDIS_DSN: Optional[RedisDsn] = getenv("REDIS_DSN")
    HOURLY_EARNINGS: Optional[int] = int(getenv("HOURLY_EARNINGS", 20))
    BOT_MANAGE_ROLE: Optional[str] = getenv("BOT_MANAGE_ROLE", "bot_manager")
    LEARN_BOT_ENDPOINT: Optional[str] = getenv("LEARN_BOT_ENDPOINT")
    LEARN_BOT_AUTHORIZATION: Optional[str] = getenv("LEARN_BOT_AUTHORIZATION")
    LEARN_BOT_ENABLED: Optional[bool] = bool(getenv("LEARN_BOT_ENABLED", "true") == "true")
    ASKING_COST: Optional[int] = int(getenv("ASKING_COST", 20))
    QUIZ_MULTIPLIER: Optional[int] = int(getenv("QUIZ_MULTIPLIER", 3))
    LIMIT_OPEN_QUIZ_BY_TIME: Optional[int] = int(getenv("LIMIT_OPEN_QUIZ_BY_TIME", 8))
    PET_LEVEL_LIMIT: Optional[int] = int(getenv("PET_LEVEL_LIMIT", 15))
    PET_LEVEL_XP_BASE: Optional[int] = int(getenv("PET_LEVEL_XP_BASE", 10))
    PET_LEVEL_XP_INCREASE_PEER_LEVEL: Optional[int] = int(getenv("PET_LEVEL_XP_INCREASE_PEER_LEVEL", 5))


env = Settings()
pets = pets_config()
