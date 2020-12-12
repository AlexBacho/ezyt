import subprocess
import logging

from .errors import ProcessingError


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