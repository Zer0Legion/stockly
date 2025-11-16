from fastapi import APIRouter, Depends

from app.dependencies import get_stockly_service
from app.errors.base_error import StocklyError
from app.models.request.send_briefing_email_request import SendEmailRequest
from app.models.request.stock_request import StockRequestInfo
from app.models.response.base_response import ErrorResponse, SuccessResponse
from app.services.stockly_service import StocklyService

router = APIRouter()


@router.get("/")
def home():
    """Default landing page for API."""
    return SuccessResponse(data="Stockly API is running.")


@router.post(
    path="/send_email",
    dependencies=[Depends(get_stockly_service)],
    responses={200: {"model": SuccessResponse}, 400: {"model": ErrorResponse}},
)
def send_email(
    param: SendEmailRequest,
    briefing_email_service: StocklyService = Depends(get_stockly_service),
):
    """
    Send an email to the user with the stock analysis.
    """
    try:
        briefing_email_service.send_briefing_email(param)
        return SuccessResponse(data="Email sent successfully.")
    except StocklyError as e:
        return ErrorResponse(error_code=e.error_code, error_message=str(e))


@router.post(
    path="/create_stockly_post",
    dependencies=[Depends(get_stockly_service)],
    responses={200: {"model": SuccessResponse}, 400: {"model": ErrorResponse}},
)
def create_stockly_post(
    stock: StockRequestInfo,
    stockly_service: StocklyService = Depends(get_stockly_service),
):
    """
    Create an end-to-end stock analysis post for a given stock request.
    """
    try:
        return stockly_service.create_end_to_end_post(stock)
    except StocklyError as e:
        return ErrorResponse(error_code=e.error_code, error_message=str(e))


@router.post(
    path="/stock_analysis",
    dependencies=[Depends(get_stockly_service)],
    responses={200: {"model": SuccessResponse}, 400: {"model": ErrorResponse}},
)
def stock_analysis(
    stock: StockRequestInfo,
    stockly_service: StocklyService = Depends(get_stockly_service),
):
    """
    Perform stock analysis for a given stock request.
    """
    try:
        return stockly_service.get_stock_analysis(stock)
    except StocklyError as e:
        return ErrorResponse(error_code=e.error_code, error_message=str(e))


@router.get(
    path="/auto_stockly_post",
    dependencies=[Depends(get_stockly_service)],
    responses={200: {"model": SuccessResponse}, 400: {"model": ErrorResponse}},
)
def auto_stockly_post(
    stockly_service: StocklyService = Depends(get_stockly_service),
):
    """
    Perform automatic stock analysis for predefined stocks.
    """
    return stockly_service.auto_stockly_post()
