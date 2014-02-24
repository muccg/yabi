# OpenStack Swift storage backend for YABI.
# Copyright (C) 2014  Centre for Comparative Genomics

import logging
from collections import namedtuple
from itertools import ifilterfalse
import swiftclient
import swiftclient.client
import swiftclient.exceptions
from .keyvaluebackend import KeyValueBackend, NEVER_A_SYMLINK, ERROR_STATUS, OK_STATUS
from yabiadmin.backend.exceptions import NotSupportedError, RetryException
from yabiadmin.backend.utils import get_credential_data, partition
from yabiadmin.yabiengine.urihelper import uriparse

logger = logging.getLogger(__name__)

class SwiftBackend(KeyValueBackend):
    """
    Storage backend using the OpenStack Swift object store through the
    python-swiftclient API.

    fixme: why is set_cred() only done on mkdir and ls?
    """

    def __init__(self, *args, **kwargs):
        super(SwiftBackend, self).__init__(*args, **kwargs)
        self._conn = None

    class SwiftPath(namedtuple("SwiftPath", ("keystone", "tenant", "bucket", "prefix"))):
        """
        Represents a location in a Swift object store with Keystone 2.0
        auth. A SwiftPath can be converted from and to a YABI-specific
        URI.
        """

        DELIMITER = "/"

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
            auth_version = "2.0"
            keystone = "https://%s/v%s/" % (parts.hostname, auth_version)

            # First part of path is the bucket, rest is the prefix
            path = filter(bool, parts.path.split(cls.DELIMITER))
            tenant = path[0] if len(path) > 0 else None
            bucket = path[1] if len(path) > 1 else None

            prefix = cls.DELIMITER.join(path[2:]) if len(path) > 2 else ""
            if len(path) > 2 and parts.path[-1] == cls.DELIMITER:
                prefix += cls.DELIMITER  # put back trailing slash

            t = cls(keystone, tenant, bucket, prefix)
            t.auth_version = auth_version
            return t

        @property
        def path_part(self):
            "Returns the file path section of the URI /tenant/bucket/prefix"
            #parts = filter(bool, [self.tenant, self.bucket, self.prefix])
            #return self.DELIMITER + self.DELIMITER.join(parts) if parts else ""
            return self.DELIMITER.join(["", self.tenant or "",
                                        self.bucket or "", self.prefix])

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
            t.auth_version = self.auth_version
            return t

    def _get_conn(self, url):
        if self._conn is None:
            params = self._get_auth_params(url)
            logger.debug("auth params: %s" % str(params))
            self._conn = swiftclient.client.Connection(**params)
        return self._conn

    def _get_auth_params(self, url):
        user, cert, key, passwd = get_credential_data(self.cred.credential)
        return {
            "authurl": url.keystone,
            "tenant_name": url.tenant,
            "auth_version": url.auth_version,
            "user": user,
            "key": passwd,
        }

    def list_bucket(self, swift, shallow=True):
        conn = self._get_conn(swift)

        def wanted(entry):
            name = entry.get("subdir", None) or entry.get("name")
            return (name == swift.prefix or
                    name.startswith(swift.ensure_trailing_slash().prefix) or
                    swift.prefix in ("", swift.DELIMITER))

        try:
            r = conn.get_container(swift.bucket, prefix=swift.prefix,
                                   full_listing=True,
                                   delimiter=swift.DELIMITER if shallow else None)
        except swiftclient.exceptions.ClientException as e:
            logger.exception("Problem listing bucket: %s" % swift.uri)
            # use this exception for lack of a better one
            raise RetryException(e)
        else:
            bucket = filter(wanted, r[1])
            return bucket

    def ls(self, uri):
        logger.debug("swift ls %s" % uri)
        self.set_cred(uri)
        swift = self.SwiftPath.parse(uri)

        bucket = self.list_bucket(swift, shallow=True)
        if len(bucket) == 1 and "subdir" in bucket[0]:
            # if uri corresponds to a "subdirectory", add a slash and
            # list again to get the contents
            swift = swift.ensure_trailing_slash()
            bucket = self.list_bucket(swift, shallow=True)

        # Keys correspond to files, prefixes to directories
        prefixes, keys = partition(lambda ob: "subdir" in ob, bucket)

        def remove_prefix(path):
            if swift.prefix.endswith(swift.DELIMITER):
                # fixme: basename() is probably enough for either case
                if path[:len(swift.prefix)] == swift.prefix:
                    return path[len(swift.prefix):]
                else:
                    return None
            else:
                return self.basename(path)

        def format_file(entry):
            name = remove_prefix(entry["name"])
            return (name, entry["bytes"],
                    self.format_iso8601_date(entry["last_modified"]),
                    NEVER_A_SYMLINK) if name else None

        def format_dir(entry):
            name = remove_prefix(entry["subdir"]).rstrip("/")
            return (name, 0, None, NEVER_A_SYMLINK) if name else None

        return {swift.path_part: {
            "files": filter(bool, map(format_file, keys)),
            "directories": filter(bool, map(format_dir, prefixes)),
        }}

    def rm(self, uri):
        logger.debug("rm(%s)", uri)
        swift = self.SwiftPath.parse(uri)

        conn = self._get_conn(swift)

        all_keys = self.list_bucket(swift, shallow=False)

        for entry in all_keys:
            if "name" in entry:
                conn.delete_object(swift.bucket, entry["name"])

        parent_dir_uri = self.parent_dir_uri(uri)
        if not self._path_exists(parent_dir_uri):
            self.mkdir(parent_dir_uri)

    def mkdir(self, uri):
        """
        Creates an empty object placeholder for a directory. If any objects
        exist with the same prefix they will be deleted (sounds a bit
        dangerous to me).
        """
        # fixme: need to support creation of buckets
        # fixme: need to prevent attempts to create tenants
        self.set_cred(uri)
        dir_uri = self.ensure_trailing_slash(uri)

        swift = self.SwiftPath.parse(dir_uri)
        conn = self._get_conn(swift)

        try:
            conn.put_object(swift.bucket, swift.prefix, "")
        except swiftclient.exceptions.ClientException as e:
            logger.exception("Error creating placeholder %s", uri)
            raise RetryException(e)  # fixme: don't like it

    def _path_exists(self, uri):
        return len(self.list_bucket(self.SwiftPath.parse(uri), shallow=True)) > 0

    CHUNKSIZE = 5 * 1024 * 1024

    def download_file(self, uri, filename, queue):
        swift = self.SwiftPath.parse(uri)
        conn = self._get_conn(swift)

        status = ERROR_STATUS

        try:
            # fixme: there is one http request per chunk i think.
            headers, contents = conn.get_object(swift.bucket, swift.prefix, resp_chunk_size=self.CHUNKSIZE)
            with open(filename, "wb") as outfile:
                map(outfile.write, contents)
        except swiftclient.exceptions.ClientError as e:
            logger.exception("Exception thrown while S3 downloading %s to %s", uri, filename)
        except IOError:
            logger.exception("Error writing %s to file", uri)
        else:
            status = OK_STATUS
        finally:
            queue.put(status)

    def upload_file(self, uri, filename, queue):
        logger.debug("upload_file(%s)", uri)

        swift = self.SwiftPath.parse(uri)
        conn = self._get_conn(swift)

        status = ERROR_STATUS

        try:
            # apparently swiftclient handles chunking, how nice
            with open(filename, "rb") as infile:
                conn.retries = 0  # will stop swiftclient seeking through infile
                conn.put_object(swift.bucket, swift.prefix, infile,
                                chunk_size=self.CHUNKSIZE)
        except swiftclient.exceptions.ClientException:
            logger.exception("Exception thrown while S3 uploading %s to %s", filename, uri)
        except IOError:
            logger.exception("Error reading from file for %s", uri)
        else:
            status = OK_STATUS
        finally:
            queue.put(status)
