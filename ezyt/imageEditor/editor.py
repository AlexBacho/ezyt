import re

from PIL import Image, ImageDraw, ImageFont
from ast import literal_eval

from .image_utils import ImageText

DEFAULT_IMAGE_SIZE = (1280, 720)
DEFAULT_FONT_SIZE = 69
DEFAULT_IMAGE_COLOR = (255, 255, 255)
DEFAULT_TEXT_COLOR = (0, 0, 0)
DEFAULT_HIGHLIGHT_COLOR = (255, 0, 0)
DEFAULT_OUTPUT_PATH = "unnamed.png"
DEFAULT_PADDING = (24, 32)
DEFAULT_MARGIN = (0, 0)


class ImageEditor:
    def __init__(self, cfg):
        self.cfg = cfg
        self.font = cfg.image.get("thumbnail_font_file")
        if not self.font:
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
            font_filename=font or self.font,
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
        font = font or self.font
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
