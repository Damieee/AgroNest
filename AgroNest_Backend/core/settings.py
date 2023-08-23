from pathlib import Path
from pydantic import BaseSettings
from fastapi import FastAPI
from fastapi_jwt_auth import AuthJWT
from fastapi_sqlalchemy import SQLAlchemyMiddleware
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

# Configure SQLAlchemy
app.add_middleware(SQLAlchemyMiddleware, database_uri=settings.DB_FILE_PATH)

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

# Configure JWT
auth = AuthJWT(app)
auth.secret_key = settings.JWT_SECRET_KEY
