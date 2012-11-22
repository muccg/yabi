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
    version='0.1',
    description='Yabi Admin',
    long_description='Yabi front end and administration web interface',
    author='Centre for Comparative Genomics',
    author_email='web@ccg.murdoch.edu.au',
    #packages = find_packages(),
    packages=packages,
    #package_data=data_files,
    package_data={
        '': [ "%s/%s"%(dirglob,fileglob)
            for dirglob in (["."] + [ '/'.join(['*']*num) for num in range(1,10) ])                         # yui is deeply nested
            for fileglob in [ '*.mako', '*.html', '*.css', '*.js', '*.png', '*.jpg', 'favicon.ico', '*.gif', 'mime.types', '*.wsgi', '*.svg' ]
        ]
    },
    zip_safe=False,
    install_requires=[
        'Django==1.3.2',
        'ccg-webservices==0.1.2',
        'ccg-registration==0.8-alpha-1',
        'ccg-makoloader==0.2.4',
        'ccg-introspect==0.1.2',
        'ccg-extras==0.1.5',
        'ccg-auth==0.3.2',
        'SQLAlchemy==0.7.1',
        'amqplib==1.0.2',
        'anyjson==0.3.3',
        'carrot==0.10.7',
        'celery==2.5.1',
        'django-celery==2.5.1',
        # Use a pacthed version of django-kombu that fixes a known bug
        #django-kombu==0.9.4
        ##'http://yabi.googlecode.com/files/django-kombu-0.9.4.1.tar.gz',
        'django-kombu==0.9.4.1',
        'django-picklefield==0.2.0',
        'django-templatetag-sugar==0.1',
        'kombu==2.1.1',
        'ordereddict==1.1',
        'pygooglechart==0.2.1',
        'pyparsing==1.5.6',
        'python-dateutil==1.5',
        'virtualenv==1.6.4',
        'wsgiref==0.1.2',
        'python-memcached==1.48',
        'Mako==0.5.0',
        'South==0.7.6',
        'django-extensions==0.7.1',
        'pycrypto>=1.9',
        'psutil',
        'nose',
        ##'http://yaphc.googlecode.com/files/yaphc-0.1.5.tgz',
        'yaphc==0.1.5',
        'BeautifulSoup==3.2.0',
        'cssutils==0.9.7',
        'httplib2==0.7.5',
        ##'https://github.com/downloads/sztamas/djamboloader/djamboloader-0.1.2.tar.gz',
        'djamboloader==0.1.2',
        'MarkupSafe==0.15',
        'wsgiref==0.1.2',
    ],
)
