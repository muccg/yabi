#!/bin/bash

. functions.sh

login
request $SERVER/admin/yabi/user/ext/json

logout
