import requests
from fastapi.encoders import jsonable_encoder

from app.utils.singleton import SingletonMeta

from .schemas import RepositoryCreate


class GitHubClient(metaclass=SingletonMeta):

    def __init__(self):
        self.client = requests.Session()
        self.client.headers.update(
            {
                "Authorization": "Bearer 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",
                "Accept": "application/vnd.github.v3+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "Python",
            }
        )

    def create_repository(self, repository_create: RepositoryCreate):
        url = "https://api.github.com/user/repos"
        response = self.client.post(url, json=jsonable_encoder(repository_create))
        return response
