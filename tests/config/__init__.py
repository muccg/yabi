from __future__ import print_function
import os, ConfigParser


class Configuration(object):

    def __init__(self, filename=None, section=None):
        config_dir = os.path.dirname(os.path.realpath(__file__))
        default_config_file = os.path.join(config_dir, "tests.conf")
        self._load_conf_file(default_config_file, section)
        if filename:
            self._load_conf_file(filename, section)

    def _load_conf_file(self, filename=None, section=None):
        print("Loading config file: %s" % filename)
        cp = ConfigParser.ConfigParser()
        cp.readfp(open(filename))
        self._load_section(cp, "DEFAULT")
        if section:
            self._load_section(cp, section)

    def _load_section(self, cp, section):
        print("Loading config section: %s" % section)
        for attr, key in self.configs:
            option = key or attr
            if cp.has_option(section, option):
                setattr(self, attr, cp.get(section, option))

    configs = (
        ("yabidir", "yabi_dir"),
        ("yabish", "yabish"),
        ("yabiusername", "yabi_username"),
        ("yabipassword", "yabi_password"),
        ("yabiadminusername", "yabi_admin_username"),
        ("yabiadminpassword", "yabi_admin_password"),
        ("yabiurl", "yabi_url"),
        ("jsondir", "json_dir"),
        ("tmpdir", "tmp_dir"),
        ("testdatadir", "test_data_dir"),
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
