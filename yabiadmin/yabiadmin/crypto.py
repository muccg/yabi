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
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
import base64
import math
import binascii

#
# this is a chunking lambda generator
#
chunkify = lambda v, l: (v[i*l:(i+1)*l] for i in range(int(math.ceil(len(v)/float(l)))))

#
# Some exceptions to notify callers of failure to decrypt if validity is being checked (not just blind decrypt)
#
class DecryptException(Exception): pass

def aes_enc(data,key):
    if not data:
        return data                         # encrypt nothing. get nothing.
        
    assert data[-1]!='\0', "encrypt/decrypt implementation uses null padding and cant reliably decrypt a binary string that ends in \\0"
    #
    # Our AES Cipher
    #
    key_hash = SHA256.new(key)
    aes = AES.new(key_hash.digest())
    
    # pad to nearest 16.
    data += '\0'*(16-(len(data)%16))
    
    # take chunks of 16
    output = ""
    for chunk in chunkify(data,16):
        output += aes.encrypt(chunk)
        
    return output
    
def aes_enc_base64(data,key,linelength=None):
    """DO an aes encrypt, but return data as base64 encoded"""
    enc = aes_enc(data,key)
    encoded = base64.encodestring(enc)
    
    if linelength:
        encoded = "\n".join(chunkify(encoded,linelength))
    
    return encoded

def aes_enc_hex(data,key,linelength=None):
    """DO an aes encrypt, but return data as base64 encoded"""
    enc = aes_enc(data,key)
    encoded = binascii.hexlify(enc)
    
    if linelength:
        encoded = "\n".join(chunkify(encoded,linelength))
    
    return encoded
      
def aes_dec(data,key, check=False):
    if not data:
        return data                     # decrypt nothing, get nothing
    
    key_hash = SHA256.new(key)
    aes = AES.new(key_hash.digest())
    
    # take chunks of 16
    output = ""
    for chunk in chunkify(data,16):
        output += aes.decrypt(chunk)
        
    # depad the plaintext
    while output.endswith('\0'):
        output = output[:-1]
    
    if contains_binary(output):
        raise DecryptException, "AES decrypt failed. Decrypted data contains binary"
    
    return output
    
def aes_dec_base64(data,key, check=False):
    """decrypt a base64 encoded encrypted block"""
    try:
        ciphertext = base64.decodestring("".join(data.split("\n")))
    except TypeError, te:
        # the credential binary block cannot be decoded
        raise DecryptException("Credential does not seem to contain binary encrypted data")
    return aes_dec(ciphertext, key, check)

def aes_dec_hex(data,key, check=False):
    """decrypt a base64 encoded encrypted block"""
    try:
        ciphertext = binascii.unhexlify("".join("".join(data.split("\n")).split("\r")))
    except TypeError, te:
        # the credential binary block cannot be decoded
        raise DecryptException("Credential does not seem to contain binary encrypted data")
    return aes_dec(ciphertext, key, check)
    
def contains_binary(data):
    """return true if string 'data' contains any binary"""
    # for now just see if there are any unprintable characters in the string
    import string
    return False in [X in string.printable for X in data]