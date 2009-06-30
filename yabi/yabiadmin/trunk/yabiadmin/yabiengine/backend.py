import httplib
from urllib import urlencode



def ls(dir):
#dir=gridftp1/cwellington/bi01/ 
    dir = urlencode(dir)
    data = {'dir':dir}
    headers = {"Content-type":"application/x-www-form-urlencoded","Accept":"text/plain"}
    conn = httplib.HTTPConnection(settings.YABIBACKEND_SERVER)
    conn.request('POST', settings.YABIBACKEND_LIST, data, headers)
    r = conn.getresponse()



    # do a try catch on status
