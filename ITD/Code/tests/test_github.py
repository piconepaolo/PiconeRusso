from fastapi import status

from app.github import schemas as github_schemas
from app.github.GitHub import GitHubClient


def test_create_repository(
    github_client: GitHubClient, repository_create: github_schemas.RepositoryCreate
):
    # Act
    response = github_client.create_repository(repository_create)

    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    # Add more assertions if needed
