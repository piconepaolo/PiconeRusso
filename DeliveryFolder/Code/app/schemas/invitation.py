from enum import Enum

from pydantic import BaseModel

from .py_object_id import PyObjectId


class InvitationType(str, Enum):
    TEAM_INVITATION = "team_invitation"
    TOURNAMENT_INVITATION = "tournament_invitation"


class InvitationBase(BaseModel):
    type: InvitationType
    creator_id: PyObjectId
    accepted: bool = False
    recipient_id: PyObjectId


class TeamInvitationCreate(InvitationBase):
    team_id: PyObjectId


class TeamInvitation(TeamInvitationCreate):
    id: PyObjectId


class TournamentInvitationCreate(InvitationBase):
    tournament_id: PyObjectId


class TournamentInvitation(TournamentInvitationCreate):
    id: PyObjectId
