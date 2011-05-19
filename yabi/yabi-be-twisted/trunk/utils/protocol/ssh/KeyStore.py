# -*- coding: utf-8 -*-
### BEGIN COPYRIGHT ###
#
# (C) Copyright 2011, Centre for Comparative Genomics, Murdoch University.
# All rights reserved.
#
# This product includes software developed at the Centre for Comparative Genomics 
# (http://ccg.murdoch.edu.au/).
# 
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, YABI IS PROVIDED TO YOU "AS IS," 
# WITHOUT WARRANTY. THERE IS NO WARRANTY FOR YABI, EITHER EXPRESSED OR IMPLIED, 
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND 
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT OF THIRD PARTY RIGHTS. 
# THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF YABI IS WITH YOU.  SHOULD 
# YABI PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR
# OR CORRECTION.
# 
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, OR AS OTHERWISE AGREED TO IN 
# WRITING NO COPYRIGHT HOLDER IN YABI, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR 
# REDISTRIBUTE YABI AS PERMITTED IN WRITING, BE LIABLE TO YOU FOR DAMAGES, INCLUDING 
# ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE 
# USE OR INABILITY TO USE YABI (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR 
# DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES 
# OR A FAILURE OF YABI TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF SUCH HOLDER 
# OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
# 
### END COPYRIGHT ###
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
        print "clear_keystore"
        assert os.path.exists(self.directory), "Can't clear keystore that doesn't exist on disk"
        
        rm_rf(self.directory)
        
    def save_identity(self, identity, tag=None):
        filename = tempfile.mktemp(dir=self.directory)
        fh = open( filename, "w" )
        fh.write( identity )
        fh.close()
        
        os.chmod( filename, 0600 )
        
        if tag:
            self.keys[tag] = filename
            
        self.files.append(filename)
        
        # TODO: fix expiry period for cache
        #def del_key_file(fn):
            #print "DELETING",fn
            #os.unlink(fn)
        
        #reactor.callLater(SSH_KEY_FILE_EXPIRY_TIME,del_key_file,filename) 
        
        return filename
        
    def delete_identity(self, tag):
        print "delte_identity",tag
        fname = self.keys[tag]
        os.unlink(fname)
        del self.keys[tag]
        self.files.remove(fname)
        
        
    
       