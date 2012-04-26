.. _faq:

Frequently Asked Questions
==========================

What backend should a file select tool use or why won't my file select run?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You have run into an evolutionary quirk of Yabi. See :ref:`nullbackend`.

What is the default stageout field for?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
See :ref:`defaultstageout`.

Why am I getting an error about accessing a "store" directory?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You need to make sure that the value given for ``YABISTORE_HOME`` in the settings.py
file is writeable by the webserver you are using. By default ``YABISTORE_HOME`` is set 
to ``.yabi/run/store/``.

How does Yabi handle the URI construction with the Backend and Backend Credential records?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

See :ref:`a_note_about_the_path_field`.

I'm trying to add a tool that takes an input directory which it will use as a working directory, how do I do this?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It helps in setting up these tools to know that Yabi always behaves in the same way when executing jobs. 

1. It creates a temp directory with a unique name
2. In that directory it creates an input and an output directory
3. It stages all input files into the input directory
4. It cds to the output directory and runs the command
5. It stages out whatever is in the output directory

So in Yabi we don't have an option to pass in dir names as the command always runs in the output dir with inputs from the inputs dir.

In the case of such tools you could write a  wrapper (in python etc) to move the input files to the output directory. Then you specify 
the inputdir to be ``.`` The other option is to use this in the command field:

``cp ../input/* . ; command_to_be_run``

We would typically then set the tool up so the parameter specifying ``.`` as the working directory was hidden to the user.