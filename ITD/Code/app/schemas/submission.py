from datetime import datetime

from pydantic import BaseModel, Field

from .py_object_id import PyObjectId


class SubmissionBase(BaseModel):
    team_id: PyObjectId
    tournament_id: PyObjectId
    battle_id: PyObjectId
    owner: str
    repo_name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SubmissionCreate(SubmissionBase):
    pass


class Submission(SubmissionBase):
    id: PyObjectId = Field(alias="_id")
