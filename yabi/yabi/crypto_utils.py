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

from . import aes_ctr
import math
import binascii
import logging
logger = logging.getLogger(__name__)

# legacy AES encryption (insecure)
AESHEXTAG = 'AES'
# legacy AES encryption (insecure) & protect with global key for memcache / prior to user login
AESTEMP = 'AESTEMP'
# AES-CTR encryption, with a HMAC. don't store with this is 'protected' or 'encrypted'
AESCTRTAG = 'AESCTR'


#
# this annotates a string with the
#
def annotate(tag, ciphertext):
    return "$%s$%s$" % (tag, ciphertext)


#
# join a split string together and de CR LF it
#
def joiner(data):
    return "".join("".join(data.split("\n")).split("\r"))


#
# notify callers of failure to decrypt if validity is being checked (not just blind decrypt)
#
class DecryptException(Exception):
    pass


class LegacyAESWrapper(object):
    """insecure as it uses AES in fixed block mode. do not use (only kept for compatibility reasons, and only for decryption)"""

    #
    # this is a chunking lambda generator
    #
    chunkify = staticmethod(lambda v, l: (v[i * l:(i + 1) * l] for i in range(int(math.ceil(len(v) / float(l))))))

    @classmethod
    def aes_dec(cls, data, key):
        from Crypto.Hash import SHA256
        from Crypto.Cipher import AES

        def contains_binary(data):
            """return true if string 'data' contains any binary"""
            # for now just see if there are any unprintable characters in the string
            import string
            return False in [X in string.printable for X in data]

        if not data:
            return data                     # decrypt nothing, get nothing

        key_hash = SHA256.new(key)
        aes = AES.new(key_hash.digest())

        # take chunks of 16
        output = ""
        for chunk in LegacyAESWrapper.chunkify(data, 16):
            output += aes.decrypt(chunk)

        # depad the plaintext
        while output.endswith('\0'):
            output = output[:-1]

        if contains_binary(output):
            raise DecryptException("AES decrypt failed. Decrypted data contains binary")

        return output

    @classmethod
    def aes_dec_hex(cls, ciphertext, key):
        """decrypt a base64 encoded encrypted block"""
        try:
            ciphertext = binascii.unhexlify(ciphertext)
        except TypeError:
            # the credential binary block cannot be decoded
            raise DecryptException("Credential does not seem to contain binary encrypted data")
        return LegacyAESWrapper.aes_dec(ciphertext, key)


def nounicode(fn):
    "decorator function, converts any unicode arguments to utf-8 bytestrings"
    def inner(*args, **kwargs):
        new_args = []
        for arg in args:
            if type(arg) is unicode:
                new_args.append(arg.encode('utf8'))
            else:
                new_args.append(arg)
        return fn(*new_args, **kwargs)
    return inner


def encrypted_block_is_legacy(data):
    "check if an annotated block is using legacy crypto"
    if data == '':
        return False
    tag, _ = deannotate(data)
    return tag == AESHEXTAG or tag == AESTEMP


@nounicode
def decrypt_annotated_block(data, key):
    "takes a annotated block and returns the encrypted value (decrypting with `key')"
    if data == '':
        return ''
    tag, ciphertext = deannotate(data)
    if ciphertext == '':
        return ''
    if tag == AESHEXTAG or tag == AESTEMP:
        return LegacyAESWrapper.aes_dec_hex(ciphertext, key)
    wrapper = aes_ctr.AESWrapper(key)
    try:
        return wrapper.decrypt(ciphertext)
    except aes_ctr.DecryptionFailure:
        raise DecryptException("Invalid key for AES-CTR encrypted data (%s / %s)" % (data, key))


@nounicode
def encrypt_to_annotated_block(data, key, nonce=None):
    "returns base64 encoded data, annotated appropriately and encrypted with `key`; nonce argument should only be specified in testing, other use is insecure"
    # don't encrypt empty string
    if data == '':
        return ''
    wrapper = aes_ctr.AESWrapper(key)
    encrypted = wrapper.encrypt(data, nonce)
    return annotate(AESCTRTAG, encrypted)


def deannotate(data):
    "deannotate annotated data"
    data = joiner(data)
    try:
        dummy, tag, cipher, dummy2 = data.split('$')
    except ValueError:
        raise DecryptException("Invalid input string to deannotate")
    if dummy or dummy2:
        raise DecryptException("Invalid input string to deannotate")
    return tag, cipher


def looks_like_annotated_block(data):
    """Looks for the $tag$ciphertext$ format.
    Returns the tag if it looks like an annotated cipherblock
    returns False if its improperly formatted
    """
    if data.startswith('$') and data.endswith('$') and data.count('$') == 3:
        try:
            tag, ciphertext = deannotate(data)
            return True
        except DecryptException:
            return False
    return False


def any_unencrypted(*args):
    "returns True if any of the `args' is unencrypted. empty values are ignored"
    return any(t != '' and (not looks_like_annotated_block(t)) for t in args)


def any_annotated_block(*args):
    "returns True if any of the `args' is an annotated block. empty values are ignored"
    return any(t != '' and looks_like_annotated_block(t) for t in args)
