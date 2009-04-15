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

