#
node default {
  include ccgcommon
  include ccgcommon::source
  include python
  include ccgapache
  include postgresql::devel
  include mysql::devel
  include environmentmodules

  class {'repo':
    enable_epel        => true,
    enable_ccgtesting  => true
  }

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
