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
        bolded_text: str = "",
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
        # Build a list of tuples: (line_text, is_bold)
        wrapped_lines: list[tuple[str, bool]] = []

        # 1) Add bolded_text (if provided) as bold lines
        bt = (bolded_text or "").strip()
        if bt:
            for paragraph in bt.splitlines():
                paragraph = paragraph.strip()
                if not paragraph:
                    wrapped_lines.append(("", True))
                    continue
                lines = textwrap.wrap(
                    paragraph,
                    width=line_width,
                    break_long_words=True,
                    replace_whitespace=True,
                    drop_whitespace=True,
                )
                wrapped_lines.extend((ln, True) for ln in lines)

        # 2) Add the rest of the caption as normal (unbold) lines
        for paragraph in (text or "").splitlines():
            paragraph = paragraph.strip()
            if not paragraph:
                wrapped_lines.append(("", False))  # preserve blank line
                continue
            lines = textwrap.wrap(
                paragraph,
                width=line_width,
                break_long_words=True,
                replace_whitespace=True,
                drop_whitespace=True,
            )
            wrapped_lines.extend((ln, False) for ln in lines)

        # Measure total height
        line_heights = []
        line_widths = []
        for line, is_bold in wrapped_lines:
            active_font = bold_font if is_bold else font
            if line == "":  # blank line approximate height of a space
                bbox = draw.textbbox((0, 0), " ", font=active_font)
            else:
                bbox = draw.textbbox((0, 0), line, font=active_font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            line_heights.append(h)
            line_widths.append(w)

        total_text_height = sum(line_heights) + line_spacing * (len(wrapped_lines) - 1)
        img_w, img_h = image.size
        start_y = max(0, img_h - total_text_height - padding)

        # Draw each line centered with a black outline (stroke) for readability
        current_y = start_y

        for i, (line, is_bold) in enumerate(wrapped_lines):
            w = line_widths[i]
            h = line_heights[i]
            x = max(0, (img_w - w) / 2)
            if line:
                active_font = bold_font if is_bold else font
                active_stroke_width = 6 if is_bold else 4
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

    def image_overlay(
        self, background_image_path: str, overlay_image_path: str, output_file_path: str
    ) -> str:
        """Overlay an image on top of a background image at the center.

        Parameters
        ----------
        background_image_path : str
            Path to the background image.
        overlay_image_path : str
            Path to the overlay image.

        Returns
        -------
        str
            Path to the output image with overlay.
        """
        logger.info(
            f"Overlaying image {overlay_image_path} on background {background_image_path}"
        )
        background = Image.open(background_image_path).convert("RGBA")
        overlay = Image.open(overlay_image_path).convert("RGBA")

        # Resize overlay: ensure its shorter side is at least 33% of the background
        # Example: if overlay is landscape (w > h), set its height to 33% of bg height
        bg_w, bg_h = background.size
        ov_w, ov_h = overlay.size

        min_ratio = 0.25
        if ov_w >= ov_h:
            # Landscape or square: drive scale by height
            target_short = int(bg_h * min_ratio)
            scale = target_short / ov_h if ov_h else 1.0
        else:
            # Portrait: drive scale by width
            target_short = int(bg_w * min_ratio)
            scale = target_short / ov_w if ov_w else 1.0

        new_ov_w = max(1, int(round(ov_w * scale)))
        new_ov_h = max(1, int(round(ov_h * scale)))

        # Ensure the resized overlay still fits within the background bounds
        fit_scale = min(bg_w / new_ov_w, bg_h / new_ov_h, 1.0)
        if fit_scale < 1.0:
            new_ov_w = max(1, int(round(new_ov_w * fit_scale)))
            new_ov_h = max(1, int(round(new_ov_h * fit_scale)))

        # Use LANCZOS resampling; Pillow removed the ANTIALIAS alias in newer versions.
        resample_filter = Image.Resampling.LANCZOS

        overlay = overlay.resize((new_ov_w, new_ov_h), resample=resample_filter)

        # Calculate position to center the overlay
        position = (
            (bg_w - new_ov_w) // 2,
            (bg_h - new_ov_h) // 2,
        )

        # Composite images
        combined = Image.new("RGBA", background.size)
        combined.paste(background, (0, 0))
        combined.paste(overlay, position, mask=overlay)

        # Save the result
        combined.convert("RGB").save(output_file_path)

        return output_file_path
