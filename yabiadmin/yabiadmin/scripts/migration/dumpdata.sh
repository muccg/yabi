#!/bin/bash

#RUN_ADMIN="django-admin.py"
RUN_ADMIN="sudo yabiadmin"

dump_data() {
    $RUN_ADMIN dumpdata --all --indent=4 $1 > json_data/$1.json
}

APPS="auth sites contenttypes admin south yabi yabiengine"

mkdir -p json_data

for app in $APPS; do
    echo "Exporting data from $app"
    dump_data $app
done

