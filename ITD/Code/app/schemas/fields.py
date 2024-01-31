from typing import Annotated

from pydantic import AfterValidator, HttpUrl


def url_is_valid(url: str):
    HttpUrl(url)
    return url


url = Annotated[str, AfterValidator(url_is_valid)]
