from enum import Enum
from typing import Union

from pydantic import BaseModel, Field

from .py_object_id import PyObjectId


class NotificationType(str, Enum):
    TOURNAMENT_INVITATION = "tournament_invitation"
    TEAM_INVITATION = "team_invitation"
    BATTLE_STATUS = "battle_status"
    TOURNAMENT_STATUS = "tournament_status"


class NotificationBase(BaseModel):
    title: str
    description: str
    notification_type: NotificationType


class TournamentInvitationNotification(BaseModel):
    invitation_id: PyObjectId
    tournament_id: PyObjectId
    tournament_name: str
    tournament_owner: PyObjectId
    tournament_owner_name: str


class TeamInvitationNotification(BaseModel):
    invitation_id: PyObjectId
    team_id: PyObjectId
    team_name: str
    team_owner: PyObjectId
    team_owner_name: str


class BattleStatusNotification(BaseModel):
    battle_id: PyObjectId
    battle_name: str
    battle_status: str


class TournamentStatusNotification(BaseModel):
    tournament_id: PyObjectId
    tournament_name: str
    tournament_status: str


class NotificationCreate(NotificationBase):
    body: Union[
        TournamentInvitationNotification,
        TeamInvitationNotification,
        BattleStatusNotification,
        TournamentStatusNotification,
    ]


class Notification(NotificationCreate):
    notification_id: PyObjectId = Field(alias="_id")
