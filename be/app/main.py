from fastapi import FastAPI
from models.responses.base import SuccessResponse

app = FastAPI()


@app.get("/")
def home():
    """
    Default landing page for API.

    Returns
    -------
    SuccessResponse[str]
        hello world string.
    """
    return SuccessResponse(data="Stockly API is running.")
