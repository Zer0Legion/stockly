from fastapi import status

from app.errors.base_error import StocklyError


class ProjectIOError(StocklyError):
    """
    Error for case where an IO error occurs.

    Parameters
    ----------
    StocklyError : stockly error
        base stockly error.
    """

    error_code: int = status.HTTP_400_BAD_REQUEST
    error_message: str

    def __init__(self, error_message: str):
        super().__init__(
            errors={"io error": [error_message]}, error_code=self.error_code
        )
        self.error_message = error_message
