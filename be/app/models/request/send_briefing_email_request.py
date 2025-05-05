from pydantic import BaseModel

from models.request.stock_request import StockRequestInfo


class SendEmailUserRequest(BaseModel):
    email: str
    name: str
    stocks: list[StockRequestInfo]


class SendEmailRequest(BaseModel):
    user_requests: list[SendEmailUserRequest]
