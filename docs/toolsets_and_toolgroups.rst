.. _toolsets_and_toolgroups:

Toolsets and Toolgroups
=======================

Before a user will see a tool in the front end you need to set up assign access to it using Toolsets and Toolgroups.

Toolsets
--------

Adding toolsets allows grouping of users to determine which tools they have access to. We 
typically have an ``allusers`` set, a ``dev`` set and maybe a ``testing`` set. On top 
of that we might have sets for individual research groups etc.

Grouping like this also means that if we are running a licenced tool, we can assign it only
to groups of users who are included in the licence.


Toolgroups
----------

Toolsgroups determine how tools are grouped in the user interface. The groups that you add here will be 
reflected in the menu on the left of user interface.

**NB:** If a user has access to a tool more than once through a couple of toolsets,
they will only see the tool once in the front end.