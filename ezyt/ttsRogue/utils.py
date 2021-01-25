import jinja2
import logging
import subprocess

from .errors import ProcessingError

DEBUG_MODE = True


def get_rendered_template(template_path, args):
    """renders and returns the template in-memory, only use with small files."""
    with open(template_path, "r") as f:
        template = jinja2.Template(f.read())
    return template.render(args)


def run_subprocess(args):
    process = subprocess.Popen(
        args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        logging.error(
            f"Subprocess failed with code: {process.returncode} msg: {stderr}"
        )
        raise ProcessingError(stderr)
    return stdout, stderr


def debug(msg, debug=DEBUG_MODE):
    logging.debug(msg)
    if debug:
        print(msg)