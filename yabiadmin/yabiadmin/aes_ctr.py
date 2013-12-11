# -*- coding: utf-8 -*-
### BEGIN COPYRIGHT ###
#
# (C) Copyright 2009 Grahame Bowland <grahame@angrygoats.net>
# (C) Copyright 2013, Centre for Comparative Genomics, Murdoch University.
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
# -*- coding: utf-8 -*-

from Crypto.Cipher import AES
import base64, math, itertools, datetime, struct, os, hmac, hashlib
import six
from six.moves import xrange

class CTR(object):
    """
    AES Counter Mode (using pycrypto) to interoperate with the aes-lib.js implementation by Chris Veness
    http://www.movable-type.co.uk/scripts/aes.html
    """
    blocksize = 16
    
    @classmethod
    def urandom_8b(self):
        "returns eight random bytes"
        while True:
            yield os.urandom(8)
    
    @classmethod
    def ord_str(cls, s):
        "convert string into list of integer byte values"
        return [ord(t) for t in s]

    @classmethod
    def chr_ord(cls, s):
        "convert list of integer byte values into string"
        return ''.join([chr(t) for t in s])
            
    @classmethod
    def pad(cls, string, try_lens):
        """
        pad a string to the first of 'try_lens' possible;
        try_lens should be sorted increasing. truncates
        to the final length if necessary
        """
        for l in try_lens:
            if len(string) <= l:
                return string + ('\0' * (l - len(string)))
        return string[:l]
    
    @classmethod
    def blocks(cls, s):
        """
        returns the number of blocks in the string
        """
        nblocks = int(math.ceil(len(s) / (1. * CTR.blocksize)))
        for i in xrange(nblocks):
            yield s[i * CTR.blocksize:(i + 1) * CTR.blocksize]
    
    @classmethod
    def generate_counterblock(cls, block_num, nonce):
        """
        generate the aes counter block determined by block_num
        using initial nonce `nonce'
        """
        counterblock = nonce + []
        for i in xrange(7, -1, -1):
            v = (block_num / (2 ** (8*i))) & 0xFF
            counterblock.append(v)
        return counterblock
        
    def __init__(self, password, key_length):
        """
        create a new AES-CTR instance. builds internal state, including the 
        internal key (which is derived from the provided password). varying
        that derivation will break decryption of existing data.
        """
        if key_length != 128 and key_length != 192 and key_length != 256:
            raise Exception("invalid key length, must be 128, 192 or 256")
        self.nbytes = key_length / 8
        pwbytes = CTR.pad(password, (self.nbytes,))
        cipher = AES.new(pwbytes)
        self.key = cipher.encrypt(pwbytes)
        self.urandom = CTR.urandom_8b()

    def ctr(self, nonce, text):
        """
        apply CTR mode to a string (internal function, don't call externally)
        """
        res = []
        cipher = AES.new(self.key)
        for block_num, block in enumerate(CTR.blocks(text)):
            counterblock = CTR.generate_counterblock(block_num, nonce)
            ciphered = cipher.encrypt(''.join((chr(t) for t in counterblock)))
            res += (x ^ y for (x, y) in itertools.izip(CTR.ord_str(ciphered), CTR.ord_str(block)))
        return res

    def decrypt(self, text, return_nonce=False):
        """
        decrypt a string in CTR mode
        optionally returns the nonce used to encrypt the string
        """
        nonce = CTR.ord_str(text[0:8])
        dec = CTR.chr_ord(self.ctr(nonce, text[8:]))
        if return_nonce:
            return dec, nonce
        else:
            return dec

    def generate_nonce(self):
        """
        generate a random nonce - random number XOR-ed with the current datetime
        as recommended by http://www.movable-type.co.uk/scripts/aes.html
        """
        u = six.advance_iterator(self.urandom)
        n = struct.pack('hbbbbbbh', *datetime.datetime.now().timetuple()[:-1])
        return [ord(x) ^ ord(y) for (x, y) in itertools.izip(u, n)]
    
    def encrypt(self, text, nonce=None):
        """
        encrypt a string. nonce can be provided, this should only be done 
        for testing. reuse of the same nonce is insecure.
        """
        if nonce is None:
            nonce = self.generate_nonce()
        res = nonce + self.ctr(nonce, text)
        return CTR.chr_ord(res)

class DecryptionFailure(Exception):
    pass

class AESWrapper(object):
    """
    wraps AES in CTR mode, prepends HMAC to data so we verify the password is valid for an encrypted data string
    uses encrypt-then-MAC as recommended by http://www.daemonology.net/blog/2009-06-24-encrypt-then-mac.html
    """

    # changing these will break decryption of data previously encoded with this wrapper
    hmac_length = 20
    hash_mod = hashlib.sha1
    key_length = 256

    def __init__(self, password):
        self.hmac = lambda text: hmac.new(password, text, AESWrapper.hash_mod).digest()
        self.ctr = CTR(password, AESWrapper.key_length)

    def encrypt(self, text, nonce=None):
        "encrypt given string, wrap in HMAC. only specify nonce in testing, reuse of the same nonce is insecure."
        ciphered = self.ctr.encrypt(text, nonce)
        return base64.encodestring(self.hmac(ciphered)[:AESWrapper.hmac_length] + ciphered).replace('\n', '')

    def decrypt(self, text):
        "decrypt a string, verifying HMAC matches password"
        decoded = base64.decodestring(text)
        hmac_digest, ciphered_data = decoded[:AESWrapper.hmac_length], decoded[AESWrapper.hmac_length:]
        if hmac_digest != self.hmac(ciphered_data)[:AESWrapper.hmac_length]:
            raise DecryptionFailure()
        return self.ctr.decrypt(ciphered_data)
