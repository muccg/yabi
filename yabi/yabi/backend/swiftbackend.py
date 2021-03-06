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

import os
import logging
from collections import namedtuple
import tempfile
from urllib import unquote
import swiftclient
import swiftclient.client
import swiftclient.exceptions
from django.conf import settings
from .fsbackend import FSBackend
from .exceptions import RetryException, FileNotFoundError
from .utils import partition
from ..yabiengine.urihelper import uriparse

logger = logging.getLogger(__name__)

NEVER_A_SYMLINK = False


class SwiftBackend(FSBackend):
    """
    Storage backend using the OpenStack Swift object store through the
    python-swiftclient API.

    fixme: why is set_cred() only done on mkdir and ls?
    """

    backend_desc = "OpenStack Swift object storage"
    backend_auth = {
        "class": "OpenStack",
        "username": "Keystone user name",
        "password": "Keystone password",
    }
    lcopy_supported = False
    link_supported = False

    def __init__(self, *args, **kwargs):
        FSBackend.__init__(self, *args, **kwargs)
        self._conn = None

    class SwiftPath(namedtuple("SwiftPath", ("keystone", "tenant", "bucket", "prefix"))):
        """
        Represents a location in a Swift object store with Keystone 2.0
        auth. A SwiftPath can be converted from and to a YABI-specific
        URI.
        """

        DELIMITER = "/"
        auth_version = "2.0"

        @classmethod
        def parse(cls, uri):
            """
            Converts YABI fake swift urls into tenant, bucket and path
            triplet.

            There is no proper Swift URL convention as far as I know
            so swift:// is used as the scheme. The host part is the
            hostname of the keystone server. HTTPS is always used, but
            it doesn't need to be on port 443. The first part of the
            URL path determines the tenant (project), next part is the
            bucket, and the rest is the prefix within the
            bucket. Keystone 2.0 auth is always used.

            If there is no tenant or bucket, they will be returned as
            None. If there is no prefix path, then prefix will be an
            empty string.
            """
            # strip off trailing double slashes and use yabi parsing routine
            if uri.endswith(cls.DELIMITER):
                uri = uri.rstrip(cls.DELIMITER) + cls.DELIMITER
            scheme, parts = uriparse(uri)

            if parts.hostname is None:
                raise ValueError("No hostname in %s" % repr(uri))

            if parts.port and parts.port != 443:
                logger.warning("Ignoring URI port %d from %s", parts.port, uri)

            # Generate keystone auth endpoint by taking the hostname
            # part of the swift url and assuming https and v2.0 api.
            keystone = "https://%s/v%s/" % (parts.hostname, cls.auth_version)

            # First part of path is the bucket, rest is the prefix
            path = filter(bool, parts.path.split(cls.DELIMITER))
            tenant = path[0] if len(path) > 0 else None
            bucket = path[1] if len(path) > 1 else None

            prefix = cls.DELIMITER.join(path[2:]) if len(path) > 2 else ""
            if len(path) > 2 and parts.path[-1] == cls.DELIMITER:
                prefix += cls.DELIMITER  # put back trailing slash

            return cls(keystone, tenant, bucket, prefix)

        @property
        def path_part(self):
            "Returns the file path section of the URI /tenant/bucket/prefix"
            parts = filter(bool, [self.tenant, self.bucket])
            if self.bucket:
                parts.append(self.prefix.lstrip("/"))
            return self.DELIMITER.join([""] + parts)

        @property
        def uri(self):
            return "swift://" + self.get_keystone_base() + self.path_part

        def get_keystone_base(self):
            return uriparse(self.keystone)[1].hostname

        def ensure_trailing_slash(self):
            "Returns a new SwiftPath that definitely has a slash on the end"
            cls = type(self)
            if self.prefix.endswith(self.DELIMITER):
                prefix = self.prefix
            else:
                prefix = self.prefix + self.DELIMITER
            t = cls(self.keystone, self.tenant, self.bucket, prefix)
            return t

        def parent_dir(self):
            """
            Returns the parent path of this path, or None if it is already the
            root path.
            """
            prefix = self.prefix.rstrip("/")
            if prefix:
                if "/" in prefix:
                    prefix = prefix[:prefix.rfind(self.DELIMITER)]
                else:
                    prefix = ""
                cls = type(self)
                return cls(self.keystone, self.tenant, self.bucket,
                           prefix + self.DELIMITER)
            return None

    def _get_conn(self, url):
        if self._conn is None:
            params = self._get_auth_params(url)
            self._conn = swiftclient.client.Connection(**params)
        return self._conn

    def _get_auth_params(self, url):
        c = self.cred.credential.get_decrypted()
        return {
            "authurl": url.keystone,
            "tenant_name": url.tenant,
            "auth_version": url.auth_version,
            "user": c.username,
            "key": c.password,
        }

    def list_bucket(self, swift, shallow=True):
        conn = self._get_conn(swift)

        def wanted(entry):
            name = entry.get("subdir", None) or entry.get("name")
            return (name == swift.prefix or
                    name.startswith(swift.ensure_trailing_slash().prefix) or
                    swift.prefix in ("", swift.DELIMITER))

        def get_content_length(entry):
            "Fills in the file size for dynamic large object entries"
            if ("name" in entry and entry.get("bytes", -1) == 0 and
                    not entry["name"].endswith("/")):
                headers = conn.head_object(swift.bucket, entry["name"])
                entry["bytes"] = int(headers.get("content-length", "") or 0)
            return entry

        try:
            r = conn.get_container(swift.bucket, prefix=swift.prefix,
                                   full_listing=True,
                                   delimiter=swift.DELIMITER if shallow else None)
        except swiftclient.exceptions.ClientException as e:
            logger.exception("Problem listing bucket: %s" % swift.uri)
            # use this exception for lack of a better one
            raise RetryException(e)
        else:
            bucket = r[1]
            return map(get_content_length, filter(wanted, bucket))

    def ls(self, uri):
        logger.debug("swift ls %s" % uri)
        self.set_cred(uri)
        swift = self.SwiftPath.parse(uri)

        bucket = self.list_bucket(swift, shallow=True)
        if (len(bucket) == 1 and "subdir" in bucket[0] and
                bucket[0]["subdir"].rstrip(swift.DELIMITER) == swift.prefix):
            # if uri corresponds to a "subdirectory", add a slash and
            # list again to get the contents
            swift = swift.ensure_trailing_slash()
            bucket = self.list_bucket(swift, shallow=True)

        def is_key_for_dir(e):
            return e["name"] == swift.prefix and e["name"].endswith(swift.DELIMITER)

        # Keys correspond to files, prefixes to directories
        prefixes, allkeys = partition(lambda ob: "subdir" in ob, bucket)
        empty_dir_entry, keys = partition(is_key_for_dir, allkeys)

        def remove_prefix(path):
            if swift.prefix.endswith(swift.DELIMITER):
                if path[:len(swift.prefix)] == swift.prefix:
                    return path[len(swift.prefix):].rstrip(swift.DELIMITER)
                else:
                    return None
            else:
                return self.basename(path.rstrip(swift.DELIMITER))

        def format_file(entry):
            name = remove_prefix(entry["name"])
            return (name, entry["bytes"],
                    self.format_iso8601_date(entry["last_modified"]),
                    NEVER_A_SYMLINK) if name else None

        def format_dir(entry):
            name = remove_prefix(entry["subdir"])
            return (name, 0, None, NEVER_A_SYMLINK) if name else None

        files = filter(bool, map(format_file, keys))
        directories = filter(bool, map(format_dir, prefixes))

        is_dir = len(list(empty_dir_entry)) != 0
        if len(files) == 0 and len(directories) == 0 and not is_dir:
            result = {}
        else:
            result = {
                swift.path_part: {
                    "files": files,
                    "directories": directories,
                }}

        return result

    def _delete_object(self, conn, bucket, prefix):
        """
        Deletes an object in a bucket. If the file is a dynamic large
        object, it takes care of segments too.
        This lovely code is adapted from swiftclient.shell.st_delete().
        """
        headers = conn.head_object(bucket, prefix)
        old_manifest = headers.get('x-object-manifest')
        conn.delete_object(bucket, prefix)

        if old_manifest:
            scontainer, sprefix = old_manifest.split('/', 1)
            scontainer = unquote(scontainer)
            sprefix = unquote(sprefix).rstrip('/') + '/'

            for delobj in conn.get_container(scontainer, prefix=sprefix)[1]:
                conn.delete_object(scontainer, delobj['name'])

    def rm(self, uri):
        logger.debug("rm(%s)", uri)
        swift = self.SwiftPath.parse(uri)

        conn = self._get_conn(swift)

        all_keys = self.list_bucket(swift, shallow=False)

        for entry in all_keys:
            if "name" in entry:
                self._delete_object(conn, swift.bucket, entry["name"])

        parent = swift.parent_dir()
        if parent and not self._path_exists(parent):
            self.mkdir(parent.uri)

    def mkdir(self, uri):
        """
        Creates an empty object placeholder for a directory. If any objects
        exist with the same prefix they will be deleted (sounds a bit
        dangerous to me).
        """
        # fixme: need to support creation of buckets
        # fixme: need to prevent attempts to create tenants
        self.set_cred(uri)

        swift = self.SwiftPath.parse(uri).ensure_trailing_slash()
        conn = self._get_conn(swift)

        try:
            conn.put_object(swift.bucket, swift.prefix, "")
        except swiftclient.exceptions.ClientException as e:
            logger.exception("Error creating placeholder %s", uri)
            raise RetryException(e)  # fixme: don't like it

    def _path_exists(self, swiftpath):
        return (swiftpath.prefix in ("", "/") or
                len(self.list_bucket(swiftpath, shallow=True)) > 0)

    CHUNKSIZE = 64 * 1024

    def download_file(self, uri, outfile):
        swift = self.SwiftPath.parse(uri)
        conn = self._get_conn(swift)

        success = False

        try:
            headers, contents = conn.get_object(swift.bucket, swift.prefix,
                                                resp_chunk_size=self.CHUNKSIZE)
            for chunk in contents:
                outfile.write(chunk)
        except swiftclient.exceptions.ClientException as e:
            logger.exception("Error downloading %s to %s", uri, outfile)
            if e.http_status == 404:
                raise FileNotFoundError(uri)
        except IOError:
            logger.exception("Error writing %s to file", uri)
        else:
            success = True
        return success

    def upload_file(self, uri, infile):
        logger.debug("upload_file(%s)", uri)

        swift = self.SwiftPath.parse(uri)
        conn = self._get_conn(swift)

        return self._swift_upload(swift, conn, infile)

    def _swift_upload(self, swift, conn, infile):
        """Puts the contents of infile into a container on swift. If the file
        is larger than 100M, it will be divided into segments using
        the "dynamic large objects" convention.

        infile is expected to be a pipe, so each segment is stored in
        a temporary file before uploading. This allows the
        python-swiftclient library to retry failed uploads.
        """
        SEGMENT_SIZE = getattr(settings, "SWIFT_BACKEND_SEGMENT_SIZE",
                               100 * 1024 * 1024)

        segment_buf = tempfile.NamedTemporaryFile()

        st = os.fstatvfs(segment_buf.fileno())
        free_space = st.f_bavail * st.f_bsize
        if free_space < SEGMENT_SIZE:
            logger.error("There is only %dM space available for %s and %dM is required." % (free_space / 1024 / 1024, segment_buf.name, SEGMENT_SIZE / 1024 / 1024))

        def load_segment():
            """Copies enough data for a segment from the fifo into a temporary
            file. Returns how much data was actually written. """
            written = 0
            while written < SEGMENT_SIZE:
                bufsize = min(64 * 1024, SEGMENT_SIZE - written)
                buf = infile.read(bufsize)
                if not buf:
                    break
                segment_buf.write(buf)
                written += len(buf)
            segment_buf.seek(0)
            return written

        def upload_segment(bucket, prefix, length):
            try:
                conn.put_object(bucket, prefix, segment_buf,
                                content_length=length,
                                chunk_size=self.CHUNKSIZE)
            except swiftclient.exceptions.ClientException:
                logger.exception("Error when uploading segment")
                raise
            except IOError:
                logger.exception("Error when uploading segment")
                raise

        def upload_manifest(bucket, prefix):
            headers = {"X-Object-Manifest": "%s_segments/%s/" % (bucket, prefix)}
            conn.put_object(bucket, prefix, "", content_length=0,
                            headers=headers)

        seg_num = 0
        last_seg = False

        while not last_seg:
            seg_size = load_segment()

            last_seg = seg_size < SEGMENT_SIZE

            if seg_num == 0 and last_seg:
                bucket = swift.bucket
                prefix = swift.prefix
            else:
                bucket = swift.bucket + "_segments"
                prefix = "%s/%s/%08d" % (swift.prefix, SEGMENT_SIZE, seg_num)
                if seg_num == 0:
                    logger.debug("%s %s will be uploaded in %s byte segments." % (swift.bucket, swift.prefix, SEGMENT_SIZE))
                    # ensure that a segments container exists
                    conn.put_container(bucket)

            upload_segment(bucket, prefix, seg_size)

            segment_buf.seek(0)
            segment_buf.truncate(0)

            seg_num += 1

        if seg_num > 1:
            upload_manifest(swift.bucket, swift.prefix)

        return True
