set -ex
echo $BASH_SOURCE
echo $-
echo installing erlang
sudo yum install erlang
wget http://www.rabbitmq.com/releases/rabbitmq-server/v3.1.3/rabbitmq-server-3.1.3-1.noarch.rpm
sudo rpm --import http://www.rabbitmq.com/rabbitmq-signing-key-public.asc
echo installing rabbitmq rpm
sudo yum install rabbitmq-server-3.1.3-1.noarch.rpm
sudo yum install python-devel
sudo yum install -y mysql-server-5.1.69-1.el6_4.x86_64
sudo yum install -y postgresql-devel libxslt-devel libxml2-devel
sudo service mysqld restart
sudo /sbin/service rabbitmq-server start