This sub-project contains end to end tests for the YABI project.

To run the tests if your YABI stack is set up and all the servers are running by

$ fab tests

at the top level yabi directory.

In case your stack is set up but the servers aren't running, you can run all the servers, run the tests and then stop the servers by:

$ fab runservers tests killservers

again at the top level yabi directory.

In case you have a cleanly checked out copy of yabi you should:

$ fab quickstart tests killservers

This will setup your quickstart environment, run all the YABI servers in the background, run all the tests and then stop all servers.


The support.YabiTestCase allows your tests to run yabish commands and to use setUpAdmin and tearDownAdmin classmethods to set up fixtures in YabiAdmin before running your test methods. For an example please see simple_tool_test.HostnameTest.

