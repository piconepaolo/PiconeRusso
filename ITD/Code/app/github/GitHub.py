import os
from base64 import b64encode
from typing import Optional

import requests
from fastapi import UploadFile
from fastapi.encoders import jsonable_encoder

from app.utils.singleton import SingletonMeta

from .schemas import RepositoryCreate


class GitHubClient(metaclass=SingletonMeta):

    owner = "ckb-plat-form"

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

    def invite_collaborator(self, repository: str, collaborator: str):
        url = f"https://api.github.com/repos/{self.owner}/{repository}/collaborators/{collaborator}"
        response = self.client.put(url)
        return response

    async def upload_file(self, repository: str, file: UploadFile):
        url = f"https://api.github.com/repos/{self.owner}/{repository}/contents/{file.filename}"
        commit_message = f"🤖 Upload of {file.filename}"
        content_bs4 = await self._get_file_content_b64(file)
        body = {
            "message": commit_message,
            "content": content_bs4,
        }
        response = self.client.put(url, json=jsonable_encoder(body))
        return response

    async def _get_file_content_b64(self, file: UploadFile):
        return b64encode(await file.read()).decode("ascii")

    def download_repository_zip(self, owner: str, repository: str) -> Optional[str]:
        url = f"https://api.github.com/repos/{owner}/{repository}/zipball"
        response = self.client.get(url)
        print(response, response.status_code)
        if response.status_code != 200:
            return None
        filename = f"./{owner}_{repository}.zip"
        with open(filename, "wb") as f:
            f.write(response.content)
        if not os.path.isfile(filename):
            return None
        return filename
