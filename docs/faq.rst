.. _faq:

Frequently Asked Questions
==========================

Admin
-----

I've installed Yabi but when I try to login why do I see this error "Unable to create a new session key."?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is most likely because you do not have caching set up and Django cannot write its session information to cache. If 
you are running memcached caching have you started memcached? If you are using file based caching, is the cache directory
writable and readable by Yabi?

What backend should a file select tool use or why won't my file select run?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You have run into an evolutionary quirk of Yabi. See :ref:`nullbackend`. If you set up Yabi from our code repository
you will find a `file select` tool was installed by default for you to use.

What is the default stageout field for?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
See :ref:`defaultstageout`.

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

.. _ssh_troubleshooting:

I'm having trouble setting up an SSH backend, what am I doing wrong?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To troubleshoot setting up a backend with SSH here is what we normally do:

1. On the box running Yabi, as the user running Yabi, we will try to ssh to the backend resource. If we want to do that from Yabi with a private key 
we'll try to use that key i.e.  `ssh -i my_priv_key user@hostname`.

2. As long as that works we will then paste the plain text of the key into the correct credential in Yabi.
Note that if the private key has a password, then it is this password that goes in the credential record, **not** the 
user's password for the backend resource.

3. From there we'll log into the front end as the user and see if we can use the files tab. If we're logged in the front end 
we can also check in the admin under Yabi Users whether we can access the backend (see :ref:`viewing_a_users_setup`).

Using just a password for ssh (not a private key) should be the same steps.

How do I get symlinking working?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The backend will use symlinks if these conditions are met:
 - the File System backend has Link Supported enabled
 - the tools in the workflow have Link Supported enabled
 - all the tools use the same File System backend

A gotcha here is that by default the File Select tool uses nullbackend for the File System backend and Execution backend.
Make sure that you change the File System backend on File Select to be localfs or scp etc, the same as the tools that will follow it.
This should ensure symlinks are used rather than copying input files.

Of course, if you select a file from a file system that is separate from the execution file 
system then Yabi has to make a copy to stage it in.
