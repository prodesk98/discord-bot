from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator
from sqlalchemy import create_engine
from config import env

engine = create_engine(
    env.POSTGRES_DSN,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=20,
    max_overflow=0
)

SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()

def get_session() -> Generator:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
