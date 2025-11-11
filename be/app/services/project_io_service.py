# Class to handle input/output operations

import json
import os

import requests

from app.errors.project_io_error import ProjectIOError
from app.models.request.stock_request import StockRequestInfo
from app.settings import Settings


class ProjectIoService:
    def __init__(self):
        self.settings = Settings().get_settings()

        self.db = {}
        self.stocks = {}
        self.content = ""

    def load_stocks(self, filename: os.PathLike) -> dict:
        with open(filename, "r") as f:
            self.stocks = json.load(f)
            return self.stocks

    def load_db(self, filename: os.PathLike):
        with open(filename, "r") as f:
            self.db = json.load(f)
            return self.db

    def generate_intro(self, user_email: str):
        org_name: str = self.settings.ORG_NAME

        if user_email in self.db:
            self.content = self.settings.CONTENT_PREFIX.format(
                self.db[user_email], org_name
            )
        else:
            self.content = self.settings.CONTENT_PREFIX.format(user_email, org_name)

    def add_next_stock(self, stock: StockRequestInfo):
        self.content += f"## {stock.long_name} ({stock.ticker})\n\n"

    def print_report(self, data: str):
        self.content += data

    def append_report(self, data: str):
        self.content += data

    def write_to_file(self, filename: os.PathLike, data: str):
        self.make_file(filename)
        with open(filename, "w", encoding="utf=8") as f:
            f.write(data)

    def append_to_file(self, filename: os.PathLike, data: str):
        self.make_file(filename)
        with open(filename, "a", encoding="utf=8") as f:
            f.write(data)

    def make_file(self, filename: os.PathLike):
        """
        Make a file with the given filename if it does not exist.

        Parameters
        ----------
        filename : os.PathLike
            filename
        """
        os.makedirs(os.path.dirname(filename), exist_ok=True)

    def download_image(self, image_url: str, filename: str = "filename.png") -> str:
        """
        Downloads an image from the given URL.

        Parameters
        ----------
        image_url : str
            url of the image
        filename : str, optional
            file name, by default "filename"

        Returns
        -------
        str
            filename

        Raises
        ------
        ProjectIOError
            If the image could not be downloaded.
        """
        try:
            img_data = requests.get(image_url).content

            with open(filename, "wb") as handler:
                handler.write(img_data)

            return filename
        except Exception as e:
            raise ProjectIOError(str(e))

    def delete_file(self, filename: str):
        """
        Deletes the file with the given filename.

        Parameters
        ----------
        filename : os.PathLike
            filename
        """
        if os.path.exists(filename):
            os.remove(filename)
