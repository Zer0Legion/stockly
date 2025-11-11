import bs4

from app.models.request.generate_image_request import SentimentEnum
from app.models.request.stock_request import StockRequestInfo


class ParserService:
    def format_html(self, stock: StockRequestInfo, txt: str):
        UNWANTED_ELEMENTS = [
            "\n",
            "  More",
            "  ",
            "About Google",
            "Get the iOS app",
            "For you",
            "(" + stock.ticker + ")",
            stock.long_name,
            "Get the Android app",
            "FollowingSingaporeWorldLocalBusinessTechnologyEntertainmentSportsScienceHealth",
        ]

        soup = bs4.BeautifulSoup(txt, features="html.parser")

        for script in soup(["script", "style"]):
            script.extract()

        aria_labels = [
            element
            for element in soup.find_all("div")
            if element.find("div") is not None
        ]
        aria_labels_set = set(
            [element.find("div").text.strip() for element in aria_labels]
        )

        aria_labels_string = " ".join(aria_labels_set)

        # remove unwanted elements
        for r in UNWANTED_ELEMENTS:
            aria_labels_string = aria_labels_string.replace(r, "")
        return aria_labels_string

    def split_numbered_points(self, text: str) -> list[str]:
        """Split text into numbered points.

        Parameters
        ----------
        text : str
            The text to split.

        Returns
        -------
        list[str]
            The list of numbered points.
        """
        points = []
        current_point = ""

        for line in text.splitlines():
            line = line.strip()
            if line and line[0].isdigit() and (line[1] == "." or line[1] == ")"):
                if current_point:
                    points.append(current_point.strip())
                current_point = line[2:].strip()
            else:
                current_point += " " + line

        if current_point:
            points.append(current_point.strip())

        return points

    def find_sentiment(self, text: str) -> SentimentEnum:
        """
        Find sentiment from the given text.

        Parameters
        ----------
        text : str
            The text to analyze.

        Returns
        -------
        SentimentEnum
            The sentiment enum.
        """
        text = text.lower()

        if text.find("sentiment") != -1:
            narrowed_text = text[text.find("sentiment") + len("sentiment") :]
            sentiment_of_narrowed_text = self.find_sentiment(narrowed_text)
            if sentiment_of_narrowed_text != SentimentEnum.NEUTRAL:
                return sentiment_of_narrowed_text

        # find first instance of word in text
        first_instances = {
            SentimentEnum.ECSTATIC: text.find("ecstatic"),
            SentimentEnum.DISASTROUS: text.find("disastrous"),
            SentimentEnum.POSITIVE: text.find("positive"),
            SentimentEnum.NEGATIVE: text.find("negative"),
            SentimentEnum.NEUTRAL: text.find("neutral"),
        }
        first_instances = {k: v for k, v in first_instances.items() if v != -1}

        if first_instances:
            first_sentiment = min(first_instances, key=lambda k: first_instances[k])
            return first_sentiment
        else:
            return SentimentEnum.NEUTRAL
