# -*- coding: utf-8 -*-

SSH_KEY_FILE_EXPIRY_TIME = 60               # 60 seconds of validity

import tempfile, os, weakref

from twisted.internet import reactor

def rm_rf(root):
    for path, dirs, files in os.walk(root, False):
        for fn in files:
            os.unlink(os.path.join(path, fn))
        for dn in dirs:
            os.rmdir(os.path.join(path, dn))
    os.rmdir(root)

class KeyStore(object):
    def __init__(self, path=None, dir=None, expiry=60):
        print "KeyStore::__init__(",path,",",dir,",",expiry,")"
        if path:
            assert dir==None, "Cannot set 'dir' AND 'path'. 'path' overides 'dir'."
            self.directory = path
        else:
            # make a temporary storage directory
            self.directory = tempfile.mkdtemp(suffix=".ssh",prefix="",dir=dir)

        self.keys = {}
        self.files = []
        
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
            
        self.files.append(filename)
        
        # lets try scheduling a deletion of this keyfile later
        def del_key_file(fn):
            print "DELETING",fn
            os.unlink(fn)
        
        reactor.callLater(SSH_KEY_FILE_EXPIRY_TIME,del_key_file,path) 
        
        return filename
        
    def delete_identity(self, tag):
        fname = self.keys[tag]
        os.unlink(fname)
        del self.keys[tag]
        self.files.remove(fname)
        
        
    
       