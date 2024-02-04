from bson import ObjectId
from pydantic import BaseModel


def embed_document_id(document: BaseModel) -> dict:
    object_dump = document.model_dump(by_alias=True)
    object_dump["_id"] = ObjectId(object_dump["_id"])
    return object_dump
