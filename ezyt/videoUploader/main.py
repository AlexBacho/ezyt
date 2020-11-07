from .uploaders import YtUploader


def upload_to_youtube(video_object):
    return YtUploader().process(video_object)
