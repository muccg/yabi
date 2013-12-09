from yabiadmin.yabi.UploadStreamer import UploadStreamer
from django.http import HttpResponse
import json
from yabiadmin.decorators import authentication_required
from yabiadmin.backend import backend

import logging
logger = logging.getLogger(__name__)


#
# Our upload streamer
#
class FileUploadStreamer(UploadStreamer):
    def __init__(self, host, port, selector, cookies, fields):
        UploadStreamer.__init__(self)
        self._host = host
        self._port = port
        self._selector = selector
        self._fields = fields
        self._cookies = cookies

    def receive_data_chunk(self, raw_data, start):
        logger.debug('{0} {1}'.format(len(raw_data), start))
        return self.file_data(raw_data)

    def file_complete(self, file_size):
        """individual file upload complete"""
        logger.info("Streaming through of file %s has been completed. %d bytes have been transferred." % (self._present_file, file_size))
        return self.end_file()

    def new_file(self, field_name, file_name, content_type, content_length, charset):
        """beginning of new file in upload"""
        logger.debug('{0} {1} {2} {3} {4}'.format(field_name, file_name, content_type, content_length, charset))
        return UploadStreamer.new_file(self, file_name)

    def upload_complete(self):
        """all files completely uploaded"""
        logger.debug('')
        return self.end_connection()

    def handle_raw_input(self, input_data, META, content_length, boundary, encoding):
        """raw input"""
        logger.debug('')
        # this is called right at the beginning. So we grab the uri detail here and initialise the outgoing POST
        self.post_multipart(host=self._host, port=self._port, selector=self._selector, cookies=self._cookies)


# TODO duplicated from ws views
@authentication_required
def put(request):
    """
    Uploads a file to the supplied URI
    """
    yabiusername = request.user.username

    logger.debug("uri: %s" % (request.GET['uri']))
    uri = request.GET['uri']

    for key, f in request.FILES.items():
        logger.debug('handling file {0}'.format(key))
        upload_handle = backend.put_file(yabiusername, f.name, uri)
        for chunk in f.chunks():
            upload_handle.write(chunk)
        upload_handle.close()

    response = {
        "level": "success",
        "message": 'no message'
    }
    return HttpResponse(content=json.dumps(response))
