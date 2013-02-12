#!/bin/sh
source virt_yabiadmin/bin/activate

if [ "$YABI_CONFIG" = "" ]; then
    YABI_CONFIG="dev_mysql"
fi

case $YABI_CONFIG in
dev_mysql)
    export PYTHONPATH=yabiadmin
    export DJANGO_SETTINGS_MODULE="yabiadmin.settings"
    ;;
dev_postgres)
    export PYTHONPATH=yabiadmin
    export DJANGO_SETTINGS_MODULE="yabiadmin.postgresqlsettings"
    ;;
quickstart)
    export DJANGO_SETTINGS_MODULE="yabiadmin.quickstartsettings"
    ;;
*)
    echo "No YABI_CONFIG set, exiting"
    exit 1
esac

python -c "from django.db import models"
python -c "import $DJANGO_SETTINGS_MODULE"
echo "DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"

nosetests $@
