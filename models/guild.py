from pydantic import BaseModel


class GuildRanking(BaseModel):
    score: int
    discord_user_id: str
