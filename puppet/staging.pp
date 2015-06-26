#
node default {
  $custom_hostname = 'aws-syd-yabi-staging.ec2.ccgapps.com.au'

  include ccgcommon
  include ccgcommon::source
  include ccgapache
  include python
  include repo::sydney
  include repo::upgrade
  include repo::clean
  include repo::repo::ius
  include repo::repo::ccgtesting
  include repo::repo::ccgdeps
  class { 'yum::repo::pgdg93':
    stage => 'setup',
  }
  include ccgdatabase::postgresql::devel
  include profile::rsyslog

  class { 'memcached':
    max_memory => '12%'
  }

  # There are some leaked local secrets here we don't care about
  $django_config = {
    deployment  => 'staging',
    dbdriver    => 'django.db.backends.postgresql_psycopg2',
    dbhost      => '',
    dbname      => 'yabi_staging',
    dbuser      => 'yabi',
    dbpass      => 'yabi',
    memcache    => 'localhost:11211',
    secret_key  => 'isbfiusbef)#$)(#)((@',
    admin_email => 'root@localhost',
    allowed_hosts => '.ccgapps.com.au localhost',
  }

  $packages = ['python27-psycopg2', 'rabbitmq-server']
  package {$packages: ensure => installed}

  # fakes3 is required for tests
  package {'fakes3':
    ensure     => installed,
    provider   => gem
  }

  ccgdatabase::postgresql::db { $django_config['dbname']:
    user     => $django_config['dbuser'],
    password => $django_config['dbpass'],
  }

  package {'yabi-admin': ensure => installed, provider => 'yum_nogpgcheck'}

  django::config { 'yabi':
    config_hash => $django_config,
  }

  django::syncdbmigrate{'yabi':
    dbsync  => true,
    notify  => Service[$ccgapache::params::service_name],
    require => [
      Ccgdatabase::Postgresql::Db[$django_config['dbname']],
      Package['yabi-admin'],
      Django::Config['yabi'] ]
  }

  package {'yabi-shell': provider => yum_nogpgcheck}

  service { 'rabbitmq-server':
    ensure     => 'running',
    enable     => true,
    hasstatus  => true,
    hasrestart => true,
    name       => 'rabbitmq-server',
    require    => Package[$packages]
  }

  service { 'celeryd':
    ensure     => 'running',
    enable     => true,
    hasstatus  => true,
    hasrestart => true,
    name       => 'celeryd',
    require    => [
      Service['rabbitmq-server'],
      Package[$packages],
      Ccgdatabase::Postgresql::Db[$django_config['dbname']],
      Package['yabi-admin'],
      Django::Config['yabi'] ]
  }

  logrotate::rule { 'celery':
    path          => '/var/log/celery/*log',
    rotate        => 7,
    rotate_every  => 'day',
    compress      => true,
    delaycompress => true,
    ifempty       => true,
    create        => true,
    create_mode   => '0664',
    create_owner  => 'celery',
    create_group  => 'celery',
  }
}
