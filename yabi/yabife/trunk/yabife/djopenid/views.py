from djopenid import util

def index(request):
    #consumer_url = util.getViewURL(request, 'djopenid.consumer.views.startOpenID')
    #server_url = util.getViewURL(request, 'djopenid.server.views.server')

    consumer_url = ''
    server_url = ''

    return render_to_response('index.html', {'consumer_url':consumer_url, 'server_url':server_url, 'h':webhelpers, 'request':request})
