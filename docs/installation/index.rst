.. _installation:

Installation
============

We currently install Yabi on CentOS servers which is the supported platform.
There is nothing preventing you to install Yabi on any other Linux distribution, but installing on CentOS is easiest using the RPMs we provide.

Theoretically, you could install on any platform that can run a Python WSGI application and Celery. Additionally you will need access to a database server (Postgresql recommended or MySQL), a message broker (we use and recommend RabbitMQ), and Memcached. 

Components
----------

As it was already mentioned in :ref:`architecture` Yabi consists of three main components. Of those at least the Yabi web application and the Yabi Backend has to be installed on the server.
The yabish command line client can also be installed on user machines if required.

The Yabi Backend is running the Celery worker processes that among other things are responsible for file operations. In case you have a lot of large files that are transferred the responsiveness of the web application could be effected.

That being said the simplest method of installation is to install both the Yabi web application and the Yabi Backend on the same server. We use this setup on all our servers and we recommend you start with the same because it is simpler and you can always optimise later if required.

The Yabi web application is a Django application. It needs a WSGI container and a web server to serve static files. We currently use and recommend Apache + mod_wsgi, if you use our RPMs you would be using the same.

The Yabi Backend is based on Celery and it is recommended that you use a dedicated message broker.We use and recommend RabbitMQ, installation instructions are provided for CentOS.

Both the Yabi web application and the Yabi Backend make use of a shared database. As a database server we use and recommend Postgresql. We assume you already have your database server installed. We do provide instructions on how to set up the Yabi database on an existing database server.

Yabi also uses Django caching and although any caching method supported by Django should work we use and recommend Memcached. We assume you have your Memcached servers already installed, we provide instructions on how to set up Yabi to use them.

Yabi sessions are also stored in Memcache. You can do the same or opt for another session backend supported by Django.

How to install
--------------

In the *how to install* section we assume that you are going to install Yabi on CentOS using our provided RPMs and that both the web application and the Yabi Backend are going to be installed on the same server.

.. toctree::
    :maxdepth: 2
 
    prerequisites
    apache
    database
    caching
    laststeps
    yabish

