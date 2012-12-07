This directory contains end to end tests for the YABI project.

To kick off the test, activate the virtual python and run nosetests:

$ source virt_yabiadmin/bin/activate
$ nosetests -v -w yabitests


List tests:

$ nosetests -v -w yabitests --collect-only


Run a single test:

$ nosetests -v -w yabitests yabitests.backend_restart_tests
