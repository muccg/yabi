#
node default {
  include globals
  include ccgcommon
  include ccgcommon::source
  include ccgapache
  include python
  include repo::sydney
  include repo::repo::ius
  include repo::repo::ccgcentos
  include repo::repo::ccgdeps
  class { 'yum::repo::pgdg93':
    stage => 'setup',
  }
  include globals
  include profile::rsyslog

  $django_config = {
    deployment            => 'prod',
    release               => '9.3.0-1',
    dbdriver              => 'django.db.backends.postgresql_psycopg2',
    dbserver              => $globals::dbhost_rds_syd_postgresql_prod,
    dbhost                => $globals::dbhost_rds_syd_postgresql_prod,
    dbname                => 'yabiadmin_prod',
    dbuser                => $globals::dbuser_syd_prod,
    dbpass                => $globals::dbpass_syd_prod,
    memcache              => $globals::memcache_syd,
    secret_key            => $globals::secretkey_aws_yabi,
    admin_email           => $globals::system_email,
    allowed_hosts         => '.ccgapps.com.au localhost',
    aws_access_key_id     => $globals::yabi_aws_access_key_id,
    aws_secret_access_key => $globals::yabi_aws_secret_access_key,
  }

  $packages = ['python27-psycopg2', 'rabbitmq-server']
  package {$packages: ensure => installed}

  package {'yabi-admin':
    ensure => $django_config['release'],
    provider => 'yum_nogpgcheck'
  }

  package {'yabi-shell':
    ensure => $django_config['release'],
    provider => 'yum_nogpgcheck'
  }

  django::config { 'yabiadmin':
    config_hash => $django_config,
  }

  # Disabled until releasing on this branch
  django::syncdbmigrate{'yabiadmin':
    dbsync  => true,
    require => [
      Package['yabi-admin'],
      Django::Config['yabiadmin'] ]
  }

  service { 'rabbitmq-server':
    ensure     => 'running',
    enable     => true,
    hasstatus  => true,
    hasrestart => true,
    name       => 'rabbitmq-server',
    require    => Package[$packages]
  }

  # Disabled until releasing on this branch
  #service { 'celeryd':
  #  ensure     => 'running',
  #  enable     => true,
  #  hasstatus  => true,
  #  hasrestart => true,
  #  name       => 'celeryd',
  #  require    => [
  #    Service['rabbitmq-server'],
  #    Package[$packages],
  #    Ccgdatabase::Postgresql[$django_config['dbname']],
  #    Package['yabi-admin'] ]
  #}

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
