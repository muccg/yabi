.. index::
   single: credentials

.. _credentials:

Credentials
===========

Any tasks carried out by Yabi are always run **as the user** not as Yabi. For this reason Yabi needs to be able
store and make use of user credentials.

.. index::
   single: encryption

A note about encryption
^^^^^^^^^^^^^^^^^^^^^^^
All credentials are stored encrypted within the Yabi system. This includes within the database and within memcache or other caching mechanisms.
When you enter details into the Add Credential screen in plain text, they are encrypted before they are added to the database.

Encryption uses one of the following. If data has been newly added it is encrypted using the SECRET_KEY in the ``settings.py`` file (see :ref:`settings`).
As soon as a user logs in any of their credentials that are encrypted with the SECRET_KEY are decypted and stored re-encrypted using their Yabi password.

How credentials are used by the backend
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
When a user logs into Yabi, their password is used to decrypt their credentials, which are then re-encrypted with the SECRET_KEY from the ``settings.py`` file
and temporarily stored in memcache or other caching system. When the backend then needs access to a resource, it is able to get the credential from memcache and 
decrypt it with the SECRET_KEY so it can use it.

In this way the credentials are stored **encrypted** both permanently (in database) and temporarily (in memcache).


Adding Credentials
------------------

In the Yabi Credential table select Add Credential and fill in the form for each user's credential. Not all the fields
will be needed, depending on the credential type.

**Description:** A name or description to identify the credential to the administrator.

**Username:** This is the username on the backend that the credential matches. This may be different than the Yabi username.
For example in Yabi my username may be andrew while on a cluster my username may be amacgregor.

**Password:** The password for the credential, either for the key itself or for the backend matching this credential.

**Cert:** The certificate for the matching backend.

**Key:** The key for the matching backend.

**User:** The Yabi user that this credential belongs to.

**Expires On:** An expiry date for the credential. At the moment the expiry date is required. If the key does not have one just pick a date far in the future.

Credential Actions
------------------

On the screen listing all Credentials there are several actions that can be taken using the Action dropdown near
the top left of the screen.

**Cache:** Will decrypt credentials and cache them in memcache. NB: You must know the login password that has encrypted the credentials.

**Delete:** Will delete credentials.

**Duplicate**: Will make a copy, again you must know the login password that has encrypted the credentials.

**Purge**: Will remove the credentials from memcache.

