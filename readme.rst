Yabi
====

Contact
-------

Hosted on Bitbucket: 

https://bitbucket.org/ccgmurdoch/yabi/

Documentation on Read the Docs: 

https://yabi.readthedocs.org/

Project Managed on JIRA: 

https://ccgmurdoch.atlassian.net/projects/YABI/

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

  - ./develop.sh start
        To start up all the docker containers needed for dev. 
        You can access the Django Yabi application on http://localhost:8000
        (replace localhost with ``$ boot2docker ip`` if using boot2docker) after this.
        You can login with one of the default users demo/demo or admin/admin.

  - ./develop.sh runtests
        Starts up all the docker containers and runs all our tests against them.

  - ./develop.sh pythonlint
        Lint your python code.

  - ./develop.sh jslint
        Lint your javascript code.

Note: Our docker containers are coordinated using fig (http://www.fig.sh/) but fig will be installed into a virtualenv environment automatically by the ``./develop.sh`` script for you.

Contributing
------------

1. Fork next_release branch
2. Make changes on a feature branch
3. Submit pull request
