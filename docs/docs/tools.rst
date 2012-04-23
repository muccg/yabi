.. _tools:

Adding Tools
============

All tools that you wish to run through Yabi must me installed on the machine where they will be executed.
Yabi can run any command line tool based on a description of the tool stored in the Yabi Tool table.

When you add a tool to the Yabi Tool table there are a number of fields to fill out. We explain each
of them here:

Name
^^^^

A unique name used for identification in the database.

Display Name
^^^^^^^^^^^^

The tool name that the user will see.

Path
^^^^

The path to the binary for this file. This will often just be binary name but can be a full path.

Description
^^^^^^^^^^^

The description of the tool that will be seen by the user.

Enabled
^^^^^^^

If checked the tool will appear to users, otherwise it will not.

Backend
^^^^^^^

The execution backend where this tool will be run.

FS Backend
^^^^^^^^^^

The file system associated with the execution backend.

Accepts Input
^^^^^^^^^^^^^

If checked, this tool will accept inputs from prior tools rather than presenting file select widgets. This should usually be checked.

CPUs
^^^^

The number of cpus that should be requested in the submission script when running this tool.

Walltime
^^^^^^^^

The walltime that should be requested in the submission script when running this tool.

Module
^^^^^^

Yabi supports the use of the `Environment Modules <http://modules.sourceforge.net/>`_ project to manage the 
dynamic modification of a user's environment via modulefiles. If you are using this system you can add
a comma-separated list of modules that should be loaded when running this tool.

Queue
^^^^^

The queue that should be requested in the submission script when running this tool.

Lcopy supported, Link supported
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If the backend this tool will run on supports local copy or symbolic link, check these boxes to make the tool use local copy or
symlink. See also :ref:`Local Copy and Link <localcopyandlink>`.