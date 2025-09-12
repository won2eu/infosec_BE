from sqlmodel import SQLModel, Field, Column
from datetime import datetime
from typing import Optional
from enum import Enum
from sqlalchemy import String

class Position(str, Enum):
    PROFESSOR = "교수"
    MASTER = "석사"
    UNDERGRADUATE = "학부연구생"

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    login_id: str = Field(unique=True, index=True)
    password: str
    name: str
    user_position: str = Field(sa_column=Column("user_position", String(20)), alias="position")
    created_at: datetime = Field(default_factory=datetime.utcnow)
