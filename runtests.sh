#!/bin/sh
source virt_yabiadmin/bin/activate
export DJANGO_SETTINGS_MODULE="yabiadmin.settings"
nosetests $@
