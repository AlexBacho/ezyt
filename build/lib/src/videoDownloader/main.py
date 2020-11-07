from .downloaders import ytDownloader

def download_from_youtube(url, args):
    return ytDownloader().process(url, args)