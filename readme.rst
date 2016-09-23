Yabi
====

About
-----

Yabi is a 3-tier application stack to provide users with an intuitive, easy to use, abstraction of compute and data environments. Developed at the Centre for Comparative Genomics (https://ccg.murdoch.edu.au/), Yabi has been deployed across a diverse set of scientific disciplines and high performance computing environments.

Yabi has a few key features:

- simplified web based access to High Performance Computing
- easy tool addition and maintenance
- handling of disparate compute and storage resouces ie. PBSPro, SGE, Torque, Slurm, SSH, SFTP, Amazon S3, Openstack Swift
- easy and powerful workflow creation environment

More docs at Read the Docs (https://yabi.readthedocs.org/).

Contact
-------

Hosted on GitHub:

https://github.com/muccg/yabi/

Documentation on Read the Docs: 

https://yabi.readthedocs.org/

Twitter:

http://twitter.com/#!/yabiproject

YouTube:

https://www.youtube.com/playlist?list=PLA7CAEC7DAA530AFA

Email:

yabi@ccg.murdoch.edu.au

For developers
--------------

We do our development using Docker containers. See: https://www.docker.com/.
You will have to set up Docker on your development machine.

Other development dependencies are Python 2 and virtualenv (https://virtualenv.pypa.io/en/latest/).

All the development tasks can be done by using the ``develop.sh`` shell script in this directory.
Please run it without any arguments for help on its usage.

Some typical usages are:

- ./develop.sh dev_rebuild
        You will need to run this the first time after you clone our repo to build the docker containers.
        You will also need to re-run it if you would like to rebuld the docker containers, for example when your python dependencies change.

- ./develop.sh dev
        To start up all the docker containers needed for dev. 
        You can access the Django Yabi application on http://localhost:8000
        (replace localhost with ``$ boot2docker ip`` if using boot2docker) after this.
        You can login with one of the default users *demo/demo* or *admin/admin*.

- ./develop.sh runtests
        Starts up all the docker containers and runs all our tests against them.

- ./develop.sh pylint
        Lint your python code.

- ./develop.sh jslint
        Lint your javascript code.

Note: Our docker containers are coordinated using docker-compose (https://docs.docker.com/compose/) but docker-compose will be installed into a virtualenv environment automatically by the ``./develop.sh`` script for you.

Contributing
------------

1. Fork next_release branch
2. Make changes on a feature branch
3. Submit pull request

Citation
--------

Hunter AA, Macgregor AB, Szabo TO, Wellington CA and Bellgard MI, Yabi: An online research environment for Grid, High Performance and Cloud computing, Source Code for Biology and Medicine 2012, 7:1 doi:10.1186/1751-0473-7-1 Published: 15 February 2012 Source Code for Biology and Medicine (http://www.scfbm.org/content/7/1/1/abstract)
