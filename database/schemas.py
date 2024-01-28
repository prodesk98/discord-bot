from models import QuizEnumChoices, QuizEnumStatus


from sqlalchemy import (
    Column, Integer, String, DateTime,
    Sequence, func, JSON, ForeignKey, Enum
)
from .session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, Sequence("users_id_seq"), primary_key=True)
    discord_user_id = Column(String(32))
    discord_guild_id = Column(String(32))
    discord_username = Column(String(50))
    discord_nick = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class CoinsHistory(Base):
    __tablename__ = "coins_history"

    id = Column(Integer, Sequence("coins_history_id_seq"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Integer)
    description = Column(String(155))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Quizzes(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, Sequence("quizzes_id_seq"), primary_key=True)
    status = Column(Enum(QuizEnumStatus))
    amount = Column(Integer)
    theme = Column(String(100))
    question = Column(String(100))
    alternatives = Column(JSON)
    truth = Column(Enum(QuizEnumChoices))
    voice_url = Column(String(1000), nullable=True, default=None)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class QuizBet(Base):
    __tablename__ = "quiz_bet"

    id = Column(Integer, Sequence("quiz_bet_id_seq"), primary_key=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Integer)
    choice = Column(Enum(QuizEnumChoices))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Scores(Base):
    __tablename__ = "scores"

    id = Column(Integer, Sequence("scores_id_seq"), primary_key=True)
    amount = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Pet(Base):
    __tablename__ = "pets"

    id = Column(Integer, Sequence("pets_id_seq"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    config_pet_id = Column(Integer)
    name = Column(String(155))
    personality = Column(String(350))
    swear_words = Column(JSON)
    informal_greeting = Column(JSON)
    level = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Guild(Base):
    __tablename__ = "guilds"

    id = Column(Integer, Sequence("guilds_id_seq"), primary_key=True)
    name = Column(String(155))
    emoji = Column(String(32))
