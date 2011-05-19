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
"""
Extract all the file extensions used in baat XML files.

Invoke extract_all(dirname) to use it on all XML files in the given directory,
or extract(filename) to use it on a single XML file.
The output will be the tool name(s) with their associated input filetype 
extensions.
"""
import glob, os, sys
from xml.dom.minidom import parse

def extract_all(dirname):
    for f in glob.glob(dirname + '/*.xml'):
        extract(f)

def extract(filename):
    doc = parse(filename)
    job_element_container = doc.getElementsByTagName('job')
    assert(job_element_container, 
           "Couldn't find required element 'job' in the XML file %s." % filename)
    tool_name = os.path.splitext(os.path.basename(filename))[0]
    extensions = extract_input_extensions(job_element_container[0])
    print (tool_name, extensions)

def extract_input_extensions(job_element):
    extensions = []
    file_types_container = job_element.getElementsByTagName('inputFiletypes')
    if file_types_container:
        for extension in file_types_container[0].getElementsByTagName('extension'):
            extensions.append(extension.firstChild.data)
    return extensions   

if __name__ == '__main__':
    extract_all(sys.argv[1])

