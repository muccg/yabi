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
import math
import binascii

#
# this is a chunking lambda generator
#
chunkify = lambda v, l: (v[i*l:(i+1)*l] for i in range(int(math.ceil(len(v)/float(l)))))

#
# this annotates a string with the 
#
annotate = lambda tag,ciphertext: "$%s$%s$"%(tag,ciphertext)

#
# join a split string together and de CR LF it
#
joiner = lambda data: "".join("".join(data.split("\n")).split("\r"))

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

# known tags
AESHEXTAG = 'AES'
AESTEMP = "AESTEMP"                     # tag for temporary decryption of aes for protection in memecache and on DB prior to user key encryption


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

def aes_enc_hex(data,key,linelength=None, tag=AESHEXTAG):
    """DO an aes encrypt, but return data as base64 encoded"""
    enc = aes_enc(data,key)
    encoded = annotate(tag,binascii.hexlify(enc))
    
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

def aes_dec_hex(data,key, check=False, tag=AESHEXTAG):
    """decrypt a base64 encoded encrypted block"""
    tag, ciphertext = deannotate(joiner(data))
       
    if tag != tag:
        raise DecryptException("Calling aes hex decrypt on non valid text. tag seems to be %s and it should be %s"%(tag,AESHEXTAG))
    
    try:
        ciphertext = binascii.unhexlify( ciphertext )
    except TypeError, te:
        # the credential binary block cannot be decoded
        raise DecryptException("Credential does not seem to contain binary encrypted data")
    return aes_dec(ciphertext, key, check)
    
def contains_binary(data):
    """return true if string 'data' contains any binary"""
    # for now just see if there are any unprintable characters in the string
    import string
    return False in [X in string.printable for X in data]
    
def looks_like_hex_ciphertext(data):
    """returns true if the string 'data' looks like it is 
    actually cipher text. Of course we can not be 100% sure... but it makes a best guess attempt
    """
    CIPHER_CHARS = '0123456789ABCDEFabcdef\n\r\t '
    for char in data:
        if char not in CIPHER_CHARS:
            return False
            
    return True
    
def looks_like_annotated_block(data):
    """Looks for the $tag$ciphertext$ format.
    Returns the tag if it looks like an annotated cipherblock
    returns False if its improperly formatted
    """
    if data.count('$')!=3:
        return False
    
    onelinedata = joiner(data)
    
    try:
        dummy,tag,ciphertext,dummy2 = onelinedata.split('$')
    except ValueError, ve:
        return False
        
    if dummy or dummy2:
        return False
    
    if not looks_like_hex_ciphertext(ciphertext):
        return False
        
    return tag
