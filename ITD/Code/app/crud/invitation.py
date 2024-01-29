from typing import Optional, Union

from fastapi.encoders import jsonable_encoder

from app import schemas
from app.api import deps
from app.core.config.settings import DatabaseSettings


def create_invitation(
    db: deps.Database,
    invitation: Union[schemas.TournamentInvitationCreate, schemas.TeamInvitationCreate],
) -> Optional[Union[schemas.TournamentInvitation, schemas.TeamInvitation]]:
    invitation_collection = db.get_collection(DatabaseSettings.INVITATION_COLLECTION)
    result = invitation_collection.insert_one(jsonable_encoder(invitation))
    if not (
        found_invitation := invitation_collection.find_one({"_id": result.inserted_id})
    ):
        return None
    if isinstance(invitation, schemas.TournamentInvitationCreate):
        created_invitation = schemas.TournamentInvitation(**found_invitation)
    elif isinstance(invitation, schemas.TeamInvitationCreate):
        created_invitation = schemas.TeamInvitation(**found_invitation)
    else:
        raise TypeError("Invalid invitation type")
    return created_invitation


def accept_invitation(
    db: deps.Database,
    invitation_id: schemas.PyObjectId,
    user: schemas.User,
) -> bool:
    invitation_collection = db.get_collection(DatabaseSettings.INVITATION_COLLECTION)
    result = invitation_collection.update_one(
        {"_id": invitation_id},
        {"$set": {"accepted": True, "recipient_id": user.id}},
    )
    if result.modified_count == 0:
        return False
    return True
