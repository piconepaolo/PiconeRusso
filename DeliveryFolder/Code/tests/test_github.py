from fastapi import status

from app.github import schemas as github_schemas
from app.github.GitHub import GitHubClient


def test_create_repository(
    github_client: GitHubClient, repository_create: github_schemas.RepositoryCreate
):
    response = github_client.create_repository(repository_create)
    assert response.status_code == status.HTTP_201_CREATED


def test_invite_collaborator(
    github_client: GitHubClient,
    repository_create: github_schemas.RepositoryCreate,
):
    response = github_client.invite_collaborator(
        repository=repository_create.name, collaborator="piconepaolo"
    )
    assert response.status_code == status.HTTP_201_CREATED


def test_download_repository_zip(
    github_client: GitHubClient,
):
    response = github_client.download_repository_zip(
        owner="piconepaolo", repository="pilly"
    )
    assert response is not None
