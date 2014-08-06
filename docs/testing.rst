.. index::
   single: testing

Testing
=======

Running Tests
-------------

Yabi has an end to end test suite for testing the full Yabi stack. 
The tests can run against Postgresql or MySql. You can run them by:

    $ ./develop.sh test_postgresql

to run them against Postgresql or

    $ ./develop.sh test_mysql

to run them against MySql.


Lint
^^^^

To lint all the Python code in Yabi run:

    $ ./develop.sh lint
    
To lint all the JavaScript code in Yabi run:

    $ ./develop.sh jslint
