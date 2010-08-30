# -*- coding: utf-8 -*-

import tempfile, os, weakref

def rm_rf(root):
    for path, dirs, files in os.walk(root, False):
        for fn in files:
            os.unlink(os.path.join(path, fn))
        for dn in dirs:
            os.rmdir(os.path.join(path, dn))
    os.rmdir(root)

class KeyStore(object):
    def __init__(self, path=None, dir=None, expiry=60):
        if path:
            assert dir==None, "Cannot set 'dir' AND 'path'. 'path' overides 'dir'."
            self.directory = path
        else:
            # make a temporary storage directory
            self.directory = tempfile.mkdtemp(suffix=".ssh",prefix="",dir=dir)

        self.keys = {}
        
    def __del__(self):
        self.clear_keystore()
        
    def clear_keystore(self):
        assert os.path.exists(self.directory), "Can't clear keystore that doesn't exist on disk"
        
        rm_rf(self.directory)
        
    def save_identity(self, identity, tag=None):
        filename = tempfile.mktemp()
        path = os.path.join( self.directory, filename )
        fh = open( path, "w" )
        fh.write( identity )
        fh.close()
        
        os.chmod( filename, 0600 )
        
        if tag:
            self.keys[tag] = filename
        
        return filename
        
    def delete_identity(self, tag):
        os.unlink(self.keys[tag])
        del self.keys[tag]
        
        
    
       