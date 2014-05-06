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

On an execution backend you can add a template for any submission scripts that will be used. Please see :ref:`submissiontemplates`.

Troubleshooting SSH
-------------------

Take a look at these FAQ
 - :ref:`ssh_troubleshooting`

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
fill in two fields: password and key. Into the yabi key field put the Amazon ACCESS ID and into the yabi password field put the Amazon SECRET KEY.

OpenStack Swift Backend
-----------------------

Yabi can use `OpenStack Object Storage`_ (commonly known as *Swift*)
as a filesystem backend. Swift is similar to S3 in that it is a
key-value store, not a heirachical file system. Yabi will present the
keys in a directory tree, using forward slashes (``/``) to separate
directory paths.

The OpenStack cluster must use Keystone_ 2.0 auth. To set up the Swift
backend, set its hostname to the hostname part of the Keystone API
endpoint. For example, if the Keystone auth URL is
``https://keystone.bioplatforms.com/v2.0/``, then the backend hostname
will be ``keystone.bioplatforms.com``.

OpenStack users are associated with projects (also called
"tenants"). In Swift, files are collected in "containers" which belong
to the project. Each project has its own set of containers. The
backend path must specify both the project and container.

============== =================================================
Backend Option Setting
============== =================================================
Name           OpenStack Swift
Description    OpenStack object storage
Scheme         ``swift``
Hostname       *The hostname part of the Keystone API endpoint.*
Port           *Not required, defaults to 443*
Path           ``/tenant/container/``
...            *All other options left blank.*
============== =================================================

When creating a credential entry for the Swift backend, use Keystone
credentials.

============ ================================================
Credential   Setting
============ ================================================
Description  OpenStack Keystone credentials for *user name*.
Username     The Keystone user name.
Password     The Keystone password.
Cert
Key
User         The Yabi user.
Expires on   A date in the future.
============ ================================================

.. _`OpenStack Object Storage`: http://swift.openstack.org/
.. _Keystone: http://docs.openstack.org/developer/keystone/
