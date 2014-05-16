import os

os.environ.update({
    "DBTYPE": "mysql",
    "DBNAME": "test_yabi",
    "DBUSER": "root",
    "DBPASS": "",
    # some tests expect these exact paths
    "TORQUE_PATH": "/opt/torque/2.3.13/bin",
    "SGE_PATH": "/opt/sge6/bin/linux-x64",
})

from yabiadmin.settings import *

DATABASES['default']['OPTIONS'] = \
    {'init_command': 'SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED'}

SWIFT_BACKEND_SEGMENT_SIZE = 1234567  # approx 1MB segments just for testing
