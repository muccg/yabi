# Yabi - a sophisticated online research environment for Grid, High Performance and Cloud computing.
# Copyright (C) 2015  Centre for Comparative Genomics, Murdoch University.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
