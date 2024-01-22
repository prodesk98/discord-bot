from typing import Optional, List, Dict

from pydantic import BaseModel
from os import getenv
from dotenv import load_dotenv
load_dotenv()


class Settings(BaseModel):
    TOKEN: Optional[str] = getenv("TOKEN")
    POSTGRES_PASSWORD: Optional[str] = getenv("POSTGRES_PASSWORD")
    POSTGRES_DSN: Optional[str] = getenv("POSTGRES_DSN")
    HOURLY_EARNINGS: Optional[float] = float(getenv("HOURLY_EARNINGS", 20.0))
    BOT_MANAGE_ROLE: Optional[str] = getenv("BOT_MANAGE_ROLE", "bot_manager")
    LEARN_BOT_ENDPOINT: Optional[str] = getenv("LEARN_BOT_ENDPOINT", None)
    LEARN_BOT_AUTHORIZATION: Optional[str] = getenv("LEARN_BOT_AUTHORIZATION", None)
    LEARN_BOT_ENABLED: Optional[bool] = bool(getenv("LEARN_BOT_ENABLED", "true") == "true")


env = Settings()
