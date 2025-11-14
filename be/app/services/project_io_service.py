# Class to handle input/output operations

import json
import os

import requests
import textwrap

from app.errors.project_io_error import ProjectIOError
from app.models.request.stock_request import StockRequestInfo
from app.settings import Settings
from PIL import Image, ImageDraw, ImageFont

from app.logging_config import get_logger

logger = get_logger(__name__)


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

    def _find_font_path(self) -> str | None:
        """Best-effort locate a TrueType font on this system.

        Checks an env override first, then common Linux/Mac/Windows locations,
        and finally known package-installed fonts like DejaVu.
        Returns a path or None if nothing suitable is found.
        """
        candidates = [
            os.environ.get("FONT_PATH"),
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Debian/Ubuntu
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
            "/Library/Fonts/Arial.ttf",  # macOS (if installed)
            "/System/Library/Fonts/Supplemental/Arial.ttf",  # macOS
            "C:/Windows/Fonts/arial.ttf",  # Windows
            "arial.ttf",
        ]
        for path in candidates:
            if path and os.path.exists(path):
                return path
        return None

    def _find_bold_font_path(self) -> str | None:
        """Best-effort locate a TrueType bold font on this system.

        Checks an env override first, then common Linux/Mac/Windows locations,
        and finally known package-installed fonts like DejaVu.
        Returns a path or None if nothing suitable is found.
        """
        candidates = [
            os.environ.get("BOLD_FONT_PATH"),
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",  # Debian/Ubuntu
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf",
            "/Library/Fonts/Arial Bold.ttf",  # macOS (if installed)
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",  # macOS
            "C:/Windows/Fonts/arialbd.ttf",  # Windows
            "arialbd.ttf",
        ]
        for path in candidates:
            if path and os.path.exists(path):
                return path
        return None

    def text_overlay(
        self,
        image_filepath: str,
        text: str,
        size: int = 35,
        padding: int = 40,
        color: tuple[int, int, int] = (255, 255, 255),
        line_width: int = 50,
        line_spacing: int = 6,
    ):
        """Draw wrapped text at the bottom-middle of the image.

        The text is wrapped so each line has <= line_width characters (word based).
        """

        logger.info(f"Adding text overlay to image: {text}")
        image = Image.open(image_filepath)
        draw = ImageDraw.Draw(image)

        # Set fonts
        font = None
        bold_font = None
        font_path = self._find_font_path()
        bold_font_path = self._find_bold_font_path()
        if font_path:
            try:
                font = ImageFont.truetype(font_path, size)
            except OSError:
                font = None
        if bold_font_path:
            try:
                bold_font = ImageFont.truetype(bold_font_path, size)
            except OSError:
                bold_font = None
        if font is None:
            font = ImageFont.load_default()
        if bold_font is None:
            bold_font = font

        # Normalize and wrap text into lines of <= line_width characters.

        # Split existing paragraphs, wrap each separately

        if len([t.strip() for t in text.split(":", 1)]) == 2:
            bolded, caption = [t.strip() for t in text.split(":", 1)]
        else:
            bolded = ""
            caption = text

        wrapped_lines: list[str] = [bolded]

        for paragraph in caption.splitlines():
            paragraph = paragraph.strip()
            if not paragraph:
                wrapped_lines.append("")  # preserve blank line
                continue
            # word wrap to max line_width chars
            lines = textwrap.wrap(
                paragraph,
                width=line_width,
                break_long_words=True,
                replace_whitespace=True,
                drop_whitespace=True,
            )
            wrapped_lines.extend(lines)

        # Measure total height
        line_heights = []
        line_widths = []
        for line in wrapped_lines:
            if line == "":  # blank line approximate height of a space
                bbox = draw.textbbox((0, 0), " ", font=font)
            else:
                bbox = draw.textbbox((0, 0), line, font=font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            line_heights.append(h)
            line_widths.append(w)

        total_text_height = sum(line_heights) + line_spacing * (len(wrapped_lines) - 1)
        img_w, img_h = image.size
        start_y = max(0, img_h - total_text_height - padding)

        # Draw each line centered with a black outline (stroke) for readability
        current_y = start_y

        for i, line in enumerate(wrapped_lines):
            w = line_widths[i]
            h = line_heights[i]
            x = max(0, (img_w - w) / 2)
            if line:
                active_font = font if i > 0 else bold_font
                active_stroke_width = 4 if i > 0 else 6
                # Using Pillow's stroke_width to create an outline
                draw.text(
                    (x, current_y),
                    line,
                    fill=color,
                    font=active_font,
                    stroke_width=active_stroke_width,
                    stroke_fill=(0, 0, 0),
                )
            current_y += h + line_spacing

        # Save the modified image
        output_filepath = image_filepath.replace(".png", "_with_text.png")
        image.save(output_filepath)

        return output_filepath


if __name__ == "__main__":

    text_size = 35
    caption = """Market Performance: Apple (AAPL) has recently been experiencing fluctuations in its stock price, influenced by broader market trends and specific company developments. While the stock has outperformed in certain periods, it has also seen declines due to overall market conditions and investor sentiment.
"""

    service = ProjectIoService()
    service.text_overlay("/workspaces/stockly/be/filename.png", caption)
