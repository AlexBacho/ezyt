import re

from PIL import Image, ImageDraw, ImageFont
from ast import literal_eval
from textwrap import wrap

from .image_utils import ImageText

DEFAULT_IMAGE_SIZE = (1280, 720)
DEFAULT_FONT_SIZE = 100
DEFAULT_IMAGE_COLOR = (255, 255, 255)
DEFAULT_TEXT_COLOR = (0, 0, 0)
DEFAULT_HIGHLIGHT_COLOR = (255, 0, 0)
DEFAULT_OUTPUT_PATH = "unnamed.png"
DEFAULT_PADDING = (16, 8)
DEFAULT_MARGIN = (8, 8)


class ImageEditor:
    def __init__(self, cfg):
        self.cfg = cfg
        self.font_file = cfg.image.get("thumbnail_font_file")
        if not self.font_file:
            raise ValueError("No font set in config. Add a path to desired .ots file.")
        self.font_size = int(cfg.image.get("font_size", DEFAULT_FONT_SIZE))
        self.text_color = literal_eval(
            cfg.image.get("text_color", str(DEFAULT_TEXT_COLOR))
        )
        self.highlight_color = literal_eval(
            cfg.image.get("highlight_color", str(DEFAULT_HIGHLIGHT_COLOR))
        )
        self.margin = literal_eval(cfg.image.get("margin", str(DEFAULT_MARGIN)))
        self.padding = literal_eval(cfg.image.get("padding", str(DEFAULT_PADDING)))

    def add_text_to_image(
        self,
        text,
        output_path=None,
        image_path=None,
        text_color=None,
        font=None,
        font_size=None,
        margin=None,
    ):
        image_base = image_path or DEFAULT_IMAGE_SIZE
        image = ImageText(image_base)
        image.write_text_box(
            margin or self.margin,
            text,
            box_width=image.size / 2,
            font_filename=font or self.font_file,
            font_size=font_size or self.font_size,
            color=text_color or self.text_color,
        )
        image.save(output_path)

    def add_highlighted_text_to_image(
        self,
        text,
        output_path=None,
        image_path=None,
        text_color=None,
        highlight_color=None,
        font=None,
        font_size=None,
        margin=None,
        padding=None,
    ):
        image_base = image_path or DEFAULT_IMAGE_SIZE
        margin = margin or self.margin
        padding = padding or self.padding
        font = font or self.font_file
        font_size = font_size or self.font_size

        image = ImageText(image_base)
        words_to_highlight = self._get_uncommon_words_from_text(text)
        xy = margin
        words = text.split()
        for word in words:
            if _get_base_word(word) in words_to_highlight:
                color = highlight_color or self.highlight_color
            else:
                color = text_color or self.text_color
            offset = image.write_text(xy, word, font, font_size=font_size, color=color)
            xy = (xy[0] + offset[0] + padding[0], xy[1])
            if xy[0] > image.size[0] / 3:
                xy = (margin[0], xy[1] + offset[1] + padding[1])
        image.save(output_path or DEFAULT_OUTPUT_PATH)

    def create_thumbnail(
        self,
        text,
        image_path=None,
        output_path=DEFAULT_OUTPUT_PATH,
        text_side="left",
        size=DEFAULT_IMAGE_SIZE,
        max_font_size=100,
    ):
        font_path = self.font_file
        if image_path:
            image = Image.open(image_path)
        else:
            image = Image.new("RGBA", size, color="white")
        width = image.width
        HEIGHT = image.height
        font_size = max_font_size
        v_margin = self.margin[1]
        CHAR_LIMIT = 12
        TEXT_COLOR = "black"

        draw_interface = ImageDraw.Draw(image)

        text_lines = wrap(text, CHAR_LIMIT)
        y, line_heights, font = self._get_textbox(
            text_lines, (width / 2, HEIGHT), v_margin, font_path, font_size
        )

        for i, line in enumerate(text_lines):
            line_width = font.getmask(line).getbbox()[2]
            for word in line.split():
                x = (width * 0.5 - line_width) // 2
                draw_interface.text((x, y), word, font=font, fill=TEXT_COLOR)

            y += line_heights[i]
        image.save(output_path)

    def _get_textbox(self, text_wrapped, dimensions, margin, font_path, font_size):
        font = ImageFont.truetype(font_path, font_size)
        _, descent = font.getmetrics()

        line_heights = [
            font.getmask(text_line).getbbox()[3] + descent + margin
            for text_line in text_wrapped
        ]
        line_heights[-1] -= margin

        height_text = sum(line_heights)

        y = (dimensions[1] - height_text) // 2

        if sum(line_heights) > dimensions[1]:
            return self._get_textbox(
                text_wrapped, dimensions, margin, font_path, font_size - 5
            )

        return (y, line_heights, font)

    def _get_uncommon_words_from_text(self, text):
        words = [_get_base_word(word) for word in text.split(" ")]
        with open(self.cfg.image.common_words_list_filepath) as f:
            for line in f:
                if (common_word := line.strip()) in words:
                    del words[words.index(common_word)]
        return words


def _get_base_word(word):
    base_word = re.findall(r"\w+", word.lower())
    return base_word[0] if base_word else word
