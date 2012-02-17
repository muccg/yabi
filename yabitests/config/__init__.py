import os, ConfigParser


class Configuration(object):

    def __init__(self, section='default'):
        self.config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "tests.conf" )
        self.section = section

        cp = ConfigParser.ConfigParser()
        cp.readfp(open(self.config_file))
        self.username = cp.get(self.section, 'username')
        self.password = cp.get(self.section, 'password')
        self.yabiurl = cp.get(self.section, 'yabiurl')
        self.test_data_dir = cp.get(self.section, 'test_data_dir')

