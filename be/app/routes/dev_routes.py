from fastapi import APIRouter, Depends

from models.request.generate_image_request import GenerateImageRequest
from models.response.base_response import SuccessResponse, ErrorResponse
from errors.base_error import StocklyError
from dependencies import get_openai_service

router = APIRouter(prefix="/dev")


@router.post(
    path="/create_openai_image",
    dependencies=[Depends(get_openai_service)],
    responses={200: {"model": SuccessResponse}, 400: {"model": ErrorResponse}},
)
def create_openai_image(generate_image_request: GenerateImageRequest):
    """
    (Dev-only) Create an image using OpenAI's image generation capabilities.
    """
    try:
        openai_service = get_openai_service()
        image_url = openai_service.generate_image_prompt(generate_image_request)
        return SuccessResponse(data=image_url)
    except StocklyError as e:
        return ErrorResponse(error_code=e.error_code, error_message=str(e))
