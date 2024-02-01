from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from .py_object_id import PyObjectId
from .battle import Battle


class TournamentStatus(str, Enum):
    REGISTERING = "REGISTERING"
    IN_PROGRESS = "IN_PROGRESS"
    CLOSED = "CLOSED"


class TournamentBase(BaseModel):
    name: str
    description: str
    start_date: datetime
    registration_deadline: datetime
    status: TournamentStatus = TournamentStatus.REGISTERING


class TournamentPartecipants(BaseModel):
    educators: list[PyObjectId] = []
    registered_students: list[PyObjectId] = []


class TournamentCreate(TournamentBase):
    ...


class TournamentUpdate(TournamentBase):
    ...


class Tournament(TournamentCreate, TournamentPartecipants):
    id: PyObjectId = Field(alias="_id")
    battles: list[Battle] = []
