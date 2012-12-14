#!/bin/sh
source virt_yabiadmin/bin/activate
export DJANGO_SETTINGS_MODULE="yabiadmin.settings"

export YABI_CONFIG="dev_mysql"
export YABI_CONFIG="dev_postgres"
export YABI_CONFIG="quickstart"

nosetests $@
