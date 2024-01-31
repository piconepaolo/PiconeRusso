from datetime import datetime

from pydantic import BaseModel, Field

from .py_object_id import PyObjectId


class SubmissionBase(BaseModel):
    team_id: PyObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SubmissionCreate(SubmissionBase):
    ...


class Submission(SubmissionBase):
    id: PyObjectId = Field(alias="_id")
