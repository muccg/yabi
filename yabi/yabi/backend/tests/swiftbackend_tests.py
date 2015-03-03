# -*- coding: utf-8 -*-

from django.utils import unittest
from yabi.backend.swiftbackend import SwiftBackend


class SwiftURIParseTests(unittest.TestCase):
    def test_basic(self):
        uri = "swift://username@keystone.bioplatforms.com:443/tenant/bucket/file.txt"
        swift = SwiftBackend.SwiftPath.parse(uri)
        self.assertEqual(swift.keystone, "https://keystone.bioplatforms.com/v2.0/")
        self.assertEqual(swift.tenant, "tenant")
        self.assertEqual(swift.bucket, "bucket")
        self.assertEqual(swift.prefix, "file.txt")
        self.assertEqual(swift.path_part, "/tenant/bucket/file.txt")
        self.assertEqual(swift.uri, uri.replace(":443", "").replace("username@", ""))

    def test_path(self):
        uri = "swift://username@keystone.bioplatforms.com:443/tenant/bucket/path/to/file.txt"
        swift = SwiftBackend.SwiftPath.parse(uri)
        self.assertEqual(swift.keystone, "https://keystone.bioplatforms.com/v2.0/")
        self.assertEqual(swift.tenant, "tenant")
        self.assertEqual(swift.bucket, "bucket")
        self.assertEqual(swift.prefix, "path/to/file.txt")
        self.assertEqual(swift.path_part, "/tenant/bucket/path/to/file.txt")
        self.assertEqual(swift.uri, uri.replace(":443", "").replace("username@", ""))

    def test_without_prefix(self):
        uri = "swift://username@keystone.bioplatforms.com:443/tenant/bucket"
        swift = SwiftBackend.SwiftPath.parse(uri)
        self.assertEqual(swift.keystone, "https://keystone.bioplatforms.com/v2.0/")
        self.assertEqual(swift.tenant, "tenant")
        self.assertEqual(swift.bucket, "bucket")
        self.assertEqual(swift.prefix, "")
        self.assertEqual(swift.path_part, "/tenant/bucket/")
        self.assertEqual(swift.uri, uri.replace(":443", "").replace("username@", "") + "/")

    def test_without_prefix_with_slash(self):
        uri = "swift://username@keystone.bioplatforms.com:443/tenant/bucket/"
        swift = SwiftBackend.SwiftPath.parse(uri)
        self.assertEqual(swift.keystone, "https://keystone.bioplatforms.com/v2.0/")
        self.assertEqual(swift.tenant, "tenant")
        self.assertEqual(swift.bucket, "bucket")
        self.assertEqual(swift.prefix, "")
        self.assertEqual(swift.path_part, "/tenant/bucket/")

    def test_without_bucket(self):
        uri = "swift://username@keystone.bioplatforms.com:443/tenant"
        swift = SwiftBackend.SwiftPath.parse(uri)
        self.assertEqual(swift.keystone, "https://keystone.bioplatforms.com/v2.0/")
        self.assertEqual(swift.tenant, "tenant")
        self.assertEqual(swift.bucket, None)
        self.assertEqual(swift.prefix, "")
        self.assertEqual(swift.path_part, "/tenant")
        self.assertEqual(swift.uri, uri.replace(":443", "").replace("username@", ""))

    def test_without_bucket_with_slash(self):
        uri = "swift://username@keystone.bioplatforms.com:443/tenant/"
        swift = SwiftBackend.SwiftPath.parse(uri)
        self.assertEqual(swift.keystone, "https://keystone.bioplatforms.com/v2.0/")
        self.assertEqual(swift.tenant, "tenant")
        self.assertEqual(swift.bucket, None)
        self.assertEqual(swift.prefix, "")
        self.assertEqual(swift.path_part, "/tenant")  # fixme?

    def test_without_tenant(self):
        uri = "swift://username@keystone.bioplatforms.com:443"
        swift = SwiftBackend.SwiftPath.parse(uri)
        self.assertEqual(swift.keystone, "https://keystone.bioplatforms.com/v2.0/")
        self.assertEqual(swift.tenant, None)
        self.assertEqual(swift.bucket, None)
        self.assertEqual(swift.prefix, "")
        self.assertEqual(swift.path_part, "")
        self.assertEqual(swift.uri, uri.replace(":443", "").replace("username@", ""))

    def test_without_tenant_with_slash(self):
        uri = "swift://username@keystone.bioplatforms.com:443/"
        swift = SwiftBackend.SwiftPath.parse(uri)
        self.assertEqual(swift.keystone, "https://keystone.bioplatforms.com/v2.0/")
        self.assertEqual(swift.tenant, None)
        self.assertEqual(swift.bucket, None)
        self.assertEqual(swift.prefix, "")
        self.assertEqual(swift.path_part, "")

    def test_without_username_port(self):
        uri = "swift://keystone.bioplatforms.com/tenant/bucket/path/to/file.txt"
        swift = SwiftBackend.SwiftPath.parse(uri)
        self.assertEqual(swift.keystone, "https://keystone.bioplatforms.com/v2.0/")
        self.assertEqual(swift.tenant, "tenant")
        self.assertEqual(swift.bucket, "bucket")
        self.assertEqual(swift.prefix, "path/to/file.txt")
        self.assertEqual(swift.path_part, "/tenant/bucket/path/to/file.txt")
        self.assertEqual(swift.uri, uri)

    def test_extra_slashes(self):
        uri = "swift://username@keystone.bioplatforms.com:443//tenant///bucket//path///to//file.txt///"
        swift = SwiftBackend.SwiftPath.parse(uri)
        self.assertEqual(swift.keystone, "https://keystone.bioplatforms.com/v2.0/")
        self.assertEqual(swift.tenant, "tenant")
        self.assertEqual(swift.bucket, "bucket")
        self.assertEqual(swift.prefix, "path/to/file.txt/")
        self.assertEqual(swift.path_part, "/tenant/bucket/path/to/file.txt/")
        self.assertEqual(swift.uri, "swift://keystone.bioplatforms.com/tenant/bucket/path/to/file.txt/")

    def test_extra_extra_slashes(self):
        uri = "swift:///username@keystone.bioplatforms.com:443/tenant/bucket/path/to/file.txt"
        self.assertRaises(ValueError, SwiftBackend.SwiftPath.parse, uri)

    def test_bad_scheme_spec(self):
        uri = "gopher://username@keystone.bioplatforms.com:443/tenant/bucket/path/to/file.txt"
        swift = SwiftBackend.SwiftPath.parse(uri)
        self.assertEqual(swift.keystone, "https://keystone.bioplatforms.com/v2.0/")

    def test_missing_scheme(self):
        uri = "//username@keystone.bioplatforms.com:443/tenant/bucket/path/to/file.txt"
        # fixme: maybe yabi code should raise ValueError instead of assertion
        self.assertRaises(AssertionError, SwiftBackend.SwiftPath.parse, uri)

    def test_very_long_uri(self):
        username = "lah" * 100
        hostname = ".".join(["keystone.bioplatforms.com"] * 100)
        path = "/qwerty/asdf/12345" * 100
        uri = "".join(["swift://", username, "@", hostname, path])
        swift = SwiftBackend.SwiftPath.parse(uri)
        self.assertEqual(swift.keystone, "https://%s/v2.0/" % hostname)
        self.assertEqual(swift.tenant, "qwerty")
        self.assertEqual(swift.bucket, "asdf")
        self.assertEqual(swift.path_part, path)

    def test_unicode_uri(self):
        uri = "swift://keystone.bioplatforms.com/☃/☣/α/β/φ.txt"
        swift = SwiftBackend.SwiftPath.parse(uri)
        self.assertEqual(swift.keystone, "https://keystone.bioplatforms.com/v2.0/")
        self.assertEqual(swift.tenant, "☃")
        self.assertEqual(swift.bucket, "☣")
        self.assertEqual(swift.prefix, "α/β/φ.txt")
        self.assertEqual(swift.path_part, "/☃/☣/α/β/φ.txt")
        self.assertEqual(swift.uri, uri)

    # todo: maybe test url escaping

    def test_ensure_trailing_slash(self):
        uri = "swift://username@keystone.bioplatforms.com:443/tenant/bucket/subdir"
        swift = SwiftBackend.SwiftPath.parse(uri)

        # case 1: no trailing slash yet
        swift = swift.ensure_trailing_slash()
        self.assertEqual(swift.keystone, "https://keystone.bioplatforms.com/v2.0/")
        self.assertEqual(swift.tenant, "tenant")
        self.assertEqual(swift.bucket, "bucket")
        self.assertEqual(swift.prefix, "subdir/")
        self.assertEqual(swift.path_part, "/tenant/bucket/subdir/")
        self.assertEqual(swift.uri, uri.replace(":443", "").replace("username@", "") + "/")

        # case 2: trailing slash already there
        swift = swift.ensure_trailing_slash()
        self.assertEqual(swift.keystone, "https://keystone.bioplatforms.com/v2.0/")
        self.assertEqual(swift.tenant, "tenant")
        self.assertEqual(swift.bucket, "bucket")
        self.assertEqual(swift.prefix, "subdir/")
        self.assertEqual(swift.path_part, "/tenant/bucket/subdir/")
        self.assertEqual(swift.uri, uri.replace(":443", "").replace("username@", "") + "/")

    def test_parent_dir(self):
        uri = "swift://username@keystone.bioplatforms.com:443/tenant/bucket/subdir/test"
        swift = SwiftBackend.SwiftPath.parse(uri)
        swift = swift.parent_dir()

        self.assertEqual(swift.keystone, "https://keystone.bioplatforms.com/v2.0/")
        self.assertEqual(swift.tenant, "tenant")
        self.assertEqual(swift.bucket, "bucket")
        self.assertEqual(swift.prefix, "subdir/")
        self.assertEqual(swift.path_part, "/tenant/bucket/subdir/")

    def test_parent_dir_slash(self):
        uri = "swift://username@keystone.bioplatforms.com:443/tenant/bucket/subdir/test/"
        swift = SwiftBackend.SwiftPath.parse(uri)
        swift = swift.parent_dir()

        self.assertEqual(swift.keystone, "https://keystone.bioplatforms.com/v2.0/")
        self.assertEqual(swift.tenant, "tenant")
        self.assertEqual(swift.bucket, "bucket")
        self.assertEqual(swift.prefix, "subdir/")
        self.assertEqual(swift.path_part, "/tenant/bucket/subdir/")

    def test_parent_dir_toplevel(self):
        uri = "swift://username@keystone.bioplatforms.com:443/tenant/bucket/subdir"
        swift = SwiftBackend.SwiftPath.parse(uri)
        swift = swift.parent_dir()

        self.assertEqual(swift.keystone, "https://keystone.bioplatforms.com/v2.0/")
        self.assertEqual(swift.tenant, "tenant")
        self.assertEqual(swift.bucket, "bucket")
        self.assertEqual(swift.prefix, "/")
        self.assertEqual(swift.path_part, "/tenant/bucket/")

    def test_parent_dir_toplevel_slash(self):
        uri = "swift://username@keystone.bioplatforms.com:443/tenant/bucket/subdir/"
        swift = SwiftBackend.SwiftPath.parse(uri)
        swift = swift.parent_dir()

        self.assertEqual(swift.keystone, "https://keystone.bioplatforms.com/v2.0/")
        self.assertEqual(swift.tenant, "tenant")
        self.assertEqual(swift.bucket, "bucket")
        self.assertEqual(swift.prefix, "/")
        self.assertEqual(swift.path_part, "/tenant/bucket/")

    def test_parent_dir_root(self):
        uri = "swift://username@keystone.bioplatforms.com:443/tenant/bucket"
        swift = SwiftBackend.SwiftPath.parse(uri)
        self.assertIsNone(swift.parent_dir())

    def test_parent_dir_root_slash(self):
        uri = "swift://username@keystone.bioplatforms.com:443/tenant/bucket/"
        swift = SwiftBackend.SwiftPath.parse(uri)
        self.assertIsNone(swift.parent_dir())
