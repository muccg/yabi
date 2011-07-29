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
Import Tools and ToolRslInfo objects from XML and RSL files into the DB.

Invoke import_tools_from(dirname) to import from all .xml files or 
import_rsls_from(dirname) to import from all .rsl files in the given
directory.
To import a single file use the xmlimport.tool or xmlimport.rsl module.
Django's ORM is used to save the entities to the DB, so the easiest
way to run the import is from a Django shell (ie. ./manage.py shell or
./manage.py shell_plus if you have Django extensions installed).
"""
import glob, os

def import_tools_from(dirname, process_from=0):
    import xmlimport.tool
    import_all(dirname, "xml", xmlimport.tool.import_tool, process_from) 

def import_rsls_from(dirname, process_from=0):
    import xmlimport.rsl
    import_all(dirname, "rsl", xmlimport.rsl.import_rsl, process_from) 

# Implementation

def import_all(dirname, ext, file_importer, process_from=0):
    assert os.path.isdir(dirname), "%s not a directory" % dirname
    all_files = glob.glob("%s/*.%s" % (dirname, ext))
    count = len(all_files)
    print "Importing from %d files in directory %s" % (count, dirname)
    for i,file in enumerate(all_files):
        if i < process_from: 
            continue
        max_digits = len(str(count))
        print "  [%*d of %*d] Importing from file %s" % (
                 max_digits, i+1, max_digits, count, file)
        file_importer(file)
    print "Done."

