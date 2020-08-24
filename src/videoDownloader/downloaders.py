import subprocess
import logging


class ProcessingError(Exception):
    pass


class baseDownloader():

    def __init__(self):
        pass

    def process(self, url, options={}):
        raise NotImplementedError

    def _run(self, args):
        process = subprocess.Popen(
            args,
            stdin=subprocess.Pipe,
            stdout=subprocess.Pipe,
            stderr=subprocess.Pipe
        )
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            logging.error(
                f'Subprocess failed with code: {process.returncode} msg: {stderr}')
            raise ProcessingError
        return stdout


class ytDownloader(baseDownloader):

    def __init__(self):
        pass

    def process(self, url, args={}):
        pass
