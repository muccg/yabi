#/usr/bin/env python

from setuptools import setup, find_packages

execfile('yabishell/version.py')

setup(name='yabish',
     version = __version__,
     description = 'Command line interface for YABI.',
     author = 'Tamas Szabo',
     author_email = 'tszabo AT ccg.murdoch.edu.au',
     url = 'http://ccg.murdoch.edu.au',
     packages = find_packages(),

     package_data = {
        'help': ['*'],
     },
     scripts = ['yabish'],
     install_requires = ['argparse', 'yaphc'],
     dependency_links = [
        "http://code.google.com/p/yaphc/downloads/list",
     ]
)
