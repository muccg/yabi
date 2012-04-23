.. _logging:

Logging
=======

Yabi uses the standard Python and Django logging mechanisms and is controlled by the logging section in the :ref:`settings`.
If you wish to add file logging for instance you would need to add a file logging handler to the handlers section and then add
name of the handler into the yabiadmin logger section. For further details consult these pages:

`http://docs.python.org/library/logging.html <http://docs.python.org/library/logging.html>`_

`https://docs.djangoproject.com/en/1.4/topics/logging/ <https://docs.djangoproject.com/en/1.4/topics/logging/>`_