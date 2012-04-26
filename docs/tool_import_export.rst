.. _tool_import_export:

Importing and Exporting Tools
=============================

It is possible to import/export tools in json format.

Exporting tools in JSON
-----------------------
In the tool listing under YabiTools you'll see the link called ``View``. This will give you an
overview of the tool including a link to ``View JSON``. Clicking on ``View JSON`` will present 
a window with a plain text JSON representation of the tool.

Importing tools in JSON
-----------------------

If you have the JSON for a tool you can use the ``Add Tool`` page to add in the tool. Go 
to: `https://127.0.0.1/yabiadmin/admin/addtool/ <https://127.0.0.1/yabiadmin/admin/addtool/>`_
or similar and paste in your JSON.

Once you have done this the tool will be added and you'll be shown the tool edit 
page. You will need to check all the details, usually you will need to change the backends 
and check things like the module settings. You will have to add the new tool to the appropriate 
:ref:`toolsets_and_toolgroups` etc.
