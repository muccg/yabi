# -*- coding: utf-8 -*-

"""setup the shell environment to mimic the config settings in a yabi conf file."""

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))                  # add our parent directory to the pythonpath

from conf import config
config.read_config()
config.sanitise()

NAME = sys.argv[1]

# configure up our YABISTORE and YABIADMIN env variables for the django application
if 'store' in config.config[NAME]:
    os.environ['YABISTORE'] = config.config[NAME]['store']
if 'admin' in config.config[NAME]:
    os.environ['YABIADMIN'] = config.config[NAME]['admin']
if 'backend' in config.config[NAME]:
    os.environ['YABIBE'] = config.config[NAME]['backend']



# Environment setup for your Django project files:
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

# custom database settings
os.environ['CUSTOMDB']='1'
for setting in ['database_engine', 'database_name', 'database_user', 'database_password', 'database_host', 'database_port','auth_ldap_server', 'auth_ldap_user_base','auth_ldap_group_base','auth_ldap_group','auth_ldap_default_group']:
    os.environ[setting.upper()] = config.config[NAME][setting]

if 'http_redirect_to_https' in config.config[NAME]:
    os.environ['HTTP_REDIRECT_TO_HTTPS'] = config.config[NAME]['http_redirect_to_https']
if 'http_redirect_to_https_port' in config.config[NAME]:
    os.environ['HTTP_REDIRECT_TO_HTTPS_PORT'] = config.config[NAME]['http_redirect_to_https_port']

if config.config[NAME]["debug"]:
    os.environ['DJANGODEBUG'] = '1'
    
# admin email
if config.config[NAME]["alert_email"]:
    os.environ['ADMIN_EMAIL_NAME'],os.environ['ADMIN_EMAIL'] = config.config[NAME]["alert_email"]

for envname in [    'YABISTORE','YABIADMIN','YABIBE','DJANGO_SETTINGS_MODULE', 'CUSTOMDB', 
                    'HTTP_REDIRECT_TO_HTTPS', 'HTTP_REDIRECT_TO_HTTPS_PORT', 'DJANGODEBUG', 'ADMIN_EMAIL_NAME', 'ADMIN_EMAIL',
                    'database_engine', 'database_name', 'database_user', 'database_password', 'database_host', 'database_port',
                    'auth_ldap_server', 'auth_ldap_user_base','auth_ldap_group_base','auth_ldap_group','auth_ldap_default_group'
               ]:
    if envname.upper() in os.environ:
        print '%s="%s"'%(envname.upper(),os.environ[envname.upper()])
