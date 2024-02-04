from random import choice, randint

from app import crud, schemas
from app.api import deps
from app.github.GitHub import GitHubClient


def evaluate(submission: schemas.Submission, db: deps.Database):
    client = GitHubClient()
    if not (
        repo_local_path := client.download_repository_zip(
            submission.owner, submission.repo_name
        )
    ):
        raise Exception("Could not download the repository")
    score = _compute_score(repo_local_path)
    crud.update_team_score(db, submission, score)


def _compute_score(repo_local_path: str) -> int:
    if not _build(repo_local_path):
        return 0
    test_score = _test(repo_local_path)
    print(f"Test score: {test_score}")
    static_analysis_score = _static_analysis(repo_local_path)
    print(f"Static analysis score: {static_analysis_score}")
    average_score = (test_score + static_analysis_score) / 2
    print(f"Average score: {average_score}")
    print(f"Average score rounded: {round(average_score, None)}")
    return round(average_score, None)


def _static_analysis(repo_local_path: str) -> float:
    return randint(0, 100)


def _build(repo_local_path: str) -> bool:
    build_choices = [True, False]
    return choice(build_choices)


def _test(repo_local_path: str) -> float:
    return randint(0, 100)
