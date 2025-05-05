from datetime import date

import requests

from settings import Settings
from errors.base_error import StocklyError
from services.email_service import EmailService
from services.openai_service import OpenAIService
from services.parser_service import ParserService
from services.project_io_service import ProjectIoService
from models.response.base_response import ErrorResponse, SuccessResponse
from models.request.send_briefing_email_request import SendEmailRequest

class BriefingEmailService:
    """The service to send the stock analysis to the user via email."""

    def __init__(
        self,
        email_service: EmailService,
        parser_service: ParserService,
        project_io_service: ProjectIoService,
        openai_service: OpenAIService,
    ):
        self.email_service = email_service
        self.parser_service = parser_service
        self.project_io_service = project_io_service
        self.openai_service = openai_service
        self.settings = Settings().get_settings()

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
