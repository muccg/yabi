#
node default {
<<<<<<< HEAD
  $custom_hostname = 'aws-syd-yabi-staging.ec2.ccgapps.com.au'

=======
>>>>>>> 909d81c7f7953a3bfadeb5c0525f54e0cac24b48
  include ccgcommon
  include ccgcommon::source
  include ccgapache
  include python
<<<<<<< HEAD
  include repo::sydney
  include repo::upgrade
  include repo::repo::ius
  include repo::repo::ccgtesting
  include repo::repo::ccgdeps
  class { 'yum::repo::pgdg93':
    stage => 'setup',
  }
  include globals
  include ccgdatabase::postgresql::devel
  include profile::rsyslog

  # There are some leaked local secrets here we don't care about
  $django_config = {
    deployment  => 'staging',
    dbdriver    => 'django.db.backends.postgresql_psycopg2',
    dbhost      => '',
    dbname      => 'yabi_staging',
    dbuser      => 'yabi',
    dbpass      => 'yabi',
    memcache    => $globals::memcache_syd,
    secret_key  => 'isbfiusbef)#$)(#)((@',
    admin_email => $globals::system_email,
    allowed_hosts => '.ccgapps.com.au localhost',
  }

=======
  include repo::epel
  include repo::ius
  include repo::pgrpms
  include repo::ccgtesting
  include globals

  # There are some leaked local secrets here we don't care about
  $django_config = {
    'deployment'  => 'staging',
    'dbdriver'    => 'django.db.backends.postgresql_psycopg2',
    'dbhost'      => '',
    'dbname'      => 'yabi_staging',
    'dbuser'      => 'yabi',
    'dbpass'      => 'yabi',
    'memcache'    => $globals::memcache_syd,
    'secretkey'   => 'isbfiusbef)#$)(#)((@',
    'admin_email' => $globals::system_email,
    custom_installroot => '/usr/local/webapps/yabiadmin/lib/python2.7/site-packages',
  }

  $celery_settings = {
    'configdir'  => '/etc/yabiadmin',
  }

  # celery config is the base django_config plus other settings
  $celery_config = merge($django_config, $celery_settings)

  class {'postgresql':
    datadir              => '/var/lib/pgsql/9.3/data',
    bindir               => '/usr/pgsql-9.3/bin',
    client_package_name  => 'postgresql93',
    server_package_name  => 'postgresql93-server',
    devel_package_name   => 'postgresql93-devel',
    service_name         => 'postgresql-9.3',
  }

  include postgresql::devel

>>>>>>> 909d81c7f7953a3bfadeb5c0525f54e0cac24b48
  $packages = ['python27-psycopg2', 'rabbitmq-server']
  package {$packages: ensure => installed}

  # tests need firefox and a virtual X server
<<<<<<< HEAD
  $testingpackages = ['xorg-x11-server-Xvfb', 'dbus-x11']
=======
  $testingpackages = ['firefox', 'xorg-x11-server-Xvfb', 'dbus-x11']
>>>>>>> 909d81c7f7953a3bfadeb5c0525f54e0cac24b48
  package {$testingpackages:
    ensure => installed,
  }

<<<<<<< HEAD
  # TODO
  # Remove the specific version when the problem described below is solved:
  # https://support.mozilla.org/en-US/questions/1025819?esab=a&s=gdk_window_get_visual&r=0&as=s
  package {'firefox':
    ensure => '31.1.0-5.el6.centos',
  }

=======
>>>>>>> 909d81c7f7953a3bfadeb5c0525f54e0cac24b48
  # fakes3 is required for tests
  package {'fakes3':
    ensure     => installed,
    provider   => gem
  }

  # TODO Need to port this across
  # drop in auth details for e2e tests
  #file {'/usr/local/src/yabi':
  #  ensure => directory
  #} ->
  #file {'/usr/local/src/yabi/staging_tests.conf':
  #  source => 'puppet:///modules/staging/yabi_staging_tests.conf'
  #}

<<<<<<< HEAD
  ccgdatabase::postgresql::db { $django_config['dbname']:
=======
  ccgdatabase::postgresql { $django_config['dbname']:
>>>>>>> 909d81c7f7953a3bfadeb5c0525f54e0cac24b48
    user     => $django_config['dbuser'],
    password => $django_config['dbpass'],
  }

  package {'yabi-admin': ensure => installed, provider => 'yum_nogpgcheck'}

  django::config { 'yabiadmin':
    config_hash => $django_config,
  }

<<<<<<< HEAD
  django::syncdbmigrate{'yabiadmin':
    dbsync  => true,
    notify  => Service[$ccgapache::params::service_name],
    require => [
      Ccgdatabase::Postgresql::Db[$django_config['dbname']],
=======
  django::config { 'yabicelery':
    config_hash => $celery_config,
  }

  django::syncdbmigrate{'yabiadmin':
    dbsync  => true,
    require => [
      Ccgdatabase::Postgresql[$django_config['dbname']],
>>>>>>> 909d81c7f7953a3bfadeb5c0525f54e0cac24b48
      Package['yabi-admin'],
      Django::Config['yabiadmin'] ]
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
<<<<<<< HEAD
      Ccgdatabase::Postgresql::Db[$django_config['dbname']],
      Package['yabi-admin'],
      Django::Config['yabiadmin'] ]
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
=======
      Ccgdatabase::Postgresql[$django_config['dbname']],
      Package['yabi-admin'],
      Django::Config['yabicelery'] ]
>>>>>>> 909d81c7f7953a3bfadeb5c0525f54e0cac24b48
  }
}
