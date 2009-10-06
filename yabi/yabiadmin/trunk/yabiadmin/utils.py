from django.utils import simplejson as json

def json_error(message):
    if type(message) is str:
        return json.dumps({'error':message})
    
    import traceback
    return json.dumps({'error':traceback.format_exc()})
