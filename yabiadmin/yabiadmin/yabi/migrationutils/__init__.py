#!/usr/bin/env python
from datetime import datetime

def add_user(orm, username, password, email, active=True, staff=False, superuser=False, created_by=None):
    user = orm['auth.user']()
    user.last_modified_by = created_by or user
    user.last_modified_on = datetime.now()
    user.created_by = created_by or user
    user.created_on = datetime.now()
    user.username = unicode(username)
    user.password = make_password_hash(password)
    user.email = email
    user.is_active = active
    user.is_staff = staff
    user.is_superuser = superuser
    return user
    
def make_password_hash(password):
    from django.contrib.auth.models import get_hexdigest
    import random
    algo = 'sha1'
    salt = get_hexdigest(algo, str(random.random()), str(random.random()))[:5]
    hsh = get_hexdigest(algo, salt, password)
    return '%s$%s$%s' % (algo, salt, hsh)
