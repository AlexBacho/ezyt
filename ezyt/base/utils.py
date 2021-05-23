import subprocess
import logging
import jinja2

from random import randint
from pathlib import Path

from .errors import ProcessingError

DEBUG = True


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


def get_rendered_template(template_path, args):
    """renders and returns the template in-memory, only use with small files."""
    with open(template_path, "r") as f:
        template = jinja2.Template(f.read())
    return template.render(args)


def get_tmp_filepath_in_dir(directory, suffix=""):
    path_format = "{directory}/tmp_{uid}{suffix}"
    while True:
        uid = str(randint(0, 999999)).zfill(6)
        path = path_format.format(directory=directory, uid=uid, suffix=suffix)
        if not Path(path).exists():
            return path


def debug(msg):
    logging.debug(msg)
    if DEBUG:
        print(msg)