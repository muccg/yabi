.. index::
   pair: yabish; command line 

Setting up Yabish
-----------------

Yabish is installed via yabi-shell RPM.

.. index::
    single: yabish

Yabish ( The command line client )
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Add CCG repo if not already done:

    ``sudo rpm -Uvh http://repo.ccgapps.com.au/repo/ccg/centos/6/os/noarch/CentOS/RPMS/ccg-release-6-2.noarch.rpm``

    ``$ sudo yum install yabi-shell-7.0.0-1.x86_64.rpm``

This installs the CLI for Yabi in ``/usr/bin/yabish``.
