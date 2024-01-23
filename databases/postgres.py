from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, AsyncAttrs, AsyncSession
from sqlalchemy import (
    Column, Integer, String,
    Boolean, Float, DateTime,
    Sequence, func, JSON
)
from config import env

engine = create_async_engine(
    env.POSTGRES_DSN,
    echo=True
)

async_session = AsyncSession(
    engine,
    expire_on_commit=False,
)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, Sequence("users_id_seq"), primary_key=True)
    discord_user_id = Column(String(32))
    discord_username = Column(String(50))
    discord_nick = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class CoinsHistory(Base):
    __tablename__ = 'coins_history'

    id = Column(Integer, Sequence("coins_history_id_seq"), primary_key=True)
    user_id = Column(Integer)
    amount = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Quizzes(Base):
    __tablename__ = 'quizzes'

    id = Column(Integer, Sequence("quizzes_id_seq"), primary_key=True)
    status = Column(Integer)
    amount = Column(Integer)
    theme = Column(String(100))
    question = Column(String(100))
    alternatives = Column(JSON)
    truth = Column(Integer)
    voice_url = Column(String(1000), nullable=True, default=None)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Scores(Base):
    __tablename__ = 'scores'

    id = Column(Integer, Sequence("scores_id_seq"), primary_key=True)
    amount = Column(Integer)
    user_id = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
