#!/bin/bash

. functions.sh

login

echo -n "New username: "
read NEW_USERNAME

request -X POST --data-urlencode "={'username': '$NEW_USERNAME'}" $SERVER/admin/yabi/user/ext/json

logout
