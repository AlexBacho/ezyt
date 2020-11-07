import json

from collections import namedtuple

from .ttsRogue.redditThief import RedditThief
from .videoDownloader.downloaders import YtDownloader
from .videoUploader.uploaders import YtUploader

from .cfg import Config
from .errors import InvalidParamError


class Ezyt:
    def __init__(self, cfg):
        self.cfg = self._get_config(cfg)
        self.reddit_scraper = RedditThief(self.cfg)
        self.yt_downloader = YtDownloader(self.cfg)
        self.yt_uploader = YtUploader(self.cfg)
        self.channels = self._load_channels()

    def _load_channels(self):
        with open(self.cfg.common.channels_filepath, "r+") as f:
            data = json.load(f)
        return data["channels"]

    def _get_config(self, cfg):
        if isinstance(cfg, Config):
            return cfg
        elif isinstance(cfg, str):
            return Config(cfg)
        else:
            raise InvalidParamError("Invalid config.")
