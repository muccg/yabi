from django.utils import unittest as unittest
import boto.s3.key
import boto.s3.prefix
import logging
from mockito import *

from yabiadmin.backend.s3backend import S3Backend
from yabiadmin.yabi import models as m

logger = logging.getLogger(__name__)

class S3BotoMockedOutTest(unittest.TestCase):

    def setUp(self):
        self.backend = S3Backend()
        self.backend.set_cred = lambda uri: True
        self.bucket = mock()
        self.backend.bucket = lambda name: self.bucket
        self.S3_URI = 's3://ignored@some-bucket-name@amazonaws-test-host.com%s'

    def test_ls_for_empty_dir(self):
        PATH = '/some/path/'
        S3_PATH = drop_starting_slash(PATH)
        when(self.bucket).get_all_keys(prefix=S3_PATH, delimiter='/').thenReturn([])

        ls_result = self.backend.ls(self.S3_URI % PATH)

        self.assertTrue(PATH in ls_result)
        self.assertEquals([], ls_result[PATH]['files'])
        self.assertEquals([], ls_result[PATH]['directories'])

    def test_ls_for_single_file(self):
        PATH = '/some/path/some_file'
        S3_PATH = drop_starting_slash(PATH)
        when(self.bucket).get_all_keys(prefix=S3_PATH, delimiter='/').thenReturn([
            make_key(S3_PATH, size=123, last_modified=u'2000-01-30T00:11:22.000Z')])

        ls_result = self.backend.ls(self.S3_URI % PATH)

        self.assertEquals(0, len(ls_result[PATH]['directories']))
        self.assertEquals(1, len(ls_result[PATH]['files']))
        ls_item = ls_result[PATH]['files'][0]
        self.assertEquals('some_file', ls_item[0])
        self.assertEquals(123, ls_item[1])
        self.assertEquals('Sun, 30 Jan 2000 00:11:22', ls_item[2])
        self.assertEquals(False, ls_item[3], "Not a symlink")

    def test_ls_a_dir_with_some_files_inside(self):
        PATH = '/some/path/'
        S3_PATH = drop_starting_slash(PATH)
        name = lambda filename: S3_PATH + filename
        when(self.bucket).get_all_keys(prefix=S3_PATH, delimiter='/').thenReturn([
            make_key(name('file1'), size=1, last_modified='1989-12-21T17:23:00.000Z'),
            make_key(name('file2'), size=2, last_modified='1989-12-22T17:23:00.000Z'),
            make_key(name('file3'), size=3, last_modified='1989-12-23T17:23:00.000Z'),
            boto.s3.prefix.Prefix(name=name('dir')),
            boto.s3.prefix.Prefix(name=name('dir2')),
        ])

        ls_result = self.backend.ls(self.S3_URI % PATH)

        expected_files = [
                ('file1', 1, 'Thu, 21 Dec 1989 17:23:00', False),
                ('file2', 2, 'Fri, 22 Dec 1989 17:23:00', False),
                ('file3', 3, 'Sat, 23 Dec 1989 17:23:00', False),
        ]
        expected_dirs = [
                ('dir', 0, None, False),
                ('dir2', 0, None, False),
        ]

        self.assertEquals(expected_files, ls_result[PATH]['files'])
        self.assertEquals(expected_dirs, ls_result[PATH]['directories'])

    def test_ls_ignores_keys_with_same_prefix(self):
        DIR_PATH = '/some/path/'
        PATH = DIR_PATH + 'file1'
        S3_DIR_PATH = drop_starting_slash(DIR_PATH)
        S3_PATH = drop_starting_slash(PATH)
        name = lambda filename: S3_DIR_PATH + filename
        when(self.bucket).get_all_keys(prefix=S3_PATH, delimiter='/').thenReturn([
            make_key(name('file1'), size=1, last_modified='1989-12-21T17:23:00.000Z'),
            make_key(name('file11')),
            make_key(name('file111')),
            boto.s3.prefix.Prefix(name=name('file1dir')),
        ])

        ls_result = self.backend.ls(self.S3_URI % PATH)

        expected_files = [
                ('file1', 1, 'Thu, 21 Dec 1989 17:23:00', False),
        ]

        self.assertEquals(expected_files, ls_result[PATH]['files'])
        self.assertEquals(0, len(ls_result[PATH]['directories']))


    def test_ls_a_dir_without_slash_at_the_end(self):
        # If we send a get_all_keys to boto on a dir without ending it in the
        # DELIMITER, it will just return the single entry as a Prefix. No items.
        # All we can do is call the method again after appending the DELIMITER
        PATH = '/some/path/'
        S3_PATH = drop_starting_slash(PATH)
        S3_WRONG_PATH = S3_PATH.rstrip('/')
        when(self.bucket).get_all_keys(prefix=S3_WRONG_PATH, delimiter='/').thenReturn([
            boto.s3.prefix.Prefix(name=S3_WRONG_PATH),
        ])
        when(self.bucket).get_all_keys(prefix=S3_PATH, delimiter='/').thenReturn([
            make_key(name=S3_PATH + 'file1'),
        ])

        ls_result = self.backend.ls(self.S3_URI % PATH.rstrip('/'))

        self.assertEquals(0, len(ls_result[PATH]['directories']))
        self.assertEquals(1, len(ls_result[PATH]['files']))
        self.assertEquals('file1', ls_result[PATH]['files'][0][0])

def drop_starting_slash(path):
    return path.lstrip('/')

def make_key(name, size=0, last_modified=u'1999-12-31T01:02:03.000Z'):
    s3key = boto.s3.key.Key(name=name)
    s3key.last_modified = last_modified
    s3key.size = size
    return s3key
