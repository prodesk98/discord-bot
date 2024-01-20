from typing import Optional

from pydantic import BaseModel
from os import getenv
from dotenv import load_dotenv
load_dotenv()


class Settings(BaseModel):
    TOKEN: Optional[str] = getenv("TOKEN")
    PREFIX: Optional[str] = getenv("PREFIX")
    POSTGRES_PASSWORD: Optional[str] = getenv("POSTGRES_PASSWORD")
    POSTGRES_DSN: Optional[str] = getenv("POSTGRES_DSN")


env = Settings()
