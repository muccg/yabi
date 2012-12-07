This directory contains end to end tests for the YABI project.

To setup your development environment, run all the YABI servers in the background, from
the top level yabi directory run:


$ ./devstack.sh start


To kick off the test, activate the virtual python and run nosetests:


$ source virt_yabiadmin/bin/activate
$ nosetests -v -w yabitests

