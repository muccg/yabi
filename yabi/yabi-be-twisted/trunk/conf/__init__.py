"""
Configuration
=============
follows a path, reading in config files. Overlays their settings on top of a default, on top of each other.
then stores the config in a sanitised form in a hash of hashes, inside the object.

Yabi then asks for various settings when it needs them
"""

import ConfigParser
import os.path
import re

SEARCH_PATH = [".yabi","yabi.conf","~/.yabi","~/.yabi/yabi.conf","/etc/yabi.conf","/etc/yabi/yabi.conf"]

##
## Support functions that do some text processing
##

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
    

# process boolean string into python boolean type
boolean_proc = lambda x: x.lower()=="true" or x.lower()=="t" or x.lower()=="yes" or x.lower()=="y"

##
## The Configuration store. Singleton.
##

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
                    },
        'global':   {
                        "user":"yabi",
                        "group":"yabi"
                    },
        'taskmanager':{
                        'simultaneous':'5',
                        'polldelay':'5',
                        'startup':'true'
                    }
    }
        
    @classmethod
    def read_from_file(cls,filename):
        conf_parser = ConfigParser.SafeConfigParser()
        conf_parser.read(filename)
        
        # main sections
        for section in cls.SECTIONS:
            if conf_parser.has_section(section):
                # process section
                
                if section not in cls.config:
                    cls.config[section] = {}
                
                for key in cls.KEYS:
                    if conf_parser.has_option(section,key):
                        cls.config[section][key] = conf_parser.get(section,key)
        
        # global section
        name = "global"
        if conf_parser.has_section(name):
            cls.config[name]['user'] = conf_parser.get(name,'user')
            cls.config[name]['group'] = conf_parser.get(name,'group')
            
        # taskmanager section
        name = "taskmanager"
        if conf_parser.has_section(name):
            cls.config[name]['polldelay'] = conf_parser.get(name,'polldelay')
            cls.config[name]['simultaneous'] = conf_parser.get(name,'simultaneous')
            cls.config[name]['startup'] = boolean_proc(conf_parser.get(name,'startup'))
            
    @classmethod
    def read_config(cls, search=SEARCH_PATH):
        for part in search:
            cls.read_from_file(os.path.expanduser(part))
            
    @classmethod
    def get_section_conf(cls,section):
        return cls.config[section]
    
    @classmethod
    def sanitise(cls):
        """Check the settings for sanity"""
        for section in cls.SECTIONS:
            cls.config[section]['startup'] = boolean_proc(cls.config[section]['startup'])
            cls.config[section]['port'] = port_setting(cls.config[section]['port'])
        
    
    ##
    ## Methods to gather settings
    ##
    @classmethod
    def yabiadmin(cls):
        return "%s:%d%s"%tuple(cls.config['admin']['port']+(cls.config['admin']['path'],))
    
    @classmethod
    def yabistore(cls):
        return "%s:%d%s"%tuple(cls.config['store']['port']+(cls.config['store']['path'],))
    
    