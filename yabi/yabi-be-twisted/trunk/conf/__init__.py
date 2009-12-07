
from urlparse import urlparse

import ConfigParser

import os.path

SEARCH_PATH = [".yabi","yabi.conf","~/.yabi","~/.yabi/yabi.conf","/etc/yabi.conf","/etc/yabi/yabi.conf"]

# we store the config inside a class
class yabiadmin(object):
    SERVER = "localhost"
    PORT = 8000
    PATH = "/yabiadmin"

    @classmethod
    def parse_url(cls,url):
        uri = "http://"+url if not urlparse(url).netloc else url
        parse = urlparse(uri)
        #print "setting yabiadmin uri to:",parse
        cls.SERVER = parse.hostname
        cls.PORT = parse.port
        cls.PATH = parse.path
    
    @classmethod
    def read_from_file(cls,filename):
        conf_parser = ConfigParser.SafeConfigParser()
        conf_parser.read(filename)
        
        cls.parse_url( 
            conf_parser.get("Servers","yabiadmin") 
                if conf_parser.has_section("Servers") and conf_parser.has_option("Servers","yabiadmin") else 
            os.environ['YABIADMIN'] 
                if 'YABIADMIN' in os.environ else
            "%s:%d%s"%(cls.SERVER,cls.PORT,cls.PATH)
        )
        
    @classmethod
    def read_config(cls, search=SEARCH_PATH):
        for part in search:
            cls.read_from_file(os.path.expanduser(part))
            
import re
def port_setting(port):
    """returns ip,port or raises exception if error"""
    re_port = re.compile(r'^(\d+\.\d+\.\d+\.\d+)(:\d+)?$')
    result = re_port.search(port)
    if result:
        ip = result.group(1)
        port = int(result.group(2)[1:]) if result.group(2) else 8000
        return ip, port
    try:
        if str(int(port))==port:
            return '0.0.0.0',int(port)
    except ValueError, ve:
        raise Exception, "malformed IP:port setting"
    
            
class Configuration(object):
    """Holds the running configuration for the full yabi stack that is running under this twistd"""
    SECTIONS = ['backend','admin','frontend','store']       # sections of the config file
    KEYS = ['port','path','startup']
    
    # defaults
    config = {
        'backend':  {
                        "port":"0.0.0.0:8000",
                        "path":"/",
                        "startup":"true"
                    },
        'admin':    {
                        "port":"0.0.0.0:8000",
                        "path":"/yabiadmin",
                        "startup":"true"
                    },
        'frontend': {
                        "port":"0.0.0.0:8000",
                        "path":"/fe",
                        "startup":"true"
                    },
        'store':    {
                        "port":"0.0.0.0:8000",
                        "path":"/store",
                        "startup":"true"
                    }
    }
    
    @classmethod
    def read_from_file(cls,filename):
        conf_parser = ConfigParser.SafeConfigParser()
        conf_parser.read(filename)
        
        for section in cls.SECTIONS:
            if conf_parser.has_section(section):
                # process section
                
                if section not in cls.config:
                    cls.config[section] = {}
                
                for key in cls.KEYS:
                    if conf_parser.has_option(section,key):
                        cls.config[section][key] = conf_parser.get(section,key)
        
    @classmethod
    def read_config(cls, search=SEARCH_PATH):
        for part in search:
            cls.read_from_file(os.path.expanduser(part))
            
    @classmethod
    def get_section_conf(cls,section)
        return cls.config[section]
    
    @classmethod
    def sanitise(cls):
        """Check the settings for sanity"""
        
    