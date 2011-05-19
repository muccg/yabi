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
"""A suite of useful parsers for us"""

import urlparse
import re
re_url_schema = re.compile(r'\w+')

DEBUG = False

def parse_url(uri):
    """Parse a url via the inbuilt urlparse. But this is slightly different
    as it can handle non-standard schemas. returns the schema and then the
    tuple from urlparse"""
    scheme, rest = uri.split(":",1)
    assert re_url_schema.match(scheme)
    return scheme, urlparse.urlparse(rest)



##
## Parse POSIX ls style listings
##

def parse_ls_generate_items(lines):
    """A generator that is passed lines of a ls output, and generates an item for each line"""
    for line in lines:
        parts=line.split(None,8)
        if line.startswith('/') and line.endswith(':'):                             # only absolute path listings are supported (start with '/', not '.')
            # header
            yield (line[:-1],)
        elif len(parts)==2:
            assert parts[0]=="total"
        elif len(parts)==9:
            # check for symlink
            nodetype='f'
            link = False
            if parts[0][0]=='l':
                #its a symlink
                link = True
                parts[8],destination=parts[8].rsplit(' -> ',1)                               # truncate linked to part
                if destination[-1]=='/':
                    nodetype='d'
            if parts[0][0]=='d':
                nodetype='d'
                parts[8]=parts[8][:-1]
            #body
            filename, filesize, date = (parts[8], int(parts[4]), "%s %s %s"%tuple(parts[5:8]))
            if filename[-1] in "*@|":
                # filename ends in a "*@|"
                yield (nodetype,filename[:-1], filesize, date, link)
            else:
                yield (nodetype,filename, filesize, date, link)
        else:
            pass                #ignore line

def parse_ls_directories(data, culldots=True):
    """generator that takes a whole bunch of listings (possibly recursive) and generates the item set for each one"""
    filelisting = None
    dirlisting = None
    presentdir = None
    for line in parse_ls_generate_items(data.split("\n")):
        if len(line)==1:
            if presentdir:
                assert filelisting!=None
                assert dirlisting!=None
                # break off this directory.
                yield presentdir,filelisting,dirlisting
            presentdir=line[0]
            filelisting=[]                  # space to store listing
            dirlisting=[]
        else:
            assert len(line)==5
            if filelisting==None and dirlisting==None:
                # we are probably a non recursive listing. Set us up for a single dir
                assert presentdir==None
                filelisting, dirlisting = [], []

            if line[0][0]=="d":
                if not culldots or (line[1][:-1]!="." and line[1][:-1]!=".."):
                    dirlisting.append(line[1:])                
            else:
                filelisting.append(line[1:])
    
    # send the last one
    if None not in [filelisting,dirlisting]:
        yield presentdir, filelisting, dirlisting
            
def parse_ls(data, culldots=True):
    """Upper level ls parser."""
    output = {}
    for name,filelisting,dirlisting in parse_ls_directories(data, culldots):
        if DEBUG:
            print "NAME",name
            print "FILELISTING",filelisting
            print "DIRLISTING",dirlisting
        if name and not name.endswith('/'):
            name = name+"/"                 # add a slash to directories missing it
        output[name] = {
            "files":filelisting,
            "directories":dirlisting
        }

    # deal with totally empty directory when -a flag is absent
    if not output:
        output[None] = {
            "files":[],
            "directories":[]
        }

    return output