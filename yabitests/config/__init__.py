import os, ConfigParser


class Configuration(object):

    def __init__(self, section='DEFAULT'):
        self.config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "tests.conf" )
        print "Loading config section: %s" % section
        self.load(section)

    def load(self, section):
        cp = ConfigParser.ConfigParser()
        cp.readfp(open(self.config_file))
        self.yabiusername = cp.get(section, 'yabi_username')
        self.yabipassword = cp.get(section, 'yabi_password')
        self.yabiadminusername = cp.get(section, 'yabi_admin_username')
        self.yabiadminpassword = cp.get(section, 'yabi_admin_password')
        self.yabiurl = cp.get(section, 'yabi_url')
        self.yabibeurl = cp.get(section, 'yabibe_url')
        self.jsondir = cp.get(section, 'json_dir')
        self.tmpdir = cp.get(section, 'tmp_dir')
        self.testdatadir = cp.get(section, 'test_data_dir')
        self.dbrebuild = cp.get(section, 'db_rebuild')
        self.yabidir = cp.get(section, 'yabi_dir')
        self.yabish = cp.get(section, 'yabish')
        self.startyabi = cp.get(section, 'startyabi')
        self.stopyabi = cp.get(section, 'stopyabi')
        self.stopyabibe = cp.get(section, 'stopyabibe')
        self.startyabibe = cp.get(section, 'startyabibe')
        self.cleanyabi = cp.get(section, 'cleanyabi')
        self.yabistatus = cp.get(section, 'yabistatus')
