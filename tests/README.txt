This directory contains end to end tests for the YABI project.

To kick off the test, activate the virtual python and run nosetests:

$ source virt_yabiadmin/bin/activate
$ export DJANGO_SETTINGS_MODULE=yabiadmin.settings
$ nosetests --logging-clear-handlers -v

The development server should already be running (./develop.sh start).

List tests:

$ nosetests -v --collect-only


Run a single test:

$ nosetests -v --logging-clear-handlers tests.idempotency_tests
