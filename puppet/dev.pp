#
node default {
<<<<<<< HEAD
  # rabbitmq fails to start without this set in dev
  $custom_hostname = 'localhost'

=======
>>>>>>> 909d81c7f7953a3bfadeb5c0525f54e0cac24b48
  include ccgcommon
  include ccgcommon::source
  include ccgapache
  include python
<<<<<<< HEAD
  include repo
  include repo::upgrade
  include repo::repo::ius
  include repo::repo::ccgtesting
  include repo::repo::ccgdeps
  class { 'yum::repo::pgdg93':
    stage => 'setup',
  }
  include ccgdatabase::postgresql::devel
  include ccgdatabase::mysql::devel

  # mysql databases
  ccgdatabase::mysql::db { 'dev_yabi': user => 'yabiapp', password => 'yabiapp' }
  ccgdatabase::mysql::db { 'test_yabi': user => 'yabiapp', password => 'yabiapp' }

  # postgresql databases
  ccgdatabase::postgresql::db {'dev_yabi': user => 'yabiapp', password => 'yabiapp'}
  ccgdatabase::postgresql::db {'test_yabi': user => 'yabiapp', password => 'yabiapp'}
=======
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
>>>>>>> 909d81c7f7953a3bfadeb5c0525f54e0cac24b48

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
