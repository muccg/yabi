#!/usr/bin/env python
import os
import sys
import pwd

production_user = "apache"

if production_user:
    (uid, gid, gecos, homedir) = pwd.getpwnam(production_user)[2:6]
    try:
        os.setgid(gid)
        os.setuid(uid)
    except OSError as e:
        sys.stderr.write("%s\nThis program needs to be run as the " % e)
        sys.stderr.write("%s user, or root.\n" % production_user)
        sys.exit(1)
    else:
        os.environ["HOME"] = homedir

if __name__ == "__main__":
    if production_user:
        # prepare the settings module for the django app
        from ccg_django_utils.conf import setup_prod_env
        setup_prod_env("yabi")
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yabi.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
