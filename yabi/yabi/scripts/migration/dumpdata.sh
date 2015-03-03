#!/bin/bash

#RUN_ADMIN="django-admin.py"
RUN_ADMIN="sudo yabi"

dump_data() {
    $RUN_ADMIN dumpdata --all --indent=4 $1 > json_data/$1.json
}

dump_data_but_exclude() {
    $RUN_ADMIN dumpdata --all --indent=4 --exclude=$2 $1 > json_data/$1.json
}

APPS="auth sites contenttypes admin south yabi"

mkdir -p json_data

for app in $APPS; do
    echo "Exporting data from $app"
    dump_data $app
done

echo "Exporting data from yabiengine (excluding Syslog)"
dump_data_but_exclude "yabiengine" "yabiengine.Syslog"

