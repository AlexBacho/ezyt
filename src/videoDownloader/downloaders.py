import subprocess
import logging

from .errors import ProcessingError


YOUTUBEDL_PATH = '/usr/bin/youtube-dl'


class baseDownloader():

    def __init__(self):
        pass

    def process(self, url, options={}):
        raise NotImplementedError

    def _run(self, args):
        process = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            logging.error(
                f'Subprocess failed with code: {process.returncode} msg: {stderr}')
            raise ProcessingError(stderr)
        return stdout


class ytDownloader(baseDownloader):

    def __init__(self):
        pass

    def process(self, url, args={}):
        args = self._get_parsed_args(args)
        self._download(url, args)

    def _download(self, url, args):
        args = (
            YOUTUBEDL_PATH,
            url,
        )
        return self._run(args)

    def _get_parsed_args(self, args):
        return args
