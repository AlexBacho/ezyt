from ezyt.base.utils import run_subprocess
from ezyt.base.errors import ProcessingError
from ezyt.base.errors import InvalidParamsError

DEFAULT_IMAGE_WIDTH = 1280
DEFAULT_IMAGE_HEIGHT = 720
DEFAULT_HTML_TO_IMAGE_BIN_PATH = "/usr/bin/wkhtmltoimage"


def get_image_from_html(
    input_path,
    output_path,
    width=DEFAULT_IMAGE_WIDTH,
    height=DEFAULT_IMAGE_HEIGHT,
    html_to_img_bin_path=DEFAULT_HTML_TO_IMAGE_BIN_PATH,
    resize_image=False,
):
    if not input_path.endswith(".html"):
        raise InvalidParamsError("Input must be valid html with a '.html' suffix.")

    args = [html_to_img_bin_path]
    if resize_image:
        args.append(
            "--width",
            str(width),
            "--height",
            str(height),
        )
    args.append(
        input_path,
        output_path,
    )
    return run_subprocess(args)
