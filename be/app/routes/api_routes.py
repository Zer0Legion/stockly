from fastapi import APIRouter, Depends

from models.request.send_briefing_email_request import SendEmailRequest
from models.response.base_response import SuccessResponse, ErrorResponse
from errors.base_error import StocklyError
from services.send_briefing_email_service import BriefingEmailService
from dependencies import get_briefing_email_service

router = APIRouter()


@router.get("/")
def home():
    """Default landing page for API."""
    return SuccessResponse(data="Stockly API is running.")


@router.post(
    path="/send_email",
    dependencies=[Depends(get_briefing_email_service)],
    responses={200: {"model": SuccessResponse}, 400: {"model": ErrorResponse}},
)
def send_email(
    param: SendEmailRequest,
    briefing_email_service: BriefingEmailService = Depends(get_briefing_email_service),
):
    """
    Send an email to the user with the stock analysis.
    """
    try:
        briefing_email_service.send_briefing_email(param)
        return SuccessResponse(data="Email sent successfully.")
    except StocklyError as e:
        return ErrorResponse(error_code=e.error_code, error_message=str(e))
