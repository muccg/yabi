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

SEP = '/'

class NodeNotFound(Exception): pass

class Directory(object):
    def __init__(self):
        self.store = {}
        self.files = {}
        self.s3folder = None            # if this has an S# folder object, store it here
        
    def __repr__(self):
        return "<S3 Directory F:%s K:%s>"%(self.files.keys(), self.store.keys())
        
    def has_node(self, key):
        return key in self.store
        
    def get_node(self, key):
        if not self.has_node(key):
            raise NodeNotFound("Node %s not found"%(key))
        return self.store[key]
        
    def add_node(self, key):
        assert not self.has_node(key)
        self.store[key] = Directory()
        return self.store[key]
        
    def process(self, key, obj):
        #print "process",key,obj
        if SEP in key:
            first, rest = key.split(SEP,1)
            #print "=",first,"=",rest
            if rest:
                if self.has_node(first):
                    # node already exists
                    self.get_node(first).process(rest,obj)
                else:
                    # new node
                    self.add_node(first).process(rest,obj)
            else:
                #print "directory folder",key
                node = self.add_node(first)
                node.s3folder=obj
        else:
            self.files[key]=obj

    def dump(self, indent=0):
        for key in self.store:
            print '..'*indent + key + " => " + str(self.store[key].files) + " folder: " + str(self.store[key].s3folder)
            self.store[key].dump(indent+1)
            
    def ls(self, path=""):
        #print "ls(",path,")"
        if SEP in path:
            # find the directory and recurse into it
            first, rest = path.split(SEP,1)
            return self.get_node(first).ls(rest)
        else:
            if not path:
                # we want this whole directory
                return [
                        (key, obj.size, obj.last_modified, False) for key,obj in sorted(self.files.iteritems())
                       ],[
                        (key, 0, '', False) for key in sorted(self.store.keys())
                       ]
            else:
                # look for file named path
                if path in self.files:
                    f = self.files[path]
                    return [ (path, f.size, f.last_modified, False) ], []
                
                # here we should have the name of a directory (and the request path was missing a trailing slash)
                assert path in self.store, "path '%s' was not found in store keys: %s"%(path,self.store.keys())
                
                # return the folder listing
                return self.store[path].ls()
                    
    def walk(self):
        """yield every object from here down"""
        # directory recursion
        for key in self.store:
            #print "key",key
            for obj in self.store[key].walk():
                #print "2",obj
                yield obj
        
        # then files
        for key in self.files:
            #print "3",self.files[key]
            yield self.files[key]
        
        #then self
        #print "4",self
        yield self
                
    def find_node(self,path):
        #print "find",path
        if SEP in path:
            # find the directory and recurse into it
            first, rest = path.split(SEP,1)
            return self.get_node(first).find_node(rest)
        else:
            if path:
                return self.get_node(path)
            else:
                return self
            

    
def make_tree(data):
    root = Directory()
    #print "DATA",data
    for key,obj in data:
        #print "processing %s => %s..."%(key,obj)
        root.process(key,obj)
        
    return root
            
        
if __name__=="__main__":
    inp = [
        ('test/test2', None),
        ('test/test2/blah', "blah"),
        ('test/test4', None),
        ('blah/', None),
        ('file', 'file')
        ]
    tree = make_tree(inp)
    
    tree.dump()
    