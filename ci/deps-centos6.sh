#!/bin/bash 
set -ex
echo $BASH_SOURCE
echo $-
sudo yum install -y libevent-devel
sudo yum install -y mysql-server
sudo yum install -y postgresql-devel
sudo service mysqld restart
