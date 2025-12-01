from fastapi import APIRouter, Depends

from app.dependencies import (
    get_alt_service,
    get_automation_logic_singleton,
    get_stockly_service,
)
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
    responses={
        200: {"model": SuccessResponse},
        400: {"model": ErrorResponse},
    },
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


@router.get(
    path="/alt_service",
    dependencies=[Depends(get_alt_service)],
    responses={200: {"model": SuccessResponse}, 400: {"model": ErrorResponse}},
)
def auto_alt_service_post(
    alt_service=Depends(get_alt_service),
):
    """
    Create and publish an Instagram post using the Alt Service.
    """
    try:
        alt_service.create_ig_post()
        return SuccessResponse(data="Alt Service Instagram post created successfully.")
    except StocklyError as e:
        return ErrorResponse(error_code=e.error_code, error_message=str(e))


@router.get(
    path="/get_pointer",
    dependencies=[Depends(get_automation_logic_singleton)],
    responses={200: {"model": SuccessResponse}, 400: {"model": ErrorResponse}},
)
def get_pointer():
    """
    Get the current pointer value from automation logic.
    """
    try:
        automation_logic = get_automation_logic_singleton()
        pointer = automation_logic.pointer
        current_stock = automation_logic.stock_requests[pointer]
        return SuccessResponse(
            data={"pointer": pointer, "current_stock": current_stock}
        )
    except StocklyError as e:
        return ErrorResponse(error_code=e.error_code, error_message=str(e))


@router.post(
    path="/set_pointer",
    responses={200: {"model": SuccessResponse}, 400: {"model": ErrorResponse}},
)
def set_pointer(new_pointer: int):
    """
    Set the pointer value in automation logic.
    """
    try:
        automation_logic = get_automation_logic_singleton()
        automation_logic.set_pointer(new_pointer)
        return SuccessResponse(data={"new_pointer": automation_logic.get_pointer()})
    except StocklyError as e:
        return ErrorResponse(error_code=e.error_code, error_message=str(e))
    except ValueError as ve:
        return ErrorResponse(error_code=400, error_message=str(ve))
