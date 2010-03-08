# -*- coding: utf-8 -*-

import tempfile, os, weakref

class KeyStore(object):
    def __init__(self, path=None, expiry=60):
        if path:
            self.path = path
        else:
            # make a temporary storage directory
            self.directory = tempfile.mkdtemp(suffix=".ssh",prefix="",dir=None)

        self.keys = {}
        

    def save_identity(self, identity):
        filename = tempfile.mktemp()
        path = os.path.join( self.directory, filename )
        fh = open( path, "w" )
        fh.write( identity )
        fh.close()
        
        return weakref.ref(filename, lambda r: os.unlink(r))
       