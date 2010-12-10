import os
import errno

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

