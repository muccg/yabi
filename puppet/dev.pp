#
node default {
  include ccgcommon
  include ccgcommon::source
  include ccgapache
  include python
  include repo::epel
  include repo::ius
  include repo::pgrpms
  include repo::ccgtesting

  class {'postgresql':
    datadir              => '/var/lib/pgsql/9.3/data',
    bindir               => '/usr/pgsql-9.3/bin',
    client_package_name  => 'postgresql93',
    server_package_name  => 'postgresql93-server',
    devel_package_name   => 'postgresql93-devel',
    service_name         => 'postgresql-9.3',
  }

  include postgresql::devel

  # mysql databases
  class { 'mysql::server':
    #root_password    => 'test',
  }
  mysql::db { 'dev_yabi':
    user     => 'yabiapp',
    password => 'yabiapp'
  }
  mysql::db { 'test_yabi':
    user     => 'yabiapp',
    password => 'yabiapp'
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

  # fakes3 is required for tests
  package {"fakes3":
    ensure     => installed,
    provider   => gem
  }

  file {'/etc/rabbitmq/rabbitmq.config':
    ensure  => present,
    # Configure disk space low watermark quite low because dev images
    # usually have small filesystems.
    content => "[{rabbit, [{disk_free_limit, 100000000}]}].\n",
    require => Package[$packages]
  } ->

  service { 'rabbitmq-server':
    ensure     => 'running',
    enable     => true,
    hasstatus  => true,
    hasrestart => true,
    name       => 'rabbitmq-server',
    require    => Package[$packages]
  }
}
