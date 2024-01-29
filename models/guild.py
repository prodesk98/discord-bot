from pydantic import BaseModel


class GuildMemberRanking(BaseModel):
    score: int
    discord_user_id: str

class GuildRanking(BaseModel):
    id: int
    name: str
    members: int
    xp: int
