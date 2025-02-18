from pydantic import BaseModel, Field
from typing import List


class Query(BaseModel):
    query: str = Field(..., min_length=3)


class Context(BaseModel):
    documentid: str
    content: str
    similarity: float


class ResponseData(BaseModel):
    thought_process: List[str]
    answer: str
    enough_context: bool


class SearchResponse(BaseModel):
    message: str
    results: List[Context]
