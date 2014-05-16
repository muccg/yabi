import os

os.environ.update({
    "DBTYPE": "pgsql",
    "DBNAME": "test_yabi",
    "DBUSER": "yabiapp",
    "DBPASS": "yabiapp",
    # some tests expect these exact paths
    "TORQUE_PATH": "/opt/torque/2.3.13/bin",
    "SGE_PATH": "/opt/sge6/bin/linux-x64",
})

from yabiadmin.settings import *

SWIFT_BACKEND_SEGMENT_SIZE = 1234567  # approx 1MB segments just for testing
