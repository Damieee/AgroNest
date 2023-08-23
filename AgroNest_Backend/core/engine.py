from core import settings
from sqlmodel import Field, SQLModel, Session, create_engine

from core.settings import settings
from sqlalchemy.orm import sessionmaker
from typing import Generator, Optional

# connect_args = {"check_same_thread": False}
connect_args = {
    "connect_timeout": 1000,
}

engine = create_engine(
    settings.DB_URL,
    echo=True,
    connect_args=connect_args,
    pool_pre_ping=True,
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# Dispose of the connection pool used if it's an _asyncio.AsyncEngine
# def disconnect():
#     SQLModel.metadata.dispose(engine)


def get_db() -> Generator:
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()