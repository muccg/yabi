import setuptools
import os
from setuptools import setup, find_packages

setup(name='yabibe',
    version='6.10.1',
    description='Yabi Backend',
    long_description='Yabi back end service',
    author='Centre for Comparative Genomics',
    author_email='web@ccg.murdoch.edu.au',
    packages=['yabibe']+[
        'yabibe.%s'%x for x in "conf ex FifoPool fs TaskManager utils log".split()
    ]+'yabibe.ex.connector yabibe.fs.connector yabibe.utils.protocol yabibe.utils.protocol.globus yabibe.utils.protocol.s3 yabibe.utils.protocol.ssh'.split(),
    package_data={'yabibe': ['conf/*.conf']},
    zip_safe=False,
    scripts=['yabibe/scripts/yabibe'],
    install_requires=[
        'pyOpenSSL==0.12',
        'pycrypto==2.3',
        'paramiko==1.7.7.1_fifopatch',
        'Mako==0.4.2',
        'MarkupSafe==0.9.3',
        'Twisted==12.0.0',
        ##'http://twisted-web2.googlecode.com/files/TwistedWeb2-10.2.0.tar.gz',
        'TwistedWeb2==10.2.0',
        'setproctitle==1.1.2',
        'wsgiref==0.1.2',
        'zope.interface==3.6.3',
        'gevent',
        'greenlet==0.3.3',
        'psutil',
        'boto==2.3.0',
        'requests==0.11.2',
    ],
)
