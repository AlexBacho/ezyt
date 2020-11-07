import json

from collections import namedtuple

from .ttsRogue.redditThief import RedditThief
from .videoDownloader.downloaders import YtDownloader
from .videoUploader.uploaders import YtUploader


class Ezyt:
    def __init__(self, cfg):
        self.cfg = cfg
        self.reddit_scraper = RedditThief(cfg)
        self.yt_downloader = YtDownloader(cfg)
        self.yt_uploader = YtUploader(cfg)
        self.channels = self._load_channels()

    def _load_channels(self):
        with open(self.cfg.common.channels_filepath, "r+") as f:
            data = json.load(f)
        return data["channels"]
