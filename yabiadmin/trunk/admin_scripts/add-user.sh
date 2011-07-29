#!/bin/bash

. functions.sh

login

echo -n "New username: "
read NEW_USERNAME

request -X POST -H "Content-Type: application/json; charset=UTF-8" --data-binary "{\"data\": {\"name\": \"$NEW_USERNAME\"}}" $SERVER/admin/yabi/user/ext/json

logout
