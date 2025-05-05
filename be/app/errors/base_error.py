class StocklyError(Exception):
    """
    The base stockly error.

    Parameters
    ----------
    Exception : exception
        The exception class.
    """

    def __init__(self, errors: dict[str, list[str]], error_code: int):
        self.errors = errors
        self.error_code = error_code

    def __str__(self) -> str:
        return super().__str__() + f" Errors: {self.errors}"
