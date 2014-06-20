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
  include ccgdatabase::mysql::devel
  include ccgdatabase::postgresql::devel

  # mysql databases
  ccgdatabase::mysql::db { 'dev_yabi': user => 'yabiapp', password => 'yabiapp' }
  ccgdatabase::mysql::db { 'test_yabi': user => 'yabiapp', password => 'yabiapp' }

  # postgresql databases/users
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
