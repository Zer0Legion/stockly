from services.aws_service import AWSService
from services.email_service import EmailService
from services.instagram_service import InstagramService
from services.openai_service import OpenAIService
from services.parser_service import ParserService
from services.project_io_service import ProjectIoService
from services.send_briefing_email_service import BriefingEmailService
from services.terms_and_conditions_service import TermsAndConditionsService


def __init__():
    pass


def get_email_service():
    return EmailService()


def get_parser_service():
    return ParserService()


def get_project_io_service():
    return ProjectIoService()


def get_openai_service():
    return OpenAIService()


def get_instagram_service():
    return InstagramService()


def get_aws_service():
    return AWSService()


def get_briefing_email_service():
    return BriefingEmailService(
        email_service=get_email_service(),
        parser_service=get_parser_service(),
        project_io_service=get_project_io_service(),
        openai_service=get_openai_service(),
    )


def get_tnc_service():
    return TermsAndConditionsService()
