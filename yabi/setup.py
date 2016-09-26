import os
from setuptools import setup

packages = ['yabi'] + ['yabi.%s' % app for app in ['yabifeapp', 'yabiengine', 'yabi', 'preview', 'backend', 'authbackends']] + ['yabi.yabi.migrations', 'yabi.yabi.migrationutils', 'yabi.yabiengine.migrations', 'yabi.yabi.templatetags', 'yabi.yabi.management', 'yabi.yabi.management.commands', 'yabi.yabifeapp.management', 'yabi.yabifeapp.management.commands', 'yabi.backend.cloud']

package_data = {
    '': ["%s/%s" % (dirglob, fileglob)
        for dirglob in (["."] + ['/'.join(['*'] * num) for num in range(1, 15)])                         # yui is deeply nested
        for fileglob in ['*.html', '*.css', '*.js', '*.png', '*.jpg', 'favicon.ico', '*.gif', 'mime.types', '*.wsgi', '*.svg', '*.feature']] +
        ['*/features/*.py'] # step definitions and terrain files for lettuce tests
}

package_scripts = ["yabi/yabi-manage.py", "yabi/yabicelery.py"]

install_requires = []

importlib_available = True
try:
    import importlib
except ImportError:
    # This will likely to happen before Python 2.7
    importlib_available = False

if not importlib_available:
    install_requires.append('importlib>=1.0.1,<1.1.0')

setup(name='yabi',
    version='9.9.4',
    description='Yabi',
    long_description='Yabi web interface',
    author='Centre for Comparative Genomics',
    author_email='yabi@ccg.murdoch.edu.au',
    packages=packages,
    package_data=package_data,
    zip_safe=False,
    scripts=package_scripts,
    install_requires=install_requires,
)
