### BEGIN COPYRIGHT ###
#
# (C) Copyright 2011, Centre for Comparative Genomics, Murdoch University.
# All rights reserved.
#
# This product includes software developed at the Centre for Comparative Genomics 
# (http://ccg.murdoch.edu.au/).
# 
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, YABI IS PROVIDED TO YOU "AS IS," 
# WITHOUT WARRANTY. THERE IS NO WARRANTY FOR YABI, EITHER EXPRESSED OR IMPLIED, 
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND 
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT OF THIRD PARTY RIGHTS. 
# THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF YABI IS WITH YOU.  SHOULD 
# YABI PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR
# OR CORRECTION.
# 
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, OR AS OTHERWISE AGREED TO IN 
# WRITING NO COPYRIGHT HOLDER IN YABI, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR 
# REDISTRIBUTE YABI AS PERMITTED IN WRITING, BE LIABLE TO YOU FOR DAMAGES, INCLUDING 
# ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE 
# USE OR INABILITY TO USE YABI (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR 
# DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES 
# OR A FAILURE OF YABI TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF SUCH HOLDER 
# OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
# 
### END COPYRIGHT ###
from yabiadmin.backend.fsbackend import FSBackend
from yabiadmin.backend.exceptions import RetryException
from yabiadmin.yabi.models import DecryptedCredentialNotAvailable
from yabiadmin.yabiengine.urihelper import uriparse
import logging
import traceback
import boto
import dateutil
from itertools import tee, ifilter, ifilterfalse


logger = logging.getLogger(__name__)


NEVER_A_SYMLINK = False
DELIMITER = '/'


class S3Backend(FSBackend):
    def ls(self, uri):
        scheme, parts = uriparse(uri)
        bucket_name = parts.hostname.split('.')[0]
        path = parts.path

        aws_access_key_id, aws_secret_access_key = self.get_access_keys()

        try:
            connection = boto.connect_s3(aws_access_key_id, aws_secret_access_key)
            bucket = connection.get_bucket(bucket_name)
            keys_and_prefixes = bucket.get_all_keys(prefix=path.lstrip(DELIMITER), delimiter=DELIMITER)
            # Keys correspond to files, prefixes to directories
            keys, prefixes = partition(lambda k: type(k) == boto.s3.key.Key, keys_and_prefixes)

            def basename(key_name):
                name = key_name.rstrip(DELIMITER)
                delimiter_last_position = name.rfind(DELIMITER)
                return name[delimiter_last_position+1:]
            files = [(basename(k.name), k.size, format_iso8601_date(k.last_modified), NEVER_A_SYMLINK) for k in keys]

            dirs = [(basename(p.name), 0, None, NEVER_A_SYMLINK) for p in prefixes]

        except boto.exception.S3ResponseError, e:
            logger.exception("Couldn't get listing from S3:")
            # TODO doing the same as SFTPBackend, but is this what we want?
            # This code is not executed by Celery tasks
            raise RetryException(e, traceback.format_exc())

        return { path: {
                   'files': files, 
                   'directories': dirs 
               }}


    def get_access_keys(self):
        credential = self.cred.credential

        if credential.is_cached:
            decrypted_credential = credential.get()
            aws_access_key_id = decrypted_credential['cert']
            aws_secret_access_key = decrypted_credential['key']
        else:
            raise DecryptedCredentialNotAvailable("Decrypted credential not available to access S3")


        return aws_access_key_id, aws_secret_access_key



def format_iso8601_date(iso8601_date):
    date = dateutil.parser.parse(iso8601_date)
    return date.strftime("%a, %d %b %Y %H:%M:%S")


def partition(pred, iterable):
    t1, t2 = tee(iterable)
    return ifilter(pred, t1), ifilterfalse(pred, t2)

