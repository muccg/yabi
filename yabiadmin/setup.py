import os
from setuptools import setup

INSTALL_ONLY_DEPENDENCIES = 'INSTALL_ONLY_DEPENDENCIES' in os.environ

if 'INSTALL_ONLY_DEPENDENCIES' in os.environ:
    packages = []
    package_data = {}
    package_scripts = []
else:
    packages = ['yabiadmin'] + ['yabiadmin.%s' % app for app in ['yabifeapp', 'yabiengine', 'yabi', 'preview', 'backend']] + ['yabiadmin.yabi.migrations', 'yabiadmin.yabi.migrationutils', 'yabiadmin.yabiengine.migrations', 'yabiadmin.yabi.templatetags', 'yabiadmin.yabifeapp.management', 'yabiadmin.yabifeapp.management.commands', 'yabiadmin.backend.cloud']

    package_data = {
        '': ["%s/%s" % (dirglob, fileglob)
              for dirglob in (["."] + ['/'.join(['*'] * num) for num in range(1, 15)])                         # yui is deeply nested
              for fileglob in ['*.html', '*.css', '*.js', '*.png', '*.jpg', 'favicon.ico', '*.gif', 'mime.types', '*.wsgi', '*.svg', '*.feature']] +
              ['*/features/*.py'] # step definitions and terrain files for lettuce tests
    }

    package_scripts = ["yabiadmin/yabiadmin-manage.py", "yabiadmin/yabicelery.py"]


install_requires = [
    'Django==1.6.10',
    # pip > 1.4 doesn't pick up pytz, because of non-standard version number
    # Bug is still under discussion: https://bugs.launchpad.net/pytz/+bug/1204837
    'pytz>=2013b',
    'ccg-django-utils==0.2.1',
    'ccg-auth==0.3.4',
    'anyjson==0.3.3',
    'celery==3.1.15',
    'amqp==1.4.6',
    'amqplib==1.0.2',
    'kombu==3.0.23',
    'billiard==3.3.0.18',
    'django-templatetag-sugar==1.0',
    'ordereddict==1.1',
    'python-memcached==1.53',
    'Mako==1.0.0',
    'South==1.0',
    'django-extensions==1.4.0',
    'beautifulsoup4==4.3.2',
    'cssutils==1.0',
    'httplib2==0.9',
    'djamboloader==0.1.4',
    'paramiko==1.15.2',
    'boto==2.35.2',
    'python-swiftclient==2.2.0',
    'python-keystoneclient==0.10.1',
    'netaddr!=0.7.13',
    'python-dateutil==2.2',
    'yaphc==0.1.5',
    'six==1.8',
    'flower>=0.7.0',
    'apache-libcloud==0.15.1',
    'ccg-libcloud-drivers==0.0.1',
    'uwsgi==2.0.8',
    'uwsgitop',
    'pyinotify==0.9.4',
    'Werkzeug',
    'psycopg2==2.5.4',
    # for tests
    'requests==2.4.1',
    'django-nose',
    'nose==1.3.4',
    'mockito>=0.5.0,<0.6.0',
    'sniffer==0.3.2',
    'model_mommy==1.2.2',
]

# Compiled python modules which are usually provided by system packages
install_requires_compiled = [
    'pycrypto==2.6.1',  # version locked as a 2.7a1 appeared in pypi
]

dev_requires = [
    'flake8==2.2.3',
    'closure-linter==2.3.13',
]

tests_require = [
    'requests==2.4.1',
    'django-nose',
    'nose==1.3.4',
    'mockito>=0.5.0,<0.6.0',
    'sniffer==0.3.2',
    'model_mommy==1.2.2',
]

postgresql_requires = [
    'psycopg2==2.5.4',
]

mysql_requires = [
    'MySQL-python==1.2.5',
]

dependency_links = [
    'https://bitbucket.org/ccgmurdoch/ccg-django-utils/downloads/ccg-django-utils-0.2.1.tar.gz',
    'https://bitbucket.org/ccgmurdoch/ccg-django-extras/downloads/ccg-auth-0.3.4.tar.gz',
    'https://yaphc.googlecode.com/files/yaphc-0.1.5.tgz',
    'https://bitbucket.org/ccgmurdoch/libcloud-drivers/downloads/ccg-libcloud-drivers-0.0.1.tar.gz',
    'https://github.com/muccg/djamboloader/archive/0.1.4.tar.gz#egg=djamboloader-0.1.4',
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
      version='9.3.0',
      description='Yabi Admin',
      long_description='Yabi front end and administration web interface',
      author='Centre for Comparative Genomics',
      author_email='yabi@ccg.murdoch.edu.au',
      packages=packages,
      package_data=package_data,
      zip_safe=False,
      scripts=package_scripts,
      install_requires=install_requires,
      dependency_links=dependency_links,
      extras_require={
          'tests': install_requires_compiled + tests_require,
          'dev': install_requires_compiled + dev_requires,
          'postgresql': install_requires_compiled + postgresql_requires,
          'mysql': install_requires_compiled + mysql_requires,
      })
