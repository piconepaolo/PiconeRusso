from typing import Optional

from fastapi.encoders import jsonable_encoder

from app import schemas
from app.api import deps
from app.core.config.settings import DatabaseSettings


def create_submission(
    db: deps.Database, submission: schemas.SubmissionCreate
) -> Optional[schemas.Submission]:
    submissions_collection = db[DatabaseSettings.SUBMISSION_COLLECTION]
    result = submissions_collection.insert_one(jsonable_encoder(submission))
    if not (
        found_submission := submissions_collection.find_one({"_id": result.inserted_id})
    ):
        return None
    created_submission = schemas.Submission(**found_submission)
    return created_submission


def get_submission_by_id(
    db: deps.Database, submission_id: str
) -> Optional[schemas.Submission]:
    submissions_collection = db[DatabaseSettings.SUBMISSION_COLLECTION]
    if not (
        found_submission := submissions_collection.find_one({"_id": submission_id})
    ):
        return None
    submission = schemas.Submission(**found_submission)
    return submission
