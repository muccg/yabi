#
node default {
  include ccgcommon
  include ccgcommon::source
  include python
  include ccgapache
  include repo::epel
  include repo::ius
  include repo::pgrpms
  include repo::ccgtesting
  include ccgdatabase::mysqldevel

  class {'postgresql':
    datadir              => '/var/lib/pgsql/9.3/data',
    bindir               => '/usr/pgsql-9.3/bin',
    client_package_name  => 'postgresql93',
    server_package_name  => 'postgresql93-server',
    devel_package_name   => 'postgresql93-devel',
    service_name         => 'postgresql-9.3',
  }

  include postgresql::devel

  class {'monit::packages':
    packages => ['rsyslog', 'sshd'],
  }

  # mysql databases
  class { 'mysql::server':
    config_hash => { root_password => '' }
  }
  mysql::db { 'dev_yabi':
    user     => 'yabiapp',
    password => 'yabiapp',
  }
  mysql::db { 'test_yabi':
    user     => 'yabiapp',
    password => 'yabiapp',
  }

  # postgresql databases/users
  ccgdatabase::postgresql{'dev_yabi': user => 'yabiapp', password => 'yabiapp'}
  postgresql::db { 'test_yabi':
    user     => 'yabiapp',
    password => 'yabiapp',
    require  => Postgresql::Database_User['yabiapp'],
  }

  # Package deps for yabi
  case $::osfamily {
    'RedHat', 'Linux': {
      $packages = [
        'rabbitmq-server',
        'openldap-devel',
        'openssl-devel',
        'libxslt-devel',
        'libxml2-devel',
        'libxml2',
        'libxslt']
    }
    'Debian': {
      $packages = [
        'rabbitmq-server',
        'libldap2-dev',
        'libssl-dev',
        'libxml2-dev',
        'libxslt1-dev']
    }
  }
  package {$packages: ensure => installed}

  # Still flavour specific
  if ($::osfamily == 'RedHat') {
    $torque_packages = ['torque', 'torque-mom', 'torque-server', 'torque-client', 'torque-scheduler']
    package {$torque_packages: ensure => installed }
  }

  package {"fakes3":
    ensure     => installed,
    provider   => gem
  }

  file {'/home/ec2-user/.ssh':
      ensure => directory,
      owner  => 'ec2-user',
      group  => 'ec2-user',
      mode   => '0600',
  }

  service { 'rabbitmq-server':
    ensure     => 'running',
    enable     => true,
    hasstatus  => true,
    hasrestart => true,
    name       => 'rabbitmq-server',
    require    => Package[$packages]
  }
}
