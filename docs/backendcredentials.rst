.. index::
   single: backend credentials

.. _backendcredentials:

Backend Credentials
===================

Backend Credentials is a linking table between a Credential and a Backend, used simply because a user 
may have one credential (say an SSH key) that is valid across multiple backends.

.. index::
   single: backend credentials; adding

Adding Backend Credentials
--------------------------

 * Add a Backend Credential and select the Backend and associated Credential.
 * Add the users home directory or subdirectory (see :ref:`a_note_about_the_path_field` for details).
 * Check `Visible` so the backend will appear to the user.
 * Select Default Stageout to indicate that this user's job results should stageout to this filesystem


.. index::
   single: backend credentials; default stageout 

.. _defaultstageout:

Default Stageout Explained
--------------------------

Yabi uses Default Stageout as a single directory where all the user's results will be staged out to. Each user 
should only have one default stageout, usually on a file server they have access to from outside of Yabi i.e. via ssh


What the user will see
----------------------

At this point if everything has worked the user should be able to log into Yabi and under the Files 
tab they will be able to see and view files on the backends you have set up.
