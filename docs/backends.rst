.. _backends:

Backends
========

In Yabi there are two types of backend - execution and storage. As the names suggest, an execution 
backend is where tasks will be run, and a storage backend is where files are stored.

To get things up and running the best idea is to set up your first backend to a resource that you can connect to via SSH.
Before trying to add the backend to Yabi you should be able to connect to it via the command line using 
ssh keys from the box running Yabi.

.. index::
   single: SSH

Setting up an SSH File System Backend
-------------------------------------

Click on Backends under Yabi heading and add a backend, using `scp` as the scheme. For example you would fill in the fields like this:

::

    Name            Example File Server
    Description     My example file server
    Scheme          scp
    Hostname        exampleserver.localdomain
    Port            22
    Path            /home/

.. index::
   single: backend; path field

.. _a_note_about_the_path_field:

A note about the Path field
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Yabi uses the information in the Backend record and the Backend Credential record to construct a URI that it uses to access 
data or execution resources. In setting up this backend I am adding ``/home/`` to the path. This is where all the Yabi 
users on this machine will find their home directories. So the backend can construct a URI from the scheme, hostname and path fields that will look like this:

``scp://exampleserver.localdomain/home/``


In a later step (:ref:`backendcredentials`) we will setup the link between Backends and a Users Credentials. In that step we will add to the 
`User Directory` field ``andrew/yabi/``. This leads to my home directory (``/home/andrew/``) and then limits Yabi access to a directory within it (``yabi/``).

So when Yabi needs to access files on that backend it combines the fields from the Backend and the Backend Credential records to derive the URI:

``scp://exampleserver.localdomain/home/andrew/yabi/``


**Please note:** While Yabi refers to the directory on the Backend Credential record as User Directory this can really point to any directory the user has access to.

.. index::
   pair: backend; local copy
   pair: backend; symbolic link

.. _localcopyandlink:

Additional Fields
^^^^^^^^^^^^^^^^^

The `Lcopy` and `Link` checkboxes come into play if an execution and storage backend have a shared filesystem. You 
can set this backend up to use local copy and link, then later specific tools can request that lcopy or link be used.


Adding an Execution Backend
---------------------------

Next we are going to add an execution backend so we can run some jobs. In this example we are going to use pbspro qsub via ssh. 
In this way we do not need to have torque and qsub set up on the same box as Yabi. Instead we just need to have our ssh credentials (:ref:`backendcredentials`)
set up to access the execution host.

Again, click on Backends under Yabi heading and add a backend, this time using `ssh+pbspro` as the scheme. For example you would fill in the fields like this:

::

    Name            Example Execution Server
    Description     My example execution server
    Scheme          ssh+pbspro
    Hostname        exampleserver.localdomain
    Port            22
    Path            /

.. index::
    pair: backend; qsub;
    pair: backend; submission script

Submission Template Field
^^^^^^^^^^^^^^^^^^^^^^^^^

On an execution backend you can add a template for any submission scripts that will be used. In this case we can add a template that 
looks like this:

::

    #!/bin/sh
    #PBS -l walltime=${walltime}
    #PBS -l mem=${memory}
    #PBS -l nodes=1:ppn=${cpus}
    %if queue == 'debugq':
    #PBS -q debugq
    %else:
    #PBS -q routequeue
    %endif
    #PBS -W group_list=my_account_id
    % for module in modules:
        module load ${module}
    % endfor
    cd '${working}'
    ${command} 1>${stdout} 2>${stderr}

This submission template uses the `Mako templating system <http://www.makotemplates.org/>`_ and in this case represents the qsub script
that will be used by Yabi to submit the job. The variables in the template are pulled from each tool that we configure (See :ref:`tools`).
This provides a powerful mechanism for determining the scripts submitted to each backend.

Submission Template Keys
^^^^^^^^^^^^^^^^^^^^^^^^

The following is a table of the keys available in the template, and their meaning. Keys are to be placed inside ${} in the template.

+--------------+----------------------------------------------------------------------------------------------------------+
| Key          | Value                                                                                                    |
+==============+==========================================================================================================+
| working      | The full path of the working directory for the job.                                                      |
+--------------+----------------------------------------------------------------------------------------------------------+
| command      | The full command line for the final task. The executable and all its passed in arguments.                |
+--------------+----------------------------------------------------------------------------------------------------------+
| modules      | A list of all the modules that need loading.                                                             |
+--------------+----------------------------------------------------------------------------------------------------------+
| cpus         | Number of cpus that should be utilised.                                                                  |
+--------------+----------------------------------------------------------------------------------------------------------+
| memory       | The amount of RAM that should be partitioned for the job.                                                |
+--------------+----------------------------------------------------------------------------------------------------------+
| walltime     | The walltime for the job.                                                                                |
+--------------+----------------------------------------------------------------------------------------------------------+
| yabiusername | The username of the yabi user that submitted the job. Can be different from the backend username.        |
+--------------+----------------------------------------------------------------------------------------------------------+
| username     | The username the job is to be run as                                                                     |
+--------------+----------------------------------------------------------------------------------------------------------+
| host         | The hostname the job is being run on                                                                     |
+--------------+----------------------------------------------------------------------------------------------------------+
| queue        | The name of the queue the job should be submitted to                                                     |
+--------------+----------------------------------------------------------------------------------------------------------+
| stdout       | The name of the yabi standard out file standard output should be directed to. Usually STDOUT.txt         |
+--------------+----------------------------------------------------------------------------------------------------------+
| stderr       | The name of the yabi standard error file standard error should be directed to. Usually STDERR.txt        |
+--------------+----------------------------------------------------------------------------------------------------------+
| arrayid      | The number (from 1 to arraysize) of this particular task in the job set.                                 |
+--------------+----------------------------------------------------------------------------------------------------------+
| tasknum      | A synonym for arrayid.                                                                                   |
+--------------+----------------------------------------------------------------------------------------------------------+
| arraysize    | The total number of tasks in the job set.                                                                |
+--------------+----------------------------------------------------------------------------------------------------------+
| tasktotal    | A synonym for arraysize.                                                                                 |
+--------------+----------------------------------------------------------------------------------------------------------+

Troubleshooting SSH
-------------------

Take a look at these FAQs
 - :ref:`ssh_troubleshooting`
 - :ref:`known_hosts`

.. index::
   pair: backend; null backend

.. _nullbackend:

Null Backend
------------
An evolutionary quirk of Yabi is that the system requires what we call a null backend for tools that should not be
executed, such as a file selection tool. We hope to remove this branch of code in a future release. To add a null 
backend follow the steps above for adding an execution backend and use these values:

::

    Name            Null Backend
    Description     Use this null backend when tools should not be executed.
    Scheme          null
    Hostname        localhost.localdomain
    Port            
    Path            /

Now add a Backend Credential (see :ref:`backendcredentials`) for the null backend. It does not matter which credential 
you associate with the Null Backend as it will not be used.

S3 Backend
----------
An S3 filesystem backend can be created by using the schema ``s3``. 
The domain of the hostname should be set to ``amazonaws.com`` and the hostname to a S3 bucket name.

For example ``mybucket.amazonaws.com`` as the hostname will access the bucket ``mybucket`` on amazon.

In setting up the credential for access to S3, your remote username is ignored, so you can place any text in here you like. You will need to 
fill in two fields: cert, and key. Into the yabi cert field put the Amazon ACCESS ID and into the yabi key field put the Amazon SECRET KEY.

