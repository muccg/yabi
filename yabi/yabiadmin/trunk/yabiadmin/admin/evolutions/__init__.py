import glob
import os

def _sorted_evolutions():
    """Returns all the sorted .py files (exluding __init__.py) with the extension and full path removed""" 
    dirname = os.path.dirname(__file__)
    evolutions = [ os.path.splitext(os.path.basename(file))[0] for file in glob.glob(dirname + '/*.py') ]
    evolutions.remove('__init__')
    return sorted(evolutions)

SEQUENCE = _sorted_evolutions()

