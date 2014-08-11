import os
from setuptools import setup

packages = ['yabiadmin'] + ['yabiadmin.%s' % app for app in ['yabifeapp', 'yabiengine', 'yabi', 'preview', 'backend']] + ['yabiadmin.yabi.migrations', 'yabiadmin.yabi.migrationutils', 'yabiadmin.yabiengine.migrations', 'yabiadmin.yabi.templatetags', 'yabiadmin.yabifeapp.management', 'yabiadmin.yabifeapp.management.commands']

install_requires = [
    'Django==1.5.4',
    # pip > 1.4 doesn't pick up pytz, because of non-standard version number
    # Bug is still under discussion: https://bugs.launchpad.net/pytz/+bug/1204837
    'pytz>=2013b',
    'ccg-webservices==0.1.2',
    'ccg-introspect==0.1.2',
    'ccg-django-utils==0.2.1',
    'ccg-auth==0.3.3',
    'anyjson==0.3.3',
    'celery==3.1.12',
    'amqp==1.4.5',
    'amqplib==1.0.2',
    'kombu==3.0.19',
    'billiard==3.3.0.17',
    'django-templatetag-sugar==0.1',
    'ordereddict==1.1',
    'python-memcached>=1.53,<2.0',
    'Mako==0.5.0',
    'South==0.7.6',
    'django-extensions>=1.2.0,<1.2.0',
    'beautifulsoup4>=4.3.2,<4.4.0',
    'cssutils>=0.9.10,<0.10.0',
    'httplib2>=0.8,<0.9',
    'djamboloader==0.1.2',
    'paramiko==1.12.1',
    'boto==2.25',
    'python-swiftclient==2.0.2',
    'python-keystoneclient==0.6.0',
    'python-dateutil>=2.1,<3.0',
    'yaphc==0.1.5',
    'six>=1.5,<1.6',
    'flower>=0.7.0',
    'apache-libcloud==0.15.1',
    'ccg-libcloud-drivers==0.0.1',
]

# Compiled python modules which are usually provided by system packages
install_requires_compiled = [
    'SQLAlchemy>=0.7.10,<0.8.0',
    'lxml>=3.3.0,<3.4.0',
    'pycrypto==2.6.1',  # version locked as a 2.7a1 appeared in pypi
]

dev_requires = [
    'flake8>=2.0,<2.1',
    'closure-linter==2.3.13',
    'Werkzeug',
    'gunicorn',
]

tests_require = [
    'requests==1.2.0',
    'django-nose',
    'nose==1.3.1',
    'mockito>=0.5.0,<0.6.0',
    'sniffer==0.3.2',
    'pyinotify==0.9.4',
    'model_mommy==1.2',
]

postgresql_requires = [
    'psycopg2>=2.5.0,<2.6.0',
]

mysql_requires = [
    'MySQL-python>=1.2.0,<1.3.0',
]

dependency_links = [
    'https://bitbucket.org/ccgmurdoch/ccg-django-utils/downloads/ccg-django-utils-0.2.1.tar.gz',
    'https://bitbucket.org/ccgmurdoch/ccg-django-extras/downloads/ccg-webservices-0.1.2.tar.gz',
    'https://bitbucket.org/ccgmurdoch/ccg-django-extras/downloads/ccg-introspect-0.1.2.tar.gz',
    'https://bitbucket.org/ccgmurdoch/ccg-django-extras/downloads/ccg-auth-0.3.3.tar.gz',
    'https://yaphc.googlecode.com/files/yaphc-0.1.5.tgz',
    'https://bitbucket.org/ccgmurdoch/libcloud-drivers/downloads/ccg-libcloud-drivers-0.0.1.tar.gz',

    'https://github.com/downloads/muccg/djamboloader/djamboloader-0.1.2.tar.gz',
    # Temporary fix
    # 'http://repo.ccgapps.com.au/djamboloader-0.1.2.tar.gz',
]

importlib_available = True
try:
    import importlib
except ImportError:
    # This will likely to happen before Python 2.7
    importlib_available = False

if not importlib_available:
    install_requires.append('importlib>=1.0.1,<1.1.0')

setup(name='yabiadmin',
      version='8.0.0',
      description='Yabi Admin',
      long_description='Yabi front end and administration web interface',
      author='Centre for Comparative Genomics',
      author_email='yabi@ccg.murdoch.edu.au',
      packages=packages,
      package_data={
          '': ["%s/%s" % (dirglob, fileglob)
              for dirglob in (["."] + ['/'.join(['*'] * num) for num in range(1, 15)])                         # yui is deeply nested
              for fileglob in ['*.html', '*.css', '*.js', '*.png', '*.jpg', 'favicon.ico', '*.gif', 'mime.types', '*.wsgi', '*.svg', '*.feature']] +
              ['*/features/*.py'] # step definitions and terrain files for lettuce tests
      },
      zip_safe=False,
      scripts=["yabiadmin/yabiadmin-manage.py", "yabiadmin/yabicelery.py"],
      install_requires=install_requires,
      dependency_links=dependency_links,
      extras_require={
          'tests': install_requires_compiled + tests_require,
          'dev': install_requires_compiled + dev_requires,
          'postgresql': install_requires_compiled + postgresql_requires,
          'mysql': install_requires_compiled + mysql_requires,
      })
