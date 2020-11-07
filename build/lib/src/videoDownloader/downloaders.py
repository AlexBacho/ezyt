import subprocess
import logging

from time import time

from .errors import ProcessingError


YOUTUBEDL_PATH = "/usr/bin/youtube-dl"
FILENAME_PREFIXES = {
    "ytDownloader": "ytVideo",
}


class BaseDownloader:
    def __init__(self):
        pass

    def process(self, url, options={}):
        raise NotImplementedError

    def _run(self, args):
        process = subprocess.Popen(
            args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            logging.error(
                f"Subprocess failed with code: {process.returncode} msg: {stderr}"
            )
            raise ProcessingError(stderr)
        return stdout

    def _get_default_filename(self):
        return get_default_filename(type(self).__name__)


class YtDownloader(BaseDownloader):
    def __init__(self, args):
        self.args = {
            # default argmunents
            "filename": self._get_default_filename(),
            "filedir": ".",
        }
        self.args.update(self._get_parsed_args(args))

    def process(self, url):
        self._download(url)

    def _download(self, url):
        return self._run(self.args)

    def _get_parsed_args(self, args):
        return args


def get_default_filename(downloader):
    prefix = FILENAME_PREFIXES[downloader]
    ts = str(int(time()))
    return prefix + ts