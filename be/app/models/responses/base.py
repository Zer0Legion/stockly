from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar('T')

class SuccessResponse(BaseModel, Generic[T]):
    data: T


class ErrorResponse(BaseModel):
    error_code: int
    error_message: str
