Installation under Apache
=========================

Yabi make extensive use of `Fabric <http://fabfile.org>`_, a Python (2.5 or higher) library and command-line tool for streamlining 
the use of SSH for application deployment or systems administration tasks. Fabric is how we typically deploy using Centos and Apache/mod_wsgi.

Prerequisites
-------------

There are build requirements on Linux systems that you may need. These commands will install them:

 $sudo yum install python-setuptools python-devel gcc openssl-devel.x86_64 postgresql84-devel

 $sudo easy_install Mercurial pip virtualenv

**NB:** You might need to change to the right postgres devel version 

Check Mercurial is installed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    $hg --version


Add new directories as needed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Make a directory for storing wsgi conf files.

    $sudo mkdir /usr/local/python/conf/ccg-wsgi/ -p

Set up a clean python for WSGI to use
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
We set up a clean Python environment using `virtualenv <http://www.virtualenv.org/>`_ so we know exactly the environment our
application is operating in. We then use the `WSGIPythonHome <http://code.google.com/p/modwsgi/wiki/ConfigurationDirectives#WSGIPythonHome>`_ 
directive to specify the cleanpython directory.

    $sudo virtualenv -p /usr/local/python/bin/python --no-site-packages /usr/local/python/cleanpython/

    $sudo /usr/local/python/cleanpython/bin/pip install virtualenv


Now check clean python is installed:

    $ /usr/local/python/cleanpython/bin/python --version

Change wsgi configuration in http.conf to include:

``WSGIPythonHome     /usr/local/python/cleanpython``


Add an include line to mod_wsgi.conf to get the Yabi wsgi file from our ccg-wsgi directory:

``Include /usr/local/python/conf/ccg-wsgi/``


Deploying Yabi
--------------

Clone the repo:

    $hg clone https://code.google.com/p/yabi/ 

Deploy Yabi Application
-----------------------

Make sure you have changed into the directory that you just checked out then:

    $cd yabiadmin/yabiadmin/

    $sh ../../bootstrap.sh

    $source virt_yabiadmin/bin/activate

    $fab release

This will ask you to specify the release tag and present you with a list of possibilities. It is also possible to supply
a Mercurial revision such as 'default' and that will be released. 

Next, make a symlink to point at the newly released yabiadmin i.e. for yabiadmin-release-5.14

    $cd /usr/local/python/ccgapps/yabiadmin/

    $ln -s yabiadmin-release-5.14 release


Deploy Yabi Backend
-------------------

Change back into the directory where you cloned Yabi earlier, then:

    $cd yabibe/yabibe/

    $sh ../../bootstrap.sh

    $fab release

    $fab start

Again you will be asked to specify a release tag.


Start Celery
------------

`Celery <http://celeryproject.org/>`_ is an asynchronous task queue/job queue used by Yabi. It needs to be started separately.

    $/etc/init.d/celeryd start

An example of our celeryd init script can be found in our `source code repository <http://code.google.com/p/yabi/source/browse/yabiadmin/admin_scripts/celeryd>`_.

Restart apache
--------------
For changes to take effect restart apache.



Sample Apache Configuration
===========================

Introduction
------------

This is a sample configuration, for more complete references:
  * `https://docs.djangoproject.com/en/1.3/howto/deployment/modwsgi/ <https://docs.djangoproject.com/en/1.3/howto/deployment/modwsgi/>`_
  * `https://code.google.com/p/modwsgi/wiki/ConfigurationGuidelines <https://code.google.com/p/modwsgi/wiki/ConfigurationGuidelines>`_
  * `https://httpd.apache.org/docs/ <https://httpd.apache.org/docs/>`_



Sample Yabi Configuration
-------------------------------

In file: ``/etc/httpd/conf.d/wsgi.conf``

::

   <IfModule mod_wsgi.c>
   LoadModule wsgi_module modules/mod_wsgi.so
   WSGISocketPrefix /var/run/httpd
   </IfModule>

In file: ``/etc/httpd/conf.d/mod_wsgi_daemons.conf``

::

   <IfModule mod_wsgi.c>
   WSGIDaemonProcess yabiadmin processes=2 threads=15 display-name=%{GROUP}
   </IfModule>


These files need to be included from your ``httpd.conf``:

::

    Include conf.d/*.conf

or:

::

    Include conf.d/wsgi.conf
    Include conf.d/mod_wsgi_daemons.conf

A sample virtual hosts configuration for a server that just runs Yabi:

::

    <VirtualHost *:80>
        ServerAdmin your_email@mailserver.com
        DocumentRoot /var/www/html
        ServerName your_server
        ErrorLog logs/yabiadmin.error_log
        CustomLog logs/yabiadmin.access_log combined
        RewriteLogLevel 3
        RewriteLog logs/yabiadmin.rewrite_log

        <Directory "/var/www/html">
        Options Indexes FollowSymLinks
        AllowOverride All
        Order allow,deny
        Allow from all
        </Directory>

        # mod_wsgi
        Include /etc/httpd/conf.d/mod_wsgi.conf
    </VirtualHost>

...and ssl:

::

    <VirtualHost *:443>
        #   General setup for the virtual host
        DocumentRoot "/var/www/html"
        ServerName your_server:443
        ServerAdmin your_email@mailserver.com
        ErrorLog logs/yabiadmin.ssl_error_log
        TransferLog logs/yabiadmin.ssl_access_log

        SSLEngine on
        SSLCipherSuite ALL:!ADH:!EXPORT56:RC4+RSA:+HIGH:+MEDIUM:+LOW:+SSLv2:+EXP:+eNULL
        SSLCertificateFile /etc/pki/tls/certs/localhost.crt
        SSLCertificateKeyFile /etc/pki/tls/private/localhost.key

        <Directory "/var/www/html">
            Options Indexes FollowSymLinks
            AllowOverride All
            Order allow,deny
            Allow from all
        </Directory>
        SetEnvIf User-Agent ".*MSIE.*" \
             nokeepalive ssl-unclean-shutdown \
             downgrade-1.0 force-response-1.0

        CustomLog /etc/httpd/logs/ssl_request_log \
              "%t %h %{SSL_PROTOCOL}x %{SSL_CIPHER}x \"%r\" %b"

        # mod_wsgi
        Include /etc/httpd/conf.d/mod_wsgi.conf
    </VirtualHost>

In file: ``/etc/httpd/conf.d/mod_wsgi.conf``:

::

    <IfModule mod_wsgi.c>
    <Location /yabiadmin>
        WSGIProcessGroup yabiadmin
    </Location>
    WSGIScriptAlias /yabiadmin /usr/local/python/ccgapps/yabiadmin/release/yabiadmin/yabiadmin.wsgi
    Alias /yabiadmin/static /usr/local/python/ccgapps/yabiadmin/release/yabiadmin/static
    Alias /yabiadmin/images /usr/local/python/ccgapps/yabiadmin/release/yabiadmin/static/images
    </IfModule>
