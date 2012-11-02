import setuptools
import os
from setuptools import setup, find_packages

packages=   ['yabiadmin'] + [ 'yabiadmin.%s'%app for app in ['yabifeapp', 'yabistoreapp','yabiengine','yabi','uploader','preview','registration'] ] + [ 'yabiadmin.yabi.migrations', 'yabiadmin.yabi.migrationutils', 'yabiadmin.yabiengine.migrations' ]
                    
data_files = {}
start_dir = os.getcwd()
for package in packages:
    data_files[package] = []
    path = package.replace('.','/')
    os.chdir(path)
    for data_dir in ('templates', 'static', 'migrations', 'fixtures'):
        data_files[package].extend(
            [os.path.join(subdir,f) for (subdir, dirs, files) in os.walk(data_dir) for f in files]) 
    os.chdir(start_dir)

def main():
    setup(name='yabiadmin',
        version='0.1',
        description='Yabi Admin',
        long_description='Yabi front end and administration web interface',
        author='Centre for Comparative Genomics',
        author_email='web@ccg.murdoch.edu.au',
        #packages = find_packages(),
        packages=packages,
        package_data=data_files,
        #package_data={
            #'': [ "%s/%s"%(dirglob,fileglob)
                    #for dirglob in (["."] + [ '/'.join(['*']*num) for num in range(1,10) ])                         # yui is deeply nested
                    #for fileglob in [ '*.mako', '*.html', '*.css', '*.js', '*.png', '*.jpg', 'favicon.ico', '*.gif', 'mime.types', '*.wsgi', '*.svg' ]
                #]
        #},
        zip_safe=False,
        install_requires=all_requires('yabiadmin/base-requirements.txt','yabiadmin/requirements.txt'),
    )


#
# Functional helpers to turn requirements.txt into package names and version strings
# What is this? LISP?
#

flatten = lambda listoflists: [ inner for outer in listoflists for inner in outer ]             # flatten a list of lists

# take a list of .txt pip dependency filenames and flatten them into only the package dependency lines as a list.
# take out comments and -r's
build_requires = lambda *files: flatten(
    [
        [ 
            line.strip() for line in open(file).readlines() 
                if  line and 
                not line.startswith('#') and 
                not line.startswith('-r ')
        ]
        for file in files
    ]
)

# lines that are urls or not
urls = lambda lines: [ line for line in lines if line.startswith('http') ]
noturls = lambda lines: [ line for line in lines if not line.startswith('http') ]
filenames = lambda urls: [ url.rsplit('/',1)[-1] for url in urls ]              # munge into just package filenames

# truncate package name
basefilename = lambda filename: [ 
    item for item in 
    [ 
        filename[:-len(ext)] if filename.endswith(ext) else None 
        for ext in ['.tgz','.tar.gz'] 
    ] 
    if item is not None 
]

basefilenames = lambda filenames: flatten( [ basefilename(files) for files in filenames ] )
parts = lambda filename: filename.split('-')                                # parts of a filename
has_number = lambda string: True in [a in string for a in '0123456789']     # string has a number somewhere in it
split_point = lambda parts: [ has_number(part) for part in parts ].index(True)          # the index of the earliest part with a number in it
number_split = lambda parts: (parts[:split_point(parts)],parts[split_point(parts):])    # split a list of strings into two lists. the first part with a number becomes the list split point.
make_package_version = lambda nameparts, versionparts: ('-'.join(nameparts),'-'.join(versionparts))         # package name, version part
make_egg_versions = lambda filenames: [ make_package_version( *number_split(parts(name)) ) for name in filenames ]
egg_versions = lambda *files: [ "%s==%s"%parts for parts in make_egg_versions(basefilenames(filenames(urls(build_requires(*files))))) ]
pypy_eggs = lambda *files: noturls(build_requires(*files))
all_requires = lambda *files: egg_versions(*files)+pypy_eggs(*files)

if __name__ == "__main__":
    main()
