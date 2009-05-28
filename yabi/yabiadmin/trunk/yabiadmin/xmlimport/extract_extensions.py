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

