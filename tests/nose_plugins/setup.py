import sys
try:
    import ez_setup
    ez_setup.use_setuptools()
except ImportError:
    pass
from setuptools import setup

setup(
    name='Setup Django',
    version='0.1',
    author='Tamas Szabo',
    author_email = 'tszabo@ccg.murdoch.edu.au',
    description = 'Setup Django before running tests',
    py_modules = ['setup_django'],
    entry_points = {
        'nose.plugins': [
            'setup_django = setup_django:SetupDjango'
            ]
        }

    )
