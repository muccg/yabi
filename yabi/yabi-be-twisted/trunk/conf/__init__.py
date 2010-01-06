# -*- coding: utf-8 -*-
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


import urlparse
import re
re_url_schema = re.compile(r'\w+')

def parse_url(uri):
    """Parse a url via the inbuilt urlparse. But this is slightly different
    as it can handle non-standard schemas. returns the schema and then the
    tuple from urlparse"""
    uri = uri.strip()
    scheme, rest = uri.split(":",1)
    assert re_url_schema.match(scheme)
    return scheme, urlparse.urlparse(rest)

SEARCH_PATH = ["~/.yabi/yabi.conf","~/.yabi/backend/yabi.conf","~/yabi.conf","~/.yabi","/etc/yabi.conf","/etc/yabi/yabi.conf"]

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

def path_sanitise(path):
    return os.path.normpath(os.path.expanduser(path))

class ConfigError(Exception):
    pass

##
## The Configuration store. Singleton.
##

class Configuration(object):
    """Holds the running configuration for the full yabi stack that is running under this twistd"""
    SECTIONS = ['backend','admin','frontend','store']       # sections of the config file
    KEYS = ['port','path','startup','sslport','ssl']
    
    # defaults
    config = {
        'backend':  {
                        "port":"0.0.0.0:8000",
                        "sslport":"0.0.0.0:8443",
                        "path":"/",
                        "startup":"true",
                        
                        "telnet":"false",
                        "telnetport":"0.0.0.0:8021",
                        
                        "fifos":"/tmp/",
                        "tasklets":"/tmp/",
                        "certificates":"/tmp/",
                        
                        "admin":None                # none means "use the one provided here"
                    },
        'admin':    {
                        "port":"0.0.0.0:8000",
                        "sslport":"0.0.0.0:8443",
                        "path":"/yabiadmin",
                        "startup":"true",
                        
                        "backend":None,
                        "store":None,
                        
                        "database":"dev",           # 'dev' or 'live'. In the future could also be 'custom' to override with a different db
                        "debug": "false"            # run the app in debug mode
                    },
        'frontend': {
                        "port":"0.0.0.0:8000",
                        "sslport":"0.0.0.0:8443",
                        "path":"/fe",
                        "startup":"true",
                        
                        "admin":None,
                        "store": None,
                    },
        'store':    {
                        "port":"0.0.0.0:8000",
                        "sslport":"0.0.0.0:8443",
                        "path":"/store",
                        "startup":"true",
                        
                        "debug": "true"             # run the app in debug mode
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
            
        # backend section
        name = "backend"
        if conf_parser.has_section(name):
            self.config[name]['admin'] = conf_parser.get(name,'admin')
            if conf_parser.has_option(name,'fifos'):
                self.config[name]['fifos'] = path_sanitise(conf_parser.get(name,'fifos'))
            if conf_parser.has_option(name,'tasklets'):
                self.config[name]['tasklets'] = path_sanitise(conf_parser.get(name,'tasklets'))
            if conf_parser.has_option(name,'certificates'):
                self.config[name]['certificates'] = path_sanitise(conf_parser.get(name,'certificates'))
            
            
        name = "admin"
        if conf_parser.has_section(name):
            self.config[name]['backend'] = conf_parser.get(name,'backend')
            self.config[name]['store'] = conf_parser.get(name,'store')
            self.config[name]['database'] = "dev" if conf_parser.has_option(name,'database') and conf_parser.get(name,'database').lower()=="dev" else "live"
            self.config[name]['debug'] = conf_parser.get(name,'debug') if conf_parser.has_option(name,'debug') else "false"

        name = "store"
        if conf_parser.has_section(name):
            self.config[name]['database'] = "dev" if conf_parser.has_option(name,'database') and conf_parser.get(name,'database').lower()=="dev" else "live"
            self.config[name]['debug'] = conf_parser.get(name,'debug') if conf_parser.has_option(name,'debug') else "false"

        name = "frontend"
        if conf_parser.has_section(name):
            self.config[name]['database'] = "dev" if conf_parser.has_option(name,'database') and conf_parser.get(name,'database').lower()=="dev" else "live"
            self.config[name]['debug'] = conf_parser.get(name,'debug') if conf_parser.has_option(name,'debug') else "false"
            self.config[name]['admin'] = conf_parser.get(name,'admin')
            self.config[name]['store'] = conf_parser.get(name,'store')
        

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
            self.config[section]['ssl'] = boolean_proc(self.config[section]['ssl'])
            self.config[section]['sslport'] = port_setting(self.config[section]['sslport'])
            
            conversions = dict( 
                telnet=boolean_proc,
                telnetport=port_setting,
                debug=boolean_proc
            )
            
            for key, value in conversions.iteritems():
                if key in self.config[section]:
                    self.config[section][key] = value(self.config[section][key])
         
    ##
    ## Methods to gather settings
    ##
    @property
    def yabiadmin(self):
        scheme,rest = parse_url(self.config['backend']['admin'])
        return "%s:%d%s"%(rest.hostname,rest.port,rest.path)
        
    @property
    def yabiadminserver(self):
        return parse_url(self.config['backend']['admin'])[1].hostname
        
    @property
    def yabiadminport(self):
        return parse_url(self.config['backend']['admin'])[1].port
    
    @property
    def yabiadminpath(self):
        return parse_url(self.config['backend']['admin'])[1].path
    
    
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