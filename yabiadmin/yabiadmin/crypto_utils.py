# -*- coding: utf-8 -*-
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
# -*- coding: utf-8 -*-
import aes_ctr
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
annotate = lambda tag,ciphertext: "$%s$%s$"%(tag,ciphertext)

#
# join a split string together and de CR LF it
#
joiner = lambda data: "".join("".join(data.split("\n")).split("\r"))


#
# notify callers of failure to decrypt if validity is being checked (not just blind decrypt)
#
class DecryptException(Exception): pass

class LegacyAESWrapper(object):
    """insecure as it uses AES in fixed block mode. do not use (only kept for compatibility reasons, and only for decryption)"""

    #
    # this is a chunking lambda generator
    #
    chunkify = lambda v, l: (v[i*l:(i+1)*l] for i in range(int(math.ceil(len(v)/float(l)))))

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
        for chunk in LegacyAESWrapper.chunkify(data,16):
            output += aes.decrypt(chunk)
            
        # depad the plaintext
        while output.endswith('\0'):
            output = output[:-1]
        
        if contains_binary(output):
            raise DecryptException, "AES decrypt failed. Decrypted data contains binary"
        
        return output

    @classmethod
    def aes_dec_hex(cls, ciphertext, key):
        """decrypt a base64 encoded encrypted block"""
        try:
            ciphertext = binascii.unhexlify( ciphertext )
        except TypeError, te:
            # the credential binary block cannot be decoded
            raise DecryptException("Credential does not seem to contain binary encrypted data")
        return aes_dec(ciphertext, key)

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

@nounicode
def aes_dec_hex(data, key):
    if data == '':
        return ''
    tag, ciphertext = deannotate(joiner(data))
    if ciphertext == '':
        return ''
    if tag == AESHEXTAG or tag == AESHEXTAG:
        return LegacyAESWrapper.aes_dec_hex(data, key)
    wrapper = aes_ctr.AESWrapper(key)
    try:
        return wrapper.decrypt(ciphertext)
    except aes_ctr.DecryptionFailure:
        raise DecryptException("Invalid key for AES-CTR encrypted data")

@nounicode
def aes_enc_hex(data, key):
    "returns base64 encoded data, annotated appropriately and encrypted with `key`"
    # don't encrypt empty string
    if data == '':
        return ''
    wrapper = aes_ctr.AESWrapper(key)
    encrypted = wrapper.encrypt(data)
    return annotate(AESCTRTAG, encrypted)
#
# this deannotates the string
#
def deannotate( string ):
    try:
        dummy,tag,cipher,dummy2 = string.split('$')
    except ValueError, ve:
        raise DecryptException("Invalid input string to deannotator")
    
    if dummy or dummy2:
        raise DecryptException("Invalid input string to deannotator")
    
    return tag, cipher

def looks_like_annotated_block(data):
    """Looks for the $tag$ciphertext$ format.
    Returns the tag if it looks like an annotated cipherblock
    returns False if its improperly formatted
    """

    if data.startswith('$') and data.endswith('$') and data.count('$') == 3:
        try:
            tag, ciphertext = deannotate(joiner(data))
            return True
        except DecryptException:
            return False
    return False

