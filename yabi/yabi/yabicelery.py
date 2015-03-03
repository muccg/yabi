#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
import os

from celery.__main__ import main

# prepare environment variables
from ccg_django_utils.conf import setup_prod_env
setup_prod_env("yabi")
os.environ["YABI_CELERY_WORKER"] = "1"

if __name__ == '__main__':
    sys.argv[0] = sys.argv[0].replace("yabicelery", "celery")
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
