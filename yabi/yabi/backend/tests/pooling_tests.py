import unittest

from yabi.backend import pooling
from mockito import *


class FakeCredential(object):
    def __init__(self, pk=1):
        self.pk = pk


class PoolingTest(unittest.TestCase):
    HOST = "localhost"
    PORT = "22"
    CREDENTIAL = FakeCredential()

    def setUp(self):
        self.pool = pooling.SSHPoolManager()
        self.connectorMock = mock()
        self.pool.connector = self.connectorMock

    def test_borrow(self):
        when(self.connectorMock).connect(self.HOST, self.PORT, self.CREDENTIAL).thenReturn("my fake connection")

        ssh = self.pool.borrow(self.HOST, self.PORT, self.CREDENTIAL)
        self.assertEqual(ssh, "my fake connection")

    def setup_mock_two_connections(self):
        when(self.connectorMock).connect(self.HOST, self.PORT, self.CREDENTIAL).thenReturn("my fake connection").thenReturn("my second fake connection")

    def test_borrow_two_object_both_connect(self):
        self.setup_mock_two_connections()
        ssh = self.pool.borrow(self.HOST, self.PORT, self.CREDENTIAL)
        ssh2 = self.pool.borrow(self.HOST, self.PORT, self.CREDENTIAL)
        self.assertEqual(ssh, "my fake connection")
        self.assertEqual(ssh2, "my second fake connection")

    def test_borrow_second_object_gets_same_connection(self):
        self.setup_mock_two_connections()
        when(self.connectorMock).is_active("my fake connection").thenReturn(True)

        ssh = self.pool.borrow(self.HOST, self.PORT, self.CREDENTIAL)
        self.pool.give_back(ssh, self.HOST, self.PORT, self.CREDENTIAL)
        ssh2 = self.pool.borrow(self.HOST, self.PORT, self.CREDENTIAL)

        self.assertEqual(ssh, "my fake connection")
        self.assertEqual(ssh2, "my fake connection", "First connection returned so, second borrow should get same object")

    def test_borrow_is_per_hostname_port_and_credential(self):
        when(self.connectorMock).connect(self.HOST, self.PORT, self.CREDENTIAL).thenReturn("my fake connection")
        when(self.connectorMock).connect("other host", self.PORT, self.CREDENTIAL).thenReturn("my other fake connection")

        ssh = self.pool.borrow(self.HOST, self.PORT, self.CREDENTIAL)
        self.pool.give_back(ssh, self.HOST, self.PORT, self.CREDENTIAL)
        ssh2 = self.pool.borrow("other host", self.PORT, self.CREDENTIAL)

        self.assertEqual(ssh, "my fake connection")
        self.assertEqual(ssh2, "my other fake connection", "First connection returned but we want to connect to another host")

    def test_connection_not_reused_if_not_active_anymore(self):
        self.setup_mock_two_connections()
        when(self.connectorMock).is_active("my fake connection").thenReturn(False)

        ssh = self.pool.borrow(self.HOST, self.PORT, self.CREDENTIAL)
        self.pool.give_back(ssh, self.HOST, self.PORT, self.CREDENTIAL)
        ssh2 = self.pool.borrow(self.HOST, self.PORT, self.CREDENTIAL)

        self.assertEqual(ssh, "my fake connection")
        self.assertEqual(ssh2, "my second fake connection", "First connection returned but connection not active anymore, so it shouldn't be returned")

    def test_release_closes_all_connections(self):
        first_connection = "first"
        second_connection = "second"
        third_connection = "third (other host"
        when(self.connectorMock).connect(self.HOST, self.PORT, self.CREDENTIAL).thenReturn(first_connection).thenReturn(second_connection)
        when(self.connectorMock).connect("other host", self.PORT, self.CREDENTIAL).thenReturn(third_connection)

        ssh = self.pool.borrow(self.HOST, self.PORT, self.CREDENTIAL)
        ssh2 = self.pool.borrow(self.HOST, self.PORT, self.CREDENTIAL)
        ssh3 = self.pool.borrow("other host", self.PORT, self.CREDENTIAL)

        self.pool.give_back(ssh, self.HOST, self.PORT, self.CREDENTIAL)
        self.pool.give_back(ssh2, self.HOST, self.PORT, self.CREDENTIAL)
        self.pool.give_back(ssh3, "other host", self.PORT, self.CREDENTIAL)

        self.pool.release()

        verify(self.connectorMock).close(first_connection)
