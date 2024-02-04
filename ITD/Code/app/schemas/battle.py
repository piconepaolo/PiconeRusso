from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field

from .fields import url
from .py_object_id import PyObjectId
from .team import Team


class CodeKata(BaseModel):
    description: str


class BattleBase(BaseModel):
    name: str
    registration_deadline: datetime
    submission_deadline: datetime
    maximum_team_size: int
    minimum_team_size: int = 1
    kata: Optional[CodeKata] = None


class BattleCreate(BattleBase):
    pass


class Battle(BattleBase):
    id: PyObjectId = Field(alias="_id", default_factory=ObjectId)
    github_repository: url
    teams: list[Team] = []
