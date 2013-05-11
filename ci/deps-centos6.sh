set -ex
echo $BASH_SOURCE
echo $-
sudo yum install -y libevent-devel
sudo yum install -y mysql-server-5.1.69-1.el6_4.x86_64
sudo yum install -y postgresql-devel
sudo service mysqld restart
