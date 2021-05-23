import jinja2
import logging
import subprocess

from .errors import ProcessingError

DEBUG_MODE = True


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