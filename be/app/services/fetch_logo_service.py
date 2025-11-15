"""
Fetch the top image from Google images for the given company logo.


"""

import requests
from bs4 import BeautifulSoup
from app.logging_config import get_logger
from app.errors.base_error import StocklyError


logger = get_logger(__name__)


class FetchLogoService:
    @staticmethod
    def fetch_company_logo(company_name: str) -> str:
        """Fetch the top image URL from Google Images for the given company name.

        Args:
            company_name (str): The name of the company to search for.
        Returns:
            str: The URL of the top image result.

        """
        try:
            search_url = f"https://www.google.com/search?tbm=isch&q={company_name}+logo"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
            }
            response = requests.get(search_url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            img_tags = soup.find_all("img")

            if len(img_tags) > 1:
                if img_tags[1].get("src") is None:
                    raise StocklyError(
                        {
                            "fetch_logo": [
                                f"No valid image source found for company: {company_name}"
                            ]
                        },
                        error_code=500,
                    )
                # The first image is usually the Google logo, so we take the second one
                logo_url = img_tags[1]["src"]
                return logo_url
            else:
                raise StocklyError(
                    {"fetch_logo": [f"No images found for company: {company_name}"]},
                    error_code=500,
                )

        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise StocklyError(
                {
                    "fetch_logo": [
                        "Failed to fetch company logo due to a network error."
                    ]
                },
                error_code=500,
            )
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            raise StocklyError(
                {
                    "fetch_logo": [
                        "An unexpected error occurred while fetching the company logo."
                    ]
                },
                error_code=500,
            )
