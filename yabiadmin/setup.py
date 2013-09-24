import setuptools
import os
from setuptools import setup, find_packages

packages=   ['yabiadmin'] + [ 'yabiadmin.%s'%app for app in ['yabifeapp', 'yabistoreapp','yabiengine','yabi','uploader','preview','registration', 'backend'] ] + [ 'yabiadmin.yabi.migrations', 'yabiadmin.yabi.migrationutils', 'yabiadmin.yabiengine.migrations' ]
                    
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

install_requires = [
        'Django==1.5.4',
         # pip > 1.4 doesn't pick up pytz, because of non-standard version number
         # Bug is still under discussion: https://bugs.launchpad.net/pytz/+bug/1204837
        'pytz>=2013b', 
        'ccg-webservices==0.1.2',
        'ccg-registration==0.8-alpha-1',
        'ccg-makoloader==0.2.6',
        'ccg-introspect==0.1.2',
        'ccg-extras==0.1.5',
        'ccg-auth==0.3.3',
        'anyjson==0.3.3',
        'SQLAlchemy==0.7.10',
        'celery==3.0.22',
        'amqplib==1.0.2',
        'django-celery==3.0.17',
        'kombu==2.5.13',
        'billiard==2.7.3.32',
        'flower==0.5.1',
        'django-templatetag-sugar==0.1',
        'ordereddict==1.1',
        'python-memcached==1.53',
        'Mako==0.5.0',
        'South==0.7.6',
        'django-extensions==1.1.1',
        'pycrypto>=2.6',
        'yaphc==0.1.5',
        'beautifulsoup4==4.2.1',
        'lxml==3.2.1',
        'cssutils==0.9.10',
        'httplib2==0.8',
        'djamboloader==0.1.2',
        'paramiko==1.10.1',
        'mockito==0.5.1',
        'boto==2.13.3',
	'python-dateutil==2.1',
    ]

importlib_available = True
try:
    import importlib
except ImportError:
    # This will likely to happen before Python 2.7
    importlib_available = False

if not importlib_available:
    install_requires.append('importlib==1.0.1')

setup(name='yabiadmin',
    version='7.0.1',
    description='Yabi Admin',
    long_description='Yabi front end and administration web interface',
    author='Centre for Comparative Genomics',
    author_email='web@ccg.murdoch.edu.au',
    packages=packages,
    package_data={
        '': [ "%s/%s"%(dirglob,fileglob)
            for dirglob in (["."] + [ '/'.join(['*']*num) for num in range(1,15) ])                         # yui is deeply nested
            for fileglob in [ '*.mako', '*.html', '*.css', '*.js', '*.png', '*.jpg', 'favicon.ico', '*.gif', 'mime.types', '*.wsgi', '*.svg' ]
        ]
    },
    zip_safe=False,
    install_requires=install_requires,
    dependency_links = [
          'http://ccg-django-extras.googlecode.com/files/ccg-webservices-0.1.2.tar.gz',
          'http://ccg-django-extras.googlecode.com/files/ccg-registration-0.8-alpha-1.tar.gz',
          'http://ccg-django-extras.googlecode.com/files/ccg-introspect-0.1.2.tar.gz',
          'http://ccg-django-extras.googlecode.com/files/ccg-extras-0.1.5.tar.gz',
          'http://ccg-django-extras.googlecode.com/files/ccg-auth-0.3.3.tar.gz',
          'http://yaphc.googlecode.com/files/yaphc-0.1.5.tgz',
          'http://github.com/downloads/muccg/djamboloader/djamboloader-0.1.2.tar.gz',
          'http://repo.ccgapps.com.au',
    ]
)
