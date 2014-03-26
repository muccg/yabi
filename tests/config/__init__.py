from __future__ import print_function
import os, ConfigParser


class Configuration(object):

    def __init__(self, section='DEFAULT'):
        self.config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "tests.conf" )
        print("Loading config section: %s" % section)
        self.load(section)

    configs = (
        ("yabiusername", "yabi_username"),
        ("yabipassword", "yabi_password"),
        ("yabiadminusername", "yabi_admin_username"),
        ("yabiadminpassword", "yabi_admin_password"),
        ("yabiurl", "yabi_url"),
        ("yabibeurl", "yabibe_url"),
        ("jsondir", "json_dir"),
        ("tmpdir", "tmp_dir"),
        ("testdatadir", "test_data_dir"),
        ("dbrebuild", "db_rebuild"),
        ("yabidir", "yabi_dir"),
        ("yabish", "yabish"),
        ("startyabi", "startyabi"),
        ("stopyabi", "stopyabi"),
        ("stopyabibe", "stopyabibe"),
        ("startyabibe", "startyabibe"),
        ("cleanyabi", "cleanyabi"),
        ("yabistatus", "yabistatus"),
        ("s3_host", None),
        ("s3_port", None),
        ("s3_user", None),
        ("s3_bucket", None),
        ("aws_access_key_id", None),
        ("aws_secret_access_key", None),
        ("keystone_host", None),
        ("swift_tenant", None),
        ("swift_username", None),
        ("swift_password", None),
        ("swift_bucket", None),
    )

    def load(self, section):
        cp = ConfigParser.ConfigParser()
        cp.readfp(open(self.config_file))
        for attr, key in self.configs:
            setattr(self, attr, cp.get(section, key or attr))
