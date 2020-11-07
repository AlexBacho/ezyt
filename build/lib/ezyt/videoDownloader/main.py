from .downloaders import YtDownloader


def get_base_config_from_args(args):
    return


def download_from_youtube(url, args=[], cfg=None):
    return YtDownloader(cfg).process(url)