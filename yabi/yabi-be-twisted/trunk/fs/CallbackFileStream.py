from twisted.web2 import stream
from zope.interface import Interface, Attribute, implements

class CallbackFileStream(stream.FileStream):
        """This is a subclass of the normal FileStream except that is triggers zero or more callbacks
        when the stream is exhausted. It does the triggereing by wrapping read() and detecting for
        a result of 'None' to be returned.
        """
        implements(stream.ISendfileableStream)
        
        def read(self, sendfile=False):
                # call the parent and get its result
                superresult=stream.FileStream.read(self,sendfile)
                
                # if the result is None, then we are finished reading. We can cleanup
                if superresult==None:
                        self.StreamFinished()
                
                # return the original data
                return superresult
                
        def AddFinishedCallback(self, callback, data):
                """Add a callback and some data to pass to it to the callback chain"""
                if hasattr(self,"_callback"):
                        self._callback.append( (callback, data) )
                else:
                        self._callback=[ (callback, data) ]
        
        def StreamFinished(self):
                """The stream is finished. Call the callback"""
                if hasattr(self,"_callback"):
                        for call,data in self._callback:
                                call(*data)
        
