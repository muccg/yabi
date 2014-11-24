#
node default {
  include ccgcommon
  include ccgcommon::source
  include python
  include ccgapache
  include repo::ius
  include repo::pgrpms
  include repo::ccgtesting
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
