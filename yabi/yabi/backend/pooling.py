from yabi.backend.utils import sshclient

from threading import RLock
import logging

logger = logging.getLogger(__name__)


_pool_manager = None


def get_ssh_pool_manager():
    global _pool_manager
    if _pool_manager is None:
        _pool_manager = SSHPoolManager()

    return _pool_manager


class SSHPoolManager(object):
    def __init__(self):
        self.connector = ConnectionManager()
        # For keys see _make_key(), values are lists with usable connections
        # to the given host, port, and credential
        self.connections = {}
        # We are using this lock for all access to the connections dict
        self.connections_lock = RLock()

    def borrow(self, hostname, port, credential):
        with self.connections_lock:
            key = self._make_key(hostname, port, credential)
            connections = self.connections.get(key, [])
            connection = self._get_next_active_connection(connections)
            if connection is not None:
                return connection

        return self.connector.connect(hostname, port, credential)

    def give_back(self, connection, hostname, port, credential):
        with self.connections_lock:
            key = self._make_key(hostname, port, credential)
            connections = self.connections.setdefault(key, [])
            connections.append(connection)

    def release(self):
        """Releases the manager itself, closing all objects"""
        global _pool_manager

        all_connections = sum(self.connections.values(), [])
        for connection in all_connections:
            self.connector.close(connection)

        self.connections = {}
        _pool_manager = None

    def _make_key(self, hostname, port, credential):
        return "%s:%s,%s" % (hostname, port, credential.pk)

    def _get_next_active_connection(self, connections):
        while len(connections) > 0:
            connection = connections.pop()
            if self.connector.is_active(connection):
                return connection
            else:
                self.connector.close(connection)
        return None


class ConnectionManager(object):
    def connect(self, host, port, credential):
        return sshclient(host, port, credential)

    def close(self, connection):
        connection.close()

    def is_active(self, connection):
        transport = connection.get_transport()
        return transport is not None and transport.is_active()
