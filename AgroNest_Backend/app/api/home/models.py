from datetime import datetime
from sqlmodel import SQLModel, Field

class Note(SQLModel, table=True):
    __tablename__ = "notes"

    id: int = Field(primary_key=True, index=True)
    title: str
    description: str
    created_at: datetime = Field(default=datetime.utcnow)
    updated_at: datetime = Field(default=datetime.utcnow, onupdate=datetime.utcnow)
