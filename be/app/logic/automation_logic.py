import json
from app.models.request.stock_request import StockRequestInfo

LIST_SIZE = 886


class AutomationLogic:

    pointer: int
    stock_requests: list[StockRequestInfo]

    def __init__(self, pointer: int = 0) -> None:
        self.pointer = pointer
        self.stock_requests = self._get_stock_request_list()

    def get_pointer(self) -> int:
        return self.pointer or 0

    def set_pointer(self, new_pointer: int) -> None:
        self.pointer = new_pointer % LIST_SIZE

    def _increment_pointer(self) -> int:
        pointer = (self.pointer + 1) % LIST_SIZE
        return pointer

    def _get_stock_request_list(self) -> list[StockRequestInfo]:
        with open("app/logic/stock_request_info.json", "r") as f:
            stock_requests_data = json.load(f)
        stock_requests = [StockRequestInfo(**data) for data in stock_requests_data]
        self.stock_requests = stock_requests
        return stock_requests

    def get_next_stock_request(self) -> StockRequestInfo:
        stock_request = self.stock_requests[self.pointer]
        self.pointer = self._increment_pointer()
        return stock_request
