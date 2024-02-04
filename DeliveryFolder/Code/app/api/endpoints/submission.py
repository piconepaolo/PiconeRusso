from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from app import EvaluationManager, crud, schemas
from app.api import deps

router = APIRouter()


@router.post("/submit")
def submit(
    submission_create: schemas.SubmissionCreate,
    background_tasks: BackgroundTasks,
    db: deps.Database = Depends(deps.get_db),
):
    if not (submission := crud.create_submission(db, submission_create)):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create submission",
        )
    background_tasks.add_task(
        EvaluationManager.evaluate,
        submission,
        db,
    )
    return {"detail": "Submission created, evaluation in progress"}
