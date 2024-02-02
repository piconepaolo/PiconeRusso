from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field

from .fields import url
from .py_object_id import PyObjectId


class TeamBase(BaseModel):
    name: str
    members: list[PyObjectId] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    repository: Optional[url] = None


class TeamCreate(BaseModel):
    name: str


class Team(TeamBase):
    id: PyObjectId = Field(alias="_id", default_factory=ObjectId)
