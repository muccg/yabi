import threading
import time
import unittest
import socket
from support import YabiTestCase

import paramiko

class TestSSHServer(paramiko.ServerInterface):
    def get_allowed_auths(self, username):
        return 'publickey,password'
    
    def check_auth_password(self, username,password):
        if (username == 'sshuser') and (password == 'sshpass'):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED
        
    def check_auth_publickey(self,username,key):
        return paramiko.AUTH_FAILED
        
    def check_channel_request(self, kind, chanid):
        return paramiko.OPEN_SUCCEEDED
     


class ClientTest(YabiTestCase):
    def setUp(self):
        YabiTestCase.setUp(self)
        
        self.sockl = socket.socket()
        self.sockl.bind(('localhost', 0))
        self.sockl.listen(1)                                    # no backlogs
        self.addr, self.port = self.sockl.getsockname()
        self.event = threading.Event()
        thread = threading.Thread(target=self._run)
        thread.start()
        
    def tearDown(self):
        self.sockl.close()
        YabiTestCase.tearDown(self)
               
    def _run(self):
        # this is our inbuilt server thread for the testing
        self.socks, addr = self.sockl.accept()                  # will only handle a single connection, and only accept it once (cant reconnect)
        self.transport_server = paramiko.Transport(self.socks)
        host_key = paramiko.RSAKey.from_private_key_file('test_keys/test_rsa.key')
        self.transport_server.add_server_key(host_key)
        server = TestSSHServer()
        self.transport_server.start_server(self.event, server)
        
    def test_connection(self):
        self.transport_client = paramiko.SSHClient()
        self.transport_client.get_host_keys().add(
            '[%s]:%d'%(self.addr, self.port),
            'ssh-rsa', 
            paramiko.RSAKey(
                data=str(paramiko.RSAKey.from_private_key_file('test_keys/test_rsa.key'))
            )
        )
        
        #with open('address.txt','w') as fh:
            #fh.write("%s %d\n"%(self.addr,self.port))
        
        #time.sleep(360.0)
        
        self.transport_client.connect(self.addr, self.port, username="sshuser", password="sshpass")
        
        self.event.wait(1.0)
        self.assert_(self.event.isSet())
        self.assert_(self.transport_server.is_active())
        self.assertEquals('sshuser', self.transport_server.get_username())
        self.assertEquals(True, self.transport_server.is_authenticated())
        
        del self.transport_client
        