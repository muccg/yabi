#
node default {
  include globals
  include ccgcommon
  include ccgcommon::source
  include ccgapache
  include python
  include repo::epel
  include repo::ius
  include repo::pgrpms
  include repo::ccgcentos
  include globals

  $django_config = {
    deployment  => 'prod',
    release     => '7.2.5-1',
    dbdriver    => 'django.db.backends.postgresql_psycopg2',
    dbserver    => $globals::dbhost_postgresql_ccg_prod,
    dbhost      => $globals::dbhost_postgresql_ccg_prod,
    dbname      => 'live_yabi',
    dbuser      => $globals::dbuser_syd_prod,
    dbpass      => $globals::dbpass_syd_prod,
    memcache    => $globals::memcache_syd,
    secret_key  => $globals::secretkey_ccg_yabi,
    admin_email => $globals::system_email,
    allowed_hosts => 'ccg.murdoch.edu.au localhost'
  }

  $packages = ['python27-psycopg2', 'rabbitmq-server']
  package {$packages: ensure => installed}

  package {'yabi-admin': 
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

  package {'yabi-shell': provider => yum_nogpgcheck}

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
}
