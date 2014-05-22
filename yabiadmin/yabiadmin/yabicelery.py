#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys

from celery.__main__ import main

# prepare environment variables
from ccg_django_utils.conf import setup_prod_env
setup_prod_env("yabiadmin", config_file="/etc/yabiadmin/yabicelery.conf")

if __name__ == '__main__':
    sys.argv[0] = sys.argv[0].replace("yabicelery", "celery")
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
