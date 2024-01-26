from typing import Optional

from pydantic import BaseModel, PostgresDsn, RedisDsn
from os import getenv
from dotenv import load_dotenv
load_dotenv()


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
    LIMIT_OPEN_QUIZ_BY_TIME: Optional[int] = int(getenv("LIMIT_OPEN_QUIZ_BY_TIME"))


env = Settings()
