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

setup(name='yabiadmin',
    version='6.15.2',
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
    install_requires=[
        'Django==1.3.7',
        'ccg-webservices==0.1.2',
        'ccg-registration==0.8-alpha-1',
        'ccg-makoloader==0.2.4',
        'ccg-introspect==0.1.2',
        'ccg-extras==0.1.5',
        'ccg-auth==0.3.2',
        'SQLAlchemy==0.7.1',
        'celery==3.0.19',
        'python-dateutil>=1.5,<2.0',
        'anyjson==0.3.3',
        'kombu>=2.1.8,<2.2.0',
        #'carrot==0.10.7',
        'amqplib==1.0.2',
        'django-celery==3.0.17',
        'django-picklefield==0.2.0',
        'django-templatetag-sugar==0.1',
        'ordereddict==1.1',
        'pygooglechart==0.2.1',
        'pyparsing==1.5.6',
        'python-memcached==1.48',
        'Mako==0.5.0',
        'South==0.7.6',
        'django-extensions==0.7.1',
        'pycrypto>=2.6',
        'psutil',
        'yaphc==0.1.5',
        'BeautifulSoup==3.2.0',
        'cssutils==0.9.7',
        'httplib2==0.7.5',
        'djamboloader==0.1.2',
        'MarkupSafe==0.15',
        'wsgiref==0.1.2',
        'requests==1.2.0',
        'gunicorn',
        'django-nose',
        'nose==1.2.1'
    ],

    dependency_links = [
          'https://pypi.python.org/packages/source/k/kombu/kombu-2.1.8.tar.gz',
          'http://ccg-django-extras.googlecode.com/files/ccg-webservices-0.1.2.tar.gz',
          'http://ccg-django-extras.googlecode.com/files/ccg-registration-0.8-alpha-1.tar.gz',
          'http://ccg-django-extras.googlecode.com/files/ccg-makoloader-0.2.4.tar.gz',
          'http://ccg-django-extras.googlecode.com/files/ccg-introspect-0.1.2.tar.gz',
          'http://ccg-django-extras.googlecode.com/files/ccg-extras-0.1.5.tar.gz',
          'http://ccg-django-extras.googlecode.com/files/ccg-auth-0.3.2.tar.gz',
          'http://yaphc.googlecode.com/files/yaphc-0.1.5.tgz',
          'http://github.com/downloads/muccg/djamboloader/djamboloader-0.1.2.tar.gz'
    ]
)
