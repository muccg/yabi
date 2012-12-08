import os, ConfigParser


class Configuration(object):

    def __init__(self, section='default'):
        self.config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "tests.conf" )
        self.section = section

        cp = ConfigParser.ConfigParser()
        cp.readfp(open(self.config_file))
        self.yabiusername = cp.get(self.section, 'yabi_username')
        self.yabipassword = cp.get(self.section, 'yabi_password')
        self.yabiadminusername = cp.get(self.section, 'yabi_admin_username')
        self.yabiadminpassword = cp.get(self.section, 'yabi_admin_password')
        self.yabiurl = cp.get(self.section, 'yabi_url')
        self.yabibeurl = cp.get(self.section, 'yabibe_url')
        self.jsondir = cp.get(self.section, 'json_dir')
        self.tmpdir = cp.get(self.section, 'tmp_dir')
        self.testdatadir = cp.get(self.section, 'test_data_dir')
        self.dbrebuild = cp.get(self.section, 'db_rebuild')
        self.timeout = cp.get(self.section, 'timeout')
        self.yabidir = cp.get(self.section, 'yabi_dir')
        self.yabish = cp.get(self.section, 'yabish')
