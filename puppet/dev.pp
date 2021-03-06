#
node default {
  # rabbitmq fails to start without this set in dev
  $custom_hostname = 'localhost'

  include ccgcommon
  include ccgcommon::source
  include ccgapache
  include python
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
        'libxslt',
        'pcre',
        'pcre-devel']
    }
    'Debian': {
      $packages = [
        'rabbitmq-server',
        'libldap2-dev',
        'libssl-dev',
        'libxml2-dev',
        'libxslt1-dev',
        'libpcre3',
        'libpcre3-dev']
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
