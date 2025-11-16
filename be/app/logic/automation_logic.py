import json
from app.models.request.stock_request import StockRequestInfo

LIST_SIZE = 886


class AutomationLogic:

    pointer: int
    stock_requests: list[StockRequestInfo]

    def __init__(self) -> None:
        self.pointer = self._get_pointer()
        self.stock_requests = self._get_stock_request_list()

    def _get_pointer(self) -> int:
        with open("app/logic/pointer.txt", "r") as f:
            pointer = int(f.read().strip())
        return pointer

    def _increment_pointer(self) -> int:
        pointer = (self.pointer + 1) % LIST_SIZE
        with open("app/logic/pointer.txt", "w") as f:
            f.write(str(pointer))
        return pointer

    def _get_stock_request_list(self) -> list[StockRequestInfo]:
        with open("app/logic/stock_request_info.json", "r") as f:
            stock_requests_data = json.load(f)
        stock_requests = [StockRequestInfo(**data) for data in stock_requests_data]
        return stock_requests

    def get_next_stock_request(self) -> StockRequestInfo:
        stock_request = self.stock_requests[self.pointer]
        self.pointer = self._increment_pointer()
        return stock_request
