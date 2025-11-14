from datetime import date

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

logger = get_logger(__name__)


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
    ):
        self.email_service = email_service
        self.parser_service = parser_service
        self.project_io_service = project_io_service
        self.openai_service = openai_service
        self.aws_service = aws_service
        self.instagram_service = instagram_service

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
        chatgpt_text = chatgpt_response["choices"][0]["message"]["content"]

        return chatgpt_text

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

                    chatgpt_response = self.openai_service.generate_written_prompt(
                        stock.ticker, cleaned_html
                    )
                    chatgpt_text = chatgpt_response["choices"][0]["message"]["content"]

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

            stock_analysis = stock_analysis.replace("Summary:", f"{stock.long_name} ({stock.exchange}:{stock.ticker}) Analysis")
            split_text = self.parser_service.split_text_for_images(stock_analysis)

            caption = f"""{date.today().strftime("%b %d")} Analysis on {stock.long_name} ({stock.exchange}:{stock.ticker})

#stockly #{stock.ticker} #{stock.exchange} #finance #stocks #investing #stockmarket #trading #wallstreet #business #genai #openai #ai #money #financialnews #economy #investment #wealth #daytrading #stockanalysis #financialfreedom #stocktips #marketanalysis"""
            
            logger.info(f"caption: {caption}")

            s3_object_names = []

            for prompt in split_text:
                logger.info(f"Generating image prompt for: {prompt}")

                image_url = self.openai_service.generate_image_prompt(
                    request=GenerateImageRequest(
                        text_prompt=prompt,
                        sentiment=self.parser_service.find_sentiment(stock_analysis),
                    ),
                )
                if image_url:
                    downloaded_file = self.project_io_service.download_image(image_url)
                    downloaded_file_with_text = self.project_io_service.text_overlay(
                        image_filepath=downloaded_file,
                        text=prompt,
                    )
                    s3_object = self.aws_service.upload_file(
                        UploadImageRequest(
                            file_path=downloaded_file_with_text,
                            bucket=self.settings.AWS_BUCKET_NAME,
                        )
                    )
                    s3_object_names.append(s3_object.object_name)

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

        # Cleanup S3 bucket
        for s3_object_name in s3_object_names:
            self.aws_service.delete_file(
                param=DeleteImageRequest(
                    bucket=self.settings.AWS_BUCKET_NAME,
                    object_name=s3_object_name,
                )
            )
        # Cleanup local files
        self.project_io_service.delete_file(filename=downloaded_file)
        self.project_io_service.delete_file(filename=downloaded_file_with_text)

        return res
