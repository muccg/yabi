#!/bin/sh
source virt_yabiadmin/bin/activate
export DJANGO_SETTINGS_MODULE="yabiadmin.settings"
export TEST_CONFIG="dev_mysql"
nosetests $@
