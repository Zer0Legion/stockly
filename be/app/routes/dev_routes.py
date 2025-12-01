from fastapi import APIRouter, Depends

from app.dependencies import (
    get_automation_logic_singleton,
    get_aws_service,
    get_instagram_service,
    get_openai_service,
)
from app.errors.base_error import StocklyError
from app.models.request.aws_service_request import (
    DeleteImageRequest,
    UploadImageRequest,
)
from app.models.request.generate_image_request import GenerateImageRequest
from app.models.request.instagram_service_request import (
    InstagramCarouselRequest,
    InstagramImageRequest,
)
from app.models.response.base_response import ErrorResponse, SuccessResponse

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


@router.post(
    path="/upload_image_to_s3",
    dependencies=[Depends(get_aws_service)],
    responses={200: {"model": SuccessResponse}, 400: {"model": ErrorResponse}},
)
def upload_image_to_s3(upload_image_request: UploadImageRequest):
    """
    (Dev-only) Upload an image to S3.
    """
    try:
        aws_service = get_aws_service()
        s3_object = aws_service.upload_file(upload_image_request)
        return SuccessResponse(data=s3_object)
    except StocklyError as e:
        return ErrorResponse(error_code=e.error_code, error_message=str(e))


@router.post(
    path="/delete_image_from_s3",
    dependencies=[Depends(get_aws_service)],
    responses={200: {"model": SuccessResponse}, 400: {"model": ErrorResponse}},
)
def delete_image_from_s3(delete_image_request: DeleteImageRequest):
    """
    (Dev-only) Delete an image from S3.
    """
    try:
        aws_service = get_aws_service()
        aws_service.delete_file(delete_image_request)
        return SuccessResponse(data="Image deleted successfully.")
    except StocklyError as e:
        return ErrorResponse(error_code=e.error_code, error_message=str(e))


@router.post(
    path="/upload_image_to_instagram",
    dependencies=[Depends(get_instagram_service)],
    responses={200: {"model": SuccessResponse}, 400: {"model": ErrorResponse}},
)
def upload_image_to_instagram(s3_object_name: str, caption: str = ""):
    """
    (Dev-only) Upload an image to Instagram.
    """
    try:
        instagram_service = get_instagram_service()
        instagram_service.publish_image(
            req=InstagramImageRequest(
                s3_object_id=s3_object_name,
                caption=caption,
            )
        )
        return SuccessResponse(data="Image uploaded to Instagram successfully.")
    except StocklyError as e:
        return ErrorResponse(error_code=e.error_code, error_message=str(e))


@router.post(
    path="/upload_carousel_to_instagram",
    dependencies=[Depends(get_instagram_service)],
    responses={200: {"model": SuccessResponse}, 400: {"model": ErrorResponse}},
)
def upload_carousel_to_instagram(s3_object_names: list[str], caption: str = ""):
    """
    (Dev-only) Upload a carousel of images to Instagram.
    """
    try:
        instagram_service = get_instagram_service()
        if instagram_service.publish_carousel_image(
            req=InstagramCarouselRequest(
                s3_object_ids=s3_object_names,
                caption=caption,
            )
        ):
            return SuccessResponse(data="Carousel uploaded to Instagram successfully.")
    except StocklyError as e:
        return ErrorResponse(error_code=e.error_code, error_message=str(e))
