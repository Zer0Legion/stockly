import bs4

from models.request.stock_request import StockRequestInfo

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
