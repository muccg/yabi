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

class ConfigError(Exception):
    pass

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
                        "startup":"true",
                        
                        "admin":None                # none means "use the one provided here"
                    },
        'admin':    {
                        "port":"0.0.0.0:8000",
                        "path":"/yabiadmin",
                        "startup":"true",
                        
                        "backend":None,
                        "store":None,
                    },
        'frontend': {
                        "port":"0.0.0.0:8000",
                        "path":"/fe",
                        "startup":"true",
                        
                        "admin":None
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
        
    def read_from_file(self,filename):
        conf_parser = ConfigParser.SafeConfigParser()
        conf_parser.read(filename)
        
        # main sections
        for section in self.SECTIONS:
            if conf_parser.has_section(section):
                # process section
                
                if section not in self.config:
                    self.config[section] = {}
                
                for key in self.KEYS:
                    if conf_parser.has_option(section,key):
                        self.config[section][key] = conf_parser.get(section,key)
        
        # global section
        name = "global"
        if conf_parser.has_section(name):
            self.config[name]['user'] = conf_parser.get(name,'user')
            self.config[name]['group'] = conf_parser.get(name,'group')
            
        # taskmanager section
        name = "taskmanager"
        if conf_parser.has_section(name):
            self.config[name]['polldelay'] = conf_parser.get(name,'polldelay')
            self.config[name]['simultaneous'] = conf_parser.get(name,'simultaneous')
            self.config[name]['startup'] = boolean_proc(conf_parser.get(name,'startup'))
            
    def read_config(self, search=SEARCH_PATH):
        for part in search:
            self.read_from_file(os.path.expanduser(part))
            
    def get_section_conf(self,section):
        return self.config[section]
    
    def sanitise(self):
        """Check the settings for sanity"""
        for section in self.SECTIONS:
            self.config[section]['startup'] = boolean_proc(self.config[section]['startup'])
            self.config[section]['port'] = port_setting(self.config[section]['port'])
        
    
    ##
    ## Methods to gather settings
    ##
    @property
    def yabiadmin(self):
        return "%s:%d%s"%tuple(self.config['admin']['port']+(self.config['admin']['path'],))
    
    @property
    def yabistore(self):
        return "%s:%d%s"%tuple(self.config['store']['port']+(self.config['store']['path'],))
    
    
    ##
    ## classify the settings into a ip/port based classification
    ##
    def classify_ports(self):
        ips = {}
        for section in self.SECTIONS:
            ip, port = self.config[section]['port']
            
            # ip number
            ipstore = ips[ip] if ip in ips else {}
            
            # then port
            portstore = ipstore[port] if port in ipstore else {}
            
            # then path
            path = self.config[section]['path']
            if path in portstore:
                # error. duplicate path
                raise ConfigError, "overlapping application paths"
            
            portstore[path] = section
            
            ipstore[port] = portstore
            ips[ip] = ipstore
            
        return ips
    
config = Configuration()