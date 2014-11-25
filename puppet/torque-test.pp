#
node default {
  include ccgcommon
  include ccgcommon::source
  include python
  include ccgapache
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
  include environmentmodules

  class {'torque':
    user => 'ec2-user'
  }

  class {'monit::packages':
    packages => ['rsyslog', 'sshd'],
  }

  file {'/home/ec2-user/.ssh':
    ensure => directory,
    owner  => 'ec2-user',
    group  => 'ec2-user',
    mode   => '0600',
  }

  file {['/opt', '/opt/yabidata', '/opt/yabidata/demo']:
    ensure => directory,
    owner  => 'ec2-user',
    group  => 'ec2-user',
    mode   => '0600',
  }

}
