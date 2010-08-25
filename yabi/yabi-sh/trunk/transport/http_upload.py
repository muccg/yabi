#!/usr/bin/env python

import httplib
import mimetypes
import os 
import email
import sys
import zipfile
import StringIO
from stat import *

# This has been copied from yabife into Transport
# encode_multipart_form has been changed, to return a FilelikeBody instead of
# streaming
# Methods: post_multipart and encode_content_length removed 

# TODO probably most of this can go, and the rest could be added to PostRequest

def encode_multipart_make_boundary():
	return '----------ThIs_Is_tHe_bouNdaRY_$'

def encode_multipart_content_type():
	return 'multipart/form-data; boundary=%s' % encode_multipart_make_boundary()

CHUNKSIZE=8192

def encode_multipart_form(fields, files):
	"""
	fields is a sequence of (name, value) elements for regular form fields.
	files is a sequence of (name, filename, value) elements for data to be uploaded as files
	Return (content_type, body) ready for httplib.HTTP instance
	"""
    body = FilelikeBody()

	BOUNDARY = encode_multipart_make_boundary()
	CRLF = '\r\n'
	L = []
	for (key, value) in fields:
		body.add_string('--' + BOUNDARY + CRLF)
		body.add_string('Content-Disposition: form-data; name="%s"' % key + CRLF)
		body.add_string(CRLF)
		body.add_string(value)
		body.add_string(CRLF)
	for (key, filename, path) in files:
		body.add_string('--' + BOUNDARY + CRLF)
		body.add_string('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename) + CRLF)
		body.add_string('Content-Type: %s' % get_content_type(filename) + CRLF)
		body.add_string(CRLF)
                body.add_file(path)
                #if type(data)==file:
                #    while True:
                #        dat=data.read(CHUNKSIZE)
                #        if len(dat)==0:
                #                break
                #        stream.send(dat)
                #else:
                #    stream.send(data)
		
		body.add_string(CRLF)
	body.add_string('--' + BOUNDARY + '--' + CRLF)
	body.add_string(CRLF)

	return body

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

		
