set -ex
echo $BASH_SOURCE
echo $-
sudo rpm --import http://binaries.erlang-solutions.com/debian/erlang_solutions.asc
sudo wget -O /etc/yum.repos.d/erlang-solutons.repo http://binaries.erlang-solutions.com/rpm/centos/erlang_solutions.repo
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