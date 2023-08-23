from pathlib import Path
from pydantic import BaseSettings
from fastapi import FastAPI
from databases import Database
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware

BASE_DIR = Path(__file__).parent.resolve()


class Settings(BaseSettings):
    """Application settings."""

    ENV: str = "dev"
    HOST: str = "localhost"
    PORT: int = 8000
    BASE_URL_: str = f"https://{HOST}:{PORT}"
    # quantity of workers for uvicorn
    WORKERS_COUNT: int = 1
    # Enable uvicorn reloading
    RELOAD: bool = True
    # Token
    JWT_SECRET_KEY: str = 'JWT_SECRET_KEY'
    # Database settings
    DB_FILE_PATH: str = f"sqlite:///{BASE_DIR}/app.db"
    DB_ECHO: bool = False
    origins: str = 'http://localhost:3000'

    @property
    def BASE_URL(self) -> str:
        return self.BASE_URL_ if self.BASE_URL_.endswith("/") else f"{self.BASE_URL_}/"


app = FastAPI()
settings = Settings()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Database
DATABASE_URL = settings.DB_FILE_PATH
database = Database(DATABASE_URL)

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

metadata = ...
