from datetime import datetime

from py_object_id import PyObjectId
from pydantic import BaseModel, Field


class SubmissionBase(BaseModel):
    team_id: PyObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SubmissionCreate(SubmissionBase):
    ...


class Submission(SubmissionBase):
    id: PyObjectId
