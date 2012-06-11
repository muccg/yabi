============
Yabi Backend
============

.. index:

The Yabi Backend is a daemon that provides execution and file services to the yabi stack. It abstracts away the details and complexity
of individual protocols and resources to provide a consistent interface to the rest of yabi.

yabi.conf Configuration
=======================

The yabi backend when started loads its configuration from a file ``yabi.conf``. The file is in the familiar INI format. This is placed inside the 
running users ``.yabi`` directory. You can find a default ``yabi.conf`` as a basis to build your configuration from the source tree 
at ``yabibe/yabibe/conf/yabi_defaults.conf``. Copy this into ``~/.yabi/yabi.conf`` and adjust it as follows:

The conf file is broken into sections *backend*, *taskmanager*, *execution* and *ssh+sge*.

backend
=======

The backend begins with the ``[backend]`` header tag and ends at the next section header tag or the end of the file.

HTTP Services
-------------

These settings control the details of any HTTP services yabi backend serves up.

:attr:`~port`
    The ip number and port to bind our HTTP interface to. Use ``0.0.0.0`` as an ip number to bind to every interface. Otherwise specify an interface ip number
    a port. Default is ``127.0.0.1:9001``. 

    Example::

        
        port 0.0.0.0:8000

:attr:`~start_http`
    Controls if the http service is started. Set to ``true`` or ``yes`` to start up. Set to ``false`` or ``no`` to not start a http service. Default is ``yes``.

    Example::

        start_http: yes

HTTPS Services
--------------

These settings control the details of any HTTPS services yabi backend serves up.

:attr:`~sslport`
    The IP number and port to bind our HTTPS service to.  Use ``0.0.0.0`` as an ip number to bind to every interface. Default is ``0.0.0.0:9431``.

    Example::

        sslport: 0.0.0.0:8443

:attr:`~keyfile`
    The location in the filesystem of the SSL server key. File should be in PEM format. Default is ``~/.yabi/run/serverkey.pem``.

    Example::

        keyfile: /etc/ssl/yabi/serverkey.pem

:attr:`~certfile`
    The location in the filesystem of the SSL server certificate. File should be in PEM format. Default is ``~/.yabi/run/servercert.pem``.

    Example::

        certfile: /etc/ssl/yabi/servercert.pem

:attr:`~start_https`
    Controls if the https service should be started up. Set to ``true`` or ``yes`` to start up. 
    Set to ``false`` or ``no`` to not start a http service. Default is ``no``.

    Example::

        start_https: yes

Admin Communication Configuration
---------------------------------

The backend needs to know where to find the yabiadmin service it should use. The way it behaves with these connection is defined by the folowing:

:attr:`~admin`
    This is the base URL where the backend sends yabiamin requests to. This should point to your yabi admin installation.

    Example::

        admin: https://myadminserver.domain.com:8000/yabiadmin/

    .. warning::
        If this is a http URL then your credentials may be prone to being sniffed on the network. To make sure the system
        is secure, use a https url and serve your yabiadmin via https.


:attr:`~admin_cert_check`
    If the url for admin is https, then this setting controls if you want the certificate chain checked during the connection. If you are using
    a self signed SSL certificate on your yabiadmin server and you dont mind openning yourself up to man in the middle attacks, set 
    this to ``no``. Default is ``yes``

    Example::

        admin_cert_check: yes

:attr:`~hmackey`
    The connections between the backend and the admin are secured using HMAC aunthentication. This setting contains a secret key shared between 
    yabi admin and the backend. It is used to authenticate and secure the access both to the backend and to certain backend specific services 
    in the yabi admin. If these keys are not the same, yabiadmin and yabi backend cannot talk to each other.

    Example::

        hamckey: our_super_secret_yabi_hmac_key

    .. warning::
        The security of the system depends on keeping this key unique and secret.

Startup Script Variables
------------------------

There are a number of ways of starting and stopping the yabi backend service. If you use one of the included init.d scripts, then you can control
paths it uses with the following variables.

.. note::
    These settings are only used by the included init.d scripts. If you are starting the backend using fabric, or twistd, you control these with
    command line parameters.

:attr:`~source`
    This setting is only used by the inbuilt init.d script to find the location of the yabibackend to run. Default is ``~/yabi/yabibe/yabibe``.

    Example::

        source: /usr/local/yabi/backend/

:attr:`~runningdir`
    Yabi needs a place to store temporary files and credentials. This is the path under which to store them. It's also
    the working directory that yabi backend will run within. Default is ``~/.yabi/run/``.

    Example::

        runningdir: /var/yabi/backend/

:attr:`~pidfile`
    When the process is startedm its process id is stored in this file. Default is ``~/.yabi/run/yabibe.pid``.

    Example::
    
        pidfile: /var/run/yabi/backend.pid

Logging
-------

These options control the way that the yabi backend logs. You can log to a file, or via syslog.

.. note::
    If starting yabi backend with the twistd command line, you can override these settings with the --logfile and --syslog command parameters.

:attr:`~logfile`
    Specify a file location to write the yabi logfile to. Default is ``~/.yabi/run/yabibe.log``.

    Example::

        logfile: /var/log/yabi.log

:attr:`~syslog_facility`
    Specify the syslog facility to log under. Default is ``LOG_DAEMON``

    Example::

        syslog_facility: LOG_LOCAL4

    .. note::
        This is only used if the backend is launched by passing --syslog into the twistd command line

:attr:`~syslog_prefix`
    All syslog reporting will be prefixed by this message. You can reference some variables in the message to assist you.
        {username}: the name of the user running the backend server
        {pid}: the processid of the backend server

    Example::

        syslog_prefix: yabi backend {username}

Temporary Storage
-----------------

:attr:`~fifos`
    Filesystem path to a writable directory where yabi backend can store FIFOs. Default is ``~/.yabi/run/backend/fifos/``

    Example::

        fifos: /var/run/yabi/backend/fifos/

:attr:`~tasklets`
    Filesystem path to a writable directory to store running tasklets in. This is used when the backend is stopped and restarted.
    The running tasklets (representing executing jobs) are serialised and stored on disk so they can be resumed on startup. Default 
    is ``~/.yabi/run/backend/tasklets/``.

    Example::

        tasklets: /var/run/yabi/backend/tasklets/ 

:attr:`~temp`
    Filesystem path where the backend can store temporary files. Default is ``~/.yabi/run/backend/temp/``.

    Example::

        temp: /var/run/yabi/backend/temp/

:attr:`~certificates`
    File system path to a writable directory where the backend can store any temporary access certificates needed to access certain
    backends. For example: short lived grid proxy certificates are stored here when accessing grid services. Default is ``~/.yabi/run/backend/certificates/``.

    Example::

        certificates: /var/run/yabi/backend/certs/

Miscellaneous
-------------

:attr:`~debug`
    Whether to turn on debug mode to get more information from the backend. Deafult is ``no``.

    Example:

        debug: no







