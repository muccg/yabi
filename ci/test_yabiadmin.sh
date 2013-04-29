#!/bin/bash 
set -ex
echo $BASH_SOURCE
echo $-
./yabictl.sh install
./yabictl.sh install
mysql -v -uroot -e "drop database test_yabi;" || true
mysql -v -uroot -e "create database test_yabi default charset=UTF8;" || true
./yabictl.sh test_yabiadmin