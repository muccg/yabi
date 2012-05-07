.. index::
   single: tools; adding

.. _tools:

Adding Tools
============

All tools that you wish to run through Yabi must me installed on the machine where they will be executed.
Yabi can run any command line tool based on a description of the tool stored in the Yabi Tool table.

When you add a tool to the Yabi Tool table there are a number of fields to fill out. We explain each
of them here:


Tool Fields
-----------

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

Tool Output Extensions
^^^^^^^^^^^^^^^^^^^^^^
This is list of all file extension patterns that this tool will output. You can enter patterns either inline by clicking the
green plus beside the extension list or via the Yabi File Extension table. The extensions should be entered using a 
`Unix Glob <http://en.wikipedia.org/wiki/Glob_(Unix)>`_ pattern such as ``*.txt``.


Tool Parameter Fields
---------------------

Tool parameter fields are used to describe each switch or flag or parameter given to the tool.

Switch
^^^^^^
The actual text for the switch that the tool will use i.e. a tool may use ``-i`` for input, so you would enter ``-i`` in this field.

Switch Use
^^^^^^^^^^

This field describes how the switch should be used. There are some basic patterns that are repeated across many tools. They are
represented with Yabi using Python string interpolation. Switch use records maybe added inline by clicking the green plus or via the Yabi
Parameter Switch Uses table.

To give an example, if a tool takes one switch ``-i my_input_file`` we would add a Parameter Switch use which we describe as "Both" and
represent this as ``%(switch)s %(value)s``. Yabi when running this tool would then produce ``-i my_input_file``.

The most commonly used parameter switch uses that we use are:

============================== ==================== ============================================================
Display                        Format String        Description
============================== ==================== ============================================================
redirect                       >%(value)s	        Use this to redirect the output of stdout into a file.
combined with equals	       %(switch)s=%(value)s	Both the switch and the value will be passed in the argument list. They will be separated joined with an equals(=) character with no spaces.
nothing	 	                                        The switch and the value won't be passed in the argument list.
combined                       %(switch)s%(value)s	Both the switch and the value will be passed in the argument list. They will be joined together with no space between them.
both	                       %(switch)s %(value)s	Both the switch and the value will be passed in the argument list. They will be separated by a space.
valueOnly                      %(value)s            Only the value will be passed in the argument list (ie. the switch won't be used)
switchOnly	                   %(switch)s	        Only the switch will be passed in the argument list.
============================== ==================== ============================================================


Rank
^^^^
The order in which the switches should appear when running the tool. Leave this blank if the order is unimportant.

Mandatory
^^^^^^^^^

Check this box if the user **must** provide an input for this parameter.

Output File
^^^^^^^^^^^

Check this if this parameter relates to an output file i.e. ``--output``

Extension Param
^^^^^^^^^^^^^^^

If an extension is selected then this extension will be appended to the filename. This should only be set for specifying output files.

Possible Values
^^^^^^^^^^^^^^^

This field accepts a JSON snippet that will be presented to the user as a dropdown select widget. Your JSON should look like this:

::

    {"value":[
    {"display":"option1","value":"value1"},
    {"display":"option2","value":"value2"},
    {"display":"option3","value":"value3"},
    {"display":"option4","value":"value4"},
    {"display":"option5","value":"value5"}
    ]}

Default Value
^^^^^^^^^^^^^

The default value that should be used for this parameter. If you have used Possible Values above this value should match one
of the values in the JSON snippet.

Helptext
^^^^^^^^

The help text that is passed to the frontend for display to the user.

File Assignment
^^^^^^^^^^^^^^^

Specifies how to deal with files that match the accepted filetypes setting.

 * No input files - This parameter does not take any input files as an argument
 * Single input file - This parameter can only take a single input file, and batch jobs will need to be created for multiple files if the user passes them in
 * Multiple input file - This parameter can take a whole string of onput files, one after the other. All matching filetypes will be passed into it

Use Output Filename
^^^^^^^^^^^^^^^^^^^

You can set a tool in Yabi to name its output file based on an input file from another parameter. i.e. If your tool runs like this: 
``mytool -i inputfile.txt`` and produces a ``.html`` output you can set Use Output Filename to ``-i`` and your output will be named
``inputfile.txt.html``. When entering your tool you should enter all other parameters first, save the record, edit it again and set this
parameter. That way the dropdown select widget only shows relevant switches.

Accepted Filetypes
^^^^^^^^^^^^^^^^^^
The extensions of accepted filetypes for this switch. When searching for input files Yabi will only consider those
that match extensions in this list. Again, the extensions should be entered using a 
`Unix Glob <http://en.wikipedia.org/wiki/Glob_(Unix)>`_ pattern such as ``*.txt``.

