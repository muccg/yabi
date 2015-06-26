from unittest import TestCase
from yabi.backend.utils import ls
from copy import copy
import os
import shutil


class LsTestCase(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.root = "/tmp/lstestdir/"
        self.link_file_src = "/tmp/mylink.txt"
        self.date_string = self.todays_date()
        self.remove_folder_structure()
        self.create_folder_structure()

    def todays_date(self):
        from datetime import datetime
        return datetime.today().strftime("%b %d %Y") # e.g. 'Jul 26 2014'

    def create_folder_structure(self):

        def write(path, content):
            with open("%s/%s" % (self.root, path), "w") as f:
                f.write(content)

        os.makedirs(self.root)
        os.makedirs(os.path.join(self.root, "foo"))
        os.makedirs(os.path.join(self.root, "bar"))
        os.makedirs(os.path.join(self.root, "foo", "baz"))

        write("foo/a.txt", "A")
        write("foo/b.txt", "B")
        write("bar/c.txt", "C")
        write("d.txt", "D")

        # create a link
        with open(self.link_file_src, "w") as lf:
            lf.write("hello")
        link_path = os.path.join(self.root, "foo", "l.txt")
        os.symlink(self.link_file_src, link_path)

    def remove_folder_structure(self):
        if os.path.exists(self.root):
            shutil.rmtree(self.root)

        if os.path.exists(self.link_file_src):
            os.unlink(self.link_file_src)

    def test_structure_produced_by_ls_is_correct(self):
        listing = ls(self.root)

        self.assertTrue(isinstance(listing, dict), "listing is not a dict: listing = %s" % listing)
        self.assertTrue(self.root in listing, "root key not in listing dictionary: listing = %s" % listing)

        value = listing[self.root]
        self.assertTrue(isinstance(value,dict), "value not a dictionary: listing = %s" % listing)

        self.assertTrue("files" in value, "listing dictionary value does not contain a files key: listing = %s" % listing)
        files_list = value['files']
        self.assertTrue(isinstance(files_list, list), "files list is not a list!: listing = %s" % listing)

        self.assertTrue(len(files_list) == 1, "files list incorrect expected 1 got %s. listing = %s" % (len(files_list), listing))
        d_tuple = files_list[0]
        self.assertTrue(isinstance(d_tuple, tuple), "file record is not a tuple - is a %s. listing = %s" % (type(d_tuple), listing))

        self.assertTrue(len(d_tuple) == 4, "file record tuple is wrong length. Expected 4 got %s. listing = %s" % (len(d_tuple), listing))
        name, size, date_string, is_a_link = d_tuple

        self.assertEquals(name, "d.txt", "File name wrong expected d.txt. Got %s. listing = %s" % (name, listing))
        self.assertEquals(size, 1, "File size string does not match. Expected %s Actual %s. listing = %s" % (1, size, listing))
        self.assertEquals(date_string, self.date_string, "File date string wrong. Expected %s. listing = %s" % (self.date_string, listing))
        self.assertEquals(is_a_link, False, 'is_a_link wrong: Expected: False, Actual:%s. listing = %s' % (is_a_link, listing))

        self.assertTrue("directories" in value, "Expected 'directories' key in listing. listing = %s" % listing)

        directories = value['directories']
        self.assertTrue(isinstance(directories, list), "Expected directories value to be a list. listing = %s" % listing)

        self.assertTrue(len(directories) == 2, "Expected 2 directories. listing = %s" % listing)

        directories_without_size = map(ignore_size, directories)
        self.assertTrue(('foo', self.todays_date(), False) in directories_without_size, 'Subdirectories wrong foo: directories = %s listing = %s' % (directories, listing))
        self.assertTrue(('bar', self.todays_date(), False) in directories_without_size, 'Subdirectories wrong bar: directories = %s listing = %s' % (directories, listing))

        listing = ls(os.path.join(self.root, 'foo'))
        foo_dir_key = "%sfoo/" % self.root

        self.assertEquals(1, len(listing))
        self.assertTrue(foo_dir_key in listing)

        foo_listing = listing[foo_dir_key]
        self.assertEquals(2, len(foo_listing))
        self.assertTrue('files' in foo_listing)
        self.assertTrue('directories' in foo_listing)

        expected_files = [('a.txt', 1, self.todays_date(), False), ('b.txt', 1, self.todays_date(),  False), ("l.txt", 15, self.todays_date(),  True)]
        self.assertEquals(foo_listing['files'], expected_files)

        expected_dirs = [('baz', self.todays_date(), False)]
        foo_dirs = foo_listing['directories']
        foo_dirs_without_size = map(ignore_size, foo_dirs)
        self.assertEquals(expected_dirs, foo_dirs_without_size)

    def test_recursive_ls(self):
        import json
        uri = "localfs://demo@localhost%s" % self.root
        # This is what was produced by old ls parsing code
        
        self.old_listing = {"/tmp/lstestdir/foo/baz/": {"files": [], "directories": []},
                            "/tmp/lstestdir/": {"files": [("d.txt", 1, self.todays_date(), False)], "directories": [("bar", 1096, self.todays_date(), False), ("foo", 1096, self.todays_date(), False)]},
                            "/tmp/lstestdir/foo/": {"files": [("a.txt", 1, self.todays_date(), False), ("b.txt", 1, self.todays_date(), False), ("l.txt", 15, self.todays_date(), True)], "directories": [("baz", 1096, self.todays_date(), False)]},
                            "/tmp/lstestdir/bar/": {"files": [("c.txt", 1, self.todays_date(), False)], "directories": []},
                            }

        def remove_dir_sizes(listing):
            new_listing = {}
            for k, v in listing.items():
                new_v = copy(v)
                new_v['directories'] = map(ignore_size, v['directories'])
                new_listing[k] = new_v
            return new_listing

        listing = ls(self.root, recurse=True)

        self.assertEquals(remove_dir_sizes(self.old_listing), remove_dir_sizes(listing), "old listing = %s\n\n\nnew listing=%s" % (self.old_listing, listing))

    def test_ls_on_file(self):
        # take the file /tmp/lstestdir/foo/b.txt
        test_file = "/tmp/lstestdir/foo/b.txt"

        listing = ls(test_file)
        file_dict = {"files": [("b.txt", 1, self.todays_date(), False)], "directories": []}
        expected = {test_file: file_dict}

        self.assertEquals(listing,expected,"ls on single file failed. Expected %s Actual %s" % (expected, listing))

    def tearDown(self):
        self.remove_folder_structure()
        TestCase.tearDown(self)


def ignore_size(directory):
    name, size, date, is_symlink = directory
    return (name, date, is_symlink)
