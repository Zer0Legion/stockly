from functools import lru_cache
from app.services.aws_service import AWSService
from app.services.email_service import EmailService
from app.services.instagram_service import InstagramService
from app.services.openai_service import OpenAIService
from app.services.parser_service import ParserService
from app.services.project_io_service import ProjectIoService
from app.services.stockly_service import StocklyService
from app.services.terms_and_conditions_service import TermsAndConditionsService
from app.services.fetch_logo_service import FetchLogoService
from app.services.alt_service.alt_service import AltService
from app.logic.automation_logic import AutomationLogic


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


def get_fetch_logo_service():
    return FetchLogoService()


def get_stockly_service():
    return StocklyService(
        email_service=get_email_service(),
        parser_service=get_parser_service(),
        project_io_service=get_project_io_service(),
        openai_service=get_openai_service(),
        aws_service=get_aws_service(),
        instagram_service=get_instagram_service(),
        fetch_logo_service=get_fetch_logo_service(),
    )


def get_tnc_service():
    return TermsAndConditionsService()


def get_alt_service():
    return AltService(
        project_io_service=get_project_io_service(),
        aws_service=get_aws_service(),
    )


# -----------------
# Singleton factories
# -----------------


@lru_cache(maxsize=1)
def get_automation_logic_singleton() -> AutomationLogic:
    """Singleton AutomationLogic instance."""
    return AutomationLogic()
