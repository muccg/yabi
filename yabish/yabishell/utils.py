import os
import errno
from itertools import tee, ifilter, ifilterfalse

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError, e: 
        if e.errno != errno.EEXIST:
            raise

def human_readable_size(num):
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

def partition(pred, iterable):
    """Partition an iterable in two iterable based on the predicate"""
    t1, t2 = tee(iterable)
    return ifilter(pred, t1), ifilterfalse(pred, t2)

