from fastapi import status

from app.errors.base_error import StocklyError


class ExternalServiceError(StocklyError):
    """
    Error for case where dialing external service failed.

    Parameters
    ----------
    StocklyError : stockly error
        base stockly error.
    """

    error_code: int = status.HTTP_503_SERVICE_UNAVAILABLE
    error_message: str

    def __init__(self, error_message: str):
        super().__init__(
            errors={"external service error": [error_message]},
            error_code=self.error_code,
        )
        self.error_message = error_message
