import requests
from openai import OpenAI

from logging_config import get_logger
from settings import Settings
from models.request.generate_image_request import GenerateImageRequest, SentimentEnum

logger = get_logger()

class OpenAIService:
    def __init__(self):
        self.cache = {}
        self.settings = Settings().get_settings()

        self.client = OpenAI(
            organization="Personal",
            project="Default project",
            api_key=self.settings.OPENAI_API_KEY,
        )

    def generate_written_prompt(self, stock_ticker: str, formatted_html: str):
        """
        Generate a written prompt for the stock based on the formatted HTML.
        """
        PROMPT = """
        I have scraped several Google News articles related to the stock {}. Please provide the following:

        1. A concise summary of the 3 main key points from these news articles. Prefix this with a '###' header, named "Summary:".
        2. An analysis of the sentiment (ecstatic, positive, neutral, negative, disastrous) of the articles based on how they affect the stock's outlook. Prefix this with a '###' header, named "Sentiment Analysis: <Your evaluation>".
        {}
        """
        if stock_ticker in self.cache:
            return self.cache[stock_ticker]
        else:
            text = PROMPT.format(stock_ticker, formatted_html)
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + self.settings.OPENAI_API_KEY,
            }
            data = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": text}],
                "temperature": 0.7,
            }

            response = requests.post(
                self.settings.OPENAI_URL, headers=headers, json=data
            ).json()
            self.cache[stock_ticker] = response

            logger.info(f"Generated written prompt for {stock_ticker}: {response}")
            return response

    def generate_image_prompt(self, request: GenerateImageRequest):
        """
        Generate an image prompt based on the text prompt.
        """

        TEMPLATE = """
        Generate an image based on the following text prompt. You may show a setting of the company that I am mentioning, and maybe show some traits specific to the company. 
        If you are about to generate an image of a person, I would prefer you to generate an executive in smartly dressed attire, 
        of different genders and races. 
        
        If possible, you are allowed to show the company logo. However, do not generate any text or numbers.

        {}

        I want to reflect the sentiment of the news articles in the image. The sentiment is {}.
        """

        self.settings =  Settings().get_settings()
        prompt = TEMPLATE.format(request.text_prompt, request.sentiment.value)

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.settings.OPENAI_API_KEY,
        }

        data = {"model": "dall-e-3", "prompt": prompt, "size": "1024x1024", "n": 1}

        response = requests.post(
            "https://api.openai.com/v1/images/generations", headers=headers, json=data
        ).json()
        if response.get("error"):
            print("Error generating image:", response["error"])
            return None

        logger.info(f"Generated image prompt response: {response}")
        image_url = response["data"][0]["url"]
        return image_url
