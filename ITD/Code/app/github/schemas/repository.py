from pydantic import BaseModel


class Repository(BaseModel):
    name: str
    description: str = ""
    private: bool = True


class RepositoryCreate(Repository):
    pass
