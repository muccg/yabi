#/usr/bin/env python

from distutils.core import setup

setup(name='yabish',
     version='0.1.0',
     description='Command line interface for YABI.',
     author='Tamas Szabo',
     author_email='tszabo AT ccg.murdoch.edu.au',
     url='http://ccg.murdoch.edu.au',
     packages=['yabishell'],
     scripts=['yabish']
)
