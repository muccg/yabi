#!/bin/bash

. functions.sh

login
request $SERVER/admin/yabi/tool/ext/json

logout
