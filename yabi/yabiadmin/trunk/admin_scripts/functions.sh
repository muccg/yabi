#!/bin/bash

COOKIE_FILE=`tempfile`
CURL=curl
SERVER=https://faramir.localdomain/yabiadmin/snapshot

cleanup () {
    rm -f $COOKIE_FILE >& /dev/null
}

login () {
    echo -n "Username [$USER]: "
    read YABI_USERNAME

    if [ "x$YABI_USERNAME" = 'x' ]
    then
        YABI_USERNAME="$USER"
    fi

    echo -n "Password: "
    stty -echo
    read YABI_PASSWORD
    stty echo
    echo

    request --data-urlencode "username=$YABI_USERNAME" --data-urlencode "password=$YABI_PASSWORD" -s $SERVER/ws/login | grep '"success": true' > /dev/null

    if [ $? -ne 0 ]
    then
        echo 'ERROR: Unable to log in.'
        cleanup
        exit 1
    fi
}

logout () {
    $CURL -k $CURLOPTS $SERVER/ws/logout >& /dev/null
    cleanup
}

request () {
    $CURL -k -b "$COOKIE_FILE" -c "$COOKIE_FILE" -H "X-Requested-With: XMLHttpRequest" "$@"
}
