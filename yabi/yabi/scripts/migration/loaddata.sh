#!/bin/bash

#RUN_ADMIN="django-admin.py"
RUN_ADMIN="sudo yabi"

flush_data() {
    $RUN_ADMIN dbshell < $1
}

flush_all_data() {
    echo "Flushing data - full db"
    flush_data flushdb.sql 
}

flush_yabi_data() {
    echo "Flushing (only Yabi) data"
    flush_data flushyabidb.sql
}

load_data() {
    echo "Loading data into $1"
    $RUN_ADMIN loaddata json_data/$1.json
}

# Main

APPS_FIRST_PHASE="sites contenttypes auth"
APPS_SECOND_PHASE="yabi yabiengine admin south"

flush_all_data

for app in $APPS_FIRST_PHASE; do
    load_data $app
done

# Importing auth users create yabi users
# Easiest is to just flush the yabi tables again after we imported the auth users
flush_yabi_data

for app in $APPS_SECOND_PHASE; do
    load_data $app
done

