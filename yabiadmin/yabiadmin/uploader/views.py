# Create your views here.

from UploadStreamer import UploadStreamer
from yabiengine.backendhelper import make_hmac


DEBUG_UPLOAD_STREAMER = True

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
        if DEBUG_UPLOAD_STREAMER:
            print "receive_data_chunk", len(raw_data), start
        return self.file_data(raw_data)
    
    def file_complete(self, file_size):
        """individual file upload complete"""
        if DEBUG_UPLOAD_STREAMER:
            print "file_complete",file_size
        logger.info("Streaming through of file %s has been completed. %d bytes have been transferred." % (self._present_file, file_size))
        return self.end_file()
    
    def new_file(self, field_name, file_name, content_type, content_length, charset):
        """beginning of new file in upload"""
        if DEBUG_UPLOAD_STREAMER:
            print "new_file",field_name, file_name, content_type, content_length, charset
        return UploadStreamer.new_file(self,file_name)
    
    def upload_complete(self):
        """all files completely uploaded"""
        if DEBUG_UPLOAD_STREAMER:
            print "upload_complete"
        return self.end_connection()
    
    def handle_raw_input(self, input_data, META, content_length, boundary, encoding, chunked):
        """raw input"""
        # this is called right at the beginning. So we grab the uri detail here and initialise the outgoing POST
        self.post_multipart(host=self._host, port=self._port, selector=self._selector, cookies=self._cookies )

#@authentication_required
def fileupload(request, url):
    return upload_file(request, request.user)

def fileupload_session(request, url, session):
    def response(message, level=ERROR, status=500):
        return HttpResponse(status=status, content=json.dumps({
            "level": level,
            "message": message,
        }))

    # Get the user out of the session. Annoyingly, we'll have to do our own
    # session handling here.
    try:
        session = Session.objects.get(pk=session)
        
        # Check expiry date.
        if session.expire_date < datetime.datetime.now():
            return response("Session expired")

        # Get the user, if set.
        request.user = user = DjangoUser.objects.get(pk=session.get_decoded()["_auth_user_id"])

        # Update the session object in the request.
        engine = import_module(settings.SESSION_ENGINE)
        request.session = engine.SessionStore(session.pk)
    except DjangoUser.DoesNotExist:
        return response("User not found", status=403)
    except KeyError:
        return response("User not logged in", status=403)
    except Session.DoesNotExist:
        return response("Unable to read session")

    return upload_file(request, user)
    
@profile_required
def upload_file(request, user):
    logger.debug('')

    host = urlparse(settings.YABIADMIN_SERVER).hostname
    port = urlparse(settings.YABIADMIN_SERVER).port
    upload_path = urlparse(settings.YABIADMIN_SERVER).path

    while len(upload_path) and upload_path[-1]=='/':
        upload_path = upload_path[:-1]
        
    # we parse the GET portion of the request to find the passed in URI before we access the request object more deeply and trigger the processing
    upload_uri = request.GET['uri']
    
    # examine cookie jar for our admin session cookie
    http = memcache_http(request)
    jar = http.cookie_jar
    cookie_string = jar.cookies_to_send_header(settings.YABIADMIN_SERVER)['Cookie']
    
    streamer = FileUploadStreamer(host=host, port=port or 80, selector=upload_path+"/ws/fs/put?uri=%s"%quote(upload_uri), cookies=[cookie_string], fields=[])
    request.upload_handlers = [ streamer ]
    
    # evaluating POST triggers the processing of the request body
    request.POST
    
    result=streamer.stream.getresponse()
    
    content=result.read()
    status=int(result.status)
    reason = result.reason
    
    #print "passing back",status,reason,"in json snippet"
    
    response = {
        "level":"success" if status==200 else "failure",
        "message":content
        }
    return HttpResponse(content=json.dumps(response))



##    from http_upload import post_multipart
    