from datetime import date

from httpx import get
import requests

from app.errors.base_error import StocklyError
from app.logging_config import get_logger
from app.models.request.aws_service_request import (
    DeleteImageRequest,
    UploadImageRequest,
)
from app.models.request.generate_image_request import GenerateImageRequest
from app.models.request.instagram_service_request import InstagramCarouselRequest
from app.models.request.send_briefing_email_request import SendEmailRequest
from app.models.request.stock_request import StockRequestInfo
from app.models.response.base_response import ErrorResponse, SuccessResponse
from app.services.aws_service import AWSService
from app.services.email_service import EmailService
from app.services.instagram_service import InstagramService
from app.services.openai_service import OpenAIService
from app.services.parser_service import ParserService
from app.services.project_io_service import ProjectIoService
from app.settings import Settings
from app.models.response.aws_service_response import S3StorageObject
from app.services.fetch_logo_service import FetchLogoService

logger = get_logger(__name__)

CAPTION_HASHTAGS = [
    "stockly",
    "finance",
    "stocks",
    "investing",
    "stockmarket",
    "trading",
    "wallstreet",
    "business",
    "genai",
    "openai",
    "ai",
    "money",
    "financialnews",
    "economy",
    "investment",
    "wealth",
    "daytrading",
    "stockanalysis",
    "financialfreedom",
    "stocktips",
    "marketanalysis",
    "education",
    "educational",
    "economics",
    "personalfinance",
]


