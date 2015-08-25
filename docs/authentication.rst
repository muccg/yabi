.. _authentication:

Yabi Authentication
===================

Yabi currently supports the following authentication methods:

    - Database Authentication - this is the default
    - LDAP Authentication
    - Kerberos and LDAP Authentication


Database Authentication
-----------------------

When using database authentication users and all their details (including passwords) are stored in the database.  
This is very similar to Django's ModelBackend with the only difference that Yabi usernames are case insensitive.  

This is the default authentication, therefore to use this you don't have to configure anything.  
You will have to manually create all users using the Yabi Administration interface. See :ref:`addingusers`.

LDAP Authentication
-------------------

This setup is a good choice if you already have users set up in a central LDAP repository and you would like them to use the same password to log in to Yabi.
Another benefit is that you won't have to manually add all users to Yabi.

You will need 2 special LDAP User Groups, the Yabi Users group and the Yabi Administrators group.
Members of the Yabi User group will have access to Yabi, members of the Yabi Administrators group will have access to Yabi and the Yabi Administration Interface.

After you've created these 2 groups, adding users to Yabi is as simple as adding your LDAP users to one of these groups.
Yabi user accounts will be automatically created in the database when the user logs in the first time into Yabi. Additionally the user's name and email is also fetched from LDAP and set in the database.

Group membership can be defined either on the user object or on the group object. The user objects can have their ``AUTH_LDAP_MEMBER_OF_ATTR`` attribute (typically *"memberOf"* or similar) to the DN of a group(s) they are member of. From the other end the group object can have their ``AUTH_LDAP_MEMBER_ATTR`` attribute (typically *"uniqueMember"*, or *"member"*) to the DN of the user(s) that are members of this group.
As long as these settings are set correctly Yabi will check both ends to check for group membership, therefore you can have some users having their groups set on the user object, others on the group object etc.

To set up LDAP authentication you will have to configure the following settings in your :ref:`settings`.

Required settings:
^^^^^^^^^^^^^^^^^^

==============================  ===============
Setting                          Description
==============================  ===============
AUTH_TYPE                       Authenticaton type. Set it to *"ldap"*.
AUTH_LDAP_SERVER                List of at least 1 ldap servers. Servers will be tried in order. Ex. *["ldaps://ldap1.your.domain", "ldap://ldap2.your.domain"]*
AUTH_LDAP_USER_BASE             Parent DN of place where your users are stored. Ex. *"ou=People, dc=your_domain"*
AUTH_LDAP_YABI_GROUP_DN         DN of the Yabi user group. Ex. *"cn=Yabi, ou=Groups, dc=your_domain"*
AUTH_LDAP_YABI_ADMIN_GROUP_DN   DN of the Yabi Administrators user group. Ex. *"cn=Yabi Administrators, ou=Groups, dc=your_domain"*
==============================  ===============

Optional settings:
^^^^^^^^^^^^^^^^^^

All these settings but ``AUTH_LDAP_SYNC_USER_ON_LOGIN`` are provided for cases when your LDAP config differs from the standard, therefore in most cases you wouldn't want to change them.

====================================  ===============
Setting                                Description
====================================  ===============
AUTH_LDAP_SYNC_USER_ON_LOGIN           If ``True`` each time a user logs in fetch their details (name, email, is a Yabi Administrator) and set it in the database. Otherwise setting the database values from LDAP happens only the first time the user logs in. Default is ``True``.
AUTH_LDAP_USER_FILTER                  LDAP search filter used when searching for your users in AUTH_LDAP_USER_BASE. Default is *"(objectclass=person)"*.
AUTH_LDAP_MEMBER_ATTR                  LDAP group attribute used to add members to a group. Default is *"uniqueMember"*.
AUTH_LDAP_MEMBER_ATTR_HAS_USER_ATTR    The User object's attribute that is stored in the AUTH_LDAP_MEMBER_ATTR above. Can be *"username"* or *"dn"*. Default is *"dn"*.
AUTH_LDAP_MEMBER_OF_ATTR               LDAP user attribute used to add members to a group. Default is *"memberOf"*.
AUTH_LDAP_USERNAME_ATTR                LDAP user attribute for username. Default is *"uid"*.
AUTH_LDAP_EMAIL_ATTR                   LDAP user attribute for email. Default is *"mail"*.
AUTH_LDAP_LASTNAME_ATTR                LDAP user attribute for last name. Default is *"sn"*.
AUTH_LDAP_FIRSTNAME_ATTR               LDAP user attribute for first name. Default is *"givenName"*.
AUTH_LDAP_REQUIRE_TLS_CERT             Require server to have a valid TLS certificate. Default is True.
====================================  ===============


Kerberos and LDAP Authentication
--------------------------------

This authentication method is very similar to the LDAP authentication method above.
The only difference is that the username and password will be checked against your Kerberos server not your LDAP server.

After that everything described in LDAP authentication applies.
Users will have to be members of the Yabi and/or Yabi Administrator LDAP groups to be able to log in into Yabi.
The database user accounts will be created automatically on first login, the user detail will be fetched from LDAP and set in the database at that time and on each login if ``AUTH_LDAP_SYNC_USER_ON_LOGIN`` is set.

To set up *Kerberos and LDAP* authentication you will have to configure all the settings in the LDAP authentication section **and** the following setting in your :ref:`settings`.

==============================  ===============
Setting                          Description
==============================  ===============
AUTH_TYPE                        Authentication type. Set it to *"kerberos+ldap"*.
AUTH_KERBEROS_REALM              Your Kerberos realm. Ex. *"CCGMURDOCH"*.
==============================  ===============

*Note*: For Kerberos Authentication to work properly the Kerberos must be configured properly on this machine.
That will likely mean ensuring that the edu.mit.Kerberos preference file has the correct realms and KDCs listed.


Fallback on Database Authentication
-----------------------------------

When the setting ``AUTH_ENABLE_DB_FALLBACK`` is set to ``True`` (default), your users will always be authenticated against the database as the last step, if the main authentication method failed.

This feature can be useful to avoid being locked out of Yabi if there is some temporary problem with your LDAP or Kerberos server.
In case you have an admin user in the Database you will always be able to log in into Yabi using that user if ``AUTH_ENABLE_DB_FALLBACK`` is set to ``True```.

