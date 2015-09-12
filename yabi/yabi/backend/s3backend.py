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

import boto3
from botocore.exceptions import ClientError
from functools import partial
from io import BytesIO
import itertools
import logging
import traceback

from django.conf import settings

from yabi.backend.fsbackend import FSBackend
from yabi.backend.exceptions import RetryException, FileNotFoundError
from yabi.yabiengine.urihelper import uriparse

logger = logging.getLogger(__name__)

NEVER_A_SYMLINK = False
DELIMITER = '/'
PART_UPLOAD_RETRIES = settings.S3_MULTIPART_UPLOAD_MAX_RETRIES


class S3Backend(FSBackend):
    """
    A key-value storage backend which uses Amazon's S3 object storage
    service through the boto package.
    """

    backend_desc = "Amazon S3 object storage"
    backend_auth = {
        "class": "AWS",
        "key": "AWS Access Key ID",
        "password": "AWS Secret Access Key",
    }
    lcopy_supported = False
    link_supported = False

    def __init__(self, *args, **kwargs):
        FSBackend.__init__(self, *args, **kwargs)
        self._bucket = None

    def bucket(self, name=None):
        if self._bucket is None:
            if name is None:
                raise ValueError("bucket not initialised")
            self._bucket = self.connect_to_bucket(name)
        return self._bucket

    def ls(self, uri):
        self.set_cred(uri)
        bucket_name, path = self.parse_s3_uri(uri)

        keys, prefixes = self.get_matching_keys_and_prefixes(bucket_name, path)

        if len(keys) == 1 and len(prefixes) == 0 and keys[0]['Key'].endswith(DELIMITER):
            # A key ending in the delimiter is a key for an empty directory
            files = []
            dirs = []
        else:
            files = [(self.basename(k['Key']), k['Size'], self.format_date(k['LastModified']), NEVER_A_SYMLINK) for k in keys]
            dirs = [(self.basename(p['Prefix']), 0, None, NEVER_A_SYMLINK) for p in prefixes]

        result = {
            path: {
                "files": files,
                "directories": dirs,
            }
        }

        return result

    def rm(self, uri):
        self.set_cred(uri)
        bucket_name, path = self.parse_s3_uri(uri)

        try:
            bucket = self.bucket(bucket_name)
            all_keys = self.get_keys_recurse(bucket_name, path)

            # Unfortunately, when passing in Unicode key names to the
            # Boto bucket.delete_objects, it throws a UnicodeEncodeError when
            # building the XML request. As a workaround, we split keys in 2 groups.
            # A group that has only valid ASCII keys and the other that has Unicode
            # keys (ie. would throw an UnicodeEncodeError on str conversion).
            # The first group of keys will be deleted with one API call to
            # bucket.delete_objects. The second group we iterate over and delete
            # one-by-one. Those will be deleted with a DELETE HTTP call, so no
            # XML 1.0 problems there.

            ASCII_keys = []
            Unicode_keys = []
            for k in map(lambda k: k['Key'], all_keys):
                try:
                    ASCII_keys.append({'Key': str(k)})
                except UnicodeEncodeError:
                    Unicode_keys.append(k)

            errors = []
            # delete_objects accepts a maximum of 1000 keys so we chunk the keys
            for keys in chunks(ASCII_keys, 1000):
                logger.debug("Deleting keys: %s", keys)
                multi_delete_result = bucket.delete_objects(Delete={'Objects': keys})
                if 'Errors' in multi_delete_result:
                    errors.extend(multi_delete_result['Errors']['Key'])

            for key in Unicode_keys:
                try:
                    bucket.Object(key).delete()
                except:
                    errors.append(key)

            if len(errors) > 0:
                # Some keys couldn't be deleted
                raise RuntimeError(
                    "The following keys couldn't be deleted when deleting uri %s: %s",
                    uri, ", ".join(errors))

        except Exception as exc:
            logger.exception("Error while trying to S3 rm uri %s", uri)
            raise RetryException(exc, traceback.format_exc())

    def mkdir(self, uri):
        self.set_cred(uri)
        dir_uri = ensure_trailing_slash(uri)
        self.rm(dir_uri)
        bucket_name, path = self.parse_s3_uri(dir_uri)

        try:
            bucket = self.bucket(bucket_name)
            key = bucket.Object(path.lstrip(DELIMITER))
            key.put(Body='')

        except Exception as exc:
            logger.exception("Error while trying to S3 rm uri %s", uri)
            raise RetryException(exc, traceback.format_exc())

    def download_file(self, uri, dst):
        try:
            bucket_name, path = self.parse_s3_uri(uri)

            bucket = self.connect_to_bucket(bucket_name)

            CHUNKSIZE = 8 * 1024

            try:
                obj = bucket.Object(path.lstrip(DELIMITER)).get()
            except ClientError as e:
                code = e.response.get('Error', {}).get('Code')
                if code == 'NoSuchKey':
                    raise FileNotFoundError(uri)
                raise

            body = obj.get('Body')
            for chunk in iter(lambda: body.read(CHUNKSIZE), b''):
                dst.write(chunk)

            return True
        except FileNotFoundError:
            logger.exception("Exception thrown while S3 downloading %s to %s", uri, dst)
            raise
        except:
            logger.exception("Exception thrown while S3 downloading %s to %s", uri, dst)
            return False

    def upload_file(self, uri, src):
        try:
            bucket_name, path = self.parse_s3_uri(uri)
            bucket = self.connect_to_bucket(bucket_name)

            # 5MB is the minimum size of a part when doing multipart uploads
            # Therefore, multipart uploads will fail if your file is smaller than 5MB
            CHUNKSIZE = 5 * 1024 * 1024

            reader = iter(lambda: src.read(CHUNKSIZE), b'')

            first_data_chunk = reader.next()
            if len(first_data_chunk) < CHUNKSIZE:
                # File is smaller than CHUNKSIZE, upload in one go (ie. no multipart)
                key = bucket.Object(path.lstrip(DELIMITER))
                key.put(Body=BytesIO(first_data_chunk))
                return True
            else:
                # File is larger than CHUNKSIZE, do multipart upload

                # Put back the first data chunk into the reader
                reader = itertools.chain(iter([first_data_chunk]), reader)
                return self.multipart_upload_file(bucket, path, reader)
        except:
            logger.exception("Exception while S3 uploading %s to %s", src, uri)
            return False

    # Implementation

    def upload_part(self, bucket, key, upload_id, data, part_no, retry_count):
        client = bucket.meta.client

        exception = None
        for try_no in range(retry_count):
            try:
                logger.debug("Uploading part %s", part_no)
                response = client.upload_part(Bucket=bucket.name,
                                              Key=key, UploadId=upload_id,
                                              PartNumber=part_no, Body=BytesIO(data))
                return {'ETag': response['ETag'], 'PartNumber': part_no}
            except Exception as exc:
                logger.warning("Failed attempt %s (of %s) to upload part. Err: %s", try_no + 1, PART_UPLOAD_RETRIES, exc)
                exception = exc

        logger.error("Failed last attempt (%s) to upload part. Giving up! Err: %s", try_no + 1, PART_UPLOAD_RETRIES, exc)
        raise exception

    def multipart_upload_file(self, bucket, path, data_reader):
        client = bucket.meta.client
        key = path.lstrip(DELIMITER)

        response = client.create_multipart_upload(Bucket=bucket.name, Key=key)
        upload_id = response['UploadId']

        try:
            parts = []
            for data in data_reader:
                part = self.upload_part(bucket, key, upload_id, data, len(parts) + 1, retry_count=PART_UPLOAD_RETRIES)
                parts.append(part)

            client.complete_multipart_upload(Bucket=bucket.name, Key=key, UploadId=upload_id, MultipartUpload={'Parts': parts})
            return True
        except:
            client.abort_multipart_upload(Bucket=bucket.name, Key=key, UploadId=upload_id)
            raise

    def parse_s3_uri(self, uri):
        if uri.endswith(DELIMITER):
            uri = uri.rstrip(DELIMITER) + DELIMITER
        scheme, parts = uriparse(uri)
        bucket_name = parts.hostname.split('.')[0]
        path = parts.path

        return bucket_name, path

    def _get_connect_params(self, bucket_name):
        c = self.cred.credential.get_decrypted()
        params = {"aws_access_key_id": c.key, "aws_secret_access_key": c.password}
        # TODO from docker containers the SSL verification fails
        # find a better fix for this
        if not settings.PRODUCTION:
            params['verify'] = False

        # TODO
        # Use different boto options for e2e tests against fakes3
        if settings.DEBUG and bucket_name == "fakes3":
            logger.info("Changing boto connection params for fakes3")
            params.update(host="s3test", port=4569, is_secure=False,
                          calling_format="boto.s3.connection.OrdinaryCallingFormat")

        return params

    def connect_to_bucket(self, bucket_name, verify=False):
        s3 = boto3.resource('s3', **self._get_connect_params(bucket_name))
        bucket = s3.Bucket(bucket_name)

        if verify:
            try:
                s3.meta.client.head_bucket(Bucket=bucket_name)
            except ClientError as e:
                error_code = int(e.response['Error']['Code'])
                if error_code == 404:
                    raise Exception("Bucket '%s' doesn't exist" % bucket_name)
                raise

        return bucket

    def get_matching_keys_and_prefixes(self, bucket_name, path):
        key_matches_path = partial(is_key_matching_name, path)
        prefix_matches_path = partial(is_prefix_matching_name, path)

        bucket = self.bucket(bucket_name)
        paginator = bucket.meta.client.get_paginator('list_objects')

        keys, prefixes = [], []
        for page in paginator.paginate(Bucket=bucket.name, Prefix=path.lstrip(DELIMITER), Delimiter=DELIMITER):
            keys += filter(key_matches_path, page.get('Contents', []))
            prefixes += filter(prefix_matches_path, page.get('CommonPrefixes', []))
        # Called on a directory with URI not ending in DELIMITER
        # We call ourself again correctly
        if len(keys) == 0 and len(prefixes) == 1 and not path.endswith(DELIMITER):
            return self.get_matching_keys_and_prefixes(bucket_name, path + DELIMITER)

        return keys, prefixes

    def get_keys_recurse(self, bucket, path):
        keys, prefixes = self.get_matching_keys_and_prefixes(bucket, path)
        for p in prefixes:
            keys.extend(self.get_keys_recurse(bucket, p['Prefix']))

        return keys

    def _path_exists(self, uri):
        bucket = self.bucket()
        _, path = self.parse_s3_uri(uri)
        return bucket.get_key(path.lstrip(DELIMITER)) is not None

    # URI and path helpers

    def basename(self, key_name):
        return FSBackend.basename(self, key_name.rstrip(DELIMITER))

    def parent_dir_uri(self, uri):
        uri = uri.rstrip(DELIMITER)
        return uri[:uri.rfind(DELIMITER)] + DELIMITER


def ensure_trailing_slash(s):
    return s if s.endswith(DELIMITER) else s + DELIMITER


def is_key_matching_name(name, key):
    return is_item_matching_name(name, key, item_name_attr='Key')


def is_prefix_matching_name(name, prefix):
    return is_item_matching_name(name, prefix, item_name_attr='Prefix')


def is_item_matching_name(name, item, item_name_attr):
    """We want to eliminate key names starting with the same prefix,
       but include keys at the next level (but not deeper) for dirs.
       Ex: listing for 'a'
           'a' included
           'abc' ignored
           'a/anything' included
           'a/anything/deeper' ignored"""
    name = name.lstrip(DELIMITER)
    item_name = item[item_name_attr]
    if item_name.rstrip(DELIMITER) == name.rstrip(DELIMITER):
        return True
    name = ensure_trailing_slash(name)

    if not item_name.startswith(name):
        return False

    item_name_end = item_name[len(name):].rstrip(DELIMITER)

    return DELIMITER not in item_name_end


def chunks(seq, chunk_size):
    for x in xrange(0, len(seq), chunk_size):
        yield seq[x:x + chunk_size]
