from fastapi import Depends, FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from models.request.generate_image_request import GenerateImageRequest
from errors.base_error import StocklyError
from settings import Settings
from models.response.base_response import SuccessResponse, ErrorResponse
from models.request.send_briefing_email_request import SendEmailRequest
from services.send_briefing_email_service import BriefingEmailService
from dependencies import (
    get_aws_service,
    get_briefing_email_service,
    get_instagram_service,
    get_project_io_service,
    get_openai_service,
    get_tnc_service,
)

app = FastAPI()
settings = Settings().get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "127.0.0.1"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.post(
    path="/send_email",
    dependencies=[
        Depends(get_briefing_email_service),
    ],
    responses={
        200: {"model": SuccessResponse},
        400: {"model": ErrorResponse},
    },
)
def send_email(
    param: SendEmailRequest,
    briefing_email_service: BriefingEmailService = Depends(get_briefing_email_service),
):
    """
    Send an email to the user with the stock analysis.

    Parameters
    ----------
    param : SendEmailRequest
        The request object containing the user requests.
    briefing_email_service : BriefingEmailService
        The briefing email service dependency, auto inject by FastAPI.

    Returns
    -------
    SuccessResponse[str]
        Email sent successfully.
    """
    try:
        briefing_email_service.send_briefing_email(param)

        return SuccessResponse(data="Email sent successfully.")
    except StocklyError as e:
        return ErrorResponse(error_code=e.error_code, error_message=str(e))

@app.post(
    path="/create_openai_image",
    dependencies=[
        Depends(get_openai_service),
    ],
    responses={
        200: {"model": SuccessResponse},
        400: {"model": ErrorResponse},
    },
)
def create_openai_image(
    generate_image_request: GenerateImageRequest,
):
    """
    Create an image using OpenAI's image generation capabilities.

    Parameters
    ----------
    generate_image_request : GenerateImageRequest
        The request object containing the image generation parameters.

    Returns
    -------
    SuccessResponse[str]
        URL of the generated image.
    """
    try:
        # Assuming openai_service is injected and has a method create_image
        openai_service = get_openai_service()
        image_url = openai_service.generate_image_prompt(generate_image_request)

        return SuccessResponse(data=image_url)
    except StocklyError as e:
        return ErrorResponse(error_code=e.error_code, error_message=str(e))
