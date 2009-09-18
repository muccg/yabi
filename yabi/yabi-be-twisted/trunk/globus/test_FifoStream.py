import FifoStream
from twisted.trial import unittest, reporter, runner
import tempfile
import os
from processing import Process, Queue
from twisted.internet import reactor, protocol
import random

CHARS = r"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()-=_+`~[]{};':,./<>?\|"

class FifoStreamTest(unittest.TestCase):
    """Test the server sets up correctly and tears down correctly."""
    count = 1024
    data = "".join([random.choice(CHARS) for num in range(1024)])        # 1 kb of data
    env = {'HOME': os.environ['HOME']}
    path = "/bin:/sbin:/usr/bin:/usr/sbin"
    
    def create_fifo(self):
        """create a fifo and return its path"""
        fname = tempfile.mktemp()
        os.mkfifo(fname)
        return fname
    
    def destroy_fifo(self,fname):
        """delete a fifo"""
        os.unlink(fname)
        
    def writer_task(self, fname, queue=None):
        """write data"""
        try:
            file = open(fname, 'w')
            file.write( self.data*self.count )
            file.close()
        except Exception, e:
            queue.put(e)
            return
        
        queue.put(None)
        
    def test_fifostream_create(self):
        """Check that the storage is created"""
        fifo = self.create_fifo()
        
        # start writing into the fifo
        q = Queue()
        p = Process(target=self.writer_task, args=(fifo,q))
        p.start()
    
        f=open(fifo)
        fifostream = FifoStream.FifoStream(f)
        self.assert_(fifostream)

        f.close()
        self.destroy_fifo(fifo)

        # because we didn't read the stream, the writer must have got a proken pipe
        exc = q.get()
        self.failIfEqual(exc,None)
        self.assertEqual(type(exc), IOError)
        self.assertEqual(exc.errno, 32)             # errno 32 = Broken Pipe
        
    def test_fifostream_read(self):
        """Check that the fifo is read through"""
        fifo = self.create_fifo()
        
        # start writing into the fifo
        q = Queue()
        p = Process(target=self.writer_task, args=(fifo,q))
        p.start()
    
        f=open(fifo)
        fifostream = FifoStream.FifoStream(f)
        self.assert_(fifostream)

        # first read
        data = fifostream.read()
        self.assertEquals(data,(self.data*self.count)[:len(data)])
        
        # keep reading until its done
        piece = ""
        while piece!=None:
            data += piece
            piece = fifostream.read()
        
        self.assertEquals(len(data),self.count*len(self.data))                  # make sure the length of the data is correct
        self.assertEquals(data,self.data*self.count)                            # make sure the data matches exactly
        
        f.close()
        self.destroy_fifo(fifo)

        # writer should have no error
        exc = q.get()
        self.assertEquals(exc,None)
        
    def test_fifostream_prepush(self):
        """Check that the fifo is read through"""
        fifo = self.create_fifo()
        
        # start writing into the fifo
        q = Queue()
        p = Process(target=self.writer_task, args=(fifo,q))
        p.start()
    
        f=open(fifo)
        fifostream = FifoStream.FifoStream(f)
        self.assert_(fifostream)

        # prepush some data
        prepush = "".join([random.choice(CHARS) for num in range(random.randint(1,2))])
        fifostream.prepush( prepush )

        # read all the data with successive calls
        data = ""
        piece = ""
        while piece!=None:
            data+=piece
            piece = fifostream.read()
        
        self.assertEquals(len(data),(self.count*len(self.data))+len(prepush))       # make sure the length of the data is correct
        self.assertEquals(data,prepush+self.data*self.count)                        # make sure the data matches exactly
        
        f.close()
        self.destroy_fifo(fifo)

        # writer should have no error
        exc = q.get()
        self.assertEquals(exc,None)
        
    def test_fifostream_close(self):
        """Check that the fifo is read through"""
        fifo = self.create_fifo()
        
        # start writing into the fifo
        q = Queue()
        p = Process(target=self.writer_task, args=(fifo,q))
        p.start()
    
        f=open(fifo)
        fifostream = FifoStream.FifoStream(f)
        self.assert_(fifostream)

        # first read
        data = fifostream.read()
        self.assertEquals(data,(self.data*self.count)[:len(data)])
        
        fifostream.close()
        self.destroy_fifo(fifo)

        # because we didn't read the stream, the writer must have got a proken pipe
        exc = q.get()
        self.failIfEqual(exc,None)
        self.assertEqual(type(exc), IOError)
        self.assertEqual(exc.errno, 32)             # errno 32 = Broken Pipe
        
    def test_fifostream_prepush_nothing(self):
        """Check that the fifo is read through"""
        fifo = self.create_fifo()
        
        # start writing into the fifo
        q = Queue()
        p = Process(target=self.writer_task, args=(fifo,q))
        p.start()
    
        f=open(fifo)
        fifostream = FifoStream.FifoStream(f)
        self.assert_(fifostream)

        fifostream.prepush("")

        # first read
        data = fifostream.read()
        self.assertEquals(data,(self.data*self.count)[:len(data)])
        
        # keep reading until its done
        piece = ""
        while piece!=None:
            data += piece
            piece = fifostream.read()
        
        self.assertEquals(len(data),self.count*len(self.data))                  # make sure the length of the data is correct
        self.assertEquals(data,self.data*self.count)                            # make sure the data matches exactly
        
        f.close()
        self.destroy_fifo(fifo)

        # writer should have no error
        exc = q.get()
        self.assertEquals(exc,None)
