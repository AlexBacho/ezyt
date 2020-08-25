import httplib2

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow


class BaseUploader():

    def __init__(self):
        pass

    def process(self, video_object):
        raise NotImplementedError

class YtUploader(BaseUploader):

    def __init__(self):
        pass

    def process(self, video_object):
        pass

    def upload(self):
        pass

    def _get_service(self, args):
        flow = flow_from_clientsecrets(
            CLIENT_SECRETS_FILE,
            scope=YOUTUBE_UPLOAD_SCOPE,
            message=MISSING_CLIENT_SECRETS_MESSAGE
        )

        storage = Storage('oauth2.json')
        credentials = storage.get()

        if credentials is None or credentials.invalid:
            credentials = run_flow(flow, storage, args)

        return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
            http=credentials.authorize(httplib2.Http()))
