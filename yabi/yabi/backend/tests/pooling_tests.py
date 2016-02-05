# Yabi - a sophisticated online research environment for Grid, High Performance and Cloud computing.
# Copyright (C) 2015  Centre for Comparative Genomics, Murdoch University.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
import mock

from yabi.backend import pooling


class FakeCredential(object):
    def __init__(self, pk=1):
        self.pk = pk


class PoolingTest(unittest.TestCase):
    HOST = "localhost"
    PORT = "22"
    CREDENTIAL = FakeCredential()

    def setUp(self):
        self.pool = pooling.SSHPoolManager()
        self.connectorMock = mock.create_autospec(pooling.ConnectionManager)
        self.pool.connector = self.connectorMock

    def test_borrow(self):
        self.connectorMock.connect.return_value = "my fake connection"

        ssh = self.pool.borrow(self.HOST, self.PORT, self.CREDENTIAL)
        self.connectorMock.connect.assert_called_with(self.HOST, self.PORT, self.CREDENTIAL)
        self.assertEqual(ssh, "my fake connection")

    def setup_mock_two_connections(self):
        self.connectorMock.connect.side_effect = ("my fake connection", "my second fake connection")

    def test_borrow_two_object_both_connect(self):
        self.setup_mock_two_connections()
        ssh = self.pool.borrow(self.HOST, self.PORT, self.CREDENTIAL)
        ssh2 = self.pool.borrow(self.HOST, self.PORT, self.CREDENTIAL)

        self.assertEqual(self.connectorMock.connect.call_count, 2)
        self.assertEqual(self.connectorMock.connect.call_args_list, [
            ((self.HOST, self.PORT, self.CREDENTIAL),),
            ((self.HOST, self.PORT, self.CREDENTIAL),)])
        self.assertEqual(ssh, "my fake connection")
        self.assertEqual(ssh2, "my second fake connection")

    def test_borrow_second_object_gets_same_connection(self):
        self.setup_mock_two_connections()
        self.connectorMock.is_active.return_value = True

        ssh = self.pool.borrow(self.HOST, self.PORT, self.CREDENTIAL)
        self.pool.give_back(ssh, self.HOST, self.PORT, self.CREDENTIAL)
        ssh2 = self.pool.borrow(self.HOST, self.PORT, self.CREDENTIAL)

        self.connectorMock.is_active.assert_called_with("my fake connection")
        self.assertEqual(ssh, "my fake connection")
        self.assertEqual(ssh2, "my fake connection", "First connection returned so, second borrow should get same object")
        self.connectorMock.connect.assert_called_once_with(self.HOST, self.PORT, self.CREDENTIAL)

    def test_borrow_is_per_hostname_port_and_credential(self):
        self.connectorMock.connect.side_effect = ("my fake connection", "my other fake connection")

        ssh = self.pool.borrow(self.HOST, self.PORT, self.CREDENTIAL)
        self.pool.give_back(ssh, self.HOST, self.PORT, self.CREDENTIAL)
        ssh2 = self.pool.borrow("other host", self.PORT, self.CREDENTIAL)

        self.assertEqual(self.connectorMock.connect.call_count, 2)
        self.assertEqual(self.connectorMock.connect.call_args_list, [
            ((self.HOST, self.PORT, self.CREDENTIAL),),
            (("other host", self.PORT, self.CREDENTIAL),)])
        self.assertEqual(ssh, "my fake connection")
        self.assertEqual(ssh2, "my other fake connection", "First connection returned but we want to connect to another host")

    def test_connection_not_reused_if_not_active_anymore(self):
        self.setup_mock_two_connections()
        self.connectorMock.connect.side_effect = ("my fake connection", "my second fake connection")
        self.connectorMock.is_active.return_value = False

        ssh = self.pool.borrow(self.HOST, self.PORT, self.CREDENTIAL)
        self.pool.give_back(ssh, self.HOST, self.PORT, self.CREDENTIAL)
        ssh2 = self.pool.borrow(self.HOST, self.PORT, self.CREDENTIAL)

        self.connectorMock.is_active.assert_called_with("my fake connection")
        self.assertEqual(ssh, "my fake connection")
        self.assertEqual(ssh2, "my second fake connection", "First connection returned but connection not active anymore, so it shouldn't be returned")

    def test_release_closes_all_connections(self):
        first_connection = "first"
        second_connection = "second"
        third_connection = "third (other host)"
        self.connectorMock.connect.side_effect = (first_connection, second_connection, third_connection)

        ssh = self.pool.borrow(self.HOST, self.PORT, self.CREDENTIAL)
        ssh2 = self.pool.borrow(self.HOST, self.PORT, self.CREDENTIAL)
        ssh3 = self.pool.borrow("other host", self.PORT, self.CREDENTIAL)

        self.pool.give_back(ssh, self.HOST, self.PORT, self.CREDENTIAL)
        self.pool.give_back(ssh2, self.HOST, self.PORT, self.CREDENTIAL)
        self.pool.give_back(ssh3, "other host", self.PORT, self.CREDENTIAL)

        self.pool.release()

        self.assertEqual(self.connectorMock.close.call_count, 3)
        self.assertTrue(((first_connection,),) in self.connectorMock.close.call_args_list)
        self.assertTrue(((second_connection,),) in self.connectorMock.close.call_args_list)
        self.assertTrue(((third_connection,),) in self.connectorMock.close.call_args_list)
