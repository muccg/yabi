.. index::
   pair: yabish; command line 

Setting up Yabish
-----------------

Yabish is installed via yabi-shell RPM.

.. index::
    single: yabish

Yabish ( The command line client )
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ``$ sudo yum install yabi-shell-7.0.0-1.x86_64.rpm``

This installs the CLI for Yabi "yabish" in /usr/local/yabish/bin
Add /usr/local/yabish/bin to your path ( in .bashrc for example) to enable running yabish more easily.

To create a clean python environment to run yabish from. Create a virtualenv as follows:

    ``$ sudo virtualenv -p /usr/bin/python2.6  --no-site-packages /usr/local/python/cleanpython``

Add pth file /usr/local/python/cleanpython/lib/python2.6/site-packages/yabiadminlib.pth
containing just the path to yabiadmin lib directory:

::
    $ cat /usr/local/python/cleanpython/lib/python2.6/site-packages/yabiadminlib.pth
    /usr/local/webapps/yabiadmin/lib/