class StocklyService:
    """The service to perform higher-level processing of stock analysis."""

    def __init__(
        self,
        email_service: EmailService,
        parser_service: ParserService,
        project_io_service: ProjectIoService,
        openai_service: OpenAIService,
        aws_service: AWSService,
        instagram_service: InstagramService,
        fetch_logo_service: FetchLogoService,
    ):
        self.email_service = email_service
        self.parser_service = parser_service
        self.project_io_service = project_io_service
        self.openai_service = openai_service
        self.aws_service = aws_service
        self.instagram_service = instagram_service
        self.fetch_logo_service = fetch_logo_service

        self.settings = Settings().get_settings()

    def get_stock_analysis(self, stock: StockRequestInfo) -> str:
        """
        Get analysis of the given stock.

        Parameters
        ----------
        stock : StockRequestInfo
            The stock request information.

        Returns
        -------
        str
            The analysis of the stock.
        """
        html_response = requests.get(self.settings.URL_NEWS + stock.full_name).text

        cleaned_html = self.parser_service.format_html(stock, html_response)

        chatgpt_response = self.openai_service.generate_written_prompt(
            stock.ticker, cleaned_html
        )
        return chatgpt_response

    def send_briefing_email(
        self,
        param: SendEmailRequest,
    ):
        """
        Send an email to the user with the stock analysis.

        Parameters
        ----------
        param : SendEmailRequest
            The request object containing the user requests.

        Returns
        -------
        SuccessResponse[str]
            Email sent successfully.
        """
        try:
            for request in param.user_requests:
                stocks = request.stocks
                self.project_io_service.generate_intro(request.name)

                for stock in stocks:
                    self.project_io_service.add_next_stock(stock)

                    html_response = requests.get(
                        self.settings.URL_NEWS + stock.full_name
                    ).text

                    cleaned_html = self.parser_service.format_html(stock, html_response)

                    chatgpt_text = self.openai_service.generate_written_prompt(
                        stock.ticker, cleaned_html
                    )

                    self.project_io_service.append_report(chatgpt_text + "\n\n")

                todays_date = date.today().strftime("%b %d")

                self.email_service.send_email(
                    to_email=request.email,
                    subject="[{}] Your {} Stock Briefing".format(
                        self.settings.ORG_NAME, todays_date
                    ),
                    body=self.project_io_service.content,
                )

            return SuccessResponse(data="Email sent successfully.")
        except StocklyError as e:
            return ErrorResponse(error_code=e.error_code, error_message=str(e))

    def _add_hashtags_to_caption(self, caption: str, stock: StockRequestInfo) -> str:
        """Add relevant hashtags to the caption.

        Parameters
        ----------
        caption : str
            The caption to add hashtags to.
        stock : StockRequestInfo
            The stock request information.

        Returns
        -------
        str
            The caption with hashtags added.
        """
        hashtags = CAPTION_HASHTAGS + [
            stock.ticker,
            stock.exchange,
        ]

        caption = caption + "\n\n"
        hashtags = " ".join([f"#{tag}" for tag in hashtags])

        return caption + hashtags

    def _create_s3_object_from_image_prompt(
        self,
        image_request: GenerateImageRequest,
        text_overlay: str,
        bolded_text: str = "",
    ) -> S3StorageObject | None:
        logger.info(f"Generating image prompt for: {image_request.text_prompt}")
        logger.info(f"bolded: {bolded_text}")
        logger.info(f"text_overlay: {text_overlay}")

        image_url = self.openai_service.generate_image_prompt(
            request=image_request,
        )
        if image_url:
            downloaded_file = self.project_io_service.download_image(image_url)
            downloaded_file_with_text = self.project_io_service.text_overlay(
                image_filepath=downloaded_file,
                text=text_overlay,
                bolded_text=bolded_text,
            )
            s3_object = self.aws_service.upload_file(
                UploadImageRequest(
                    file_path=downloaded_file_with_text,
                    bucket=self.settings.AWS_BUCKET_NAME,
                )
            )
            if s3_object:
                self.cleanup_temp_files(
                    local_files=[
                        downloaded_file,
                        downloaded_file_with_text,
                    ]
                )
                return s3_object
            else:
                logger.error(
                    f"Failed to upload image to S3 for prompt: {image_request.text_prompt} with sentiment: {image_request.sentiment}"
                )
                return None
        else:
            logger.error(
                f"Failed to generate image for prompt: {image_request.text_prompt} with sentiment: {image_request.sentiment}"
            )
            return None

    def create_end_to_end_post(
        self, stock: StockRequestInfo
    ) -> SuccessResponse[str] | ErrorResponse:
        """
        Create an end-to-end stock analysis post for a given stock request.

        Parameters
        ----------
        stock_request : StockRequestInfo
            The stock request information.

        Returns
        -------
        SuccessResponse[str]
            Post created successfully.
        """
        logger.info("Starting create_end_to_end_post for %s", stock.ticker)
        try:
            stock_analysis = (
                self.get_stock_analysis(stock).replace("#", "").replace("**", "")
            )

            stock_analysis = stock_analysis.replace(
                "Summary:",
                f"{stock.long_name} ({stock.exchange}:{stock.ticker}) Analysis:",
            )
            sentiment = self.parser_service.find_sentiment(stock_analysis)
            split_text = self.parser_service.split_text_for_images(stock_analysis)

            intro_text, body_text = split_text[0], split_text[1:]

            caption = f"""{date.today().strftime("%b %d")} Analysis on {stock.long_name} ({stock.exchange}:{stock.ticker})"""

            caption = self._add_hashtags_to_caption(caption, stock)

            logger.info(f"caption: {caption}")

            s3_object_names = []

            company_logo_url = self.fetch_logo_service.fetch_company_logo(
                stock.full_name
            )
            if company_logo_url:
                company_logo_filepath = self.project_io_service.download_image(
                    company_logo_url
                )
                overlaid_logo_path = self.project_io_service.image_overlay(
                    background_image_path=self.settings.BACKGROUND_IMAGE_PATH,
                    overlay_image_path=company_logo_filepath,
                    output_file_path="overlaid_logo.png",
                )
                overlaid_logo_path_with_text = self.project_io_service.text_overlay(
                    image_filepath=overlaid_logo_path,
                    text="",
                    bolded_text=intro_text,
                )
                logo_s3_object = self.aws_service.upload_file(
                    UploadImageRequest(
                        file_path=overlaid_logo_path_with_text,
                        bucket=self.settings.AWS_BUCKET_NAME,
                    )
                )
                if logo_s3_object:
                    s3_object_names.append(logo_s3_object.object_name)

                    self.cleanup_temp_files(
                        local_files=[
                            company_logo_filepath,
                            overlaid_logo_path,
                            overlaid_logo_path_with_text,
                        ]
                    )

            for prompt in body_text:
                if "sentiment analysis" in prompt.lower() and "\n" in prompt:
                    header, body = prompt.split("\n", 1)
                elif ":" in prompt:
                    header, body = prompt.split(":", 1)
                else:
                    header = ""
                    body = prompt
                s3_object = self._create_s3_object_from_image_prompt(
                    GenerateImageRequest(
                        text_prompt=prompt,
                        sentiment=sentiment,
                    ),
                    text_overlay=body,
                    bolded_text=header,
                )
                if s3_object:
                    s3_object_names.append(s3_object.object_name)

            s3_object_names.append(self.settings.LAST_INSTAGRAM_PICTURE_S3_NAME)

            logger.info(f"S3 Object Names: {s3_object_names}")

            if self.instagram_service.publish_carousel_image(
                req=InstagramCarouselRequest(
                    s3_object_ids=s3_object_names,
                    caption=caption,
                )
            ):
                res = SuccessResponse(data="Post created successfully.")

        except StocklyError as e:
            res = ErrorResponse(error_code=e.error_code, error_message=str(e))

        self.cleanup_temp_files(
            s3_object_names=s3_object_names,
        )

        return res

    def cleanup_temp_files(
        self, s3_object_names: list[str] = [], local_files: list[str] = []
    ):
        """
        Cleanup temporary files created during processing.
        """
        # Cleanup S3 bucket
        for s3_object_name in s3_object_names:
            if s3_object_name != self.settings.LAST_INSTAGRAM_PICTURE_S3_NAME:
                self.aws_service.delete_file(
                    param=DeleteImageRequest(
                        bucket=self.settings.AWS_BUCKET_NAME,
                        object_name=s3_object_name,
                    )
                )
        # Cleanup local files
        for local_file in local_files:
            self.project_io_service.delete_file(filename=local_file)

    def auto_stockly_post(self) -> None:
        """
        Create an automatic stockly post. Meant for CRON job.
        """
        from app.dependencies import get_automation_logic_singleton

        logger.info("Starting auto_stockly_post")
        logic = get_automation_logic_singleton()
        req = logic.get_next_stock_request()
        res = self.create_end_to_end_post(req)
        if res and isinstance(res, SuccessResponse):
            logger.info(f"Auto stockly post created for {req.ticker} successfully.")
        else:
            logger.error(f"Failed to create auto stockly post for {req.ticker}.")
