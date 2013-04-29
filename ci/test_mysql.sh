#!/bin/bash -ex
./yabictl.sh install
mysql -v -uroot -e "drop database test_yabi;" || true
mysql -v -uroot -e "create database test_yabi default charset=UTF8;"
./yabictl.sh test_mysql
