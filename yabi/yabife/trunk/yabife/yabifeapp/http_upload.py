#!/usr/bin/env python
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

import httplib
import mimetypes
import os 
import email
import sys
import zipfile
import StringIO
from stat import *

def post_multipart(host, selector, fields, files):
	"""
	Post fields and files to an http host as multipart/form-data.
	fields is a sequence of (name, value) elements for regular form fields.
	files is a sequence of (name, filename, value) elements for data to be uploaded as files
	Return the server's response page.
	"""
	#print "post_multipart"
	content_type=encode_multipart_content_type()
	h = httplib.HTTPConnection(host)
	h.putrequest('POST', selector)
	h.putheader('content-type', content_type)
	h.putheader('content-length', str(encode_content_length(fields, files)))
	h.endheaders()
	encode_multipart_formdata(h,fields, files)
	#h.send(body)
	#errcode, errmsg, headers = h.getreply()
	return h
	#return h.file.read()


def encode_multipart_make_boundary():
	return '----------ThIs_Is_tHe_bouNdaRY_$'

def encode_multipart_content_type():
	return 'multipart/form-data; boundary=%s' % encode_multipart_make_boundary()

CHUNKSIZE=8192

def encode_multipart_formdata(stream,fields, files):
	"""
	fields is a sequence of (name, value) elements for regular form fields.
	files is a sequence of (name, filename, value) elements for data to be uploaded as files
	Return (content_type, body) ready for httplib.HTTP instance
	"""
	#print "encode_multipart_formdata(",stream,",",fields,",",files,")"
	BOUNDARY = encode_multipart_make_boundary()
	CRLF = '\r\n'
	L = []
	for (key, value) in fields:
		stream.send('--' + BOUNDARY + CRLF)
		stream.send('Content-Disposition: form-data; name="%s"' % key + CRLF)
		stream.send(CRLF)
		stream.send(value)
		stream.send(CRLF)
	for (key, filename, data) in files:
		stream.send('--' + BOUNDARY + CRLF)
		stream.send('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename) + CRLF)
		stream.send('Content-Type: %s' % get_content_type(filename) + CRLF)
		stream.send(CRLF)
		
                if type(data)==file:
                    while True:
                        dat=data.read(CHUNKSIZE)
                        if len(dat)==0:
                                break
                        stream.send(dat)
                else:
                    stream.send(data)
		
		stream.send(CRLF)
	stream.send('--' + BOUNDARY + '--' + CRLF)
	stream.send(CRLF)
	return
	
def encode_content_length(fields, files):
	#print "encode_content_length(",fields,",",files,")"
	BOUNDARY = encode_multipart_make_boundary()
	CRLF = '\r\n'
	length=0
	for (key, value) in fields:
		length+=len('--' + BOUNDARY + CRLF)
		length+=len('Content-Disposition: form-data; name="%s"' % key + CRLF)
		length+=len(CRLF)
		length+=len(value)
		length+=len(CRLF)
	for (key, filename, data) in files:
		length+=len('--' + BOUNDARY + CRLF)
		length+=len('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename) + CRLF)
		length+=len('Content-Type: %s' % get_content_type(filename) + CRLF)
		length+=len(CRLF)
		if type(data)==file:
                    length+=os.stat(data.name)[ST_SIZE]
                else:
                    length+=len(data)
		length+=len(CRLF)
	length+=len('--' + BOUNDARY + '--' + CRLF)
	length+=len(CRLF)
	return length

def get_content_type(filename):
	return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

def extract_zip( filename, dir ):
	print "unzipping",filename
	zf = zipfile.ZipFile( filename )
	namelist = zf.namelist()
	dirlist = filter( lambda x: x.endswith( '/' ), namelist )
	filelist = filter( lambda x: not x.endswith( '/' ), namelist )
	# make base
	pushd = os.getcwd()
	if not os.path.isdir( dir ):
		os.mkdir( dir )
	os.chdir( dir )
	# create directory structure
	dirlist.sort()
	for dirs in dirlist:
		dirs = dirs.split( '/' )
		prefix = ''
		for dir in dirs:
			dirname = os.path.join( prefix, dir )
			if dir and not os.path.isdir( dirname ):
				os.mkdir( dirname )
			prefix = dirname
	# extract files
	for fn in filelist:
		try:
			out = open( fn, 'wb' )
			buffer = StringIO.StringIO( zf.read( fn ))
			buflen = 2 ** 20
			datum = buffer.read( buflen )
			while datum:
				out.write( datum )
				datum = buffer.read( buflen )
			out.close()
		finally:
			print fn
	os.chdir( pushd )
	
def output(s, outfile = sys.stdout):
	outfile.write(s)

def decode_part(msg):
	"Decode one part of the message"
	
	decode_headers(msg)
	encoding = msg["Content-Transfer-Encoding"]
	
	if encoding in (None, '', '7bit', '8bit', 'binary'):
		outstring = str(msg.get_payload())
	else: # Decode from transfer ecoding to text or binary form
		outstring = str(msg.get_payload(decode=1))
		set_header(msg, "Content-Transfer-Encoding", "8bit")
		msg["X-MIME-Autoconverted"] = "from %s to 8bit by %s id %s" % (encoding, host_name, sys.arv[0])
	
	# Test all mask lists and find what to do with this content type
	masks = []
	ctype = msg.get_content_type()
	if ctype:
		masks.append(ctype)
	mtype = msg.get_content_maintype()
	if mtype:
		masks.append(mtype + '/*')
	masks.append('*/*')
	
	for content_type in masks:
		if content_type in GlobalOptions.totext_mask:
			totext(msg, outstring)
			return
		elif content_type in GlobalOptions.binary_mask:
			output_headers(msg)
			output(outstring)
			return
		elif content_type in GlobalOptions.ignore_mask:
			output_headers(msg)
			output("\nMessage body of type `%s' skipped.\n" % content_type)
			return
		elif content_type in GlobalOptions.error_mask:
			raise ValueError, "content type `%s' prohibited" % content_type
	
	# Neither content type nor masks were listed - decode by default
	totext(msg, outstring)
	

def extract_multipart(filename, dir):
	"""TODO: check this works and work on delegate support"""
	msg = email.message_from_file(infile)
	boundary = msg.get_boundary()
	
	if msg.is_multipart():
		for subpart in msg.get_payload():
			output("\n--%s\n" % boundary)
			decode_part(subpart)
	
		output("\n--%s--\n" % boundary)
	
		if msg.epilogue:
			output(msg.epilogue)
	
	else:
		if msg.has_key("Content-Type"): # Simple one-part message - decode it
			decode_part(msg)
	
		else: # Not a message, just text - copy it literally
			output(str(msg))

		
